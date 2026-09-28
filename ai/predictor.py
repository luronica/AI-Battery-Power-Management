"""Load only the locally trained artifact; degrade to a bounded physical estimate."""

import math
import logging
import warnings

import joblib
import sklearn

from ai.features import FEATURES
from battery.analytics import NOMINAL_CAPACITY_AH


class RuntimePredictor:
    def __init__(self, path):
        self.model = None
        self.metadata = None
        self.reason = "Model is unavailable. Train it with python -m ai.train_model."
        try:
            # Pickle/joblib files must be trusted: this path is never taken from API input.
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                artifact = joblib.load(path)
            if artifact["features"] != FEATURES:
                raise ValueError("Feature schema mismatch")
            if artifact["metadata"]["sklearn_version"] != sklearn.__version__:
                raise ValueError("Retrain with the installed scikit-learn version")
            if artifact["model"].n_features_in_ != len(FEATURES):
                raise ValueError("Model feature count mismatch")
            self.model = artifact["model"]
            self.metadata = artifact["metadata"]
            self.reason = "Loaded locally trained synthetic-data model."
        except Exception as error:
            logging.exception("Runtime model loading failed: %s", path)
            self.reason = f"Model unavailable ({type(error).__name__}); calculated fallback in use."

    @staticmethod
    def fallback(reading):
        draw = max(0.015, 0.7 * reading["current"] + 0.3 * reading["recent_average_current"])
        charge = NOMINAL_CAPACITY_AH * reading["soh"] / 100 * reading["soc"] / 100
        return min(48.0, max(0.0, charge / draw))

    def predict(self, reading):
        reason = self.reason
        in_domain = (3.0 <= reading["voltage"] <= 4.2
                     and 0.015 <= reading["current"] <= 0.5
                     and 15 <= reading["temperature"] <= 40
                     and 0.5 <= reading["soc"] <= 100
                     and 60 <= reading["soh"] <= 100
                     and 0.015 <= reading["recent_average_current"] <= 0.5)
        if self.model is not None and in_domain:
            try:
                result = float(self.model.predict([[reading[name] for name in FEATURES]])[0])
                if not math.isfinite(result) or result < 0:
                    raise ValueError("Invalid model output")
                return {"predicted_runtime": round(min(result, 48), 4),
                        "model_status": "ACTIVE", "runtime_method": "ML regression",
                        "model_reason": "Synthetic-data Random Forest prediction; hours at current operating conditions."}
            except Exception:
                logging.exception("Runtime model prediction failed")
                reason = "Prediction failed; calculated fallback in use."
        elif self.model is not None:
            reason = "Outside the model training range; calculated fallback in use."
        return {"predicted_runtime": round(self.fallback(reading), 4),
                "model_status": "FALLBACK", "runtime_method": "Calculated estimate",
                "model_reason": reason + " Estimates are capped at 48 hours."}
