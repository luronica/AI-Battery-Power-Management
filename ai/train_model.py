"""Train and evaluate a runtime forest against an independent synthetic holdout."""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from ai.features import FEATURES
from ai.generate_dataset import generate

ROOT = Path(__file__).resolve().parents[1]


def train():
    dataset = ROOT / "data/battery_training_data.csv"
    if not dataset.exists():
        generate(dataset)
    data = np.loadtxt(dataset, delimiter=",", skiprows=1)
    x_train, x_test, y_train, y_test = train_test_split(
        data[:, :-1], data[:, -1], test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=120, max_depth=18,
                                  min_samples_leaf=2, random_state=42, n_jobs=1)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    # Transparent non-ML comparator on exactly the same held-out rows.
    baseline = np.clip(2 * x_test[:, 4] / 100 * x_test[:, 3] / 100
                       / (0.7 * x_test[:, 1] + 0.3 * x_test[:, 6]), 0, 48)
    metrics = {"mae_hours": float(mean_absolute_error(y_test, predictions)),
               "rmse_hours": float(np.sqrt(mean_squared_error(y_test, predictions))),
               "r2": float(r2_score(y_test, predictions)),
               "baseline_mae_hours": float(mean_absolute_error(y_test, baseline))}
    metadata = {"model": "RandomForestRegressor", "features": FEATURES,
                "metrics": metrics, "training_rows": len(x_train), "test_rows": len(x_test),
                "seed": 42, "trees": 120, "sklearn_version": sklearn.__version__,
                "trained_at": datetime.now(timezone.utc).isoformat(),
                "dataset": "Independent synthetic scenarios; 80/20 held-out split",
                "target_unit": "hours", "runtime_cap_hours": 48,
                "limitations": "Synthetic holdout accuracy is not real-battery validation.",
                "feature_importances": dict(zip(FEATURES, model.feature_importances_.tolist()))}
    folder = ROOT / "models"
    folder.mkdir(exist_ok=True)
    temporary = folder / "runtime_model.tmp"
    joblib.dump({"model": model, "metadata": metadata, "features": FEATURES}, temporary, compress=3)
    temporary.replace(folder / "runtime_model.pkl")
    (folder / "model_metrics.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return metadata


if __name__ == "__main__":
    train()
