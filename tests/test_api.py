import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from app import create_app
from battery.service import BatteryService

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = {"voltage": 3.85, "current": 0.12, "temperature": 29.5,
          "device_load": 0.45, "source": "esp32"}


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "battery.db"
        self.app = create_app({"TESTING": True, "START_WORKER": False,
                               "DATABASE_PATH": self.path})
        self.service = self.app.extensions["battery_service"]
        self.client = self.app.test_client()

    def tearDown(self):
        self.service.stop()
        self.folder.cleanup()

    def test_routes_and_read_only_get(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        for path in ("/static/css/style.css", "/static/js/dashboard.js"):
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, "text/javascript" if path.endswith(".js") else "text/css")
        self.assertEqual(self.client.get("/api/missing").status_code, 404)
        self.assertEqual(self.client.get("/api/telemetry").json["system"]["status"], "ONLINE")
        self.service.tick(0)
        self.service.tick(2)
        first = self.client.get("/api/telemetry").json
        second = self.client.get("/api/telemetry").json
        self.assertEqual(first["telemetry"]["id"], second["telemetry"]["id"])
        self.assertEqual(len(second["history"]), 3)
        self.assertGreater(first["telemetry"]["energy_consumed"], 0)
        self.assertEqual(first["telemetry"]["model_status"], "ACTIVE")
        for limit in ("0", "61", "abc", "1.2", "-1", "²", "9" * 5000):
            self.assertEqual(self.client.get("/api/telemetry?limit=" + limit).status_code, 400)

    def test_esp32_post_and_source_isolation(self):
        self.service.tick(0)
        self.service.tick(2)
        response = self.client.post("/api/telemetry", json=SAMPLE)
        self.assertEqual(response.status_code, 201)
        reading = response.json
        self.assertAlmostEqual(reading["power"], 3.85 * 0.12)
        self.assertEqual(reading["energy_consumed"], 0)
        self.assertEqual(reading["source"], "esp32")
        self.assertEqual(reading["model_status"], "ACTIVE")
        self.assertFalse(self.service.controls["simulation_enabled"])
        self.assertIsNone(self.service.tick(4))
        snapshot = self.client.get("/api/telemetry").json
        self.assertEqual(len(snapshot["history"]), 1)
        with self.service.db.connection() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0], 4)

    def test_input_validation_and_size_limit(self):
        for payload in ([], None, {}, {**SAMPLE, "voltage": "3.85"},
                        {**SAMPLE, "current": True}, {**SAMPLE, "temperature": float("nan")},
                        {**SAMPLE, "current": -1}, {**SAMPLE, "voltage": float("inf")},
                        {**SAMPLE, "voltage": 10 ** 500},
                        {**SAMPLE, "device_load": 5}, {**SAMPLE, "source": "simulation"},
                        {**SAMPLE, "unknown": 1}):
            with self.subTest(payload=payload):
                # Explicit null body avoids Flask test client's no-json special case.
                import json
                result = self.client.post("/api/telemetry", data=json.dumps(payload), content_type="application/json")
                self.assertEqual(result.status_code, 400)
        self.assertEqual(self.client.post("/api/telemetry", data="{}").status_code, 415)
        self.assertEqual(self.client.post("/api/telemetry", data="{", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/telemetry", data=" " * 5000, content_type="application/json").status_code, 413)

    def test_controls_pause_resume_reset(self):
        first = self.service.tick(0)
        self.service.tick(2)
        response = self.client.post("/api/control", json={"simulation_enabled": False})
        self.assertEqual(response.json["system"]["status"], "PAUSED")
        self.assertIsNone(self.service.tick(20))
        self.client.post("/api/control", json={"simulation_enabled": True, "device_load": "HIGH"})
        resumed = self.service.tick(100)
        self.assertEqual(resumed["integration_seconds"], 0)
        self.assertEqual(resumed["device_load"], 0.9)
        reset = self.client.post("/api/control", json={"reset": True}).json["telemetry"]
        self.assertEqual(reset["energy_consumed"], 0)
        self.assertNotEqual(reset["session_id"], first["session_id"])
        self.assertEqual(len(self.service.snapshot()["history"]), 1)
        for payload in ({}, {"simulation_enabled": "yes"}, {"device_load": "EXTREME"}, {"reset": 1}, {"other": 1}):
            self.assertEqual(self.client.post("/api/control", json=payload).status_code, 400)

    def test_restart_restores_state_and_no_downtime_energy(self):
        self.service.tick(0)
        latest = self.service.tick(2)
        restored = BatteryService(self.path, ROOT / "models/runtime_model.pkl")
        self.assertEqual(restored.snapshot()["telemetry"]["id"], latest["id"])
        resumed = restored.tick(1000)
        self.assertEqual(resumed["energy_consumed"], latest["energy_consumed"])
        self.assertEqual(resumed["session_id"], latest["session_id"])

    def test_real_time_integrator_gap_and_stale(self):
        self.service.receive(SAMPLE, now=0)
        reading = self.service.receive(SAMPLE, now=30)
        self.assertAlmostEqual(reading["energy_consumed"], 0.462 * 30 / 3600, places=6)
        gap = self.service.receive(SAMPLE, now=200)
        self.assertEqual(gap["energy_consumed"], reading["energy_consumed"])
        self.assertIn("gap", gap["quality_note"])
        self.service.latest["timestamp"] = (datetime.now(timezone.utc) - timedelta(seconds=31)).isoformat()
        self.assertEqual(self.service.snapshot()["system"]["status"], "STALE")

    def test_db_failure_rolls_back_estimation(self):
        self.service.tick(0)
        before = self.service.analytics["simulation"].export()
        with patch.object(self.service.db, "save", side_effect=sqlite3.OperationalError("test failure")):
            with self.assertRaises(sqlite3.OperationalError):
                self.service.tick(2)
        self.assertEqual(before, self.service.analytics["simulation"].export())
        self.assertEqual(self.service.last_sim_time, 0)

    def test_concurrent_posts_and_history_bound(self):
        with ThreadPoolExecutor(max_workers=4) as executor:
            readings = list(executor.map(lambda _: self.service.receive(SAMPLE), range(65)))
        self.assertEqual(len(set(x["id"] for x in readings)), 65)
        self.assertEqual(len(self.service.snapshot()["history"]), 60)

    def test_temperature_event_and_fallback(self):
        response = self.client.post("/api/telemetry", json={**SAMPLE, "temperature": 50})
        self.assertEqual(response.json["power_mode"], "CRITICAL")
        self.assertEqual(response.json["model_status"], "FALLBACK")
        self.assertTrue(any("temperature detected" in item["message"] for item in self.service.db.events()))


if __name__ == "__main__":
    unittest.main()
