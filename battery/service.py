"""One synchronized pipeline shared by simulation and ESP32 input."""

import copy
import logging
import threading
import time
import uuid
from datetime import datetime, timezone

from ai.predictor import RuntimePredictor
from battery.analytics import BatteryAnalytics
from battery.power_manager import POLICIES, recommendations, select_policy
from battery.simulator import BatterySimulator
from database.db import Database


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class BatteryService:
    def __init__(self, database_path, model_path):
        self.db = Database(database_path)
        self.predictor = RuntimePredictor(model_path)
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.thread = None
        self.last_error = None
        self.last_sim_time = None
        self.last_esp_time = None
        self._restore(self.db.load_state() or {})

    def _restore(self, state):
        self.controls = state.get("controls", {"simulation_enabled": True, "device_load": "MEDIUM", "time_scale": 120})
        self.source = state.get("source", "simulation")
        self.latest = state.get("latest")
        self.simulator = BatterySimulator(state.get("simulator"))
        self.analytics = {source: BatteryAnalytics(state.get("analytics", {}).get(source))
                          for source in ("simulation", "esp32")}
        self.sessions = state.get("sessions", {source: uuid.uuid4().hex for source in self.analytics})
        self.modes = state.get("modes", {source: "BALANCED" for source in self.analytics})
        self.hot = state.get("hot", {source: False for source in self.analytics})

    def _state(self):
        return {"controls": self.controls, "source": self.source, "latest": self.latest,
                "simulator": self.simulator.export(), "sessions": self.sessions,
                "analytics": {key: value.export() for key, value in self.analytics.items()},
                "modes": self.modes, "hot": self.hot}

    def _transaction(self, operation):
        """Rollback in-memory integration if SQLite cannot commit the sample."""
        before = copy.deepcopy(self._state())
        times = self.last_sim_time, self.last_esp_time
        try:
            return operation()
        except Exception:
            self._restore(before)
            self.last_sim_time, self.last_esp_time = times
            raise

    def _process(self, sample, dt, events=None, quality=None):
        events = list(events or [])
        now = utc_now()
        source = sample["source"]
        reading = self.analytics[source].process({**sample, "timestamp": now}, dt)
        reading.update(self.predictor.predict(reading))
        policy = select_policy(reading, self.modes[source])
        reading.update({"power_mode": policy["mode"], "policy": policy,
                        "session_id": self.sessions[source], "quality_note": quality or "",
                        "integration_seconds": round(dt, 3),
                        "time_scale": self.controls["time_scale"] if source == "simulation" else 1})
        reading["recommendations"] = recommendations(reading)
        reading["recommendation"] = reading["recommendations"][0]
        if policy["mode"] != self.modes[source]:
            events.append((now, f"Power mode changed from {self.modes[source]} to {policy['mode']} ({source}).", "info"))
            events.append((now, "Energy optimization policy selected: " + "; ".join(policy["actions"]), "info"))
        abnormal = sample["temperature"] >= 36 or sample["temperature"] <= 0
        if abnormal and not self.hot[source]:
            events.append((now, f"Abnormal temperature detected: {sample['temperature']:.1f} °C ({source}).", "warning"))
        elif self.hot[source] and not abnormal:
            events.append((now, f"Temperature returned to the normal demo range ({source}).", "info"))
        self.hot[source] = abnormal
        self.modes[source] = policy["mode"]
        events.append((now, f"Telemetry sample received ({source}); runtime updated via {reading['runtime_method']}.", "info"))
        if quality:
            events.append((now, quality, "warning"))
        self.source, self.latest = source, reading
        self.db.save(self._state(), events, reading)
        self.last_error = None
        return copy.deepcopy(reading)

    def tick(self, now=None):
        """Called by a single worker, never by GET /api/telemetry."""
        with self.lock:
            if not self.controls["simulation_enabled"]:
                self.last_sim_time = None
                return None

            def operation():
                tick_time = time.monotonic() if now is None else now
                # Do not invent hours of consumption after computer sleep or restart.
                real_dt = 0 if self.last_sim_time is None else max(0, min(5, tick_time - self.last_sim_time))
                dt = real_dt * self.controls["time_scale"]
                sample = self.simulator.sample(dt, self.controls["device_load"],
                                               POLICIES[self.modes["simulation"]]["current_factor"])
                self.last_sim_time = tick_time
                return self._process(sample, dt)

            return self._transaction(operation)

    def receive(self, sample, now=None):
        with self.lock:
            def operation():
                tick_time = time.monotonic() if now is None else now
                dt = 0 if self.last_esp_time is None else max(0, tick_time - self.last_esp_time)
                quality = None
                if dt > 60:
                    dt = 0
                    quality = "ESP32 gap exceeded 60 seconds; unknown gap energy was not integrated."
                events = []
                if self.controls["simulation_enabled"]:
                    events.append((utc_now(), "ESP32 telemetry received; simulation paused to keep sources separate.", "info"))
                self.controls["simulation_enabled"] = False
                self.last_sim_time = None
                self.last_esp_time = tick_time
                return self._process(sample, dt, events, quality)

            return self._transaction(operation)

    def control(self, changes):
        with self.lock:
            def operation():
                events = []
                if changes.get("reset"):
                    self.simulator = BatterySimulator()
                    self.analytics["simulation"] = BatteryAnalytics()
                    self.sessions["simulation"] = uuid.uuid4().hex
                    self.modes["simulation"] = "BALANCED"
                    self.hot["simulation"] = False
                    self.last_sim_time = None
                    if self.source == "simulation":
                        self.latest = None
                    events.append((utc_now(), "Simulation reset to 78% charge; a new session started. Stored history retained.", "info"))
                for key in ("simulation_enabled", "device_load"):
                    if key in changes and self.controls[key] != changes[key]:
                        self.controls[key] = changes[key]
                        events.append((utc_now(), f"Demo control changed: {key} = {changes[key]}", "info"))
                        if key == "simulation_enabled":
                            self.last_sim_time = None
                            self.last_esp_time = None
                            if changes[key]:
                                self.source, self.latest = "simulation", None
                self.db.save(self._state(), events)
            self._transaction(operation)
            return self.snapshot()

    def snapshot(self, limit=60):
        with self.lock:
            age = None
            if self.latest:
                age = max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(self.latest["timestamp"])).total_seconds())
            state = ("ERROR" if self.last_error else
                     "PAUSED" if self.source == "simulation" and not self.controls["simulation_enabled"] else
                     "WAITING" if self.latest is None else
                     "STALE" if age > (10 if self.source == "simulation" else 30) else "ONLINE")
            points = self.db.history(self.source, self.sessions[self.source], limit)
            chart_keys = ("id", "timestamp", "soc", "voltage", "current", "temperature", "power")
            return {"status": "success", "telemetry": copy.deepcopy(self.latest),
                    "system": {"status": state, "source": self.source, "sample_age_seconds": age,
                               "message": self.last_error or "", "poll_interval_seconds": 2},
                    "controls": dict(self.controls),
                    "history": [{key: point[key] for key in chart_keys} for point in points],
                    "activity": self.db.events(),
                    "model": {"available": self.predictor.model is not None,
                              "reason": self.predictor.reason, "metadata": self.predictor.metadata}}

    def start(self):
        with self.lock:
            if self.thread and self.thread.is_alive():
                return
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, name="battery-simulator", daemon=True)
            self.thread.start()

    def _run(self):
        while not self.stop_event.is_set():
            try:
                self.tick()
            except Exception:
                logging.exception("Telemetry worker failed")
                with self.lock:
                    self.last_error = "Telemetry processing failed. Check the server log."
            self.stop_event.wait(2)

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
