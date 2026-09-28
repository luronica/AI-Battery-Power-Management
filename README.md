# AI-Based Smart Battery-Aware Power Management System

**Intelligent Energy Monitoring & Adaptive Power Optimization for IoT Devices**

A working final-year engineering capstone prototype extending the original Flask dashboard. It runs without hardware using a correlated battery simulator, and accepts real ESP32 telemetry through the same processing pipeline.

The dashboard uses a professional light theme: white cards, a grey-blue workspace, blue navigation, semantic status badges, five live charts, and a recorded activity timeline. The former top prototype banner has been removed; technical assumptions and limitations remain documented below. Battery algorithms, telemetry APIs, model features, and the trained Random Forest are unchanged by the redesign.

## 1. Problem statement and objectives

Battery-powered IoT devices often use fixed sampling and communication schedules despite changing battery reserve, temperature, and workload. This project demonstrates how telemetry, battery estimates, a runtime regression model, and explainable control rules can help adapt those schedules.

Objectives:

- Monitor voltage, current, temperature, device activity, power, and accumulated energy.
- Estimate SoC using hybrid coulomb counting and voltage correction; estimate SoH from assumed usable capacity.
- Predict remaining runtime with a genuine scikit-learn regression model.
- Select PERFORMANCE, BALANCED, POWER SAVING, or CRITICAL using multiple inputs.
- Demonstrate reduced simulated current under energy-saving policies.
- Show live charts, recommendations, model metrics, and recorded system events.
- Accept validated ESP32 readings and store both sources in SQLite.

**This is not a production Battery Management System.** SoC and SoH are prototype estimates. The ML model is trained on synthetic data. Real battery validation requires calibrated sensing and experimental battery data. The application does not replace electrical protection hardware.

## 2. Architecture

```text
Simulated IoT device (120x battery clock) OR ESP32 (real time)
                            |
               Shared Flask processing service
                            |
      Battery analytics -> ML runtime prediction / fallback
                            |
             Rule-based power-management engine
                            |
              SQLite telemetry + state + events
                            |
             REST API -> live Chart.js dashboard
                            |
       Policy feeds back into simulated current consumption
```

The backend takes a simulation sample approximately every two wall-clock seconds. GET requests read existing data; opening more browser tabs does not increase discharge. One worker and a lock serialize simulation, controls, and ESP32 posts. Run a **single server process**; multiple workers would create competing simulators.

## 3. Technology stack and project structure

- Frontend: HTML, CSS, plain JavaScript; locally bundled Chart.js 4.4.8.
- Backend: Python 3.10, Flask; Gunicorn for Linux deployment.
- AI: NumPy, scikit-learn `RandomForestRegressor`, joblib.
- Storage: Python's built-in `sqlite3`.
- Tests: Python `unittest`; optional real-browser smoke test using Node and installed Edge/Chrome.
- Development: VS Code. No npm installation, Firebase, or frontend framework is required.

```text
AI_Battery_Power_Management/
├── app.py
├── requirements.txt
├── gunicorn.conf.py
├── render.yaml
├── README.md
├── .gitignore
├── .github/workflows/checks.yml
├── battery/
│   ├── __init__.py
│   ├── analytics.py
│   ├── simulator.py
│   ├── power_manager.py
│   └── service.py
├── ai/
│   ├── __init__.py
│   ├── features.py
│   ├── generate_dataset.py
│   ├── train_model.py
│   └── predictor.py
├── database/
│   ├── __init__.py
│   └── db.py
├── data/
│   ├── battery_training_data.csv
│   └── battery.db
├── models/
│   ├── runtime_model.pkl
│   └── model_metrics.json
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/
│       ├── dashboard.js
│       ├── chart.umd.min.js
│       └── chart.LICENSE.md
└── tests/
    ├── test_battery.py
    ├── test_model.py
    ├── test_api.py
    ├── test_deployment.py
    ├── http_smoke.py
    └── browser_smoke.mjs
```

SQLite may temporarily create `battery.db-wal` and `battery.db-shm`. These are normal journal files. The generated model and training data are already included in this workspace.

## 4. Installation and running

Open this project folder in VS Code and run from its terminal (PowerShell, bash, or another shell):

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000/**. Stop with **Ctrl+C**. Debug mode and the development reloader are disabled. Local defaults are `127.0.0.1:5000`; `FLASK_HOST` and `PORT` override them. Application and browser API URLs do not require a particular hostname or port. Project-relative paths are anchored to `app.py`, not the terminal's working directory.

Dependencies and the trained model have already been set up in the current environment. For normal subsequent launches, only `python app.py` is needed. All frontend assets are local; internet access is needed for installation, not for running the dashboard.

To regenerate the dataset, retrain, initialize the database, and check the backend:

```powershell
python -m ai.generate_dataset
python -m ai.train_model
python -m database.db
python -m unittest discover -s tests -v
node --check static/js/dashboard.js
```

Stop and restart Flask after retraining so it loads the new artifact. Database initialization is also automatic at application startup and does not erase existing records. Dataset generation and training replace their respective generated files. Tests use temporary databases and leave the demonstration database untouched.

Optional browser test (Node 22+ and Microsoft Edge installed):

```powershell
node tests/browser_smoke.mjs
```

It starts a temporary server on port 5001 and a headless browser on debug port 9223, verifies controls and chart rendering, and saves screenshots in a temporary directory. Both ports must be free. Set `BROWSER_PATH` to a Chrome executable if Edge is unavailable.

### Deploy to Render

The repository contains a Render Blueprint (`render.yaml`) and exports `app` from `app.py`, so the production command is exactly:

```bash
gunicorn app:app
```

`gunicorn.conf.py` binds to `0.0.0.0:$PORT` (8000 when `PORT` is not set), uses **one worker with four request threads**, disables preloading, and starts/stops the simulator within that worker. Do not increase worker count, enable preloading, or scale to multiple instances: this application deliberately keeps one shared in-memory simulation/estimation state. The existing API lock serializes access.

**SQLite persistence:** the supplied Blueprint selects Render's **paid Starter service** and a **1 GB persistent disk** mounted at `/var/data`. `DATA_DIR=/var/data` makes SQLite create `/var/data/battery.db` at runtime. No database migration or build-time database creation is necessary. A persistent disk is not available on Render's free service; without it, telemetry/state are lost on restart or redeploy. [Render persistent disk documentation](https://render.com/docs/disks)

Deployment steps:

1. Push this project to your GitHub repository with the project files at the repository root. Include `models/runtime_model.pkl`, `models/model_metrics.json`, `requirements.txt`, `gunicorn.conf.py`, `render.yaml`, templates, static assets, and Python modules. The existing model is approximately 20 MB and must be committed as the actual file, not an unresolved Git LFS pointer. Do not commit `data/battery.db`, journal files, local environments, or credentials; `.gitignore` excludes runtime data and common secret files.
2. Check the **Backend and Linux deployment checks** workflow in GitHub Actions. It installs pinned packages on Ubuntu/Python 3.10.20, runs the backend tests, checks JavaScript syntax, then starts the exact Gunicorn command and verifies the health endpoint, loaded model, SQLite history, telemetry POST, and controls.
3. In Render, choose **New → Blueprint**, connect that GitHub repository, select the branch to deploy, and use the root `render.yaml`.
4. Review the selected Starter service and persistent disk, then deploy. The Blueprint sets:

   | Setting | Value |
   | --- | --- |
   | Runtime | Python |
   | Build command | `pip install -r requirements.txt` |
   | Start command | `gunicorn app:app` |
   | Health check path | `/health` |
   | Python version | `3.10.20` |
   | Persistent data directory | `/var/data` |
   | Instances / Gunicorn workers | 1 / 1 |

5. Wait for Render to report the service healthy, then open the HTTPS `onrender.com` URL it provides. `/health` should return `{"status":"healthy","model":"loaded","database":"connected"}`. Check `/api/telemetry`, then try the simulation controls on the dashboard.
6. For ESP32 integration online, replace the local API base URL with `https://<your-service>.onrender.com/api/telemetry` and use an HTTPS-capable client with certificate validation. Browser requests already use relative `/api/...` URLs, so no frontend URL changes are needed.

For manual setup instead of a Blueprint, choose **New → Web Service**, connect the same repository, select the Python runtime and Starter instance, enter the commands/table above, set `PYTHON_VERSION=3.10.20` and `DATA_DIR=/var/data`, attach a 1 GB disk at `/var/data`, and set health check path `/health`. Render supplies `PORT`; do not hard-code it in the service settings. [Render Flask deployment documentation](https://render.com/docs/deploy-flask)

For a disposable free-tier demonstration, remove the `disk` block, change `plan` to `free`, and remove `DATA_DIR` from the Blueprint (or use `data`). Accept that its local SQLite database and simulator state are ephemeral. The supplied configuration intentionally preserves data instead.

Environment configuration:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | 5000 locally; 8000 in Gunicorn | Server listening port; Render supplies its own value |
| `FLASK_HOST` | `127.0.0.1` | Host for `python app.py`; Gunicorn binds all interfaces independently |
| `DATA_DIR` | `data` relative to project root | Writable database directory; `/var/data` on Render |
| `DATABASE_PATH` | `<DATA_DIR>/battery.db` | Optional explicit SQLite file override |
| `MODEL_PATH` | `models/runtime_model.pkl` relative to project root | Optional trusted model artifact override |

The saved forest contains scikit-learn data and metadata, not Windows filesystem paths. Its existing NumPy, scikit-learn, and joblib versions remain pinned. Render uses the same Python 3.10 minor version; no model regeneration or retraining occurs during the build. The model stays in the repository's `models/` folder, outside the writable data disk. Health reports `model: "fallback"` if loading fails, and the existing calculated fallback still operates.

The endpoints and control behavior remain unchanged and do not include authentication. On a public demo, visitors can change the shared simulation controls or POST readings. Use demonstration data only; this is not a private multi-user or real-device production service. Adding access control would be a separate API change.

Gunicorn is a Unix/Linux server; use `python app.py` on Windows. This workspace has no installed Linux runtime, so an actual Gunicorn/Linux run must be confirmed by the included GitHub Actions job or Render deploy. Local Flask, exported WSGI app, environment configuration, model loading, health checks, and browser functionality are tested here. No GitHub push or Render service creation is performed by this preparation.

## 5. Demo walkthrough

1. Open the dashboard: simulation starts with approximately 78% charge, 94% assumed health, and MEDIUM load.
2. Select LOW; let readings settle for about 10 seconds. Note current, power, and runtime.
3. Select HIGH; current and power rise, runtime decreases, and the control policy may change. Saving policies may subsequently reduce current, demonstrating feedback.
4. Observe the five live charts and the policy actions. Up to 60 readings for the selected source/session are shown.
5. Turn simulation OFF: samples stop and the dashboard says PAUSED. Stored readings remain visible.
6. Use Reset simulation to start a new simulation session at 78% charge, zero accumulated energy, and simulation ON. The selected load is retained. Historical rows remain in SQLite.
7. Send the ESP32 example below: the dashboard switches to ESP32 and simulation pauses automatically.
8. Send an elevated-temperature example to demonstrate CRITICAL mode and recommendations. Temperatures outside the training range show FALLBACK.
9. Turn simulation ON to return to the saved simulation state. Stop ongoing ESP32 posts first; a new post always selects ESP32 again.

**Time scale:** 120 battery seconds per wall second for simulation. A normal two-second update represents approximately four battery minutes. Runtime predictions remain in **battery hours at current conditions**, not accelerated wall-clock hours. The nominal capacity remains 2 Ah, so the accelerated clock rather than an unrealistically tiny battery makes discharge visible. Pauses and application downtime are not counted as battery operation. A delayed simulation update integrates at most five wall seconds to avoid a large jump after computer sleep.

## 6. Battery analytics

Assumptions describe a **single discharging lithium-ion cell**, not a multi-cell pack or charging model:

| Quantity | Prototype method |
| --- | --- |
| Power (W) | `voltage * current` |
| Energy (Wh) | Trapezoidal integration: `(previous_power + power) / 2 * elapsed_seconds / 3600` |
| Coulomb-counted SoC (%) | Previous SoC minus average-current consumption divided by usable Ah, times 100 |
| Voltage SoC (%) | Piecewise resting-voltage lookup, after approximate `current * 0.08 ohm` load-drop compensation |
| Hybrid SoC (%) | Coulomb-counted SoC slowly corrected toward voltage SoC, bounded 0–100%; voltage at/below 3.0 V gives 0% |
| SoH (%) | `estimated_usable_capacity / nominal_capacity * 100` = `1.88 / 2.0 * 100` = 94% |
| Consumption trend | Current compared with the prior recent average, with a 15% plus 5 mA dead band |
| Recent averages | Last 12 samples, separately for simulation and ESP32 |

The voltage correction weight is `min(0.08, 1 - exp(-elapsed_seconds / 1800))`. The first sample initializes SoC from voltage and accumulates no energy because no interval is known.

**SoH is an assumed capacity ratio, not a health measurement inferred from one sensor reading.** The simulator uses the same 1.88 Ah usable-capacity assumption. It does not invent rapid battery aging during a demo. Change capacity constants only when the real battery has been characterized, then regenerate/retrain the synthetic model if nominal capacity changes.

Voltage, current, temperature, and activity are correlated in simulation. Higher activity increases target current; a saving policy scales that draw. Current changes gradually, integrated charge determines resting voltage, load produces voltage sag, and a thermal lag ties temperature to current. Small noise is added around this state. A depleted simulated cell draws zero current.

For ESP32, elapsed time comes from the server's monotonic receive clock. Client timestamps are not accepted. Gaps above 60 seconds are excluded from integration and logged because consumption during the gap is unknown. That causes undercounting over gaps; it is preferable to claiming an unmeasured interval. State and recent history survive restart, but the first interval after restart/source switch does not include offline time.

## 7. AI runtime prediction

`python -m ai.generate_dataset` creates **16,000 independent synthetic operating scenarios** with seed 42. Voltage, current, load, temperature, and recent behavior have related values. Synthetic runtime labels use remaining usable charge, a weighted current estimate, temperature/activity efficiency assumptions, and small unobserved noise. Labels are capped at 48 hours. These labels are **not experimental battery run-to-empty measurements**.

Features:

1. Voltage
2. Current
3. Temperature
4. Estimated SoC
5. Estimated SoH
6. Calculated power
7. Recent average current
8. Recent average power
9. Device load

The model uses 120 regression trees, maximum depth 18, minimum leaf size 2, and fixed random seed 42. A forest averages the decisions of many trees, learns nonlinear feature relationships, and is explainable through input importance. Training uses 12,800 rows; an untouched 3,200-row random holdout evaluates prediction. The data consists of independent scenarios rather than adjacent samples from the same discharge sequence.

Recorded evaluation (`models/model_metrics.json`):

| Held-out metric | Result |
| --- | ---: |
| MAE | 0.303377 hours (about 18.20 minutes) |
| RMSE | 0.593301 hours (about 35.60 minutes) |
| R² | 0.995506 |
| Calculated charge/current baseline MAE | 0.374505 hours |

The forest improves on the included baseline on this synthetic holdout. High R² primarily demonstrates that the model learned the synthetic generator's relationships; it does **not** prove real-world accuracy or superiority to a calibrated physical estimator. Future real-data evaluation should split by device/discharge cycle, not randomly across adjacent samples.

Only remaining runtime is an ML output. Power, SoC, SoH, energy, trends, recommendations, and policy decisions are calculations or rules. The model's runtime prediction feeds the decision engine.

`runtime_model.pkl` contains the forest, ordered feature schema, and metadata. Only load this locally generated trusted artifact; pickle/joblib formats must not be loaded from untrusted uploads. The application never accepts a model path through its API.

### Fallback behavior

Missing/corrupt/incompatible artifacts, failed prediction, or out-of-domain readings use a bounded calculated estimate:

```text
remaining_charge_Ah = nominal_capacity_Ah * SoH/100 * SoC/100
draw_A = max(0.015, 0.7 * current + 0.3 * recent_average_current)
fallback_hours = clamp(remaining_charge_Ah / draw_A, 0, 48)
```

Model-domain checks cover 3.0–4.2 V, 0.015–0.50 A (instantaneous and recent average), 15–40 °C, 0.5–100% SoC, and 60–100% SoH. The dashboard labels FALLBACK and changes the runtime heading to a calculated estimate. Zero-current estimates are bounded, not infinite. A zero-SoC estimate returns zero runtime. Fallback is continuity behavior, not a validated safety guarantee.

## 8. Smart power-management logic

Rules are evaluated in priority order using SoC, predicted runtime, current, temperature, device load, and the previous mode. Thresholds are illustrative demonstration choices.

| Mode | Entry conditions (any unless noted) | Sampling policy | Communication policy | Assumed saving vs PERFORMANCE |
| --- | --- | --- | --- | ---: |
| CRITICAL | SoC ≤10%; runtime ≤0.25 h; temperature ≥40 °C or ≤0 °C | 30 s | Essential alerts only; otherwise sleep | 75% |
| POWER SAVING | SoC ≤30%; runtime ≤1.5 h; temperature ≥36 °C; current ≥0.40 A | 15 s | Transmit every 30 s | 45% |
| PERFORMANCE | **All:** SoC ≥70%; runtime ≥3 h; temperature <33 °C; device load ≥0.7; no higher-priority rule | 2 s | Wi-Fi always active | 0% |
| BALANCED | Other normal conditions | 5 s | Normal Wi-Fi; batch routine messages | 18% |

Recovery margins reduce rapid switching: CRITICAL is retained until SoC ≥13%, runtime ≥0.4 h, and temperature is between 2 and 38 °C. POWER SAVING is retained below 34% SoC or 1.8 h runtime, at temperature ≥34.5 °C, or while estimated unthrottled current remains ≥0.36 A. PERFORMANCE can remain active down to 65% SoC if its other conditions hold. The unthrottled-current recovery check prevents reduced current from immediately undoing its own saving policy.

The simulator applies the previous policy's current multiplier (`1.0`, `0.82`, `0.55`, `0.25`) to the next load target. Displayed savings are **assumed percentage current reduction under the same load**, not measured cumulative energy savings against a real device. Sampling/radio schedules are returned control policies; the backend keeps monitoring at two-second intervals. The backend does not drive ESP32 peripherals. Firmware must implement those policies.

Recommendations use actual readings: rising/high draw suggests reduced sampling, elevated temperature suggests lower processing load, low predicted runtime suggests conservation, and critical charge suggests recharge and essential sensing only. Activity entries come from real sample processing, mode transitions, abnormal-temperature transitions, controls, and quality warnings; there are no random log messages.

## 9. REST API

All API responses are JSON. POST requests need `Content-Type: application/json`. Bodies are limited to 4 KiB, inputs use finite numeric validation (booleans/strings are not numbers), unknown fields are rejected, and SQL values are parameterized. APIs are intended for a local/trusted-LAN demo and do not implement authentication or TLS.

### GET `/api/telemetry?limit=60`

Returns the latest reading, live system status, controls, up to 60 chart points, recent events, and model metadata. `limit` must be an integer 1–60. This is read-only; it does not create a new telemetry row.

```text
status: "success"
telemetry: latest processed reading, or null before the first sample
system: {status, source, sample_age_seconds, message, poll_interval_seconds}
controls: {simulation_enabled, device_load, time_scale}
history: [{id, timestamp, soc, voltage, current, temperature, power}, ...]
activity: [{id, timestamp, message, level}, ...]
model: {available, reason, metadata}
```

System status can be ONLINE, WAITING, PAUSED, STALE, or ERROR. ESP32 data becomes stale after 30 seconds without a reading, simulation after 10 seconds. A failed browser fetch shows OFFLINE and retains visibly stale last readings. History belongs to the selected source and simulation session, so switching sources never connects unrelated chart series.

### POST `/api/telemetry`

```json
{
  "voltage": 3.85,
  "current": 0.12,
  "temperature": 29.5,
  "device_load": 0.45,
  "source": "esp32"
}
```

| Field | Accepted range / meaning |
| --- | --- |
| voltage | 2.5–4.3 V, one cell |
| current | 0–2 A, discharge only |
| temperature | −20–80 °C; abnormal values trigger policies |
| device_load | 0–1 normalized activity |
| source | Optional; must equal `esp32` if supplied |

The broader ingestion range allows abnormal-but-plausible readings to trigger warnings and fallback. It is not a declaration that those conditions are safe. Negative charging current is outside this prototype's scope.

Returns **201 Created** with `status: "success"` and processed fields including `id`, server UTC `timestamp`, `soc`, `soh`, `power`, `energy_consumed`, `predicted_runtime`, `power_mode`, `model_status`, `runtime_method`, `recommendation`, `recommendations`, `policy`, `source`, and `session_id`. Runtime is in **hours**, energy in **Wh**, interval in **seconds**, and SoC/SoH/saving in **percent**. `policy` includes `sampling_interval`, `communication_policy`, `actions`, `estimated_energy_saving`, and `reason`.

An accepted ESP32 POST pauses simulation and selects the ESP32 stream. Invalid requests do not change controls or stored telemetry. Return to simulation using the dashboard switch or the control API.

PowerShell example:

```powershell
$payload = @{
    voltage = 3.85
    current = 0.12
    temperature = 29.5
    device_load = 0.45
    source = "esp32"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/telemetry" -Method Post -ContentType "application/json" -Body $payload
```

Set `temperature = 42.0` for a deliberate CRITICAL/FALLBACK demonstration. It is stored as an ESP32 API example; it is not a real hardware measurement.

### POST `/api/control`

Optional fields (at least one is required):

```json
{"simulation_enabled": true, "device_load": "HIGH", "reset": false}
```

`simulation_enabled` and `reset` are JSON booleans. `device_load` is LOW, MEDIUM, or HIGH. `reset: true` resets simulation state only; use `simulation_enabled: true` as well to resume it. The dashboard reset button does both. Returns **200 OK** with the same snapshot shape as GET.

Error responses use `{"status":"error","error":"explanation"}`: 400 for validation/malformed JSON, 413 for oversized bodies, 415 for unsupported content type, 404 for missing APIs, and 503 for SQLite failures.

### GET `/health`

```json
{"status": "healthy", "model": "loaded", "database": "connected"}
```

The endpoint checks that the model is loaded and the telemetry table can be queried. It returns HTTP 200 for a healthy instance. A missing/unusable model returns `status: "degraded"`, `model: "fallback"`, and HTTP 200 so the existing fallback service remains available. A database failure returns `status: "unhealthy"`, `database: "unavailable"`, and HTTP 503. Responses are not cached and do not disclose filesystem paths.

## 10. SQLite storage

`data/battery.db` is initialized automatically. The `telemetry` table stores id, server UTC timestamp, voltage, current, temperature, device load, SoC, SoH, power, energy consumed, predicted runtime, power mode, source, session id, model status, and a JSON detail snapshot. `events` stores real system events; `state` stores estimator, simulator, and control state.

Simulation and ESP32 use the same telemetry schema but separate charge/energy estimators. The simulator reset starts a new session without deleting history. To bound disk growth, the database retains the latest 10,000 telemetry rows and 1,000 events across sources. Cumulative estimator state survives this retention. Sample, events, and state commit together; failed writes roll back in-memory estimates. SQLite connections are short-lived and use WAL mode.

## 11. ESP32 integration

1. Calibrate appropriate voltage, current, and temperature sensing for the battery. Convert units to volts, amps, and Celsius; provide normalized workload from 0 to 1.
2. Connect the computer and ESP32 to the same trusted Wi-Fi network using your own provisioning process. This project contains no Wi-Fi passwords or credentials.
3. Start the server on the LAN interface:

   ```powershell
   $env:FLASK_HOST = "0.0.0.0"
   python app.py
   ```

4. Use `ipconfig` to find the computer's LAN IPv4 address. The ESP32 URL is `http://<computer-LAN-IP>:5000/api/telemetry`; `localhost` on ESP32 means the ESP32 itself.
5. If needed, allow Python/port 5000 on the Windows private-network firewall. Do not expose this unauthenticated development server to the public internet.
6. From firmware, use an HTTP client to POST the documented JSON every 2–5 seconds. Read the HTTP 201 response, then use `policy.sampling_interval`, communication policy, and actions to implement device behavior. Sensor sampling can follow policy while a heartbeat keeps monitoring fresh.
7. If firmware sends less often than every 30 seconds, the dashboard can show STALE between posts; intervals beyond 60 seconds intentionally leave an integration gap. Critical-mode minimal communication therefore needs a suitable heartbeat or revised stale/integration thresholds in a real implementation.
8. Stop ESP32 transmission before switching back to simulation. Otherwise the next POST takes over again.

Return to local-only binding in a new terminal, or run `Remove-Item Env:FLASK_HOST` before the next launch.

## 12. Validation and limitations

Backend tests cover energy units, gradual discharge and load response, all policy modes, missing/corrupt model fallback, out-of-domain readings, real model prediction, validated API input, source isolation, pause/reset, history limits, concurrency, persistence, integration gaps, stale state, and database rollback. The browser test checks five actual Chart.js instances, load-driven current/power/runtime changes, pause/reset, ESP32 takeover, fallback labeling, mobile width, and behavior when the chart asset fails.

Validation completed for the light-theme/deployment update: all 21 backend tests passed, including health success/fallback/database-failure checks, environment paths, WSGI export, and Gunicorn lifecycle configuration. Headless Edge verified all five updating light-theme charts, controls, ESP32 POST, AI prediction, banner removal, and layouts at 1440, 1366, 1024, 768, 390, and 320 pixels without horizontal overflow or clipped metric cards. JavaScript passed Node's syntax check. The Render Blueprint passed validation against Render's official JSON schema. Live Flask HTTP checks cover `/`, `/health`, GET/POST `/api/telemetry`, and controls using a temporary SQLite database. Actual Linux Gunicorn execution is configured in GitHub Actions and has not been run on this Windows-only workstation.

A browser-only startup issue was discovered during testing: Windows MIME associations prevented scripts from executing with `nosniff` enabled. Flask now explicitly registers JavaScript and CSS MIME types, and the backend test checks those response headers. Input validation was also hardened against oversized integers and non-ASCII history-limit values. A delayed pre-control GET response is discarded so it cannot overwrite a more recent control result.

Remaining limitations:

- Synthetic training and simulation do not reproduce all cell chemistry, aging, hysteresis, sensor noise, or environmental effects.
- SoH is a configurable capacity assumption. SoC voltage mapping and resistance are illustrative, not cell-specific calibrations.
- Predictions assume the current operating conditions continue; changing policies or workload changes the estimate.
- Sampling/communication/processing actions are a simulated policy, not complete ESP32 control firmware.
- Only one discharging cell/device and one server process are supported. No charging, device identities, authentication, or multi-user controls. Render terminates HTTPS at its edge; the local Flask development server does not provide TLS.
- Energy is not integrated during pause, downtime, or long unknown ESP32 gaps.
- This prototype is not a battery safety/protection system and does not make laboratory-grade accuracy claims.

Future improvements include calibrated current/voltage sensing, real discharge-cycle datasets and per-device validation, measured usable-capacity tracking, temperature-dependent chemistry models, firmware acknowledgements, measured before/after energy savings, device identities, authentication, TLS, charging support, and a separately managed sampling service for deployment.

## 13. References and third-party software

- [Flask API documentation](https://flask.palletsprojects.com/en/stable/api/)
- [scikit-learn RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
- [scikit-learn model persistence](https://scikit-learn.org/stable/model_persistence.html)
- [Chart.js integration](https://www.chartjs.org/docs/latest/getting-started/integration)

Chart.js 4.4.8 is bundled unchanged from its published distribution. Its MIT license is included in `static/js/chart.LICENSE.md`.
