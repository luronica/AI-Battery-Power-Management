"""Understandable single-cell discharge estimates, not a calibrated BMS."""

import math
from collections import deque

NOMINAL_CAPACITY_AH = 2.0
USABLE_CAPACITY_AH = 1.88
# Illustrative resting-voltage curve for a single lithium-ion cell.
CURVE = [(3.0, 0), (3.3, 5), (3.5, 15), (3.65, 35),
         (3.75, 55), (3.85, 75), (4.0, 90), (4.2, 100)]


def interpolate(value, points):
    if value <= points[0][0]:
        return float(points[0][1])
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if value <= x1:
            return y0 + (y1 - y0) * (value - x0) / (x1 - x0)
    return float(points[-1][1])


def voltage_soc(voltage, current):
    return interpolate(voltage + current * 0.08, CURVE)


def soc_voltage(soc):
    return interpolate(soc, [(s, v) for v, s in CURVE])


class BatteryAnalytics:
    def __init__(self, state=None):
        state = state or {}
        self.soc = state.get("soc")
        self.energy = state.get("energy", 0.0)
        self.elapsed = state.get("elapsed", 0.0)
        self.previous = state.get("previous")
        self.recent = deque(state.get("recent", []), maxlen=12)

    def export(self):
        return {"soc": self.soc, "energy": self.energy, "elapsed": self.elapsed,
                "previous": self.previous, "recent": list(self.recent)}

    def process(self, sample, elapsed_seconds):
        voltage, current = sample["voltage"], sample["current"]
        power = voltage * current
        dt = max(0.0, elapsed_seconds)
        estimated_voltage_soc = voltage_soc(voltage, current)
        if self.soc is None:
            self.soc = estimated_voltage_soc
        if self.previous is not None and dt:
            average_current = (self.previous["current"] + current) / 2
            average_power = (self.previous["power"] + power) / 2
            self.energy += average_power * dt / 3600
            counted_soc = max(0.0, self.soc - average_current * dt / 3600
                              / USABLE_CAPACITY_AH * 100)
            # Slow voltage correction avoids replacing coulomb counting on each poll.
            correction = min(0.08, 1 - math.exp(-dt / 1800))
            self.soc = min(100.0, max(0.0, counted_soc
                           + correction * (estimated_voltage_soc - counted_soc)))
        if voltage <= 3.0:
            self.soc = 0.0
        self.elapsed += dt
        self.previous = {"current": current, "power": power}
        previous_average = (sum(x["current"] for x in self.recent) / len(self.recent)
                            if self.recent else current)
        self.recent.append(self.previous)
        avg_current = sum(x["current"] for x in self.recent) / len(self.recent)
        avg_power = sum(x["power"] for x in self.recent) / len(self.recent)
        trend = "STABLE"
        if current > previous_average * 1.15 + 0.005:
            trend = "INCREASING"
        elif current < previous_average * 0.85 - 0.005:
            trend = "DECREASING"
        temperature = sample["temperature"]
        condition = ("TEMPERATURE ALERT" if temperature >= 40 or temperature <= 0
                     else "LOW CHARGE" if self.soc <= 20 else "NORMAL ESTIMATED HEALTH")
        return {**sample, "soc": round(self.soc, 3),
                "soh": USABLE_CAPACITY_AH / NOMINAL_CAPACITY_AH * 100,
                "power": round(power, 6), "energy_consumed": round(self.energy, 6),
                "elapsed_battery_seconds": round(self.elapsed, 2),
                "recent_average_current": avg_current, "recent_average_power": avg_power,
                "consumption_trend": trend, "battery_condition": condition,
                "nominal_capacity_ah": NOMINAL_CAPACITY_AH,
                "estimated_usable_capacity_ah": USABLE_CAPACITY_AH}
