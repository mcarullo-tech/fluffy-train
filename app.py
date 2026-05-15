import threading
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from generating_sentences import generate_observation
from roam_automation import submit_observation

app = Flask(__name__)
lock = threading.Lock()
runner_thread = None
stop_event = threading.Event()
state = {
    "running": False,
    "mode": "demo",
    "interval_minutes": 5,
    "last_run": None,
    "last_status": "Idle"
}
logs = []
MAX_LOG_ENTRIES = 200

PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AutoROAM Web</title>
<style>
:root {
  color-scheme: light;
  --bg: #eef4fb;
  --surface: #ffffff;
  --surface-alt: #f7faff;
  --text: #14213d;
  --text-muted: #4b5563;
  --accent: #2563eb;
  --accent-strong: #1d4ed8;
  --danger: #dc2626;
  --shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
}
html, body {
  margin: 0;
  min-height: 100%;
  background: linear-gradient(180deg, #f0f6ff 0%, #dce9f8 100%);
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text);
}
body {
  padding: 24px;
}
.container {
  max-width: 980px;
  margin: 0 auto;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}
h1 {
  margin: 0;
  font-size: clamp(2rem, 2.5vw, 2.75rem);
  letter-spacing: -0.03em;
}
p.subtitle {
  margin: 10px 0 0;
  color: var(--text-muted);
  line-height: 1.6;
}
.card {
  background: var(--surface);
  border-radius: 24px;
  box-shadow: var(--shadow);
  padding: 24px;
}
.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1.2fr 0.8fr;
}
.controls {
  display: grid;
  gap: 12px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.field label {
  font-weight: 600;
  color: var(--text-muted);
}
.field input,
.field select {
  border: 1px solid #cbd5e1;
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 1rem;
  background: #f8fbff;
  outline: none;
}
.field input:focus,
.field select:focus {
  outline: 2px solid rgba(37, 99, 235, 0.2);
}
.button-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
button {
  border: none;
  border-radius: 14px;
  padding: 14px 24px;
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  cursor: pointer;
  transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
}
button:hover {
  transform: translateY(-1px);
  filter: brightness(1.05);
}
button:active {
  transform: translateY(0);
}
.status-panel {
  background: var(--surface-alt);
  border-radius: 20px;
  padding: 20px;
  display: grid;
  gap: 10px;
}
.status-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}
.status-item strong {
  color: var(--text-muted);
  font-weight: 600;
}
.message {
  color: var(--danger);
  font-weight: 600;
  min-height: 24px;
}
.log-panel {
  width: 100%;
  height: 340px;
  max-height: 380px;
  margin-top: 16px;
  padding: 18px;
  border-radius: 20px;
  background: #0f172a;
  color: #e2e8f0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.95rem;
  line-height: 1.55;
  white-space: pre-wrap;
  overflow: auto;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.16);
}
@media (max-width: 760px) {
  .grid { grid-template-columns: 1fr; }
  .header { flex-direction: column; align-items: stretch; }
}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>AutoROAM Web</h1>
      <p class="subtitle">Generate or submit ROAM observations automatically on a schedule, with a live activity log.</p>
    </div>
  </div>
  <div class="card grid">
  <div class="controls">
    <div class="field">
      <label for="interval">Interval (minutes)</label>
      <input id="interval" type="number" min="0.1" step="0.5" value="5">
    </div>
    <div class="field">
      <label for="mode">Mode</label>
      <select id="mode">
        <option value="demo">Generate only</option>
        <option value="submit">Submit to ROAM</option>
      </select>
    </div>
    <div class="button-row">
      <button id="toggle" type="button">Start</button>
      <div class="message" id="message"></div>
    </div>
  </div>
  <div class="status-panel">
    <div class="status-item"><strong>Status</strong><span id="status">Idle</span></div>
    <div class="status-item"><strong>Last run</strong><span id="last_run">Never</span></div>
    <div class="status-item"><strong>Mode</strong><span id="current_mode">demo</span></div>
    <div class="status-item"><strong>Interval</strong><span id="current_interval">5</span> min</div>
  </div>
</div>
<pre id="log" class="log-panel" readonly>Observation/action history will appear here...</pre>
<script>
let running = false;
const button = document.getElementById('toggle');
const intervalInput = document.getElementById('interval');
const modeSelect = document.getElementById('mode');
const statusEl = document.getElementById('status');
const lastRunEl = document.getElementById('last_run');
const currentMode = document.getElementById('current_mode');
const currentInterval = document.getElementById('current_interval');
const messageEl = document.getElementById('message');
const logEl = document.getElementById('log');

button.addEventListener('click', async () => {
  if (!running) {
    await startWorker();
  } else {
    await stopWorker();
  }
});

async function startWorker() {
  messageEl.textContent = '';
  const intervalMinutes = parseFloat(intervalInput.value) || 5;
  const mode = modeSelect.value;
  try {
    const response = await fetch('/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ interval_minutes: intervalMinutes, mode })
    });
    const result = await response.json();
    if (result.success) {
      running = true;
      button.textContent = 'Stop';
      statusEl.textContent = 'Running';
      currentMode.textContent = mode;
      currentInterval.textContent = intervalMinutes;
    } else {
      messageEl.textContent = result.message || 'Unable to start';
    }
  } catch (error) {
    messageEl.textContent = 'Start failed: ' + error.message;
  }
}

async function stopWorker() {
  messageEl.textContent = '';
  try {
    const response = await fetch('/stop', { method: 'POST' });
    const result = await response.json();
    if (result.success) {
      running = false;
      button.textContent = 'Start';
      statusEl.textContent = 'Stopped';
    } else {
      messageEl.textContent = result.message || 'Unable to stop';
    }
  } catch (error) {
    messageEl.textContent = 'Stop failed: ' + error.message;
  }
}

async function refresh() {
  try {
    const [statusRes, logsRes] = await Promise.all([fetch('/status'), fetch('/logs')]);
    const status = await statusRes.json();
    const data = await logsRes.json();

    statusEl.textContent = status.running ? 'Running' : 'Idle';
    lastRunEl.textContent = status.last_run || 'Never';
    currentMode.textContent = status.mode;
    currentInterval.textContent = status.interval_minutes;

    if (!running && status.running) {
      running = true;
      button.textContent = 'Stop';
    } else if (running && !status.running) {
      running = false;
      button.textContent = 'Start';
    }

    const visibleLogs = data.logs.slice(0, 50);
    logEl.textContent = visibleLogs.map(entry => `${entry.timestamp} [${entry.mode.toUpperCase()}] ${entry.observation}\\n${entry.action}\\nResult: ${entry.result}\\n`).join('\\n');
  } catch (error) {
    messageEl.textContent = 'Unable to refresh status/logs: ' + error.message;
  }
}

setInterval(refresh, 2000);
refresh();
</script>
</body>
</html>"""


def add_log(location, observation, action, mode, result, detail):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": location,
        "observation": observation,
        "action": action,
        "mode": mode,
        "result": result,
        "detail": detail
    }
    with lock:
        logs.insert(0, entry)
        del logs[MAX_LOG_ENTRIES:]
        state["last_run"] = entry["timestamp"]
        state["last_status"] = result


def worker_loop(interval_minutes, mode):
    state["running"] = True
    state["mode"] = mode
    state["interval_minutes"] = interval_minutes
    state["last_status"] = "Started"

    try:
        while not stop_event.is_set():
            location, observation, action = generate_observation()
            if mode == "submit":
                success, detail = submit_observation(location, observation, action)
                result = "Submitted" if success else "Submission failed"
            else:
                success = False
                detail = "Generated only"
                result = "Generated"

            add_log(location, observation, action, mode, result, detail)
            if stop_event.wait(interval_minutes * 60):
                break
    finally:
        state["running"] = False
        state["last_status"] = "Stopped"


def start_worker(interval_minutes, mode):
    global runner_thread, stop_event
    if runner_thread and runner_thread.is_alive():
        return False, "A run is already in progress."

    stop_event.clear()
    runner_thread = threading.Thread(target=worker_loop, args=(interval_minutes, mode), daemon=True)
    runner_thread.start()
    return True, "Started successfully."


def stop_worker():
    stop_event.set()


@app.route('/')
def index():
    return render_template_string(PAGE_HTML)


@app.route('/start', methods=['POST'])
def start():
    payload = request.get_json(silent=True) or {}
    try:
        interval_minutes = float(payload.get('interval_minutes', 5))
        if interval_minutes <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify(success=False, message='Enter a valid positive interval in minutes.')

    mode = payload.get('mode', 'demo')
    if mode not in ('demo', 'submit'):
        mode = 'demo'

    success, message = start_worker(interval_minutes, mode)
    return jsonify(success=success, message=message)


@app.route('/stop', methods=['POST'])
def stop():
    stop_worker()
    return jsonify(success=True, message='Stopped successfully.')


@app.route('/status')
def status():
    with lock:
        return jsonify(state)


@app.route('/logs')
def get_logs():
    with lock:
        return jsonify(logs=logs)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
