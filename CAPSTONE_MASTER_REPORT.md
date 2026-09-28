# AI-Based Smart Battery-Aware Power Management System for IoT Devices

## Master technical reference for academic reporting

**Document purpose:** a source-grounded reference for the final capstone report, a suggested ten-week progress report, weekly 5W1H submissions, presentation preparation, and viva discussion.

**Inspection date:** 28 September 2026. **Project inspected:** the existing `AI_Battery_Power_Management` workspace. The local Git history inspected contained commit `690d533`, titled `Initial complete AI battery power management system`. This identifies a local source snapshot; it does not establish a ten-week development history, a successful GitHub push, or a live Render deployment.

### Evidence and interpretation conventions

- **Implemented:** behavior directly supported by the inspected source files, configuration, dataset, database schema, or saved model artifact.
- **Recorded validation:** a result reported in the current `README.md`, with corresponding test code inspected. It is not a newly executed test result from this documentation task.
- **Engineering interpretation:** an explanation of motivation, likely design rationale, or intended benefit inferred from the implementation. Such explanations are not measured experimental results.
- **Suggested academic progression:** a logical allocation of the completed work across ten weeks. It must not be submitted as a verified historical diary without matching it to the student's actual dates, records, and supervisor feedback.
- **Future work:** a proposed extension that is not implemented in the inspected project.

The inspection read application modules, frontend files, tests, README, deployment files, dataset contents, model metadata, and the trusted saved model. The existing SQLite schema was queried using an immutable, read-only SQLite connection. The CSV was counted, test methods were counted through syntax-tree inspection, and the saved model's structure was inspected without fitting or predicting. The application, test suite, training scripts, and dataset generator were not run for this report. Commands included below are instructions for later use, not a record that they were executed during documentation.

### Important boundaries for academic claims

1. **Only remaining battery runtime is predicted by machine learning.** SoC, SoH, power, energy, trends, recommendations, and policy decisions use calculations or explicit rules.
2. **SoH is presently an assumed capacity ratio:** 1.88 Ah usable capacity divided by 2.0 Ah nominal capacity. It is not a measured aging diagnosis.
3. **The runtime model was trained and evaluated on synthetic scenarios.** Its R² is a coefficient of determination, not classification accuracy or proof of real-cell performance.
4. **The simulator invokes the shared service directly.** It does not send HTTP requests to its own telemetry API.
5. **SQLite persistence occurs after analytics, runtime prediction, policy selection, and recommendation generation.** A database-first prediction flow would misrepresent the current code.
6. **Power-control schedules are returned policies.** They alter simulated current through a multiplier; no supplied ESP32 firmware actually changes hardware sampling, Wi-Fi, processing, or sleep states.
7. **Render and GitHub Actions are prepared in configuration.** This report does not claim a verified cloud deployment or a successful remote CI run.

## Contents

1. [Project overview](#1-project-overview)
2. [Overall 5W1H project summary](#2-overall-5w1h-project-summary)
3. [Implemented system architecture](#3-implemented-system-architecture)
4. [Technology stack](#4-technology-stack)
5. [Project file structure](#5-project-file-structure)
6. [Battery telemetry](#6-battery-telemetry)
7. [State of Charge](#7-state-of-charge-soc)
8. [State of Health](#8-state-of-health-soh)
9. [Power and energy calculations](#9-power-and-energy-calculations)
10. [AI and machine-learning component](#10-ai-and-machine-learning-component)
11. [Actual model performance](#11-actual-model-performance)
12. [Smart power management](#12-smart-power-management)
13. [Recommendation engine](#13-recommendation-engine)
14. [Database](#14-database)
15. [REST API](#15-rest-api)
16. [Current web dashboard](#16-current-web-dashboard)
17. [Live data visualization](#17-live-data-visualization)
18. [ESP32 integration](#18-esp32-integration)
19. [Simulation demonstration](#19-simulation-demonstration)
20. [Testing and evidence](#20-testing-and-evidence)
21. [Deployment](#21-deployment)
22. [Security and validation](#22-security-and-validation)
23. [Project limitations](#23-project-limitations)
24. [Future scope](#24-future-scope)
25. [Detailed ten-week development breakdown](#25-detailed-ten-week-development-breakdown)
26. [Ten-week deliverable table](#26-ten-week-deliverable-table)
27. [Viva summary](#27-viva-summary)

## 1. Project overview

**Sources:** [README.md](README.md), [app.py](app.py), [battery/service.py](battery/service.py), and [templates/index.html](templates/index.html).

### 1.1 Project identity and domain

| Item | Description |
| --- | --- |
| Academic project title | AI-Based Smart Battery-Aware Power Management System for IoT Devices |
| Dashboard heading | AI-Based Smart Battery-Aware Power Management System |
| Dashboard subtitle | Intelligent Energy Monitoring & Adaptive Power Optimization for IoT Devices |
| Domain | Internet of Things, battery monitoring, energy-aware embedded-system control, applied regression, and web-based engineering visualization |
| Current form | A single-device software prototype with a battery simulator, an ESP32-compatible API, analytics, a saved regression model, SQLite storage, and a live browser dashboard |
| Current interface | Professional light-mode dashboard with live numeric readings, charts, controls, recommendations, and recorded events |

### 1.2 Problem statement

Battery-powered IoT devices must divide a limited energy supply between sensing, processing, and communication. A fixed operating schedule does not respond to a falling charge reserve, increased current draw, changing workload, or elevated temperature. A user also needs more context than a single voltage reading to understand whether a device is likely to continue operating for an acceptable period.

The project addresses this educational engineering problem by combining telemetry, transparent battery estimates, runtime prediction, and an explainable operating-mode policy in one observable system. It does not claim to replace a hardware battery-protection circuit or a calibrated commercial Battery Management System.

### 1.3 Motivation

**Engineering interpretation:** an IoT device that knows its approximate energy condition can trade sensing and communication frequency against operating duration. A combined dashboard makes those trade-offs visible and provides a useful capstone demonstration of sensing interfaces, software estimation, ML inference, persistence, and control feedback.

Simulation makes development possible before a physical ESP32 and calibrated battery sensors are available. The common processing service allows a real device to supply readings later without replacing the analytics and visualization layers.

### 1.4 Proposed and implemented solution

The application receives or simulates voltage, current, temperature, and normalized device activity. It estimates charge and health, calculates power and accumulated energy, predicts remaining runtime using a saved Random Forest, and selects an operating mode. It generates recommendations from those results and stores the processed reading and related events in SQLite. A browser polls the Flask backend and updates cards and five charts without reloading the page.

In simulation, the selected policy reduces the next target current. The resulting change in current influences future power, discharge, temperature, predictions, and decisions. This is a demonstrable software feedback loop. For a real ESP32, the backend returns the policy but firmware must implement the physical response.

### 1.5 Main objectives

1. Demonstrate changing IoT battery telemetry without requiring hardware.
2. Support validated ESP32-compatible telemetry through an HTTP JSON API.
3. Explain and implement prototype SoC, SoH, power, and energy calculations.
4. Train, save, load, and use a genuine regression model for remaining runtime.
5. Provide a calculated fallback when ML inference is unavailable or unsuitable.
6. Select operating modes using several factors rather than SoC alone.
7. Display useful recommendations, control policies, and actual application events.
8. Maintain bounded local history and recover useful state after a restart.
9. Provide a responsive dashboard and automated checks.
10. Prepare a single-process deployment on Render while preserving the existing algorithms.

### 1.6 Scope and intended IoT use case

The implemented scope is one discharging cell/device represented by either simulation or an ESP32-labelled stream. Multiple POST clients would still share the same ESP32 estimator; the system does not identify and manage separate devices.

**Illustrative intended use case, not a supplied hardware implementation:** a battery-operated environmental sensing node periodically samples sensors, performs local processing, and transmits data over Wi-Fi. When reserve becomes low or thermal/current conditions worsen, the node could sample or transmit less frequently and limit nonessential processing according to the returned policy.

The repository does not include sensor drivers, an ESP32 sketch, calibrated battery experiments, charging control, authentication, or multi-device management.

### 1.7 Expected benefits

**Engineering interpretation:** expected benefits include better visibility of battery condition, easier demonstration of load-dependent consumption, earlier recognition of low predicted runtime, and a clear interface for future adaptive firmware. These are design benefits, not measured claims about increased real battery lifetime. The implemented saving percentages are policy assumptions, not experimentally established energy reductions.

## 2. Overall 5W1H project summary

**Sources:** [app.py](app.py), [battery/service.py](battery/service.py), [ai/predictor.py](ai/predictor.py), and [static/js/dashboard.js](static/js/dashboard.js).

| Question | Project-specific explanation |
| --- | --- |
| **WHAT** | A web-based battery-monitoring and power-management prototype was developed. It combines telemetry, battery estimation, ML runtime prediction, rule-based policies, storage, and visualization. |
| **WHY** | Battery reserve and workload change over time. Monitoring and adaptable operating policies provide a way to study the trade-off between IoT service activity and available energy. Real savings still require hardware validation. |
| **WHO** | The simulator or a future ESP32 supplies readings; Flask validates external requests; the shared service coordinates analytics; the Random Forest predicts runtime; the policy and recommendation functions interpret conditions; SQLite stores results; a student/operator observes and controls the demonstration through the browser. |
| **WHERE** | Simulation, analytics, ML inference, policy selection, and SQLite execute in the Python server process. HTML/CSS/JavaScript and Chart.js execute in the browser. Future sensor measurement and physical policy application execute on ESP32. Render hosting is configured but not verified by this report. |
| **WHEN** | Simulation runs in a background loop with an approximately two-second wait between iterations. A valid ESP32 POST is processed when received. Every processed sample passes through analytics, prediction, policy selection, recommendations, and persistence. The browser requests a new snapshot about two seconds after the previous request finishes. |
| **HOW** | Both telemetry sources enter the same service through different entry points. The service calculates and predicts, selects actions, records results, and exposes a snapshot. JavaScript updates the interface from JSON. The selected simulation policy influences the next simulated current target. |

The student/developer and academic supervisor are reasonable stakeholders for reporting and review; their actual personal identities and division of work are not encoded in the project.

## 3. Implemented system architecture

**Primary evidence:** `BatteryService._process()`, `tick()`, `receive()`, and `snapshot()` in [battery/service.py](battery/service.py).

### 3.1 Actual processing order

```text
SOURCE A: simulated IoT battery                 SOURCE B: ESP32-compatible client
BatterySimulator.sample()                      voltage/current/temperature/load
        |                                                   |
        | direct Python call                      HTTP POST /api/telemetry
        |                                                   |
BatteryService.tick()                           JSON and range validation
        |                                                   |
        |                                          BatteryService.receive()
        +--------------------------+------------------------+
                                   |
                          shared lock + _process()
                                   |
                  BatteryAnalytics.process(sample, elapsed)
                    SoC, SoH, power, energy, recent averages
                                   |
                        RuntimePredictor.predict()
                  saved Random Forest OR calculated fallback
                                   |
                            select_policy()
                  mode, schedules, actions, assumed savings
                                   |
                           recommendations()
                                   |
                     assemble real application events
                                   |
                         Database.save() transaction
                    telemetry + events + current state
                                   |
                      latest in-memory result / DB history
                                   |
                         GET /api/telemetry snapshot
                                   |
                 JavaScript fetch -> cards + five Chart.js graphs

FEEDBACK: previous simulated mode -> current_factor -> next simulated reading
CONTROL: dashboard -> POST /api/control -> simulation state/load/reset
HARDWARE RESPONSE: POST response -> future ESP32 firmware applies policy
```

The simulator does not use HTTP for ingestion. Its direct call and the ESP32 API converge on the same `_process()` method. Database storage is deliberately shown after inference and decision-making because that is the implemented order.

### 3.2 Layer responsibilities

| Layer | Responsibility | Main implementation |
| --- | --- | --- |
| Input source | Create correlated simulated readings or submit external measured values | `battery/simulator.py`; external ESP32 client |
| HTTP interface | Render the page, validate POST bodies, return snapshots/control results/health | `app.py` |
| Service coordination | Select source, calculate elapsed time, serialize shared-state access, track sessions, invoke the pipeline | `battery/service.py` |
| Battery analytics | Calculate power and energy, estimate SoC and SoH, calculate recent behavior and condition labels | `battery/analytics.py` |
| Runtime prediction | Load the trained artifact; check model domain; produce ML runtime or fallback | `ai/predictor.py` |
| Power policy | Select a mode and its operating policy using thresholds and recovery margins | `battery/power_manager.py::select_policy()` |
| Recommendations | Produce condition-based advisory messages | `battery/power_manager.py::recommendations()` |
| Persistence | Commit processed telemetry, events, and state; retrieve bounded history | `database/db.py` |
| Presentation | Display metrics, policies, recommendations, controls, and live charts | `templates/index.html`, `static/css/style.css`, `static/js/dashboard.js` |
| Deployment | Export the WSGI app and configure one Gunicorn worker and Render storage | `app.py`, `gunicorn.conf.py`, `render.yaml` |

### 3.3 State, concurrency, and recovery

The service uses a `threading.RLock` to serialize simulation ticks, received telemetry, controls, and snapshots. There is one background simulator thread per service instance. `start()` checks whether its thread is already alive before creating another one.

Simulation and ESP32 have separate analytics objects, session identifiers, previous modes, and abnormal-temperature flags. An accepted ESP32 POST sets `simulation_enabled` to false. A later simulation ON command selects the simulation source again. A new ESP32 POST can take over again; there is no device-authentication or arbitration protocol.

Before a mutating operation, `_transaction()` copies the current state and timing markers. On an exception it reconstructs the previous service state and restores those markers. SQLite commits the corresponding records within a transaction. The simulator exports SoC, current, and temperature; it does not persist its random-number generator's internal state, so restart recovery is not exact noise-sequence replay.

The snapshot is an assembled view, not a new sample. It combines the latest processed reading, controls, freshness status, source/session-specific chart history, recent events, and model information. The Flask `before_request` hook can start the worker if needed, but the GET telemetry handler itself does not advance the simulator or insert a reading.

## 4. Technology stack

**Sources:** [requirements.txt](requirements.txt), Python imports, frontend assets, test files, and deployment configuration. The reasons below are **engineering interpretations** of suitability, not documented records of a formal technology-selection study.

| Technology | Purpose | Where used | Reason for selection / suitability |
| --- | --- | --- | --- |
| Python | Server logic, simulation, numerical preparation, model training/inference | `app.py`, `battery/`, `ai/`, `database/`, Python tests | One readable language covers the prototype's backend and ML work. |
| Flask **3.1.2** | HTTP routes, JSON responses, template/static serving | `app.py` | A small application can expose a REST interface without a larger framework. |
| HTML / Jinja template rendering | Dashboard structure and static-asset URLs | `templates/index.html` | Clear server-rendered markup with no frontend build system. |
| CSS | Light visual theme, responsive grids, badges, timeline, accessibility states | `static/css/style.css` | Direct control of the engineering dashboard layout. |
| JavaScript / Fetch API | Polling, DOM updates, control POSTs, chart updates | `static/js/dashboard.js` | Live updates without page reload or an additional UI framework. |
| Chart.js **4.4.8** | Five time-series line charts | Locally bundled `static/js/chart.umd.min.js` | Responsive browser charts with tooltips and legends; no runtime CDN dependency. |
| SQLite / Python `sqlite3` | Telemetry, events, persistent service state | `database/db.py`; default `data/battery.db` | A local relational store suitable for one-device demonstration and simple setup. |
| NumPy **2.2.6** | Synthetic random sampling, clipping, CSV matrix loading, evaluation calculation | `ai/generate_dataset.py`, `ai/train_model.py` | Numerical arrays and reproducible synthetic-data operations. |
| scikit-learn **1.7.2** | Regression, data splitting, evaluation metrics | `ai/train_model.py`, `ai/predictor.py` | Established implementations of a lightweight tabular ML workflow. |
| Random Forest Regression | Remaining-runtime regression | Saved `RandomForestRegressor` | Models nonlinear tabular relationships and supports a simple ensemble explanation. |
| Joblib **1.5.2** | Save and load the trained model bundle | `ai/train_model.py`, `ai/predictor.py` | Convenient persistence of scikit-learn estimators and metadata. |
| Gunicorn **26.2.0** | Linux WSGI serving | `gunicorn.conf.py`, `render.yaml`, CI | Serves Flask behind a production hosting platform; configured for one shared-state worker. |
| HTTP/JSON REST interface | ESP32-compatible ingestion and browser controls | `/api/telemetry`, `/api/control` | A common protocol available to browsers and embedded Wi-Fi clients. |
| Git | Local version control | Existing `.git/`, `.gitignore`, inspected local commit | Tracks project files and excludes runtime data. |
| GitHub / GitHub Actions | Prepared repository hosting and automated Linux checks | `.github/workflows/checks.yml`; README deployment instructions | Provides a route from version control to reproducible CI and Render integration. Remote success was not verified. |
| Render | Prepared hosted web service and persistent disk | `render.yaml` | Configuration describes deployment of the existing Flask system. Live service operation is not established here. |
| Node.js 22+ | Optional JavaScript syntax/browser test tooling | `tests/browser_smoke.mjs`, CI | Uses built-in WebSocket/fetch/process APIs; no npm dependencies are required. |
| Edge / Chrome / Chromium DevTools Protocol | Optional headless browser integration test | `tests/browser_smoke.mjs` | Checks actual rendering, controls, charts, and responsive behavior. |
| VS Code | Documented development environment | README workflow | Provides an editor and terminal for the Python/frontend project. |

**Pandas is not used:** it is absent from `requirements.txt` and the inspected application imports. CSV generation uses Python's `csv` module; training data is loaded with `numpy.loadtxt`. Firebase, MQTT, TensorFlow, React, Bootstrap, and an ORM are also not implemented dependencies. ESP32 is an integration target, not supplied firmware in this repository.

## 5. Project file structure

**Evidence:** filesystem inspection, source reads, dataset/model inspection, and read-only database-schema inspection. Generated `__pycache__` folders and Git internals are omitted from the readable tree.

```text
AI_Battery_Power_Management/
├── .git/                                  # Existing local version-control metadata
├── .gitignore
├── .github/
│   └── workflows/checks.yml
├── app.py
├── gunicorn.conf.py
├── render.yaml
├── requirements.txt
├── README.md
├── CAPSTONE_MASTER_REPORT.md               # This documentation file
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

| File or group | Actual responsibility |
| --- | --- |
| `app.py` | Flask factory and exported `app`; input validation; page, telemetry, control, and health routes; environment-based paths; local startup. Importing it initializes a service/database, so it was read rather than imported during this documentation task. |
| `battery/analytics.py` | Capacity assumptions, piecewise voltage curve, hybrid SoC, SoH ratio, power/energy, recent averages, trend, and condition labels. |
| `battery/simulator.py` | Correlated changing readings with gradual current response, charge depletion, load-related voltage sag, thermal lag, and bounded noise. |
| `battery/power_manager.py` | Four policy definitions, ordered decision logic, recovery margins, and condition-based recommendation strings. |
| `battery/service.py` | Background worker, common pipeline, locks, source switching, timing, snapshots, event generation, state restoration, and transactional coordination. |
| `ai/features.py` | Ordered list of nine input feature names shared by generation, training, and inference. |
| `ai/generate_dataset.py` | Reproducible synthetic scenario and runtime-label generation; writes a CSV only when explicitly run. |
| `ai/train_model.py` | Reads or creates the dataset, splits it, trains the forest, evaluates it and a baseline, writes a model bundle and metrics JSON. |
| `ai/predictor.py` | Trusted artifact loading, feature/version checks, model-domain checks, prediction, and calculated fallback. |
| `database/db.py` | SQLite schema creation, connection lifecycle, atomic save, retention, history retrieval, and event retrieval. |
| `data/battery_training_data.csv` | Inspected CSV containing 16,000 data rows, nine features, and one target column; not real telemetry history. |
| `data/battery.db` | Existing default SQLite database for runtime telemetry, events, and state. Its schema matches `database/db.py`. |
| `models/runtime_model.pkl` | Existing Joblib bundle; inspected size 20,170,964 bytes; contains a fitted 120-tree, nine-feature forest, feature names, and metadata. |
| `models/model_metrics.json` | Saved evaluation values, feature importance, model/training metadata; matches metadata inside the inspected artifact. |
| `templates/index.html` | Light-mode dashboard structure with all metric/section/control elements and local assets. |
| `static/css/style.css` | Responsive light theme and semantic state styling. |
| `static/js/dashboard.js` | Relative API requests, update scheduling, control feedback, safe text rendering, and chart updates. |
| `static/js/chart.umd.min.js` | Bundled Chart.js distribution; inspected header identifies version 4.4.8. It is not project-authored analytics code. |
| `static/js/chart.LICENSE.md` | Included Chart.js MIT license. |
| `tests/` | Unit/API/deployment test definitions, HTTP smoke script, and headless browser integration script. |
| `gunicorn.conf.py` | One Linux worker, four threads, dynamic port, simulator lifecycle hooks, timeouts, and console logs. |
| `render.yaml` | Prepared Python web service, build/start commands, health path, environment settings, and persistent disk. |
| `.github/workflows/checks.yml` | Prepared Ubuntu backend, syntax, and Gunicorn/HTTP checks for pushes, pull requests, and manual runs. |
| `.gitignore` | Excludes Python caches, virtual environments, runtime SQLite files/journals, temporary models, environment secrets, and logs. |
| `README.md` | Existing setup, use, formulas, APIs, limitations, test-result record, and Render instructions. |

The three package `__init__.py` files identify the battery, AI, and database packages and contain short package descriptions. SQLite can create WAL/shared-memory journal files during normal application use; they are not additional application modules.

## 6. Battery telemetry

**Sources:** [battery/simulator.py](battery/simulator.py), [battery/service.py](battery/service.py), and `validate_telemetry()` in [app.py](app.py).

### 6.1 Input variables and metadata

| Variable | Meaning | Unit / representation | Origin |
| --- | --- | --- | --- |
| `voltage` | Single-cell terminal voltage | V | Simulator or external POST |
| `current` | Discharge current | A, nonnegative | Simulator or external POST |
| `temperature` | Battery thermal reading | °C | Simulator or external POST |
| `device_load` | Normalized activity indicator | Dimensionless, 0–1 | Simulator load mapping or external POST |
| `timestamp` | Time the backend processes the sample | UTC ISO-formatted string with millisecond precision | Server, not accepted as a POST field |
| `source` | Which input stream supplied the reading | `simulation` or `esp32` | Simulator/service or validated POST |
| `session_id` | Stream/session identifier for history selection | UUID hexadecimal string | Service; simulation receives a new identifier on reset |
| `integration_seconds` | Time interval used for this analytics update | Battery seconds in simulation; real elapsed seconds for ESP32 | Service |
| `time_scale` | Relation between simulated and real elapsed time | 120 for simulation; 1 for ESP32 | Service |

Derived values include SoC, SoH, power, energy consumed, recent average current/power, tracked battery time, runtime, condition/trend labels, and selected policy. These are not all sensor measurements.

### 6.2 Simulation starting state and load mapping

Unless restored from stored state, the simulator begins with internal SoC **78.0%**, current **0.20 A**, temperature **28.4 °C**, and pseudorandom seed **42**. The service's initial controls are simulation ON, MEDIUM load, and time scale 120. The initial previous mode is BALANCED. A restart can restore saved settings instead of these defaults.

| UI load | Numeric activity `L` | Unoptimized target `0.055 + 0.44L` | BALANCED target before noise (`×0.82`) |
| --- | ---: | ---: | ---: |
| LOW | 0.15 | 0.121 A | 0.09922 A |
| MEDIUM | 0.45 | 0.253 A | 0.20746 A |
| HIGH | 0.90 | 0.451 A | 0.36982 A |

The targets in this table are **derived examples from the source equations**, not promised measured values. Actual readings change gradually, contain small noise, and respond to the previously selected mode.

### 6.3 Correlated simulation equations

For activity `L` and policy multiplier `f`:

```text
target_current = (0.055 + 0.44 × L) × f + Uniform(-0.004, +0.004) A
new_current = old_current + 0.55 × (target_current - old_current)
consumed_Ah = ((old_current + new_current) / 2) × Δt / 3600
internal_SoC = max(0, internal_SoC - consumed_Ah / 1.88 × 100)
```

When internal SoC reaches zero, the returned current is set to zero. The thermal and voltage calculations then use the resulting current:

```text
thermal_target = 25 + 28 × new_current
temperature += (thermal_target - temperature)
               × (1 - exp(-max(Δt, 2) / 600))
temperature += Uniform(-0.025, +0.025) °C

voltage = OCV_from_internal_SoC - 0.08 × new_current
          + Uniform(-0.003, +0.003) V
voltage = clamp(voltage, 3.0, 4.2)
```

`OCV_from_internal_SoC` is the inverse piecewise curve described in Section 7. Output voltage is rounded to four decimal places, current to five, and temperature to two. Temperature and current are generated by the model; they are not independently clipped to the originally suggested 25–40 °C and 0.05–0.50 A demonstration ranges. In particular, saving policies can produce current below 0.05 A, and depletion produces zero current. These distinctions matter when reporting actual implementation.

The simulator's internal SoC is its synthetic physical state. The dashboard SoC is separately estimated by `BatteryAnalytics` from the resulting readings and elapsed time. They should be related, but they are not simply the same variable copied to the screen.

### 6.4 Timing and discharge acceleration

The worker executes a tick and then waits two seconds. Processing time means the wall-clock interval is approximately, not exactly, two seconds. The monotonic clock supplies elapsed time:

```text
simulation_Δt = min(5, max(0, elapsed_wall_seconds)) × 120
```

The first tick after startup/resume uses zero integration time. A usual two-second interval represents about 240 battery seconds, or four battery minutes. A delayed tick is capped at 600 battery seconds. Simulation OFF stops new simulated readings; paused/offline time is not integrated. The displayed runtime is in battery hours under current conditions, not accelerated demonstration wall-clock hours.

### 6.5 ESP32 mode and validated ranges

An external client sends `voltage`, `current`, `temperature`, and `device_load`; `source` is optional but must equal `esp32` if present. The server supplies the timestamp and uses the same analytics/prediction/policy pipeline.

| POST field | Accepted inclusive range |
| --- | --- |
| `voltage` | 2.5–4.3 V |
| `current` | 0–2 A |
| `temperature` | −20–80 °C |
| `device_load` | 0–1 |

These are ingestion-validation limits, not safe-operating limits or model-training limits. An abnormal but accepted reading can trigger CRITICAL mode or ML fallback.

ESP32 elapsed time comes from server receive intervals measured by `time.monotonic()`. If a gap is greater than 60 seconds, integration time is set to zero and a quality warning is recorded. The code does not invent consumption during that unknown gap. The first received sample after startup also has zero integration time. The accepted POST pauses simulation and selects the ESP32 history, while the simulation's own estimator state remains separate.

## 7. State of Charge (SoC)

**Source:** `BatteryAnalytics.process()`, `voltage_soc()`, and `CURVE` in [battery/analytics.py](battery/analytics.py).

### 7.1 Meaning and prototype role

State of Charge describes the remaining charge reserve as a percentage of a chosen usable-capacity reference. Here it is a software estimate; the server does not directly measure electrochemical charge. Current and voltage may themselves be simulated or supplied by an external client.

### 7.2 Voltage-based component

The terminal voltage is approximately compensated for load-related sag using an assumed resistance:

```text
V_corrected = V_terminal + I × 0.08 Ω
SoC_voltage = piecewise_linear_lookup(V_corrected)
```

The implemented lookup points are:

| Resting-voltage reference (V) | SoC (%) |
| ---: | ---: |
| 3.00 | 0 |
| 3.30 | 5 |
| 3.50 | 15 |
| 3.65 | 35 |
| 3.75 | 55 |
| 3.85 | 75 |
| 4.00 | 90 |
| 4.20 | 100 |

Between two points `(V0, S0)` and `(V1, S1)`:

```text
S(V) = S0 + (S1 - S0) × (V - V0) / (V1 - V0)
```

Values below or above the lookup range use the endpoint SoC values. The first processed sample initializes SoC using this corrected-voltage estimate.

### 7.3 Consumption / coulomb-counting component

For a known positive interval and an existing preceding reading:

```text
I_average = (I_previous + I_current) / 2
consumed_Ah = I_average × Δt_seconds / 3600
SoC_counted = max(0, SoC_previous - consumed_Ah / Q_usable × 100)
Q_usable = 1.88 Ah
```

This is trapezoidal integration of current over time, expressed in Ah before conversion to percentage points. The same method applies to ESP32 readings and simulated readings; their elapsed-time scales differ.

### 7.4 Hybrid correction

The code gradually corrects the counted estimate toward the voltage estimate:

```text
α = min(0.08, 1 - exp(-Δt_seconds / 1800))
SoC_hybrid = clamp(SoC_counted + α × (SoC_voltage - SoC_counted), 0, 100)
```

The correction weight cannot exceed 0.08 in one processed interval. With no previous sample or zero elapsed time, that integration/correction branch is skipped. Independently, terminal voltage at or below **3.0 V** forces SoC to **0%**. The returned SoC is rounded to three decimal places; the dashboard normally shows one decimal place.

### 7.5 Interpretation and limitations

**Engineering interpretation:** coulomb counting tracks consumption between readings, while the voltage term gives a reference that can counter accumulated drift. The implementation is easier to explain than a full electrochemical observer but relies on simplified assumptions.

- The lookup curve and 0.08 Ω resistance are illustrative, not calibrated to an identified physical cell.
- There is no temperature-dependent voltage curve, charging efficiency, hysteresis model, or sensor-offset calibration.
- Nonnegative discharge current is required; charging is not supported by the API.
- Ignored gaps mean unobserved charge consumption cannot be recovered accurately.
- Voltage correction may move the estimate slightly upward even while the synthetic cell is discharging; strict monotonicity is not guaranteed for the hybrid estimate.
- A sensible-looking SoC trace is not evidence of laboratory-grade accuracy.

## 8. State of Health (SoH)

**Source:** capacity constants and returned `soh` in [battery/analytics.py](battery/analytics.py).

### 8.1 Meaning and actual calculation

Capacity-based State of Health expresses usable battery capacity relative to nominal capacity:

```text
SoH (%) = estimated_usable_capacity_Ah / nominal_capacity_Ah × 100
        = 1.88 / 2.00 × 100
        = 94%
```

The implementation exports `nominal_capacity_ah = 2.0` and `estimated_usable_capacity_ah = 1.88` with each reading. The ratio is the same for simulation and ESP32 processing.

### 8.2 Important assumption

The usable capacity is a fixed constant in the inspected source. It is not estimated online from charge/discharge experiments, cycle count, internal resistance, or a health-prediction model. Consequently, the operational dashboard's SoH normally remains 94% even as SoC falls.

The synthetic ML dataset samples SoH between 60% and 100% to expose the runtime regressor to different assumed capacities. That training variation does not make the deployed SoH estimator dynamic.

### 8.3 Limitations

This implementation demonstrates the meaning of a capacity ratio and its effect on remaining charge. A physically meaningful health estimate would require a validated usable-capacity estimate for the actual battery and periodic re-characterization. It should not be described as detecting real battery degradation or measuring remaining useful lifetime.

## 9. Power and energy calculations

**Source:** [battery/analytics.py](battery/analytics.py).

### 9.1 Instantaneous power

```text
P = V × I
```

Voltage is in volts and current in amperes, so power is in watts. It is calculated from telemetry, not predicted by the Random Forest. The JSON value is rounded to six decimal places; the dashboard normally shows three.

### 9.2 Accumulated energy

The implementation uses trapezoidal power integration:

```text
P_average = (P_previous + P_current) / 2
ΔE_Wh = P_average × Δt_seconds / 3600
E_total_Wh = E_previous_Wh + ΔE_Wh
```

The first reading contributes no interval energy. Simulation uses accelerated battery seconds, while ESP32 uses accepted real receive intervals. Cumulative energy is separate for each source, saved in estimator state, and rounded to six decimal places in the API. The dashboard displays four decimal places.

Resetting simulation starts its energy count from zero and creates a new simulation session. SQLite retention can remove old sample rows without resetting the cumulative energy held in state.

### 9.3 Simple numerical example

**Worked example, not an additional experiment:** suppose voltage stays at 3.80 V and current at 0.20 A for one hour, with the same power at both interval endpoints.

```text
P = 3.80 × 0.20 = 0.76 W
ΔE = (0.76 + 0.76)/2 × 3600/3600 = 0.76 Wh
consumed charge = 0.20 × 1 = 0.20 Ah
uncorrected SoC reduction = 0.20 / 1.88 × 100 ≈ 10.64 percentage points
```

The hybrid voltage correction can change the final SoC reduction from that uncorrected value. The energy example is also the scenario asserted by `test_energy_integrates_in_watt_hours`.

### 9.4 Recent behavior and condition labels

The estimator retains up to **12** recent current/power pairs. The current sample is included in the averages returned as `recent_average_current` and `recent_average_power` for inference.

The trend compares the current reading against the average of the prior deque, before appending the new sample:

```text
INCREASING: I_current > 1.15 × previous_recent_average + 0.005 A
DECREASING: I_current < 0.85 × previous_recent_average - 0.005 A
STABLE:     neither condition is true
```

On the first sample, the reference average is that sample's own current. Battery condition is `TEMPERATURE ALERT` for temperature ≥40 °C or ≤0 °C; otherwise it is `LOW CHARGE` for SoC ≤20%; otherwise it is `NORMAL ESTIMATED HEALTH`. This label is a rule-based summary, not a separate diagnosis of measured health.

## 10. AI and machine-learning component

**Sources:** [ai/features.py](ai/features.py), [ai/generate_dataset.py](ai/generate_dataset.py), [ai/train_model.py](ai/train_model.py), [ai/predictor.py](ai/predictor.py), [models/model_metrics.json](models/model_metrics.json), and read-only inspection of the existing `runtime_model.pkl` bundle.

### 10.1 Purpose and exact prediction target

The model predicts **remaining battery runtime in hours**, under the operating conditions represented by the input vector. The CSV target is `runtime_hours`; the online API output field is `predicted_runtime`. Output is limited to 48 hours.

**Engineering interpretation:** runtime is a useful decision variable because the same SoC can support different durations at different current draws. A regressor demonstrates how multiple measurements and recent behavior can be mapped to an operating-duration estimate. The current synthetic experiment does not establish that ML is inherently better than a well-calibrated physical model.

The model does not predict SoC, SoH, temperature, power mode, battery faults, or remaining lifetime over months. It is not a language model, reinforcement-learning controller, or online-learning system.

### 10.2 Actual dataset size and organization

Read-only CSV inspection found:

- **16,000 data rows**, excluding the header.
- **10 columns per row:** nine inputs and one target.
- The generator's default random seed is **42**, through `numpy.random.default_rng`.
- Rows describe independent synthetic operating scenarios, not a time-ordered experimental discharge dataset.
- The current CSV is separate from the telemetry table in SQLite. Runtime telemetry is not automatically appended to the training CSV.

The exact ordered header is:

```text
voltage,current,temperature,soc,soh,power,recent_average_current,recent_average_power,device_load,runtime_hours
```

### 10.3 Synthetic input generation

In the following equations, `Uniform(a,b)` denotes the generator's uniform sampling and `Normal(μ,σ)` denotes its normal sampling. The upper endpoint of a uniform draw is not generally included; the listed intervals describe the intended sampling domain. `clip(x,a,b)` limits a value to the stated bounds.

```text
SoC = Uniform(0.5, 100)
SoH = Uniform(60, 100)
load = Uniform(0, 1)
factor = randomly choose from [1.0, 0.82, 0.55, 0.25]

current = clip((0.055 + 0.44 × load) × factor + Normal(0, 0.006), 0.015, 0.5)
recent_average_current = clip(current × Uniform(0.75, 1.25), 0.015, 0.5)
temperature = clip(25 + 28 × current + Normal(0, 4), 15, 40)
voltage = clip(OCV_from_SoC - 0.08 × current + Normal(0, 0.006), 3.0, 4.2)
power = voltage × current
recent_average_power = recent_average_current
                       × clip(voltage + Normal(0, 0.015), 3.0, 4.2)
```

These relationships prevent the dataset from being a collection of unrelated random columns. Current depends on activity and a policy-like factor; temperature depends partly on current; voltage depends on SoC and current; power depends on voltage/current.

The sampled `factor` is a data-generation parameter, not one of the nine model features. The synthetic recent-average inputs are constructed around the instantaneous reading; they are not computed from an actual sequence of twelve historical samples. Online inference does use the actual recent deque from the estimator. This approximation is a training-to-operation limitation.

### 10.4 Synthetic target generation

The exact target construction is:

```text
effective_draw = 0.7 × current + 0.3 × recent_average_current
remaining_charge = 2.0 × (SoH / 100) × (SoC / 100) Ah
thermal_efficiency = 1 - 0.004 × abs(temperature - 25)
activity_efficiency = 0.98 - 0.04 × load

runtime_hours = remaining_charge / effective_draw
                × thermal_efficiency
                × activity_efficiency
                × Normal(1, 0.025)

runtime_hours = clip(runtime_hours, 0, 48)
```

The target is therefore a synthetic, physically motivated runtime calculation with assumed efficiency effects and noise. The regression model learns an approximation to these generated relationships. It has not learned from measured physical run-to-empty experiments.

### 10.5 Ordered feature list and feature engineering

| Position | Feature | Meaning | Online origin |
| ---: | --- | --- | --- |
| 1 | `voltage` | Terminal voltage in V | Input telemetry |
| 2 | `current` | Discharge current in A | Input telemetry |
| 3 | `temperature` | Temperature in °C | Input telemetry |
| 4 | `soc` | Hybrid estimated remaining charge percentage | Battery analytics |
| 5 | `soh` | Assumed usable/nominal capacity percentage | Battery analytics |
| 6 | `power` | Instantaneous V × I in W | Battery analytics |
| 7 | `recent_average_current` | Average over up to twelve latest current readings | Battery analytics |
| 8 | `recent_average_power` | Average over up to twelve latest power readings | Battery analytics |
| 9 | `device_load` | Normalized workload/activity | Input telemetry or simulator load mapping |

Derived battery state, instantaneous power, and recent averages are the implemented feature engineering. The code does not standardize features, impute missing values, perform dimensionality reduction, run feature selection, or include timestamps as input features. Invalid external readings are rejected before inference rather than imputed.

### 10.6 Selected model and inspected configuration

The saved estimator is a fitted `RandomForestRegressor` with **nine input features and 120 fitted trees**. These properties were inspected in the artifact rather than assumed from the training script alone.

| Parameter | Actual value | Interpretation |
| --- | --- | --- |
| `n_estimators` | 120 | Number of regression trees |
| `max_depth` | 18 | Maximum allowed depth per tree |
| `min_samples_leaf` | 2 | Minimum samples in a leaf |
| `min_samples_split` | 2 | Minimum samples required to consider a split |
| `criterion` | `squared_error` | Split criterion based on squared regression error |
| `bootstrap` | `True` | Trees use bootstrap samples of training rows |
| `max_features` | 1.0 | All input features are available as split candidates |
| `random_state` | 42 | Reproducible model randomness |
| `n_jobs` | 1 | One computational job for fitting/prediction |
| `oob_score` | `False` | No out-of-bag evaluation is requested |
| `warm_start` | `False` | Model is not incrementally extended between fits |
| `monotonic_cst` | `None` | No monotonicity constraints are imposed |

The constructor explicitly sets trees, depth, leaf size, seed, and job count. The other values above were confirmed from the saved estimator's parameters.

**Engineering interpretation of suitability:** a forest averages many decision-tree regressors, can represent nonlinear interactions, does not require a neural-network training pipeline, and exposes feature-importance values. It is explainable during a viva as an ensemble that averages the outputs of multiple trees. No formal comparison against many alternative ML families or hyperparameter search is implemented.

### 10.7 Training and testing procedure

`train()` performs the following steps:

1. Locate `data/battery_training_data.csv` relative to the project root.
2. Generate it only if it is missing.
3. Load the numerical data using `numpy.loadtxt`, skipping the header.
4. Use the first nine columns as `X` and the last column as target `y`.
5. Call `train_test_split(..., test_size=0.2, random_state=42)`.
6. Fit the Random Forest on **12,800 training rows**.
7. Predict targets for **3,200 held-out rows**.
8. Calculate MAE, square-root-of-MSE as RMSE, and R².
9. Evaluate a transparent calculated baseline on the same held-out inputs.
10. Save the estimator, ordered features, and metadata in a compressed Joblib bundle; write metadata to JSON.

There is one reproducible random holdout split. No k-fold cross-validation, independent real-cell dataset, learning-curve study, or hyperparameter tuning procedure is present. Random scenario splitting is appropriate for this synthetic construction; future experimental sequences should be split by device or discharge cycle to avoid overly optimistic evaluation from adjacent correlated samples.

### 10.8 Serialization and loading

The training bundle contains:

```text
{
  model: fitted RandomForestRegressor,
  metadata: training/evaluation information,
  features: ordered feature-name list
}
```

Training writes `models/runtime_model.tmp` using `joblib.dump(..., compress=3)` and then replaces `models/runtime_model.pkl`. It separately writes `models/model_metrics.json`. The inspected metadata inside the current artifact exactly matches the current JSON file.

The predictor loads a trusted local artifact once when its instance is created. It treats loading warnings as errors, verifies the feature-name list, and checks that recorded and installed scikit-learn versions match. Missing, corrupt, incompatible, or otherwise unloadable artifacts cause fallback mode rather than a training operation. The application does not automatically retrain or hot-reload a changed artifact.

The model is numeric estimator data, not a Windows-specific sensor interface. Environment configuration locates the artifact on Linux or Windows; the deployment pins the relevant library versions. Actual Linux execution still requires the configured CI/deployment checks to run.

### 10.9 Online prediction and domain checks

For every processed telemetry sample, `predict()` receives the analytics result. It allows ML inference only when the saved model is available and these checks all pass:

| Checked value | Inclusive allowed model domain |
| --- | --- |
| Voltage | 3.0–4.2 V |
| Current | 0.015–0.50 A |
| Temperature | 15–40 °C |
| SoC | 0.5–100% |
| SoH | 60–100% |
| Recent average current | 0.015–0.50 A |

Power, average power, and device load do not have additional domain checks inside this function; they originate from the validated/derived pipeline. These simple bounds do not constitute a statistical out-of-distribution detector.

The predictor builds one row in the exact order in `FEATURES`, calls `model.predict`, checks for a finite nonnegative result, caps it at 48 hours, and rounds it to four decimal places. It returns `model_status: "ACTIVE"`, `runtime_method: "ML regression"`, and an explanatory `model_reason`.

A RuntimePredictor instance containing a loaded model can still return FALLBACK for a particular reading outside the checked domain. Thus the health endpoint's `model: "loaded"` is different from a sample's `model_status: "ACTIVE"`.

### 10.10 Calculated fallback

When inference cannot be used:

```text
draw = max(0.015, 0.7 × current + 0.3 × recent_average_current) A
charge = 2.0 × (SoH / 100) × (SoC / 100) Ah
fallback_runtime = min(48, max(0, charge / draw)) hours
```

This returns `model_status: "FALLBACK"` and `runtime_method: "Calculated estimate"`. Reasons distinguish unavailable artifacts, out-of-range inputs, and prediction failures. Results are rounded to four decimals. The minimum current denominator avoids division by zero and unbounded estimates; the cap means an idle device does not receive an infinite prediction. Zero SoC gives zero runtime.

The fallback does not include the generator's thermal/activity efficiency factors. It maintains continuity of the dashboard and decision pipeline; it is not guaranteed conservative in every physical condition.

### 10.11 Calculation versus ML classification

| Output | How it is produced | Academically accurate wording |
| --- | --- | --- |
| SoC | Hybrid voltage/coulomb calculation | Estimated SoC |
| SoH | Fixed usable/nominal capacity ratio | Capacity-based prototype SoH estimate |
| Power | V × I | Calculated power |
| Energy | Trapezoidal integration | Calculated accumulated energy |
| Consumption trend | Threshold comparison against prior average | Rule-based trend label |
| Remaining runtime, ACTIVE | Random Forest prediction | ML-predicted remaining runtime |
| Remaining runtime, FALLBACK | Charge/current calculation | Calculated fallback runtime |
| Power mode | Ordered thresholds using several inputs, including runtime | Rule-based, runtime-informed power policy |
| Recommendations | Explicit condition/message rules | Rule-based recommendations informed by analytics and runtime |

## 11. Actual model performance

**Evidence:** [models/model_metrics.json](models/model_metrics.json), whose contents match the metadata in the inspected saved artifact. These values were read, not recalculated by retraining.

| Metric | Exact saved value | Readable interpretation |
| --- | ---: | --- |
| MAE | **0.3033769681590672 hours** | About **18.20 minutes** average absolute error on the synthetic holdout |
| RMSE | **0.5933013436852731 hours** | About **35.60 minutes**, with larger errors penalized more strongly |
| R² | **0.9955057093051844** | Coefficient of determination on the synthetic test targets; not accuracy |
| Calculated baseline MAE | **0.3745046590968543 hours** | About **22.47 minutes** average absolute error for the baseline |

Other saved metadata:

- Model: `RandomForestRegressor`.
- Training rows: **12,800**; testing rows: **3,200**.
- Trees: **120**; seed: **42**; scikit-learn version: **1.7.2**.
- Recorded training timestamp: **2026-09-28T14:29:25.457284+00:00**.
- Target unit: hours; runtime cap: 48 hours.
- Dataset description: independent synthetic scenarios with an 80/20 holdout split.

### 11.1 Metric definitions

For true synthetic targets `y_i`, predictions `ŷ_i`, `n` test rows, and mean target `ȳ`:

```text
MAE  = (1/n) × Σ |y_i - ŷ_i|
RMSE = sqrt((1/n) × Σ (y_i - ŷ_i)^2)
R²   = 1 - [Σ (y_i - ŷ_i)^2 / Σ (y_i - ȳ)^2]
```

MAE is easy to discuss as an average time error. RMSE is more sensitive to a smaller number of large mistakes. R² compares prediction error with the variation in targets around their mean; it is not the fraction of predictions that are correct and must not be presented as “99.55% accuracy.”

### 11.2 Baseline and interpretation

The baseline uses the held-out SoH, SoC, current, and recent average current:

```text
baseline_hours = clip(2 × SoH/100 × SoC/100
                      / (0.7 × current + 0.3 × recent_average_current), 0, 48)
```

The forest's recorded MAE is lower than that baseline on the same synthetic holdout. The comparison establishes a result for this specific generator and split, not superiority over real calibrated battery estimation or all possible baselines.

### 11.3 Saved feature importance

The metadata includes the forest's feature importances. The following percentages are derived by multiplying the saved fractions by 100 and rounding:

| Feature | Approximate importance |
| --- | ---: |
| Current | 54.1251% |
| Voltage | 21.5104% |
| SoC | 12.0901% |
| Recent average current | 9.5266% |
| SoH | 2.1049% |
| Power | 0.3476% |
| Recent average power | 0.1613% |
| Device load | 0.0696% |
| Temperature | 0.0644% |

These are model-specific split-based importances, not experimental causal contributions. Correlated inputs such as voltage/SoC and current/power can share or redistribute importance. Small synthetic importance does not mean a variable is physically irrelevant or unimportant to the rule-based safety-oriented thresholds.

### 11.4 Validity of the reported result

Synthetic targets were generated from known relationships closely related to the input features. Learning those relationships can produce high R². **This evaluation does not establish real-world battery prediction accuracy.** It does not quantify error across cell chemistries, aging states, sensor offsets, real duty cycles, or unseen environmental conditions. The repository contains no measured discharge-validation study or confidence interval for physical-device runtime.

## 12. Smart power management

**Source:** [battery/power_manager.py](battery/power_manager.py), especially `POLICIES` and `select_policy()`.

### 12.1 Inputs and algorithm type

Mode selection uses estimated SoC, predicted or fallback runtime, current, temperature, normalized device load, and previous mode. SoH and power are not directly tested by the decision branches, although SoH can influence runtime prediction. The engine is an ordered, deterministic rule system; it is not a separately trained classifier.

### 12.2 Exact selection order

The first matching branch wins:

1. **Enter CRITICAL** if SoC ≤10%, runtime ≤0.25 hours, temperature ≥40 °C, or temperature ≤0 °C.
2. **Retain CRITICAL** when the previous mode was CRITICAL and any of these is true: SoC <13%, runtime <0.4 hours, temperature ≥38 °C, or temperature ≤2 °C.
3. **Enter POWER SAVING** if SoC ≤30%, runtime ≤1.5 hours, temperature ≥36 °C, or current ≥0.40 A.
4. **Retain POWER SAVING** when the previous mode was POWER SAVING and any of these is true: SoC <34%, runtime <1.8 hours, temperature ≥34.5 °C, or `current / 0.55 ≥ 0.36 A`.
5. **Select PERFORMANCE** only when all remaining conditions hold: SoC ≥70% for entry, or ≥65% if the previous mode was PERFORMANCE; runtime ≥3 hours; temperature <33 °C; device load ≥0.7.
6. **Otherwise select BALANCED**.

The strictness of the comparison operators matters. For example, leaving the CRITICAL hold condition requires temperature **greater than 2 °C and less than 38 °C**, as well as SoC ≥13% and runtime ≥0.4 hours. Leaving one hold condition does not guarantee BALANCED; a subsequent branch can still select POWER SAVING.

### 12.3 Operating policies

| Mode | Sampling interval | Communication policy returned by code | Optimization actions | Current factor | Assumed saving |
| --- | ---: | --- | --- | ---: | ---: |
| PERFORMANCE | 2 s | Wi-Fi always active | Full sensor sampling; full processing enabled | 1.00 | 0% |
| BALANCED | 5 s | Normal Wi-Fi; batch routine messages | Sample every 5 seconds; batch routine telemetry | 0.82 | 18% |
| POWER SAVING | 15 s | Transmit every 30 seconds | Reduce sensor sampling; disable nonessential processing | 0.55 | 45% |
| CRITICAL | 30 s | Essential alerts only; otherwise sleep | Essential sensing only; minimize radio and processor activity | 0.25 | 75% |

Each returned policy also includes `mode`, a readable `reason`, and `control_type: "SIMULATED POLICY"`.

### 12.4 Recovery margins and feedback

Different entry and recovery thresholds reduce frequent switching near a boundary. The POWER SAVING recovery expression divides measured current by its assumed 0.55 multiplier to approximate unthrottled demand. This prevents a reduction caused by the saving policy from immediately being mistaken for permanently reduced workload.

This is a simplified policy assumption and is applied to both sources. For ESP32, its interpretation is strongest only if the firmware actually follows the returned mode and produces a comparable current reduction; there is no acknowledgement or measured-actuation verification.

The next simulator tick uses the previous simulated mode's factor. There can therefore be a short delay between selecting a load/mode and seeing its full current response, further softened by the simulator's 0.55 current-relaxation coefficient.

### 12.5 What “energy saving” means here

```text
estimated_energy_saving (%) = round((1 - current_factor) × 100)
```

The percentage is a configured relative target-current reduction compared with PERFORMANCE at the same nominal load. It is not a measured energy saving over an experiment, nor a comparison between two accumulated-energy traces. Voltage changes, noise, current transients, and changing modes mean measured simulated power ratios need not exactly equal the displayed percentage.

The sampling and communication intervals are policy descriptions. The backend does not change its approximately two-second telemetry monitoring loop to 5, 15, or 30 seconds when the mode changes. Real firmware would need to implement those schedules.

## 13. Recommendation engine

**Source:** `recommendations()` in [battery/power_manager.py](battery/power_manager.py).

Recommendations are deterministic messages based on current analytics and the selected mode. They are not generated by a language model and do not use a second trained model.

| Implemented condition | Returned recommendation |
| --- | --- |
| Temperature ≥36 °C | “Temperature is elevated. Reduce processing load and check the battery environment.” |
| Temperature ≤0 °C | “Temperature is below the prototype operating range. Inspect the battery before continuing.” |
| SoC ≤10% | “Battery reserve is critical. Keep essential sensing only and recharge the battery.” |
| Runtime ≤1.5 hours | “Predicted runtime is low. Use power-saving operation and plan a recharge.” |
| Otherwise, if mode is POWER SAVING | “Retain reduced sampling and communication until battery and load recovery thresholds are met.” |
| Trend is INCREASING **or** current ≥0.35 A | “Battery consumption is increasing or high. Reduce sensor sampling and communication frequency.” |
| No previous message applies and mode is PERFORMANCE | Normal-range message followed by “Performance operation supports the current high workload.” |
| No previous message applies and mode is not PERFORMANCE | Normal-range message followed by “Balanced operation is recommended.” |

Several messages can be returned together. Temperature, charge, and consumption checks are independent. Only the low-runtime/retain-saving pair uses `if`/`elif`, so those two messages are mutually exclusive in one evaluation.

The service returns the full `recommendations` list and also `recommendation`, which is its first element. That first element follows source-code order; it is not a learned relevance ranking. The dashboard displays the list in the highlighted recommendation panel.

## 14. Database

**Sources:** [database/db.py](database/db.py), [battery/service.py](battery/service.py), and the existing database schema inspected through `mode=ro&immutable=1`. No telemetry rows were inserted, updated, or deleted for this report.

### 14.1 Location and initialization

The default file is `data/battery.db`. `DATA_DIR` can select another directory, and `DATABASE_PATH` can override the full file path. Relative configuration paths are anchored to the project root. On the prepared Render configuration, the file is `/var/data/battery.db`.

`Database.__init__()` creates the parent directory and missing tables, and enables WAL journaling. Connections use a ten-second SQLite timeout and `sqlite3.Row` access, commit or roll back through a context manager, and are explicitly closed. A separate database server or ORM is not used.

### 14.2 Relevant schema

The following is a readable formatting of the implemented schema:

```sql
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS telemetry (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         TEXT NOT NULL,
    voltage           REAL NOT NULL,
    current           REAL NOT NULL,
    temperature       REAL NOT NULL,
    device_load       REAL NOT NULL,
    soc               REAL NOT NULL,
    soh               REAL NOT NULL,
    power             REAL NOT NULL,
    energy_consumed   REAL NOT NULL,
    predicted_runtime REAL NOT NULL,
    power_mode        TEXT NOT NULL,
    source            TEXT NOT NULL,
    session_id        TEXT NOT NULL,
    model_status      TEXT NOT NULL,
    details           TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS telemetry_stream
ON telemetry (source, session_id, id);

CREATE TABLE IF NOT EXISTS events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    message   TEXT NOT NULL,
    level     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS state (
    id    INTEGER PRIMARY KEY CHECK (id = 1),
    value TEXT NOT NULL
);
```

SQLite can also maintain its internal auto-increment bookkeeping; that is not an additional application-defined feature.

### 14.3 Important data meanings

| Table/field | Meaning |
| --- | --- |
| `telemetry.timestamp` | Server UTC processing timestamp |
| `voltage`, `current`, `temperature`, `device_load` | Original validated/generated inputs |
| `soc`, `soh`, `power`, `energy_consumed` | Estimated/calculated quantities; energy is cumulative Wh for that source/session state |
| `predicted_runtime` | Hours, whether produced by ML or fallback |
| `power_mode`, `model_status` | Selected operating mode and per-reading prediction status |
| `source`, `session_id` | Source/session isolation for history |
| `details` | JSON snapshot containing additional fields such as policy, recommendations, averages, and quality note |
| `events.message`, `events.level` | Actual event description and `info`/`warning` level |
| `state.value` | JSON snapshot of controls, source, latest reading, simulator state, estimator state, sessions, modes, and temperature flags |

The database schema does not itself contain numeric-range CHECK constraints for telemetry; API validation and application calculations provide those checks before storage.

### 14.4 Storage transaction

After the full processing pipeline, `Database.save()`:

1. Inserts one telemetry row if a reading was supplied.
2. Assigns the generated integer id back to the reading/latest state.
3. Inserts events associated with the operation.
4. Inserts or updates the single state row with id 1.
5. Prunes old telemetry and events by their auto-increment ids.
6. Commits these changes together.

JSON serialization disallows NaN values. SQL data values use parameter placeholders; the constructed telemetry column list is internal, not taken from an API payload. Controls can save events/state without a new telemetry row.

The state includes both source estimators. Simulation reset resets its estimator and changes its session id but does not erase all database history. There is no separate ESP32 reset endpoint.

### 14.5 Retention and retrieval

- Retention keeps at most the recent **10,000 telemetry ids** and **1,000 event ids** under normal sequential insertion. These limits are shared across sources, not per device.
- At approximately one simulation row every two seconds, 10,000 rows represent roughly 5.5 hours of wall-clock history, not 5.5 accelerated battery hours.
- History selects rows by the current `source` and `session_id`, orders by descending id, applies the requested limit, and reverses them into chronological order for display.
- API history defaults to 60 points and accepts limits 1–60.
- `events()` returns the newest **16 events** by default. Events are global and can contain messages from both sources.
- The service projects chart history to `id`, `timestamp`, `soc`, `voltage`, `current`, `temperature`, and `power`; the database retains more details than that compact response list.

## 15. REST API

**Source:** route declarations, validators, configuration, and error handlers in [app.py](app.py), plus service return values.

### 15.1 Endpoint inventory

| Method | Path | Purpose | Input | Successful output |
| --- | --- | --- | --- | --- |
| GET | `/` | Serve the dashboard | None | HTML, normally HTTP 200 |
| GET | `/static/<path:filename>` | Flask's static-file route for CSS/JS assets | Relative static asset path | Asset body with appropriate MIME type |
| GET | `/api/telemetry` | Retrieve current reading, controls, status, charts, events, model metadata | Optional `limit=1..60` | JSON snapshot, HTTP 200 |
| POST | `/api/telemetry` | Accept and process an ESP32-compatible reading | Valid JSON telemetry object | Flat processed reading plus `status`, HTTP 201 |
| POST | `/api/control` | Change simulation controls or reset simulation | One or more recognized control fields | Snapshot JSON, HTTP 200 |
| GET | `/health` | Check loaded-model state and database query availability | None | Health JSON; HTTP 200 or 503 as described below |

Flask also supplies its normal automatic HEAD/OPTIONS handling where applicable. There are no implemented `/api/history`, login, user-management, or model-training endpoints.

### 15.2 GET telemetry snapshot

`limit` must be an ASCII digit string of at most two characters whose integer value is between 1 and 60. The default is `60`. Invalid values return HTTP 400.

The response contract is:

```text
{
  status: "success",
  telemetry: <latest processed reading object, or null>,
  system: {
    status: <ONLINE | WAITING | PAUSED | STALE | ERROR>,
    source: <simulation | esp32>,
    sample_age_seconds: <number or null>,
    message: <string>,
    poll_interval_seconds: 2
  },
  controls: {
    simulation_enabled: <boolean>,
    device_load: <LOW | MEDIUM | HIGH>,
    time_scale: 120
  },
  history: [<up to limit recent chart-point objects>],
  activity: [<up to 16 recorded event objects>],
  model: {available: <boolean>, reason: <string>, metadata: <object or null>}
}
```

This is **type notation**, not a captured response. Chart history is restricted to the current source/session. Repeated GET calls do not each create another sample.

### 15.3 POST telemetry request

```json
{
  "voltage": 3.85,
  "current": 0.12,
  "temperature": 29.5,
  "device_load": 0.45,
  "source": "esp32"
}
```

The first four fields are required; `source` defaults to `esp32`. No other fields are accepted. Numeric strings, booleans used as numbers, NaN, infinity, out-of-range values, arrays, null, and malformed input are rejected. Temperature, voltage, current, and activity limits are listed in Section 6.

The response is a **flat** object with `status: "success"` and the processed fields; it is not wrapped in the GET endpoint's `telemetry` envelope. Important fields include:

```text
status, id, timestamp, source, session_id,
voltage, current, temperature, device_load,
soc, soh, power, energy_consumed, elapsed_battery_seconds,
recent_average_current, recent_average_power,
consumption_trend, battery_condition,
nominal_capacity_ah, estimated_usable_capacity_ah,
predicted_runtime, model_status, runtime_method, model_reason,
power_mode, policy, recommendations, recommendation,
quality_note, integration_seconds, time_scale
```

Runtime and mode depend on the received inputs and previous estimator/mode state, so a fixed numerical response should not be fabricated for an academic report. For the input above, instantaneous power is deterministically `3.85 × 0.12 = 0.462 W`.

### 15.4 POST controls

Example accepted request:

```json
{
  "simulation_enabled": true,
  "device_load": "HIGH",
  "reset": false
}
```

At least one recognized field is required. `simulation_enabled` and `reset` must be JSON booleans; `device_load` must be LOW, MEDIUM, or HIGH. Unknown keys are rejected.

`reset: true` resets simulation state, energy, and its session id. It does not by itself require simulation to turn on. The dashboard's reset button sends both `reset: true` and `simulation_enabled: true`. The selected load is retained unless explicitly changed. Reset does not delete telemetry history and does not reset the ESP32 estimator.

### 15.5 Health endpoint

When the model is loaded and a query of the telemetry table succeeds:

```json
{"status": "healthy", "model": "loaded", "database": "connected"}
```

If the model is unavailable but the database is queryable, the endpoint returns HTTP 200 with `status: "degraded"` and `model: "fallback"`. This allows the existing calculated fallback to remain available. A SQLite query failure returns HTTP 503 with `status: "unhealthy"` and `database: "unavailable"`.

The health check performs a read query of the telemetry table. It does not verify a new write transaction, perform a live model prediction, confirm hardware connectivity, or comprehensively test the background worker. It is an availability indicator with a deliberately limited scope.

### 15.6 Errors and headers

| HTTP status | Implemented use |
| --- | --- |
| 400 | Invalid payload fields/types/ranges, invalid controls or history limit, malformed JSON |
| 404 | Missing API path or resource |
| 405 | Unsupported method, through Flask's HTTP handling |
| 413 | Body exceeds `MAX_CONTENT_LENGTH = 4096` bytes |
| 415 | POST body is not supplied as supported JSON content type |
| 503 | Database-operation failure; health uses its own unhealthy response |

API validation and handled API HTTP errors use `{"status":"error","error":"explanation"}`. Non-API HTTP errors follow normal Flask handling. API and health responses set `Cache-Control: no-store`; all responses set `X-Content-Type-Options: nosniff`. The app explicitly registers JavaScript and CSS MIME types.

## 16. Current web dashboard

**Sources:** [templates/index.html](templates/index.html), [static/css/style.css](static/css/style.css), and [static/js/dashboard.js](static/js/dashboard.js).

### 16.1 Current visual design

The interface is **light mode**, not the earlier dark dashboard. Its main background is `#F4F7FB`, cards are white, primary text is navy `#172B4D`, and the primary accent is blue `#2563EB`. Borders are subtle, shadows are soft, and status text accompanies color so state is not communicated through color alone.

The desktop sidebar is 224 px wide, white, and uses a blue active-navigation indicator. Links navigate to Overview, Battery telemetry, AI analysis, Power management, and System activity on the same page. The header preserves the project heading and subtitle and displays System, Data Source, and AI Model badges.

The former top PROTOTYPE disclaimer banner is absent. Individual cards and model/policy descriptions still distinguish estimates, ML predictions, and assumed savings; the technical limitations are documented in README and this report.

### 16.2 Visible information

| Interface area | Actual contents |
| --- | --- |
| Header badges | System state, SIMULATION/ESP32 source, AI model ACTIVE/FALLBACK/READY state |
| Battery overview | SoC, SoH, voltage, current, temperature, power, remaining runtime, current mode |
| SoC and SoH cards | Large percentages and progress bars; estimated/assumed-capacity descriptions |
| Energy strip | Accumulated energy in Wh, tracked battery time, and integration/source note |
| Telemetry section | Five live charts and recent-sample count |
| AI Battery Analysis | Remaining runtime, trend, battery condition, model status/reason, highlighted recommendations |
| Expandable model information | Model type, tree count, seed, train/test counts, metrics, feature names, synthetic-evaluation caveat |
| Smart Power Management | Mode badge, reason, sampling interval, communication policy, optimization actions, assumed saving percentage |
| Recent System Activity | Actual recorded events in a timeline-style feed, with timestamps and warning markers |
| Demo controls | Simulation toggle; LOW/MEDIUM/HIGH load selector; Reset simulation |

### 16.3 Status interpretation

The service evaluates status in this order: ERROR if its worker error marker is set; PAUSED for an inactive simulation source; WAITING if no latest reading exists; STALE if age is greater than 10 seconds for simulation or 30 seconds for ESP32; otherwise ONLINE.

The browser displays OFFLINE on a failed refresh and keeps the prior readings visible with an error message. OFFLINE is a frontend fetch state, not another value returned in the server's `system.status` field. READY is used in the frontend when a model is loaded but no reading is yet available.

An ONLINE simulated source means fresh simulated data is being processed. It does not prove physical hardware is connected. A model ACTIVE badge describes the latest reading's successful ML prediction, not a laboratory-validated prediction.

Semantic styling uses green for ONLINE/ACTIVE/BALANCED, blue for information/PERFORMANCE/READY, orange for warnings/POWER SAVING/FALLBACK/PAUSED/STALE, and red for CRITICAL/ERROR/OFFLINE.

### 16.4 JavaScript update mechanism

1. Deferred scripts initialize the five chart objects after the document is parsed.
2. `poll()` fetches relative URL `/api/telemetry`; no localhost URL is embedded in dashboard requests.
3. `fetchJson()` disables caching and applies an eight-second abort timeout.
4. `render()` updates numeric text, progress bars, badges, controls, recommendations, model details, and events.
5. A request-in-flight flag prevents overlapping poll requests; polling waits 500 ms if busy with another request/control.
6. The next normal poll is scheduled 2,000 ms after the preceding request finishes. Network/processing latency therefore adds to the apparent update interval.
7. A control revision counter prevents a response requested before a control change from overwriting the newer control state.
8. Control requests POST JSON to `/api/control`; controls are disabled while the operation is busy, and the load selector is disabled when simulation is off.
9. Rendering uses `textContent` and created DOM elements for server-provided strings, rather than inserting untrusted HTML.

Runtime hours are rounded to whole minutes for display as `h` and `min`. On FALLBACK, the runtime heading changes to explicitly identify fallback. Failure to load Chart.js produces a chart warning while numeric telemetry can continue updating.

### 16.5 Responsiveness and accessibility features

The CSS includes breakpoints at 1650, 1300, 1050, 760, and 380 px. Metrics change from four columns to two; charts and analysis sections stack as width decreases. At 760 px and below, the sidebar becomes an above-content navigation area with horizontally scrollable links rather than a fixed side panel.

Implemented accessibility-related features include a skip link, named navigation, labeled controls, visible keyboard focus, meter semantics, chart accessible labels, status/alert roles, and reduced-motion styling. These features are not evidence of a complete accessibility audit or certification.

## 17. Live data visualization

**Source:** `chartSpecs`, chart initialization, and chart update logic in [static/js/dashboard.js](static/js/dashboard.js).

| Chart | Meaning | Unit | Line color | Axis configuration |
| --- | --- | --- | --- | --- |
| State of Charge | Hybrid estimate of remaining charge over received samples | % | Blue `#2563EB` | Fixed 0–100 |
| Voltage | Terminal-voltage evolution | V | Teal `#0F766E` | Suggested 3.0–4.2, not hard clipping |
| Current | Changing discharge draw | A | Purple `#7C3AED` | Starts from zero |
| Temperature | Thermal response/received temperature | °C | Brown-orange `#B45309` | Suggested 24–40, not hard clipping |
| Power Consumption | Calculated V × I history | W | Blue-teal `#0369A1` | Starts from zero |

Each is a responsive line chart with light grid lines, bottom legend, white tooltip, a small translucent fill, and animation disabled for regular updates. `maintainAspectRatio` is false; the CSS-controlled container supplies height. Canvas backgrounds are transparent over white chart cards.

The server returns at most 60 recent points and the frontend additionally applies `slice(-60)`. Charts update only when a key based on source, session, newest id, and point count changes. The frontend replaces labels/data and calls `chart.update("none")`; it does not create five new chart objects on every poll.

X-axis labels use the server receipt timestamps formatted in the browser's local time. They are categorical sample positions rather than a continuous time scale, so irregular ESP32 intervals do not produce proportionally spaced gaps. Simulation discharge uses accelerated battery time even though labels show wall-clock receipt time.

**Engineering interpretation:** live charts help a student connect a load change to current, power, voltage, temperature, and reserve trends. They also reveal pauses and source changes. They should not be used to infer that a displayed two-minute wall-clock window equals two minutes of simulated battery discharge.

## 18. ESP32 integration

**Implemented boundary:** a validated REST ingestion endpoint and returned policy. **Not implemented:** an ESP32 firmware program, sensor wiring/calibration, physical actuation, or acknowledgement protocol.

### 18.1 Expected integration path

```text
ESP32 sensor readings and device activity
                |
            Wi-Fi network
                |
     HTTP POST /api/telemetry (JSON)
                |
   Flask validation -> shared service
                |
 battery analytics -> runtime prediction
                |
 power policy -> recommendations -> SQLite
                |
 HTTP 201 processed reading + policy response
                |
 ESP32 firmware interprets and applies policy (future hardware work)
```

For a local network, run Flask with `FLASK_HOST=0.0.0.0` and use the computer's LAN address, not `localhost` on the ESP32. For a deployed service, firmware would use the assigned HTTPS URL and certificate validation. Network credentials and sensor calibration belong to firmware/provisioning and are not included here.

### 18.2 Request and response contract

The expected request is the four numeric fields plus optional source shown in Section 15. An ESP32 HTTP client should set `Content-Type: application/json` and handle both the 201 success response and JSON error responses.

The relevant policy portion of the successful response has this **structural form**, not a newly captured device measurement:

```text
{
  status: "success",
  source: "esp32",
  timestamp: <server UTC ISO timestamp>,
  soc: <number, percent>,
  soh: <number, percent>,
  power: <number, watts>,
  energy_consumed: <number, watt-hours>,
  predicted_runtime: <number, hours>,
  model_status: <ACTIVE | FALLBACK>,
  power_mode: <PERFORMANCE | BALANCED | POWER SAVING | CRITICAL>,
  policy: {
    mode: <selected mode>,
    sampling_interval: <2 | 5 | 15 | 30 seconds>,
    communication_policy: <descriptive string>,
    current_factor: <1.0 | 0.82 | 0.55 | 0.25>,
    actions: [<descriptive action strings>],
    reason: <selection explanation>,
    estimated_energy_saving: <0 | 18 | 45 | 75 percent>,
    control_type: "SIMULATED POLICY"
  },
  recommendation: <first recommendation>,
  recommendations: [<one or more messages>],
  ... additional reading fields listed in Section 15
}
```

Firmware should use a stable mode-to-action mapping rather than treat free-form explanation strings as executable instructions. Implementing real sampling, processor throttling, radio scheduling, and deep sleep is future hardware work. The server does not confirm that returned actions were applied.

### 18.3 Practical timing and scope constraints

The README suggests posting every 2–5 seconds for a demonstration. That recommendation is not enforced as a device interval by the server. In contrast, some returned policies describe 30-second communication or essential alerts only. Without a separate heartbeat, such firmware could appear STALE, and gaps above 60 seconds would be excluded from energy integration. That trade-off should be addressed when actual firmware is designed.

All accepted external requests belong to one `esp32` source; there is no `device_id`, sequence-number validation, device timestamp acceptance, or anti-replay check. Stop ongoing device posts before switching to simulation, because the next accepted POST takes control of the selected source again.

## 19. Simulation demonstration

This is a repeatable **demonstration procedure**, not a claim that a new experiment was performed while preparing this report. It uses the implemented controls and requires no physical ESP32.

| Step | Action | Observation and explanation |
|---|---|---|
| 1 | Start the existing application using the commands in Section 21 and open the dashboard. | A fresh installation starts simulation; restored controls can instead leave it paused or on ESP32. Check the displayed source. |
| 2 | Turn Simulation ON, or select Reset Simulation to begin a fresh simulated session. | Reset resumes simulation and resets its charge/energy state. It does not erase historical database records. |
| 3 | Select MEDIUM load and observe several updates. | Current moves gradually toward its workload/policy target. Voltage, temperature, power, runtime, and charts update together. |
| 4 | Select LOW load and wait several samples. | Current and power generally decrease; predicted remaining runtime generally increases. The response is smoothed rather than an instantaneous replacement with an independent random number. |
| 5 | Note current, power, SoC, runtime, policy, and the consumption trend. | These are useful screenshots or a small observation table for an academic demonstration. Record the source and session to avoid mixing runs. |
| 6 | Select MEDIUM again. | Observe the transition toward intermediate consumption. A trend label can return to STABLE once the recent-current window catches up. |
| 7 | Select HIGH and allow several updates. | Increased requested activity raises consumption relative to LOW, although automatic policy reduction can partly offset the increase. |
| 8 | Compare AI runtime, sampling interval, communication policy, and estimated saving. | Runtime changes with the feature vector. Rule-based mode selection uses multiple conditions; a particular mode is not guaranteed solely by selecting a load. |
| 9 | Inspect recommendations and Recent System Activity. | Telemetry and prediction events occur during processing. Mode-change and temperature events appear only when their implemented conditions occur. |
| 10 | Continue the accelerated simulation. | Battery time advances at 120 times accepted wall-clock elapsed time. Falling charge/runtime may trigger conserving modes. Do not promise an exact transition time because workload and feedback affect discharge. |
| 11 | Turn Simulation OFF. | Sampling pauses; repeated browser polls do not themselves create readings. Existing charts remain available and system status becomes PAUSED for a paused simulation source. |
| 12 | Select Reset Simulation. | A new simulation session begins, with a fresh history view and restored initial simulator state. The selected load is retained unless changed separately. |

For a controlled comparison, use the same initial conditions and load duration in separate sessions. Record that savings are policy assumptions and that accelerated simulated battery time differs from the timestamps displayed on the chart. A visual comparison is not a measured physical energy-efficiency experiment.

An optional API demonstration can POST a deliberately elevated temperature, such as `42.0` °C with otherwise valid values. This activates the ESP32 stream, pauses simulation, selects CRITICAL, and uses runtime fallback because temperature is outside the ML prediction domain. Label this explicitly as **manually supplied test telemetry**, not a real sensor measurement. Stop external posts and reset or re-enable simulation afterward.

## 20. Testing and evidence

**Evidence distinction:** the test files were inspected, but tests, the application, browser automation, and training were not run for this documentation task. The existing README records earlier successful validation. The following counts describe test methods present in the current source; they are not newly executed results.

### 20.1 Automated backend test inventory

There are **21 automated backend test methods** across four Python test modules: 5 battery tests, 2 model tests, 9 API tests, and 5 deployment tests.

| File / test method | Main behavior checked |
|---|---|
| `tests/test_battery.py`: `test_energy_integrates_in_watt_hours` | Power/energy units and integration against a known numerical result. |
| `test_simulator_load_and_discharge` | Gradual discharge and different responses to LOW and HIGH loads. |
| `test_all_modes_and_non_soc_triggers` | All four modes, non-SoC triggers, and policy hysteresis. |
| `test_optimization_lowers_current` | Reduced policy factor lowers simulated current and consumption relative to an unrestricted comparison. |
| `test_empty_battery` | Depleted-battery behavior. |
| `tests/test_model.py`: `test_trained_model` | Saved-model loading, ACTIVE predictions, expected load/runtime relationship, and recorded metric thresholds. |
| `test_missing_corrupt_and_out_of_domain` | Missing/corrupt artifact and out-of-domain fallback, including zero-charge runtime behavior. |
| `tests/test_api.py`: `test_routes_and_read_only_get` | Page/static routes, MIME types, snapshot behavior, history-limit validation, and missing routes. |
| `test_esp32_post_and_source_isolation` | Accepted external telemetry, processed power, simulation pause, persistence, and separate source histories. |
| `test_input_validation_and_size_limit` | Invalid ranges/types, booleans, nonfinite numbers, huge integers, extra fields, malformed JSON, content type, and body size. |
| `test_controls_pause_resume_reset` | Control validation, pause/resume timing, and new-session reset with retained stored history. |
| `test_restart_restores_state_and_no_downtime_energy` | Persisted service state and exclusion of server downtime from consumption integration. |
| `test_real_time_integrator_gap_and_stale` | Real elapsed-time integration, long-gap exclusion, and stale-source status. |
| `test_db_failure_rolls_back_estimation` | Database failure does not leave the in-memory estimator advanced beyond committed state. |
| `test_concurrent_posts_and_history_bound` | Concurrent requests, unique stored sample identifiers, and the bounded recent-history response. |
| `test_temperature_event_and_fallback` | Abnormal temperature produces the relevant critical policy, warning event, and fallback. |
| `tests/test_deployment.py`: `test_wsgi_export_and_health` | Application export and health response with a loaded model and accessible database. |
| `test_health_preserves_fallback_and_reports_db_failure` | Degraded-but-available missing-model behavior versus an unavailable database. |
| `test_environment_storage_and_model_paths` | Environment-configured storage/model locations. |
| `test_gunicorn_bind_and_worker_lifecycle` | Environment port, single worker, no preload, and worker start/stop hooks through configuration-level tests. |
| `test_light_template_has_no_prototype_banner` | Light-template markers, banner removal, and unique header identification. |

The model test checks saved metric values; it does not establish a new real-battery validation result. Configuration-level Gunicorn tests are not equivalent to running a production Linux service.

### 20.2 Browser, JavaScript, and HTTP checks

`tests/browser_smoke.mjs` is a separate browser integration script using a Chromium-family browser and its debugging interface. It starts a temporary test setup and checks:

- Five real Chart.js instances and updating datasets, rather than merely the presence of canvas tags.
- Light-theme presentation and absence of the removed prototype banner.
- LOW/HIGH load changes in current, power, runtime, and charge behavior.
- Simulation pause/reset and external telemetry takeover.
- Critical/fallback labels after high-temperature telemetry.
- Model-information expansion, page-width/metric-card layout checks, and browser runtime errors.
- Continued numeric dashboard operation if the Chart.js asset is unavailable.

The script includes desktop/tablet/mobile widths; the README records earlier checks at **1440, 1366, 1024, 768, 390, and 320 pixels**. These are specific viewport checks, not a claim of testing every browser/device or a formal accessibility audit. Browser tooling is separate from runtime application dependencies.

`tests/http_smoke.py` targets a running server, checks `/`, `/health`, telemetry progression, an ESP32 POST, source changes, and controls. It sends modifying requests and should target a disposable test database when preservation of current demonstration history matters.

The documented JavaScript syntax check is:

```text
node --check static/js/dashboard.js
```

This detects syntax errors, not all browser interaction problems. The documented backend command is:

```text
python -m unittest discover -s tests -v
```

These commands are provided for future verification and were **not executed** during report preparation.

### 20.3 Recorded results and continuous integration

The [README](README.md) records that all 21 backend tests passed for the light-theme/deployment update, that Node's syntax check passed, that headless Edge verified live functionality and responsive layouts, and that the Render Blueprint passed official-schema validation. It also records successful live Flask HTTP checks using temporary storage. Those are **existing documented results**, not independent reruns in this report.

[`.github/workflows/checks.yml`](.github/workflows/checks.yml) prepares Ubuntu, Python 3.10.20, and Node 22; installs dependencies; runs backend tests and the dashboard syntax check; starts Gunicorn with temporary storage; waits for health; and runs the HTTP smoke script. The browser smoke script is not part of that workflow. Presence of the workflow establishes CI preparation, not evidence that a hosted workflow run or cloud deployment has succeeded.

The README documents earlier fixes for Windows JavaScript/CSS MIME associations, oversized-integer and history-limit validation, and stale pre-control GET responses overwriting newer control state. Relevant implementation safeguards are present. No such fixes were made during this documentation task.

### 20.4 Evidence still required for stronger validation

No physical-battery accuracy experiment, real ESP32 firmware endurance test, measured control-policy savings trial, formal security assessment, or quantitative code-coverage result is established by these files. A final academic submission should distinguish unit/integration correctness from experimental battery-model validity. Attach actual dated test output, photographs, screenshots, and deployment logs only when those records exist.

## 21. Deployment

Sources: [app.py](app.py), [gunicorn.conf.py](gunicorn.conf.py), [render.yaml](render.yaml), [requirements.txt](requirements.txt), [README.md](README.md), and [CI workflow](.github/workflows/checks.yml).

### 21.1 Deployment architecture and current evidence

```text
Local development:
VS Code / terminal -> Python -> Flask -> local SQLite + saved model
                                      -> browser dashboard

Prepared production workflow:
local Git repository -> GitHub repository -> Render build
                                          -> Gunicorn (one process)
                                              -> Flask
                                              -> simulator/service thread
                                              -> SQLite on persistent disk
                                              -> bundled runtime model
Browser / future ESP32 -> deployment URL -> REST endpoints
```

Git metadata exists locally. GitHub Actions and Render configuration files are present. This report does not verify a GitHub push, successful CI run, public deployment URL, or running Render instance. Those must be documented with actual deployment evidence if claimed in a final report.

### 21.2 Local installation and execution

From the project root, a Windows PowerShell setup using the virtual environment's executable directly is:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

If dependencies are already installed in the active Python environment, the existing local command remains:

```text
python app.py
```

Open `http://localhost:5000` with the default environment. The local host defaults to `127.0.0.1` and local port to `5000`; `FLASK_HOST` and `PORT` can override them. The URL is an example for local execution, not a hard-coded frontend API dependency. No retraining or dataset regeneration is needed to use the checked-in saved model.

For Linux/macOS virtual environments, the equivalent executable is `.venv/bin/python`. Gunicorn is the prepared Linux production entry point; local Windows execution uses Flask through `python app.py`.

### 21.3 Render Blueprint

The actual `render.yaml` declares:

| Setting | Repository value |
|---|---|
| Service type/runtime | Web service / Python |
| Name | `ai-battery-power-management` |
| Plan | `starter` |
| Instances | `1` |
| Build | `pip install -r requirements.txt` |
| Start | `gunicorn app:app` |
| Health path | `/health` |
| Python version | `3.10.20` |
| Data directory | `/var/data` |
| Unbuffered output | `PYTHONUNBUFFERED=1` |
| Disk | `battery-storage`, mounted at `/var/data`, size 1 GB |

The supplied configuration is a persistent-disk deployment, not a free-instance Blueprint. The README explains that using a free/ephemeral instance without persistent storage can lose SQLite history and saved state across instance replacement or redeployment. A paid persistent disk or an external database is required for durable cloud history in that deployment design. This is a documented storage implication; hosting plan availability and pricing are not audited here.

### 21.4 Production process settings

`gunicorn app:app` loads the repository's `gunicorn.conf.py` from the project root:

- Bind: `0.0.0.0` and environment `PORT`, defaulting to `8000` for Gunicorn.
- One worker process, `gthread`, four threads, and `preload_app=False`.
- Request timeout 60 seconds and graceful timeout 30 seconds.
- Access/error logs to standard streams.
- Start the battery service in `post_worker_init`; stop it in `worker_exit`.

One process is intentional: simulator/estimator state and locking are process-local. Increasing worker or instance counts without redesign could create competing simulators and inconsistent ownership of state. The app's local port and Gunicorn's default port differ; Render supplies its production port through the environment.

Paths are built relative to project files or explicit environment overrides. `DATA_DIR`, `DATABASE_PATH`, and `MODEL_PATH` support deployment-specific locations; the normal model remains `models/runtime_model.pkl`. Dependency versions are pinned, and the predictor checks the serialized scikit-learn version. Linux portability is prepared through these paths and the CI configuration; this report does not claim a newly executed Linux run.

### 21.5 Deployment procedure for a student

1. Keep application files, the saved model, model metadata, requirements, Gunicorn configuration, and Blueprint in the repository. Do not add local secrets or the live SQLite database; consult `.gitignore`.
2. Commit the intended project state and push to a GitHub repository under the student's control.
3. Review the configured CI job and its actual results.
4. Connect the repository to Render and create the service using the Blueprint. Review the declared plan and persistent disk before provisioning.
5. Confirm the build command, start command, Python version, data directory, and health path match the committed files.
6. After deployment, inspect logs and request `/health`, `/`, and `/api/telemetry`. Use controlled POST/control checks against the intended demonstration environment.
7. Open the public dashboard, verify live updates, and document the actual URL and date. Test history persistence separately if it is part of the deployment claim.
8. Before exposing real devices or confidential telemetry, add the security and operational controls described in Sections 22–24.

These are instructions for a future/operator-run deployment. No account, remote repository, or hosting configuration was changed for this report.

## 22. Security and validation

### 22.1 Implemented safeguards

| Safeguard | Actual implementation and scope |
|---|---|
| Payload validation | Telemetry must be a JSON object with the expected fields, finite numeric values, valid ranges, and accepted source. Booleans are rejected as numbers. Unknown fields are rejected. |
| Control validation | Only documented control keys, exact boolean values, and LOW/MEDIUM/HIGH load values are accepted. |
| Request bounds | Maximum request body is 4096 bytes; history limit is constrained to 1–60 and validated before use. |
| Database queries | SQL parameters are used for data values; table/column statements are application-defined. |
| Consistent state | Service locking serializes shared state changes; transaction failure restores estimator state and timing. This is correctness protection, not user authentication. |
| Error handling | Validation/HTTP errors have structured API responses; SQLite failures produce a service-unavailable response. |
| Browser output | Dynamic display values are assigned through text-oriented DOM operations rather than treating API strings as HTML. |
| Response headers | `nosniff` is set; JavaScript/CSS MIME types are registered explicitly; API and health responses are not cached. |
| Configuration | Storage/model paths and binding can use environment values. Runtime code is not tied to a Windows drive path. |
| Credentials | No ESP32 Wi-Fi credentials, API secret, or cloud account credentials are required in the application source. `.gitignore` excludes common local environment files. |
| Model fallback | Missing, incompatible, corrupt, or unsupported-domain model conditions result in a labeled calculated runtime estimate. |

The `source: "esp32"` field is a routing label, **not proof of device identity**. Any client able to access the unauthenticated endpoint can submit that label. Server receipt timestamps also do not prove when a sensor measured a value.

### 22.2 Current security boundaries

There is no implemented API authentication, per-device authorization, user account system, control ownership, rate limiting, replay protection, or multi-tenant isolation. A reachable client can submit telemetry and change demo controls. Local Flask execution does not provide TLS. Cloud edge HTTPS and proper firmware certificate verification would need to be considered in a real deployment.

Joblib/pickle artifacts must be trusted: loading an untrusted serialized Python model is not safe merely because its feature metadata is checked. The model path is deployment configuration, not an API upload feature. Protect model and configuration files through deployment access controls.

Input validation prevents many malformed requests but does not certify physical sensor truth or battery safety. Persisted state and read-only health queries improve reliability, but `/health` does not establish sensor calibration, successful actuator execution, database write availability, or full worker liveness. This application is a monitoring/control-policy prototype, not a hardware protection circuit.

## 23. Project limitations

1. **Synthetic ML evidence:** the training and test distributions are generated by the same mathematical procedure. Strong held-out metrics demonstrate learning within that synthetic setting, not validated field performance.
2. **Simplified simulated physics:** the simulator omits detailed electrochemical dynamics, battery chemistry variation, realistic aging trajectories, charging behavior, and a calibrated environmental model.
3. **Prototype SoC:** lookup voltage, a fixed resistance correction, current integration, and a gradual correction form an estimator. Unknown initial conditions, sensor bias, capacity mismatch, and the illustrative voltage curve limit accuracy.
4. **Assumed SoH:** operational usable capacity is fixed at 1.88 Ah against 2.0 Ah nominal, producing 94%. It is not inferred from measured degradation or laboratory capacity tests.
5. **No calibrated physical sensing:** the repository supplies an ESP32-compatible HTTP interface, not a completed calibrated sensor/firmware installation.
6. **Conditional runtime prediction:** the estimate depends on current/recent operating features and synthetic capacity assumptions. Future workload and policy changes can invalidate an earlier estimate. Output is capped at 48 hours and has no calibrated confidence interval.
7. **Domain limitations:** the accepted telemetry range is broader than the ML domain. Fallback is intentional for unsupported inputs; it is an estimate, not a guaranteed conservative runtime bound.
8. **Simulated control effects:** policy factors alter simulated current. Sampling intervals, radio actions, and savings percentages are not verified physical ESP32 energy savings.
9. **Time accounting:** simulation accelerates battery time, while external telemetry uses server elapsed time. Pauses, restarts, and long unknown external gaps do not accumulate energy. Chart timestamps represent receipt time, not accelerated battery time.
10. **Single-device architecture:** there is one selected source and no external device identifiers. Separate simulation/ESP32 estimators are not a multi-device fleet feature.
11. **Single-process scaling:** shared state relies on one Gunicorn worker and one configured instance. Horizontal scaling needs a different worker/state architecture.
12. **Finite retained history:** only the latest 10,000 telemetry rows and 1,000 events are kept globally. The dashboard shows at most 60 samples; it is not a complete archival analysis system.
13. **Cloud persistence:** SQLite durability depends on persistent storage. An ephemeral Render deployment can lose local data when replaced/redeployed.
14. **Security maturity:** public production use needs authentication, device identity, transport/security controls, and operational monitoring beyond the current prototype.
15. **Validation scope:** automated tests and documented browser checks verify selected software behaviors. They do not replace physical battery experiments, safety certification, or broad production reliability testing.

These limitations qualify the claims rather than negate the implementation: the system does implement a shared telemetry pipeline, saved ML inference, persistence, automatic policies, responsive live visualization, and hardware-compatible ingestion.

## 24. Future scope

Everything in this section is **future work**, not an implemented feature.

| Future work | Engineering purpose and connection to the present project |
|---|---|
| Calibrated voltage/current/temperature sensing | Replace simulated or manually supplied values with measured readings and quantified sensor error. |
| Controlled discharge experiments | Collect capacity, temperature, load, and cutoff data across cells and operating conditions. |
| Real discharge dataset | Retrain/evaluate runtime prediction using independent batteries or cycles, with leakage-resistant splits and physical ground truth. |
| Improved SoC estimator | Fit cell-specific OCV/resistance parameters, correct sensor bias, and evaluate a suitable observer/filter against reference measurements. |
| Measured SoH | Estimate usable capacity from validated full/partial cycle observations instead of retaining the fixed capacity assumption. |
| ESP32 policy execution | Implement sampling, radio scheduling, optional workload reduction, and acknowledgements of applied settings. |
| Deep-sleep integration | Coordinate sleep, wake-up, heartbeat, stale detection, and energy integration so long reporting gaps are handled deliberately. |
| Measured savings study | Compare equivalent device workloads before/after control changes with external energy measurement and repeatable trials. |
| Charging support | Introduce signed-current conventions and appropriate charge-state/energy behavior with explicit tests. |
| Cloud database and managed sampling worker | Separate persistence and background processing from web serving to improve durability and scaling. |
| Multi-device management | Add authenticated device IDs, per-device histories/estimators, configuration, and dashboards. |
| Authentication and authorization | Protect ingestion and controls; establish firmware credentials and secure transport practices. |
| Anomaly detection | Identify unusual thermal/current/voltage behavior using validated rules or a separately evaluated model. |
| Predictive maintenance | Use longitudinal degradation evidence to estimate maintenance needs; current runtime prediction is not remaining useful life prediction. |
| Mobile-focused experience | Extend the existing responsive web UI with additional mobile interaction/accessibility testing or a dedicated application if justified. |
| Uncertainty and monitoring | Report prediction uncertainty, detect distribution shift, and track model validity after deployment. |

A sensible sequence is physical sensing and trustworthy data first, then calibrated analytics/model evaluation, then verified actuation, and finally broader cloud/multi-device operation.

## 25. Detailed ten-week development breakdown

### How to use this academic progression

The following is a **suggested logical reconstruction of development**, based on the completed implementation. It is **not a verified historical work diary**. The inspected repository does not establish ten separate dated weeks of work. Do not present these entries as attendance records, experimental logs, or supervisor-approved milestones without supporting evidence.

Each week describes work that logically leads to the current system. OUTPUT/RESULT identifies the proposed milestone represented by existing artifacts; CHALLENGES identifies likely engineering challenges, not documented incidents unless explicitly stated elsewhere. WHO refers to roles/components rather than named contributors. Students should add their actual dates, responsibilities, screenshots, commit references, observations, and supervisor feedback. Earlier weeks need not contain the final code organization or all later functionality.

### Week 1 — Problem Definition and Requirement Analysis

**WHAT:** Define the problem of managing a battery-powered IoT device whose workload and communication activity affect operating time. Establish the proposed system's responsibilities: monitoring, prototype battery estimates, runtime prediction, automatic policy selection, and an operator dashboard. Separate a demonstrable software prototype from a production battery-management or safety system.

**WHY:** A clear problem boundary prevents inaccurate claims and unnecessary scope. The project needs a measurable output beyond displaying sensor numbers: it must connect changing consumption with estimated runtime and an explainable operating policy.

**WHO:** The student development team and academic supervisor are the intended planning roles. The eventual stakeholders are the dashboard operator and battery-powered IoT device. Flask, the model, and ESP32 are prospective system components at this stage, not completed integrations.

**WHERE:** Requirement notes and academic planning documents, with feasibility review in the VS Code/Python development environment. No physical sensor installation is required to define the problem.

**WHEN:** Initial project stage, before implementation of telemetry, model training, or frontend integration.

**HOW:** Break the objectives into inputs, processing, outputs, and exclusions. Inputs are voltage, current, temperature, and normalized device activity. Outputs include estimated charge/health, power/energy, predicted hours, and policy actions. Identify the need for simulation because physical hardware may not yet be available. Explicitly reserve ML for runtime prediction.

**OUTPUT/RESULT:** A proposed requirement specification and scope matching Sections 1–2 and the current README: a single-device prototype, simulation-first operation, ESP32-compatible ingestion, local persistence, and clear technical limitations.

**CHALLENGES:** Likely issues include distinguishing SoC from SoH, runtime from battery lifetime, and simulated savings from measured savings; keeping objectives achievable within a capstone schedule.

**LEARNING:** Requirements analysis, engineering problem formulation, measurable acceptance criteria, and responsible interpretation of estimation accuracy.

**NEXT STEP:** Translate requirements into component boundaries and a runnable application skeleton. Suggested reporting evidence: the student's actual requirement sheet and an approved scope diagram.

### Week 2 — System Architecture and Project Setup

**WHAT:** Define the architecture and organize the Python backend, HTML template, CSS/JavaScript assets, data directory, and model directory. Establish a minimal Flask page route before introducing full telemetry processing.

**WHY:** Separation of responsibilities makes the application understandable and testable. An early runnable interface confirms that the development environment works before battery algorithms and ML introduce additional dependencies.

**WHO:** The student developer, Flask application, browser, and planned battery/AI/database modules. The supervisor can review whether the proposed architecture supports the agreed objectives.

**WHERE:** VS Code, a Python virtual environment, the local project root, `app.py`, `templates/`, and `static/`. The final modular files provide evidence of the architecture's eventual implementation.

**WHEN:** Foundation stage after requirements and before dynamic data generation. A basic dashboard at this point need not include the later light-theme polish or trained model.

**HOW:** Map data flow into a shared processing service rather than duplicate simulator and device pipelines. Plan environment-relative paths and a model artifact location. Start with the `/` route, page title/subtitle, and essential metric placeholders. Establish version-control exclusions for environments, generated caches, local databases, and secrets. Add dependencies as their features are implemented.

**OUTPUT/RESULT:** A runnable Flask project structure and an architecture definition that can evolve into the current `battery/`, `ai/`, and `database/` packages. Final source evidence includes `app.py`, package modules, template/static directories, and `.gitignore`.

**CHALLENGES:** Likely issues include Python interpreter selection in VS Code, correct template/static paths, avoiding circular imports, and deciding which layer owns application state.

**LEARNING:** HTTP request/response basics, Flask templating, dependency isolation, modular design, configuration versus application logic, and local version control.

**NEXT STEP:** Add a battery simulator that can supply coherent changing readings without hardware. Suggested evidence: an actual folder-tree capture and an early locally rendered page, if available.

### Week 3 — Battery Telemetry Simulation

**WHAT:** Implement correlated simulated voltage, current, temperature, activity, and timestamps with gradual battery discharge. Introduce LOW, MEDIUM, and HIGH requested loads and repeatable random fluctuations.

**WHY:** Simulation makes the system demonstrable before calibrated ESP32 sensing exists. Physically related changes are more useful than unrelated random numbers for exercising analytics, charts, and later policy feedback.

**WHO:** The student developer, `BatterySimulator`, the shared service's timing mechanism, and the future dashboard operator. The simulator represents the device; it is not an actual hardware measurement source.

**WHERE:** Primarily `battery/simulator.py`, with service integration in `battery/service.py` and battery behavior tests in `tests/test_battery.py`.

**WHEN:** First dynamic-data stage, following the application skeleton and preceding full analytics and storage integration.

**HOW:** Initialize simulated charge at 78%, use seeded fluctuations, move current gradually toward an activity/policy target, consume charge from integrated current, derive voltage from the charge curve with a resistive drop, and move temperature toward a current-related thermal target. Use normalized activity values 0.15, 0.45, and 0.90. Apply the 120-times demonstration timescale through the service, while retaining real receipt timestamps.

**OUTPUT/RESULT:** A functioning hardware-independent telemetry source with load-sensitive consumption and gradual discharge. The final code supports direct calls into the shared service rather than self-POSTing through HTTP.

**CHALLENGES:** Likely issues include selecting understandable demonstration parameters, keeping numerical units consistent, making changes visible without abrupt unrealistic jumps, and avoiding charging-like behavior after depletion. Restarts and pauses also require careful elapsed-time handling.

**LEARNING:** Stateful simulation, seeded randomness, first-order response smoothing, charge integration, and the difference between simulation time and wall-clock time.

**NEXT STEP:** Process raw readings into power, energy, SoC, and SoH. Suggested evidence: a reproducible LOW-versus-HIGH comparison with recorded durations and an explicit simulation label.

### Week 4 — Battery Analytics: Power, Energy, SoC and SoH

**WHAT:** Implement the battery analytics layer: instantaneous power, accumulated energy, hybrid SoC, capacity-ratio SoH, recent averages, and consumption trend.

**WHY:** Raw voltage/current values alone do not communicate remaining charge, cumulative use, or changing consumption. This layer provides interpretable engineering features for both users and the subsequent ML/policy components.

**WHO:** The student developer, `BatteryAnalytics`, the simulator, and the eventual external telemetry stream. The dashboard and predictor consume the calculated outputs later.

**WHERE:** `battery/analytics.py`, associated service state, and analytics tests. Formula derivation belongs in the academic calculations section rather than being hidden behind the AI label.

**WHEN:** After raw simulation behaves coherently and before the completed persistence/prediction pipeline.

**HOW:** Compute `P = V × I`; integrate trapezoidal average power over seconds divided by 3600 for Wh. Estimate voltage-based SoC using the lookup curve and `V + 0.08I`. Integrate consumed Ah against 1.88 Ah usable capacity, then apply the bounded time-dependent voltage correction. Calculate SoH as `1.88 / 2.0 × 100 = 94%`. Maintain a twelve-sample window for current/power summaries and compare current with the prior window for trend classification.

**OUTPUT/RESULT:** An explainable analytics module with explicit units and assumptions. Tests represent checks for energy units, discharge, and depleted-battery behavior. The result is an estimator, not proof of laboratory accuracy.

**CHALLENGES:** Likely issues include converting seconds to hours, handling the first sample without a prior interval, preventing negative charge, and avoiding integration during unknown gaps. Another challenge is honestly documenting fixed SoH instead of implying online degradation measurement.

**LEARNING:** Coulomb counting, interpolation, numerical integration, estimator initialization, smoothing, units, and the distinction between measured inputs and estimated state.

**NEXT STEP:** Persist processed telemetry and expose a validated external API. Suggested evidence: a hand-checked energy example, the implemented equations, and actual analytics test output when run during development.

### Week 5 — Database and Flask API Integration

**WHAT:** Add SQLite history/state storage, validated ingestion, snapshot retrieval, and simulation controls. Establish one processing route shared by simulated and externally posted telemetry.

**WHY:** Persistence supports history, restart continuity, and event reporting. A defined API lets future hardware integrate without rewriting battery calculations. Source isolation prevents simulation consumption from being mixed with external-device consumption.

**WHO:** Flask routes, `BatteryService`, `Database`, battery estimators, the browser client, and a test HTTP client representing ESP32.

**WHERE:** `app.py`, `database/db.py`, `battery/service.py`, and `tests/test_api.py`. Development checks should use temporary databases where preservation of demonstration history matters.

**WHEN:** Integration stage after basic telemetry/analytics. Prediction and policy fields can be connected to the final pipeline as their modules become available in subsequent weeks; this progression does not imply they were trained already.

**HOW:** Define `telemetry`, `events`, and `state` tables; use parameterized queries and a transaction to save a processed reading, events, and state together. Validate finite numeric telemetry and strict control values. Implement GET snapshots and POST ingestion/control endpoints. Separate simulation and ESP32 sessions, pause simulation after external ingestion, and bound recent history. Add locking and rollback handling so failures do not advance uncommitted estimates.

**OUTPUT/RESULT:** A persistent, validated service boundary and usable API contract. In the final system, persistence occurs after analytics, runtime prediction, policy selection, and recommendations.

**CHALLENGES:** Likely issues include concurrent requests, SQLite transactions, malformed JSON, source switching, time gaps, restart recovery, and distinction between reading a snapshot and generating a sample.

**LEARNING:** REST semantics, HTTP status codes, schema design, transactions, serialization, state restoration, concurrency, and defensive input validation.

**NEXT STEP:** Generate a reproducible training dataset using the same feature definitions consumed by prediction. Suggested evidence: actual request/response captures, table schema, and temporary-database test results.

### Week 6 — Synthetic Dataset Generation and Feature Engineering

**WHAT:** Define the nine runtime-model inputs and generate synthetic scenarios with a known runtime target. Store the reproducible dataset as `data/battery_training_data.csv`.

**WHY:** A supervised regressor requires labeled examples, while real battery discharge records are not yet available. A transparent generator permits a working ML demonstration and exposes the assumptions that limit its validity.

**WHO:** The student developer, NumPy generator, shared feature list, subsequent training script, and analytics outputs that must match model inputs.

**WHERE:** `ai/features.py`, `ai/generate_dataset.py`, and the CSV dataset. This is Python/NumPy work; Pandas is not required by the implemented project.

**WHEN:** ML preparation stage after telemetry units and analytics are defined, before fitting the regression model.

**HOW:** Use seed 42 to sample 16,000 independent scenarios across charge, health, workload, policy factor, and temperature. Derive current, voltage, power, and approximate recent-average features using the implemented formulas and noise. Calculate target hours from available charge divided by effective current, adjusted for temperature/activity and target noise, then clip to 0–48 hours. Preserve the exact feature ordering used by training and inference.

**OUTPUT/RESULT:** A ten-column CSV containing nine input features and `runtime_hours`, plus an explicit feature contract. The inspected saved dataset contains 16,000 data rows. These are synthetic scenarios, not 16,000 measured battery cycles or continuous physical observations.

**CHALLENGES:** Likely issues include plausible feature correlations, avoiding inconsistent units, matching training/inference order, and explaining why generated recent averages are not actual rolling measurements. Synthetic target assumptions can dominate apparent model performance.

**LEARNING:** Supervised learning datasets, reproducibility, feature engineering, target construction, distribution limits, and the difference between simulated labels and experimental ground truth.

**NEXT STEP:** Split the dataset, fit the regressor, compare with a baseline, and serialize the artifact. Suggested evidence: the generator equations, CSV header/row count, and a reproducible generation record from actual development.

### Week 7 — AI Runtime Prediction Model Training and Evaluation

**WHAT:** Train and evaluate the Random Forest runtime regressor, save its metadata/artifact, and integrate model loading and prediction with a labeled fallback.

**WHY:** This is the actual ML component of the project. It maps current/recent telemetry features to remaining hours while preserving service availability when inference cannot be trusted or the artifact is unavailable.

**WHO:** `train_model.py`, scikit-learn, Joblib, `RuntimePredictor`, the shared service, and model tests. The academic reviewer evaluates whether claims match the available evidence.

**WHERE:** `ai/train_model.py`, `ai/predictor.py`, `models/runtime_model.pkl`, `models/model_metrics.json`, and `tests/test_model.py`.

**WHEN:** After feature/dataset preparation and before automatic policy decisions are connected to ML runtime output.

**HOW:** Use an 80/20 split with seed 42: 12,800 training and 3,200 test rows. Fit 120 trees with maximum depth 18 and minimum leaf size 2. Evaluate MAE, RMSE, and R² and compare MAE with the implemented arithmetic baseline. Save the fitted model, ordered features, version, and metrics. At inference, validate compatibility/domain, predict hours, and use the calculated fallback on supported failure paths.

**OUTPUT/RESULT:** The inspected artifact and JSON record MAE 0.3033769681590672 h, RMSE 0.5933013436852731 h, and R² 0.9955057093051844; baseline MAE is 0.3745046590968543 h. These saved results are synthetic-data evaluation, not physical battery accuracy.

**CHALLENGES:** Likely issues include overly optimistic synthetic evaluation, keeping feature order stable, serialized-library compatibility, and avoiding misleading “AI” labels for ordinary calculations. Fallback must remain visible rather than silently impersonate ML output.

**LEARNING:** Regression, train/test separation, ensemble trees, error metrics, baseline comparison, serialization, inference-domain checks, and graceful degradation.

**NEXT STEP:** Use runtime with charge, temperature, current, and load in an explainable power-management engine. Suggested evidence: saved metrics and actual training/test logs if retained; do not invent missing learning curves or cross-validation experiments.

### Week 8 — Smart Power Management and Recommendation Engine

**WHAT:** Implement PERFORMANCE, BALANCED, POWER SAVING, and CRITICAL decisions, their control-policy descriptions, hysteresis, and telemetry-based recommendations.

**WHY:** Monitoring becomes battery-aware management when observed conditions influence device behavior. Multiple inputs and recovery thresholds make the policy more useful and stable than a single SoC threshold.

**WHO:** `power_manager.py`, analytics and runtime outputs, the simulator that consumes policy factors, event logging, and the user reviewing the decision reason. A future ESP32 would implement returned actions physically.

**WHERE:** `battery/power_manager.py`, `battery/service.py`, simulator feedback, and policy/behavior tests.

**WHEN:** Decision-layer stage after runtime prediction and core battery analytics exist.

**HOW:** Apply ordered critical, saving, performance, and default-balanced checks. Include runtime, temperature, current, load, and prior-mode recovery conditions. Map modes to sampling intervals 2/5/15/30 seconds and current factors 1.00/0.82/0.55/0.25. Return communication/actions and assumed savings of 0/18/45/75%. Generate recommendations from thermal, charge, runtime, and consumption conditions. Record actual policy transitions and temperature events.

**OUTPUT/RESULT:** An explainable rules engine and closed-loop simulator response, with explicit policy reasons and recommendations. The next simulated sample uses the selected factor; backend sampling does not itself become the returned sensor interval.

**CHALLENGES:** Likely issues include rapid mode oscillation, precedence between thermal safety-oriented conditions and performance demand, and feedback reducing current enough to prematurely exit saving mode. Hysteresis and the normalized-current recovery condition address this design concern.

**LEARNING:** Rule-based control, state machines, hysteresis, feedback, priority ordering, human-readable explanations, and distinction between ML prediction and policy logic.

**NEXT STEP:** Present the full pipeline clearly in a live dashboard. Suggested evidence: a threshold table, actual mode-transition logs, and a controlled simulated-current comparison; do not label assumed percentages as measured hardware savings.

### Week 9 — Frontend Dashboard, Live Charts and Full Integration

**WHAT:** Integrate live metrics, five charts, analysis, policy actions, real activity events, and demo controls in the current professional light-mode interface.

**WHY:** A capstone demonstration needs to make the engineering behavior observable. Clear labels let an audience distinguish calculated battery quantities, ML runtime, fallback, source changes, and assumed control effects.

**WHO:** Dashboard users, the HTML/CSS/JavaScript frontend, Chart.js, Flask snapshot/control endpoints, and the shared service.

**WHERE:** `templates/index.html`, `static/css/style.css`, `static/js/dashboard.js`, and the bundled Chart.js distribution. Browser checks provide interaction and responsive-layout evidence.

**WHEN:** Presentation and end-to-end integration stage after backend behavior is available. The final light theme represents the current implementation, regardless of the exact historical timing of the earlier dark-theme design.

**HOW:** Build white metric cards on a light grey-blue background, a compact sidebar, status badges, and prominent SoC/SoH meters. Fetch snapshots approximately every two seconds without reloading the page. Update SoC, voltage, current, temperature, and power charts with at most sixty samples. Wire simulation/load/reset controls to POST requests. Handle busy controls, request timeouts, stale pre-control responses, fallback indicators, and missing chart-library behavior. Remove the top prototype banner while retaining limitations in documentation.

**OUTPUT/RESULT:** The current responsive dashboard with AI Battery Analysis, Smart Power Management, model information, and an actual event timeline. The browser smoke script exercises key interaction and layout behaviors.

**CHALLENGES:** Likely issues include chart resizing, compact mobile values, fetch races, readable light-theme colors, and keeping controls synchronized with source takeover. The README specifically records an earlier MIME-type issue and its correction.

**LEARNING:** Asynchronous JavaScript, DOM updates, data visualization, responsive CSS, usability, request lifecycle management, and end-to-end integration.

**NEXT STEP:** Consolidate testing, external API documentation, deployment configuration, and academic evidence. Suggested evidence: real screenshots at multiple widths and recorded LOW/HIGH/pause/reset demonstrations.

### Week 10 — Testing, ESP32 API Preparation, GitHub and Cloud Deployment Preparation

**WHAT:** Consolidate automated tests, browser/HTTP checks, ESP32 integration documentation, health reporting, Gunicorn/Render setup, and final technical reporting. Treat deployment as prepared unless an actual hosted instance is independently evidenced.

**WHY:** A working local prototype needs reproducible validation and a clear route to demonstration hosting. Final reporting must separate software readiness from physical hardware validation and verified cloud operation.

**WHO:** Student developer/tester, future ESP32 firmware implementer, Git/GitHub workflow, Render service configuration, Gunicorn, and academic reviewers. No named contributors or deployment accounts are inferred.

**WHERE:** `tests/`, `.github/workflows/checks.yml`, `gunicorn.conf.py`, `render.yaml`, `README.md`, the local Git repository, and deployment tooling when actually used.

**WHEN:** Final integration/verification stage after all core components are present, followed by evidence collection and viva preparation.

**HOW:** Exercise backend tests with temporary storage, syntax-check JavaScript, and use browser checks for charts, controls, and viewport widths. Validate `/health` behavior for loaded/fallback/database-failure cases. Document the ESP32 JSON contract and distinguish firmware policy execution from server-side simulation. Configure one Gunicorn process, environment-based paths/port, persistent storage, and CI HTTP smoke checks. Record actual results and remaining limitations rather than retraining merely to produce a new report.

**OUTPUT/RESULT:** The repository contains 21 backend tests, browser/HTTP scripts, health and deployment preparation, API instructions, and documentation. README records prior passing checks. GitHub/Render files support a deployment workflow, but a successful push, CI run, and live cloud service require separate evidence.

**CHALLENGES:** Likely issues include Windows/Linux process differences, SQLite persistence, multi-worker state conflicts, trustworthy model loading, unauthenticated public controls, and demonstrating APIs without claiming completed physical sensing.

**LEARNING:** Verification versus validation, deployment configuration, health semantics, persistent storage, CI, test isolation, security boundaries, and accurate academic communication.

**NEXT STEP:** Submit evidence-backed reports and presentation materials; then pursue calibrated hardware/data experiments as future work. Suggested evidence: real test logs, screenshots, commit IDs, and any actual cloud URL/deployment logs, clearly dated.

## 26. Ten-week deliverable table

This table summarizes the **suggested progression**, not verified historical dates or completion records for individual weeks.

| Week | Main activity | Tools/technologies | Suggested deliverable | Result represented by the current project |
|---|---|---|---|---|
| 1 | Problem and requirements | Engineering analysis, project documentation | Problem statement, objectives, scope | Defined single-device monitoring/prediction/control-policy prototype. |
| 2 | Architecture and setup | VS Code, Python, Flask, HTML/CSS/JS, Git | Project skeleton and architecture | Modular backend, template/static structure, local entry point. |
| 3 | Battery simulation | Python, seeded randomness | Load-sensitive telemetry generator | Correlated readings, accelerated discharge, hardware-free demonstration. |
| 4 | Battery analytics | Python, engineering equations, unit tests | Power/energy/SoC/SoH module | Hybrid SoC, assumed 94% SoH, Wh integration, recent trends. |
| 5 | Storage and API | Flask, SQLite, JSON, unittest | Validated ingestion and persistence | Shared pipeline, source/session isolation, controls and history. |
| 6 | Dataset/features | Python, NumPy, CSV | Reproducible synthetic dataset | 16,000 rows, nine inputs and runtime target. |
| 7 | ML training/evaluation | scikit-learn, Random Forest, Joblib | Model artifact and metrics | Saved regressor, synthetic test metrics, labeled fallback. |
| 8 | Power/recommendation logic | Python rules, simulator feedback | Four-mode policy engine | Multi-input decisions, hysteresis, recommendations, simulated savings. |
| 9 | Dashboard/integration | HTML, CSS, JavaScript, Chart.js | Responsive live light dashboard | Five charts, analysis/policy/event panels and functional controls. |
| 10 | Validation/deployment preparation | unittest, Node/browser checks, Gunicorn, GitHub Actions, Render | Test evidence and deployment documentation | 21 backend tests and documented earlier results; cloud configuration prepared. |

## 27. Viva summary

### What is innovative about this project?

The project combines telemetry, prototype battery-state estimation, ML runtime prediction, explainable operating policies, simulated control feedback, persistence, and live visualization in one working pipeline. Its capstone contribution is the integration and demonstration of battery-aware IoT behavior. It does not claim invention of Random Forest, a new electrochemical estimator, or proven state-of-the-art prediction accuracy.

### Where exactly is AI used?

AI/ML is used only to predict **remaining battery runtime in hours** from nine current/recent telemetry features. Power, SoC, SoH, trend labels, recommendations, and operating modes are calculated or rule-based. When the model cannot be used, the dashboard explicitly labels a calculated fallback.

### Why is this called battery-aware power management?

The mode depends on estimated charge, runtime, temperature, current, requested activity, and previous mode. Those conditions determine whether performance or conservation is appropriate. The policy therefore responds to battery condition and consumption rather than using a fixed operating schedule.

### How does the system save power?

It proposes reduced sampling, communication, and nonessential processing in conserving modes. In the current simulator, a mode-specific factor reduces target current, demonstrating the effect on consumption and discharge. Real ESP32 savings require firmware to apply the policy and physical measurements to verify the result. The displayed 0%, 18%, 45%, and 75% values are policy assumptions.

### How are SoC and SoH calculated?

SoC combines charge consumption from current integration with a gradual correction toward voltage-derived charge, including a simple resistive compensation. SoH is usable capacity divided by nominal capacity times 100. The operational values are 1.88 Ah and 2.0 Ah, so SoH is 94%; it is an assumption, not a measured aging estimate.

### What does Random Forest predict?

It predicts remaining operating hours, capped at 48 hours, from voltage, current, temperature, SoC, SoH, power, recent average current/power, and device load. It does not predict long-term remaining useful life, cell failure, or SoC directly.

### Why was Random Forest selected?

As an engineering rationale, tree ensembles are suitable for nonlinear relationships and interacting tabular inputs without requiring feature scaling. They are straightforward to train, serialize, and explain at a capstone level. The repository uses 120 trees; it does not contain a comprehensive comparison proving this is the best possible algorithm.

### What happens when battery conditions deteriorate?

Ordered rules move toward POWER SAVING or CRITICAL based on low charge/runtime, excessive consumption, or temperature conditions. Recovery thresholds help avoid repeated switching. The service produces recommendations and actual transition events, while the next simulated sample uses the new policy factor. This is not a substitute for hardware battery protection.

### Can the system work without ESP32?

Yes. Its built-in simulator produces correlated telemetry and discharges gradually under LOW, MEDIUM, or HIGH requested loads. The shared service processes those readings directly, and the dashboard can control the demonstration without hardware.

### How will ESP32 be integrated?

Firmware will measure calibrated voltage/current/temperature, estimate normalized load, and POST JSON over Wi-Fi to `/api/telemetry`. The server returns processed analytics, predicted runtime, recommendations, and a control policy. Firmware must actually implement the returned sampling/radio/processing behavior. The current repository provides the API, not complete physical integration.

### What are the current limitations?

Training data and battery behavior are synthetic, SoC is a prototype estimator, SoH is fixed by assumed capacity, and savings/control effects are simulated. There is no calibrated hardware validation, charging support, production authentication, or multi-device fleet management. SQLite persistence and single-process state must be respected during deployment.

### What would be required for real-world deployment?

Calibrated sensing and independent battery experiments, real-data model evaluation, verified firmware actuation, suitable hardware protection, secure device identity/transport, durable storage, operational monitoring, and a scalable state-processing design. Deploying the web app to Render alone does not establish those capabilities.

### Is the reported R² an accuracy percentage?

No. R² is the regression coefficient of determination. Here it is approximately 0.9955 on held-out synthetic samples. MAE is approximately 0.3034 hours and RMSE 0.5933 hours. None establishes real-world battery prediction accuracy without independent physical validation.

### Why does SQLite storage come after prediction and policy selection?

The service builds a complete processed reading first, including runtime, policy, and recommendations. It then commits that reading, related events, and updated state together. This preserves a consistent snapshot of the decision made for each stored sample.

### How should the ten-week report be presented honestly?

Use Sections 25–26 as a logical reporting framework and replace suggested milestones with actual dated evidence where available. Do not claim the whole system existed in Week 1, invent experiments, label API test data as sensor readings, or present deployment preparation as a verified hosted deployment.

### Final evidence checklist for academic submission

- Cite the actual formulas, feature order, policy thresholds, and metric values documented in this report.
- State whether each figure comes from simulation, a manual API payload, or a real sensor experiment.
- Label SoC/SoH as estimates and runtime as ML output or calculated fallback as applicable.
- Separate stored prior validation results from any new test execution.
- Attach actual weekly evidence rather than treating the suggested progression as historical proof.
- Identify future hardware, security, and calibration work as future scope.

This report was prepared by inspecting the current repository and existing artifacts. Its creation does not retrain the model, regenerate the dataset, execute the application, or change application code, configuration, frontend, or database contents.

**Final file-integrity check:** comparison with the earlier inspection snapshot confirmed unchanged hashes for application source, configuration, frontend, dataset, model, and other existing files except `data/battery.db`. The database hash differed. This documentation task issued no database writes and did not launch the application; the cause of the database change was not established. Consequently, this report confirms no database modification by the documentation workflow, but does not claim that the database remained unchanged across the entire inspection interval. Git status showed only the new report as an untracked change; the local database is ignored by Git.
