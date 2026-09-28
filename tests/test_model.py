import tempfile
import unittest
from pathlib import Path

from ai.predictor import RuntimePredictor

ROOT = Path(__file__).resolve().parents[1]


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.sample = dict(voltage=3.85, current=0.12, temperature=29.5, soc=78, soh=94,
                           power=0.462, recent_average_current=0.12,
                           recent_average_power=0.462, device_load=0.45)

    def test_trained_model(self):
        predictor = RuntimePredictor(ROOT / "models/runtime_model.pkl")
        result = predictor.predict(self.sample)
        self.assertEqual(result["model_status"], "ACTIVE", predictor.reason)
        self.assertGreater(result["predicted_runtime"], 0)
        high_load = {**self.sample, "current": 0.4, "power": 1.54,
                     "recent_average_current": 0.4, "recent_average_power": 1.54, "device_load": 0.9}
        self.assertLess(predictor.predict(high_load)["predicted_runtime"], result["predicted_runtime"])
        metrics = predictor.metadata["metrics"]
        self.assertGreater(metrics["r2"], 0.85)
        self.assertLess(metrics["mae_hours"], 1)

    def test_missing_corrupt_and_out_of_domain(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing.pkl"
            self.assertEqual(RuntimePredictor(path).predict(self.sample)["model_status"], "FALLBACK")
            path.write_text("not a model", encoding="utf-8")
            self.assertEqual(RuntimePredictor(path).predict(self.sample)["model_status"], "FALLBACK")
        model = RuntimePredictor(ROOT / "models/runtime_model.pkl")
        self.assertEqual(model.predict({**self.sample, "temperature": 60})["model_status"], "FALLBACK")
        depleted = model.predict({**self.sample, "soc": 0, "current": 0})
        self.assertEqual(depleted["predicted_runtime"], 0)


if __name__ == "__main__":
    unittest.main()
