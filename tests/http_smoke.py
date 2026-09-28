"""Check a running instance; use a temporary database because this posts data."""

import json
import sys
import time
import urllib.request


def check(base):
    def request(path, payload=None):
        req = urllib.request.Request(base.rstrip("/") + path,
                                     data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, response.read()

    def get_json(path, payload=None):
        status, body = request(path, payload)
        return status, json.loads(body)

    assert request("/")[0] == 200
    status, health = get_json("/health")
    assert status == 200 and health == {"status": "healthy", "model": "loaded", "database": "connected"}
    first = get_json("/api/telemetry")[1]
    assert first["telemetry"] and first["telemetry"]["model_status"] == "ACTIVE"
    time.sleep(2.2)
    assert get_json("/api/telemetry")[1]["telemetry"]["id"] > first["telemetry"]["id"]
    status, reading = get_json("/api/telemetry", {"voltage": 3.85, "current": 0.12,
                               "temperature": 29.5, "device_load": 0.45, "source": "esp32"})
    assert status == 201 and reading["model_status"] == "ACTIVE"
    assert reading["power"] == 0.462 and reading["predicted_runtime"] > 0
    state = get_json("/api/telemetry")[1]
    assert state["telemetry"]["id"] == reading["id"] and not state["controls"]["simulation_enabled"]
    status, state = get_json("/api/control", {"reset": True, "simulation_enabled": True, "device_load": "HIGH"})
    assert status == 200 and state["controls"]["device_load"] == "HIGH"
    print("PASS: homepage, health, live sampling, SQLite-backed history, ESP32 POST, model prediction, controls")


if __name__ == "__main__":
    check(sys.argv[1])
