"""Explainable rule-based control using estimated and ML-derived inputs."""

POLICIES = {
    "PERFORMANCE": {"sampling_interval": 2, "communication_policy": "Wi-Fi always active",
                    "current_factor": 1.0, "actions": ["Full sensor sampling", "Full processing enabled"]},
    "BALANCED": {"sampling_interval": 5, "communication_policy": "Normal Wi-Fi; batch routine messages",
                 "current_factor": 0.82, "actions": ["Sample every 5 seconds", "Batch routine telemetry"]},
    "POWER SAVING": {"sampling_interval": 15, "communication_policy": "Transmit every 30 seconds",
                     "current_factor": 0.55, "actions": ["Reduce sensor sampling", "Disable nonessential processing"]},
    "CRITICAL": {"sampling_interval": 30, "communication_policy": "Essential alerts only; otherwise sleep",
                 "current_factor": 0.25, "actions": ["Essential sensing only", "Minimize radio and processor activity"]},
}


def select_policy(reading, previous_mode="BALANCED"):
    soc, runtime = reading["soc"], reading["predicted_runtime"]
    temperature, current = reading["temperature"], reading["current"]
    if soc <= 10 or runtime <= 0.25 or temperature >= 40 or temperature <= 0:
        mode, reason = "CRITICAL", "Critical charge, runtime, or temperature threshold reached."
    elif previous_mode == "CRITICAL" and (soc < 13 or runtime < 0.4 or temperature >= 38 or temperature <= 2):
        mode, reason = "CRITICAL", "Critical recovery margin has not yet been reached."
    elif soc <= 30 or runtime <= 1.5 or temperature >= 36 or current >= 0.40:
        mode, reason = "POWER SAVING", "Low reserve, short runtime, elevated temperature, or high current."
    elif previous_mode == "POWER SAVING" and (soc < 34 or runtime < 1.8 or temperature >= 34.5
                                              or current / POLICIES["POWER SAVING"]["current_factor"] >= 0.36):
        mode, reason = "POWER SAVING", "Retaining savings until recovery thresholds are met."
    elif soc >= (65 if previous_mode == "PERFORMANCE" else 70) and runtime >= 3 and temperature < 33 and reading["device_load"] >= 0.7:
        mode, reason = "PERFORMANCE", "High workload with healthy battery reserve and safe temperature."
    else:
        mode, reason = "BALANCED", "Normal load and battery conditions."
    policy = dict(POLICIES[mode])
    policy.update({"mode": mode, "reason": reason,
                   "estimated_energy_saving": round((1 - policy["current_factor"]) * 100),
                   "control_type": "SIMULATED POLICY"})
    return policy


def recommendations(reading):
    messages = []
    if reading["temperature"] >= 36:
        messages.append("Temperature is elevated. Reduce processing load and check the battery environment.")
    if reading["temperature"] <= 0:
        messages.append("Temperature is below the prototype operating range. Inspect the battery before continuing.")
    if reading["soc"] <= 10:
        messages.append("Battery reserve is critical. Keep essential sensing only and recharge the battery.")
    if reading["predicted_runtime"] <= 1.5:
        messages.append("Predicted runtime is low. Use power-saving operation and plan a recharge.")
    elif reading["power_mode"] == "POWER SAVING":
        messages.append("Retain reduced sampling and communication until battery and load recovery thresholds are met.")
    if reading["consumption_trend"] == "INCREASING" or reading["current"] >= 0.35:
        messages.append("Battery consumption is increasing or high. Reduce sensor sampling and communication frequency.")
    if not messages:
        messages.append("Battery level and temperature are within the normal demo range. "
                        + ("Performance operation supports the current high workload."
                           if reading["power_mode"] == "PERFORMANCE" else "Balanced operation is recommended."))
    return messages
