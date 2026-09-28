"""Healthy demo lifecycle checks using disposable databases and real inference."""
import tempfile
import unittest
from pathlib import Path

from app import create_app
from battery.service import BatteryService

ROOT = Path(__file__).resolve().parents[1]


class DemoInitializationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "fresh.db"
        self.app = create_app({"TESTING": True, "START_WORKER": False,
                               "DATABASE_PATH": self.path})
        self.service = self.app.extensions["battery_service"]
        self.client = self.app.test_client()

    def tearDown(self):
        self.service.stop()
        self.folder.cleanup()

    def assertHealthy(self, snapshot):
        reading = snapshot["telemetry"]
        self.assertTrue(snapshot["controls"]["simulation_enabled"])
        self.assertEqual(snapshot["controls"]["device_load"], "MEDIUM")
        self.assertEqual(reading["source"], "simulation")
        self.assertTrue(80 <= reading["soc"] <= 90)
        self.assertEqual(reading["soh"], 94)
        self.assertTrue(3.9 <= reading["voltage"] <= 4.1)
        self.assertTrue(0.10 <= reading["current"] <= 0.20)
        self.assertTrue(27 <= reading["temperature"] <= 30)
        self.assertAlmostEqual(reading["power"], reading["voltage"] * reading["current"], places=6)
        self.assertGreater(reading["predicted_runtime"], 0)
        self.assertEqual(reading["model_status"], "ACTIVE")
        self.assertEqual(reading["power_mode"], "BALANCED")
        self.assertEqual(reading["energy_consumed"], 0)
        self.assertEqual(len(snapshot["history"]), 1)
        self.assertTrue(reading["recommendations"])

    def test_fresh_database_immediately_has_healthy_prediction(self):
        self.assertHealthy(self.client.get("/api/telemetry").json)
        self.assertEqual(self.client.get("/health").json["model"], "loaded")

    def test_reset_from_depleted_and_esp32_returns_processed_sample(self):
        old_session = self.service.sessions["simulation"]
        self.service.simulator.soc = 0
        self.service.tick(0)
        self.service.control({"device_load": "HIGH"})
        self.service.receive(dict(voltage=3, current=0, temperature=25,
                                  device_load=0.9, source="esp32"))
        esp_state = self.service.analytics["esp32"].export()
        response = self.client.post("/api/control", json={"reset": True})
        self.assertEqual(response.status_code, 200)
        self.assertHealthy(response.json)
        self.assertNotEqual(old_session, response.json["telemetry"]["session_id"])
        self.assertEqual(esp_state, self.service.analytics["esp32"].export())
        with self.service.db.connection() as connection:
            self.assertGreater(connection.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0], 1)

    def test_restart_recovers_depleted_simulation(self):
        self.service.simulator.soc = 0
        self.service.tick(0)
        old_session = self.service.sessions["simulation"]
        restored = BatteryService(self.path, ROOT / "models/runtime_model.pkl")
        self.assertHealthy(restored.snapshot())
        self.assertNotEqual(old_session, restored.sessions["simulation"])

    def test_loads_change_consumption_runtime_and_discharge_gradually(self):
        results = {}
        for load in ("LOW", "MEDIUM", "HIGH"):
            self.service.control({"reset": True})
            self.service.control({"device_load": load})
            previous = self.service.latest
            for second in range(0, 22, 2):
                reading = self.service.tick(second)
                self.assertGreater(reading["current"], 0)
                self.assertAlmostEqual(reading["power"], reading["voltage"] * reading["current"], places=6)
                self.assertLess(abs(reading["soc"] - previous["soc"]), 2)
                self.assertEqual(reading["model_status"], "ACTIVE")
                previous = reading
            results[load] = reading
        for lower, higher in (("LOW", "MEDIUM"), ("MEDIUM", "HIGH")):
            self.assertLess(results[lower]["current"], results[higher]["current"])
            self.assertLess(results[lower]["power"], results[higher]["power"])
            self.assertLess(results[lower]["energy_consumed"], results[higher]["energy_consumed"])
            self.assertGreater(results[lower]["soc"], results[higher]["soc"])
            self.assertGreater(results[lower]["predicted_runtime"], results[higher]["predicted_runtime"])

    def test_missing_model_keeps_healthy_calculated_fallback_and_logs_reason(self):
        with self.assertLogs(level="ERROR") as captured:
            service = BatteryService(Path(self.folder.name) / "fallback.db",
                                     Path(self.folder.name) / "missing.pkl")
        self.assertIn("FileNotFoundError", "\n".join(captured.output))
        reading = service.snapshot()["telemetry"]
        self.assertEqual(reading["model_status"], "FALLBACK")
        self.assertGreater(reading["predicted_runtime"], 0)
        self.assertGreater(reading["soc"], 80)
