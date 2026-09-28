// Optional real-browser integration check. Uses Node 22+ and installed Edge/Chrome;
// no npm dependencies. All database/profile/screenshots live in a temporary folder.
import {spawn} from "node:child_process";
import {mkdtemp, writeFile} from "node:fs/promises";
import {existsSync} from "node:fs";
import {tmpdir} from "node:os";
import path from "node:path";
import assert from "node:assert/strict";

const root = path.resolve(import.meta.dirname, "..");
const work = await mkdtemp(path.join(tmpdir(), "battery-browser-"));
const browserCandidates = process.platform === "win32"
    ? [path.join(process.env["ProgramFiles(x86)"] || "", "Microsoft/Edge/Application/msedge.exe"),
        path.join(process.env.ProgramFiles || "", "Google/Chrome/Application/chrome.exe")]
    : ["/usr/bin/microsoft-edge", "/usr/bin/google-chrome", "/usr/bin/chromium", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"];
const browserPath = process.env.BROWSER_PATH || browserCandidates.find(candidate => existsSync(candidate));
assert.ok(browserPath, "Set BROWSER_PATH to an installed Edge/Chrome/Chromium executable.");
const backend = spawn(process.env.PYTHON || "python", ["-B", "app.py"], {
    cwd: root, windowsHide: true, stdio: ["ignore", "pipe", "pipe"],
    env: {...process.env, PORT: "5001", FLASK_HOST: "127.0.0.1", DATABASE_PATH: path.join(work, "test.db")},
});
let backendOutput = "";
backend.stderr.on("data", data => { backendOutput += data; });
const browser = spawn(browserPath, ["--headless=new", "--disable-gpu", "--no-first-run",
    "--no-default-browser-check", "--remote-debugging-port=9223", `--user-data-dir=${path.join(work, "profile")}`,
    "about:blank"], {windowsHide: true, stdio: "ignore"});
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function until(fn, description, timeout = 20000) {
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
        try { const result = await fn(); if (result) return result; } catch {}
        await delay(200);
    }
    throw new Error(`Timed out: ${description}`);
}
let socket;
let sequence = 0;
const pending = new Map();
const exceptions = [];
const browserLog = [];
function cdp(method, params = {}) {
    return new Promise((resolve, reject) => {
        const id = ++sequence;
        const timeout = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 15000);
        pending.set(id, {resolve, reject, timeout});
        socket.send(JSON.stringify({id, method, params}));
    });
}
async function evaluate(expression) {
    const response = await cdp("Runtime.evaluate", {expression, returnByValue: true, awaitPromise: true});
    if (response.exceptionDetails) throw new Error(JSON.stringify(response.exceptionDetails));
    return response.result.value;
}
async function api(endpoint, body) {
    const response = await fetch(`http://127.0.0.1:5001${endpoint}`, body ? {
        method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body),
    } : {});
    assert.ok(response.ok, `API ${endpoint}: ${response.status}`);
    return response.json();
}

try {
    await until(async () => (await fetch("http://127.0.0.1:5001/")).ok, "test Flask server");
    const health = await (await fetch("http://127.0.0.1:5001/health")).json();
    assert.deepEqual(health, {status: "healthy", model: "loaded", database: "connected"});
    const scriptResponse = await fetch("http://127.0.0.1:5001/static/js/dashboard.js");
    assert.ok(scriptResponse.headers.get("content-type").includes("javascript"), "JavaScript MIME type");
    const targets = await until(async () => (await fetch("http://127.0.0.1:9223/json")).json(), "browser debugger");
    socket = new WebSocket(targets.find(target => target.type === "page").webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { socket.addEventListener("open", resolve, {once: true}); socket.addEventListener("error", reject, {once: true}); });
    socket.addEventListener("message", ({data}) => {
        const result = JSON.parse(data);
        if (result.method === "Runtime.exceptionThrown") exceptions.push(result.params.exceptionDetails);
        if (result.method === "Log.entryAdded") browserLog.push(result.params.entry);
        if (pending.has(result.id)) {
            const request = pending.get(result.id);
            clearTimeout(request.timeout);
            pending.delete(result.id);
            if (result.error) request.reject(new Error(JSON.stringify(result.error)));
            else request.resolve(result.result);
        }
    });
    await cdp("Runtime.enable");
    await cdp("Log.enable");
    await cdp("Page.enable");
    await cdp("Emulation.setDeviceMetricsOverride", {width: 1440, height: 1050, deviceScaleFactor: 1, mobile: false});
    await cdp("Page.navigate", {url: "http://127.0.0.1:5001/"});
    await until(() => evaluate("document.getElementById('model-status')?.textContent === 'ACTIVE'"), "live model status");
    assert.equal(await evaluate("Object.keys(Chart.instances).length"), 5);
    assert.equal(await evaluate("document.documentElement.scrollWidth <= window.innerWidth"), true, "desktop overflow");
    assert.ok(await evaluate("Chart.getChart('soc-chart').data.datasets[0].data.length > 0"));
    assert.equal(await evaluate("document.getElementById('connection-error').hidden"), true);
    assert.equal(await evaluate("document.querySelector('.demo-note')"), null, "prototype banner removed");
    assert.equal(await evaluate("getComputedStyle(document.body).backgroundColor"), "rgb(244, 247, 251)");
    assert.equal(await evaluate("getComputedStyle(document.querySelector('.metric')).backgroundColor"), "rgb(255, 255, 255)");
    const initialChartLength = await evaluate("Chart.getChart('soc-chart').data.labels.length");

    await evaluate("document.getElementById('device-load').value='LOW'; document.getElementById('device-load').dispatchEvent(new Event('change'))");
    await delay(8500);
    const low = (await api("/api/telemetry")).telemetry;
    await evaluate("document.getElementById('device-load').value='HIGH'; document.getElementById('device-load').dispatchEvent(new Event('change'))");
    await delay(8500);
    const high = (await api("/api/telemetry")).telemetry;
    assert.ok(high.current > low.current * 1.5, "load increases current");
    assert.ok(high.power > low.power * 1.5, "load increases power");
    assert.ok(high.predicted_runtime < low.predicted_runtime, "load reduces predicted runtime");
    assert.ok(high.soc < low.soc, "battery discharges");
    assert.ok(await evaluate(`Object.values(Chart.instances).every(chart => chart.data.labels.length > ${initialChartLength} && chart.options.plugins.legend.display && chart.options.scales.y.grid.color === '#edf1f6')`), "all five charts update in light mode");

    await evaluate("document.getElementById('simulation-toggle').click()");
    await until(async () => !(await api("/api/telemetry")).controls.simulation_enabled, "pause simulation");
    const paused = (await api("/api/telemetry")).telemetry.id;
    await delay(2500);
    assert.equal((await api("/api/telemetry")).telemetry.id, paused);
    await until(() => evaluate("document.getElementById('system-status').textContent.includes('PAUSED')"), "paused status");
    await evaluate("document.getElementById('reset-simulation').click()");
    await until(async () => (await api("/api/telemetry")).controls.simulation_enabled, "reset resumes simulation");

    const esp = await api("/api/telemetry", {voltage: 3.85, current: 0.12, temperature: 50, device_load: 0.45, source: "esp32"});
    assert.equal(esp.power_mode, "CRITICAL");
    await until(() => evaluate("document.getElementById('data-source').textContent === 'ESP32' && document.getElementById('model-status').textContent === 'FALLBACK'"), "ESP32 fallback render");
    assert.equal(await evaluate("document.getElementById('runtime-label').textContent"), "Remaining Runtime · Fallback");
    assert.equal(await evaluate("document.getElementById('policy-mode').textContent"), "CRITICAL");

    await api("/api/control", {reset: true, simulation_enabled: true, device_load: "MEDIUM"});
    await until(() => evaluate("document.getElementById('data-source').textContent === 'SIMULATION' && document.getElementById('model-status').textContent === 'ACTIVE'"), "simulation restore");
    await evaluate("document.querySelector('.model-information').open=true");
    await until(() => evaluate("Chart.getChart('soc-chart').data.labels.length >= 4"), "chart history before screenshots");
    let image = await cdp("Page.captureScreenshot", {format: "png", captureBeyondViewport: true});
    await writeFile(path.join(work, "desktop.png"), Buffer.from(image.data, "base64"));
    for (const width of [1366, 1024, 768, 320]) {
        await cdp("Emulation.setDeviceMetricsOverride", {width, height: 900, deviceScaleFactor: 1, mobile: width <= 768});
        await delay(350);
        assert.equal(await evaluate("document.documentElement.scrollWidth <= window.innerWidth"), true, `overflow at ${width}px`);
        assert.equal(await evaluate("[...document.querySelectorAll('.metric')].every(card => card.scrollWidth <= card.clientWidth)"), true, `metric clipping at ${width}px`);
    }
    await cdp("Emulation.setDeviceMetricsOverride", {width: 390, height: 844, deviceScaleFactor: 1, mobile: true});
    await delay(500);
    assert.equal(await evaluate("document.documentElement.scrollWidth <= window.innerWidth"), true, "mobile overflow");
    image = await cdp("Page.captureScreenshot", {format: "png", captureBeyondViewport: true});
    await writeFile(path.join(work, "mobile.png"), Buffer.from(image.data, "base64"));

    // Confirm a missing chart library does not prevent numeric telemetry updates.
    await cdp("Network.enable");
    await cdp("Network.setBlockedURLs", {urls: ["*chart.umd.min.js*"]});
    await cdp("Network.setCacheDisabled", {cacheDisabled: true});
    await cdp("Page.reload", {ignoreCache: true});
    await until(() => evaluate("document.getElementById('chart-message')?.textContent.includes('could not load') && document.getElementById('model-status')?.textContent === 'ACTIVE'"), "chart failure fallback");
    assert.deepEqual(exceptions, [], "browser JavaScript exceptions");
    console.log(JSON.stringify({result: "PASS", charts: 5, low_current: low.current, high_current: high.current,
        low_runtime: low.predicted_runtime, high_runtime: high.predicted_runtime,
        checks: ["health endpoint", "light theme", "banner removed", "all live charts", "load controls", "pause", "reset", "ESP32", "fallback", "1440/1366/1024/768/390/320px layouts", "missing chart asset"],
        screenshots: work}, null, 2));
} catch (error) {
    console.error(error);
    console.error(JSON.stringify(exceptions));
    console.error(JSON.stringify(browserLog));
    try { console.error(await evaluate("({ready:document.readyState, text:document.body.innerText.slice(-1500), chart:typeof Chart})")); } catch {}
    console.error(backendOutput.slice(-3000));
    process.exitCode = 1;
} finally {
    if (socket?.readyState === WebSocket.OPEN) {
        try { await cdp("Browser.close"); } catch {}
        socket.close();
    }
    browser.kill();
    backend.kill();
}
