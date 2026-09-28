"""Reproducible independent synthetic operating scenarios, not measured cells."""

import csv
from pathlib import Path

import numpy as np

from ai.features import FEATURES
from battery.analytics import NOMINAL_CAPACITY_AH, soc_voltage

ROOT = Path(__file__).resolve().parents[1]


def generate(path=ROOT / "data/battery_training_data.csv", count=16000, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(count):
        soc = rng.uniform(0.5, 100)
        soh = rng.uniform(60, 100)
        load = rng.uniform(0, 1)
        factor = rng.choice([1.0, 0.82, 0.55, 0.25])
        current = float(np.clip((0.055 + 0.44 * load) * factor + rng.normal(0, 0.006), 0.015, 0.5))
        average_current = float(np.clip(current * rng.uniform(0.75, 1.25), 0.015, 0.5))
        temperature = float(np.clip(25 + current * 28 + rng.normal(0, 4), 15, 40))
        voltage = float(np.clip(soc_voltage(soc) - current * 0.08 + rng.normal(0, 0.006), 3.0, 4.2))
        average_power = average_current * float(np.clip(voltage + rng.normal(0, 0.015), 3.0, 4.2))
        # A synthetic future discharge assumption with modest unobserved variation.
        effective_draw = 0.7 * current + 0.3 * average_current
        thermal_efficiency = 1 - 0.004 * abs(temperature - 25)
        activity_efficiency = 0.98 - 0.04 * load
        runtime = NOMINAL_CAPACITY_AH * soh / 100 * soc / 100 / effective_draw
        runtime *= thermal_efficiency * activity_efficiency * rng.normal(1, 0.025)
        values = [voltage, current, temperature, soc, soh, voltage * current,
                  average_current, average_power, load, float(np.clip(runtime, 0, 48))]
        rows.append(values)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FEATURES + ["runtime_hours"])
        writer.writerows(rows)
    return path


if __name__ == "__main__":
    print(f"Generated synthetic scenarios: {generate()}")
