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
body { font-family: Arial, sans-serif; margin: 20px; }
label { display: inline-block; margin-right: 12px; }
input, select, button { font-size: 1rem; margin: 4px 0; }
textarea { width: 100%; height: 280px; margin-top: 12px; padding: 10px; font-family: Consolas, monospace; font-size: 0.95rem; }
.status { margin-top: 12px; }
</style>
</head>
<body>
<h1>AutoROAM Web</h1>
<div>
  <label>Interval (minutes): <input id="interval" type="number" min="0.1" step="0.5" value="5"></label>
  <label>Mode:
    <select id="mode">
      <option value="demo">Generate only</option>
      <option value="submit">Submit to ROAM</option>
    </select>
  </label>
  <button id="toggle">Start</button>
</div>
<div class="status">
  <strong>Status:</strong> <span id="status">Idle</span><br>
  <strong>Last run:</strong> <span id="last_run">Never</span><br>
  <strong>Mode:</strong> <span id="current_mode">demo</span><br>
  <strong>Interval:</strong> <span id="current_interval">5</span> min
</div>
<div id="message" style="margin-top: 10px; color: #c00;"></div>
<textarea id="log" readonly placeholder="Observation/action history will appear here..."></textarea>
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
    await start();
  } else {
    await stop();
  }
});

async function start() {
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

async function stop() {
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

    logEl.value = data.logs.map(entry => `${entry.timestamp} [${entry.mode.toUpperCase()}] ${entry.observation}\\n${entry.action}\\nResult: ${entry.result}\\n`).join('\\n');
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
