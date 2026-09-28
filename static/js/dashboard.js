"use strict";

const byId = (id) => document.getElementById(id);
const setText = (id, value) => { byId(id).textContent = value; };
const formatNumber = (value, digits = 2) => Number.isFinite(value) ? value.toFixed(digits) : "—";
const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString();
function formatRuntime(hours) {
    if (!Number.isFinite(hours)) return "—";
    const minutes = Math.round(hours * 60);
    return `${Math.floor(minutes / 60)} h ${minutes % 60} min`;
}

const navigationLinks = document.querySelectorAll("nav a");
function updateNavigation() {
    const target = location.hash || "#dashboard";
    navigationLinks.forEach((link) => {
        const active = link.getAttribute("href") === target;
        link.classList.toggle("active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
    });
}
window.addEventListener("hashchange", updateNavigation);
updateNavigation();

const charts = new Map();
const chartSpecs = [
    ["soc", "State of Charge (%)", "#2563eb", {min: 0, max: 100}],
    ["voltage", "Voltage (V)", "#0f766e", {suggestedMin: 3, suggestedMax: 4.2}],
    ["current", "Current (A)", "#7c3aed", {beginAtZero: true}],
    ["temperature", "Temperature (°C)", "#b45309", {suggestedMin: 24, suggestedMax: 40}],
    ["power", "Power (W)", "#0369a1", {beginAtZero: true}],
];
if (typeof Chart !== "undefined") {
    Chart.defaults.color = "#52627a";
    Chart.defaults.font.family = '"Segoe UI", Arial, sans-serif';
    for (const [key, label, color, range] of chartSpecs) {
        charts.set(key, new Chart(byId(`${key}-chart`), {
            type: "line",
            data: {labels: [], datasets: [{label, data: [], borderColor: color,
                backgroundColor: `${color}12`, borderWidth: 2, pointRadius: 1,
                pointHoverRadius: 4, fill: true, tension: 0.25}]},
            options: {
                responsive: true, maintainAspectRatio: false, animation: false,
                interaction: {intersect: false, mode: "index"},
                plugins: {
                    legend: {display: true, position: "bottom", labels: {
                        color: "#45556c", usePointStyle: true, pointStyle: "line",
                        boxWidth: 20, padding: 14, font: {size: 12},
                    }},
                    tooltip: {
                        backgroundColor: "#ffffff", titleColor: "#172b4d", bodyColor: "#45556c",
                        borderColor: "#dbe3ef", borderWidth: 1, padding: 12,
                        titleFont: {size: 12, weight: "600"}, bodyFont: {size: 12},
                        displayColors: true, boxPadding: 5,
                    },
                },
                scales: {
                    x: {grid: {display: false}, border: {color: "#e2e8f0"},
                        ticks: {color: "#52627a", maxTicksLimit: 4, maxRotation: 0, font: {size: 11}}},
                    y: {...range, grid: {color: "#edf1f6"}, border: {display: false},
                        ticks: {color: "#52627a", maxTicksLimit: 5, padding: 8, font: {size: 11}}},
                },
            },
        }));
    }
}

let snapshot = null;
let busy = false;
let requestInFlight = false;
let timer = null;
let lastChartKey = null;
let controlRevision = 0;

function setList(id, items) {
    const nodes = items.map((message) => {
        const li = document.createElement("li");
        li.textContent = message;
        return li;
    });
    byId(id).replaceChildren(...nodes);
}

function setMode(id, mode) {
    const node = byId(id);
    node.textContent = mode;
    node.dataset.mode = mode;
}

function renderModel(model) {
    const parent = byId("model-info");
    parent.replaceChildren();
    const metadata = model.metadata;
    const lines = metadata ? [
        `${metadata.model} · ${metadata.trees} trees · seed ${metadata.seed}`,
        `${metadata.training_rows.toLocaleString()} training / ${metadata.test_rows.toLocaleString()} test scenarios`,
        `MAE: ${metadata.metrics.mae_hours.toFixed(3)} h · RMSE: ${metadata.metrics.rmse_hours.toFixed(3)} h`,
        `R²: ${metadata.metrics.r2.toFixed(4)} · calculated baseline MAE: ${metadata.metrics.baseline_mae_hours.toFixed(3)} h`,
        `Inputs: ${metadata.features.join(", ")}`,
        "80/20 split of independent synthetic scenarios. These metrics do not establish accuracy on real batteries.",
        "Runtime is in battery hours at the current operating conditions, capped at 48 hours.",
    ] : [model.reason];
    for (const line of lines) {
        const paragraph = document.createElement("p");
        paragraph.textContent = line;
        parent.append(paragraph);
    }
}

function updateControlState(connected = true) {
    byId("simulation-toggle").disabled = !connected || busy;
    byId("reset-simulation").disabled = !connected || busy;
    byId("device-load").disabled = !connected || busy || !snapshot?.controls.simulation_enabled;
}

function render(data) {
    snapshot = data;
    const reading = data.telemetry;
    const status = data.system.status;
    setText("system-status", status === "ONLINE" ? "System Online" : `System ${status}`);
    byId("system-status").dataset.status = status;
    setText("data-source", data.system.source.toUpperCase());
    const modelStatus = reading?.model_status || (data.model.available ? "READY" : "FALLBACK");
    setText("model-status", modelStatus);
    byId("model-status").dataset.mode = modelStatus;
    byId("model-indicator").dataset.mode = modelStatus;
    setText("last-sample", reading ? `${formatTime(reading.timestamp)} · ${Math.floor(data.system.sample_age_seconds)}s ago` : "Waiting");
    setText("telemetry-badge", `${data.system.source.toUpperCase()} · ${status}`);
    const simEnabled = data.controls.simulation_enabled;
    byId("simulation-toggle").checked = simEnabled;
    setText("simulation-state", simEnabled ? "ON" : "OFF");
    byId("device-load").value = data.controls.device_load;
    setText("clock-note", simEnabled
        ? `Simulation clock: ${data.controls.time_scale}× · 2 wall seconds ≈ 4 battery minutes`
        : "Simulation paused · ESP32 posts use real elapsed time");
    updateControlState();

    const error = byId("connection-error");
    error.hidden = !["STALE", "ERROR"].includes(status);
    error.textContent = data.system.message || "Telemetry is stale. Displaying the last received sample; check the device connection.";
    for (const [key, digits] of [["soc", 1], ["soh", 1], ["voltage", 3], ["current", 3], ["temperature", 1], ["power", 3]]) {
        setText(key, formatNumber(reading?.[key], digits));
    }
    for (const key of ["soc", "soh"]) {
        const meter = byId(`${key}-meter`);
        meter.firstElementChild.style.width = `${reading?.[key] || 0}%`;
        if (reading) meter.setAttribute("aria-valuenow", reading[key]);
        else meter.removeAttribute("aria-valuenow");
    }
    const runtime = formatRuntime(reading?.predicted_runtime);
    setText("runtime", runtime);
    setText("runtime-label", reading?.model_status === "FALLBACK" ? "Remaining Runtime · Fallback" : "AI Predicted Runtime");
    setText("runtime-method", reading?.runtime_method || "Waiting for prediction");
    setText("energy", formatNumber(reading?.energy_consumed, 4));
    setText("battery-time", reading ? formatRuntime(reading.elapsed_battery_seconds / 3600) : "—");
    setText("energy-note", reading?.quality_note || (data.system.source === "simulation"
        ? "Integrated on the accelerated battery clock, since simulation reset."
        : "Integrated from server receipt intervals; unknown gaps over 60 seconds are excluded."));
    setMode("power-mode", reading?.power_mode || "—");
    setText("analysis-runtime", runtime);
    setText("consumption-trend", reading?.consumption_trend || "—");
    setText("battery-condition", reading?.battery_condition || "—");
    setText("analysis-model", modelStatus);
    setText("model-reason", reading?.model_reason || data.model.reason);
    setList("recommendations", reading?.recommendations || ["Waiting for the first reading."]);
    const policy = reading?.policy;
    setMode("policy-mode", policy?.mode || "Waiting");
    setText("policy-reason", policy?.reason || "Waiting for telemetry.");
    setText("sampling-interval", policy ? `${policy.sampling_interval} seconds` : "—");
    setText("communication-policy", policy?.communication_policy || "—");
    setText("energy-saving", policy ? `${policy.estimated_energy_saving}% · assumed` : "—");
    setList("optimization-actions", policy?.actions || ["Waiting for telemetry."]);
    renderModel(data.model);

    const activityNodes = data.activity.map((event) => {
        const item = document.createElement("li");
        const dot = document.createElement("span");
        dot.className = `activity-dot ${event.level === "warning" ? "warning-dot" : ""}`;
        const content = document.createElement("div");
        content.textContent = event.message;
        const time = document.createElement("small");
        time.textContent = formatTime(event.timestamp);
        content.append(time);
        item.append(dot, content);
        return item;
    });
    byId("activity-list").replaceChildren(...activityNodes);

    const points = data.history.slice(-60);
    const chartKey = `${data.system.source}:${reading?.session_id}:${points.at(-1)?.id}:${points.length}`;
    if (chartKey !== lastChartKey) {
        for (const [key, chart] of charts) {
            chart.data.labels = points.map((point) => formatTime(point.timestamp));
            chart.data.datasets[0].data = points.map((point) => point[key]);
            chart.update("none");
        }
        lastChartKey = chartKey;
    }
    setText("chart-message", charts.size
        ? `${points.length} recent samples · charts follow the selected source and session`
        : "Chart.js could not load. Refresh and check the local chart asset. Live numeric readings remain available.");
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, {...options, cache: "no-store", signal: AbortSignal.timeout(8000)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || `Request failed (${response.status})`);
    return result;
}

function showError(error) {
    setText("system-status", "System OFFLINE");
    byId("system-status").dataset.status = "OFFLINE";
    const banner = byId("connection-error");
    banner.hidden = false;
    banner.textContent = `Unable to refresh telemetry: ${error.message}. Last readings may be stale. Retrying automatically.`;
    updateControlState(false);
}

async function poll() {
    clearTimeout(timer);
    if (busy || requestInFlight) {
        timer = setTimeout(poll, 500);
        return;
    }
    requestInFlight = true;
    const requestedRevision = controlRevision;
    try {
        const result = await fetchJson("/api/telemetry");
        // A control request can start while this GET is in flight. Discard that old view.
        if (!busy && requestedRevision === controlRevision) render(result);
    } catch (error) {
        if (!busy && requestedRevision === controlRevision) showError(error);
    } finally {
        requestInFlight = false;
        timer = setTimeout(poll, 2000);
    }
}

async function changeControls(changes) {
    if (busy) return;
    busy = true;
    controlRevision += 1;
    updateControlState();
    setText("control-feedback", "Applying control…");
    try {
        render(await fetchJson("/api/control", {method: "POST",
            headers: {"Content-Type": "application/json"}, body: JSON.stringify(changes)}));
        setText("control-feedback", "Control applied. Readings respond on the next simulation tick.");
    } catch (error) {
        setText("control-feedback", `Control failed: ${error.message}`);
        if (snapshot) {
            byId("simulation-toggle").checked = snapshot.controls.simulation_enabled;
            byId("device-load").value = snapshot.controls.device_load;
        }
    } finally {
        busy = false;
        updateControlState();
    }
}

byId("simulation-toggle").addEventListener("change", (event) => changeControls({simulation_enabled: event.target.checked}));
byId("device-load").addEventListener("change", (event) => changeControls({device_load: event.target.value}));
byId("reset-simulation").addEventListener("click", () => changeControls({reset: true, simulation_enabled: true}));
poll();
