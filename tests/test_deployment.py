import os
import runpy
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app import ROOT, app, create_app


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.application = create_app({"TESTING": True, "START_WORKER": False,
                                       "DATABASE_PATH": Path(self.folder.name) / "battery.db"})
        self.client = self.application.test_client()
        self.service = self.application.extensions["battery_service"]

    def tearDown(self):
        self.service.stop()
        self.folder.cleanup()

    def test_wsgi_export_and_health(self):
        self.assertTrue(callable(app))
        initial_id = self.service.latest["id"]
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "healthy", "model": "loaded", "database": "connected"})
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        with self.service.db.connection() as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0], 1)
        self.assertEqual(self.service.latest["id"], initial_id)

    def test_health_preserves_fallback_and_reports_db_failure(self):
        self.service.predictor.model = None
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "degraded")
        self.assertEqual(response.json["model"], "fallback")
        with patch.object(self.service.db, "connection", side_effect=sqlite3.OperationalError("test")):
            response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["database"], "unavailable")

    def test_environment_storage_and_model_paths(self):
        with patch.dict(os.environ, {"DATA_DIR": self.folder.name, "MODEL_PATH": "models/runtime_model.pkl"}):
            os.environ.pop("DATABASE_PATH", None)
            configured = create_app({"START_WORKER": False})
        self.assertEqual(configured.config["DATABASE_PATH"], Path(self.folder.name) / "battery.db")
        self.assertEqual(configured.config["MODEL_PATH"], ROOT / "models/runtime_model.pkl")
        self.assertIsNotNone(configured.extensions["battery_service"].predictor.model)
        with patch.dict(os.environ, {"DATABASE_PATH": str(Path(self.folder.name) / "override.db")}):
            overridden = create_app({"START_WORKER": False})
        self.assertEqual(overridden.config["DATABASE_PATH"].name, "override.db")

    def test_gunicorn_bind_and_worker_lifecycle(self):
        with patch.dict(os.environ, {"PORT": "12345"}):
            settings = runpy.run_path(str(ROOT / "gunicorn.conf.py"))
        self.assertEqual(settings["bind"], "0.0.0.0:12345")
        self.assertEqual(settings["workers"], 1)
        self.assertFalse(settings["preload_app"])
        service = Mock()
        worker = SimpleNamespace(wsgi=SimpleNamespace(extensions={"battery_service": service}))
        settings["post_worker_init"](worker)
        settings["worker_exit"](None, worker)
        service.start.assert_called_once()
        service.stop.assert_called_once()

    def test_light_template_has_no_prototype_banner(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn('name="color-scheme" content="light"', html)
        self.assertNotIn('class="demo-note"', html)
        self.assertNotIn("SoC and SoH are estimates. Runtime uses", html)
        for identity in ("system-status", "data-source", "model-status"):
            self.assertEqual(html.count(f'id="{identity}"'), 1)


if __name__ == "__main__":
    unittest.main()
