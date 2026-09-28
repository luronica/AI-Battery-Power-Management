"""Correlated load/current/voltage/temperature with integrated charge depletion."""

import math
import random

from battery.analytics import USABLE_CAPACITY_AH, soc_voltage

LOADS = {"LOW": 0.15, "MEDIUM": 0.45, "HIGH": 0.90}


class BatterySimulator:
    def __init__(self, state=None, seed=42):
        state = state or {}
        self.soc = state.get("soc", 85.0)
        self.current = state.get("current", 0.15)
        self.temperature = state.get("temperature", 28.4)
        self.random = random.Random(seed)

    def export(self):
        return {"soc": self.soc, "current": self.current, "temperature": self.temperature}

    def sample(self, elapsed_seconds, load="MEDIUM", current_factor=0.82):
        activity = LOADS[load]
        target = (0.055 + 0.44 * activity) * current_factor
        target += self.random.uniform(-0.004, 0.004)
        old_current = self.current
        self.current += (target - self.current) * 0.55
        dt = max(0.0, elapsed_seconds)
        consumed_ah = (old_current + self.current) / 2 * dt / 3600
        self.soc = max(0.0, self.soc - consumed_ah / USABLE_CAPACITY_AH * 100)
        if self.soc == 0:
            self.current = 0.0
        thermal_target = 25 + self.current * 28
        self.temperature += (thermal_target - self.temperature) * (1 - math.exp(-max(dt, 2) / 600))
        self.temperature += self.random.uniform(-0.025, 0.025)
        voltage = soc_voltage(self.soc) - self.current * 0.08 + self.random.uniform(-0.003, 0.003)
        return {"voltage": round(max(3.0, min(4.2, voltage)), 4),
                "current": round(self.current, 5), "temperature": round(self.temperature, 2),
                "device_load": activity, "source": "simulation"}
