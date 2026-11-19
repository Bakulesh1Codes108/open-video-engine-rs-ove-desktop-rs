#!/usr/bin/env python3
"""
Lightweight Studio & RPA Pipeline Server for Antigravity Video Studio.
Serves:
  - '/' or '/studio' -> Pro Desktop NLE Studio UI (app/studio_pro.html)
    with DaVinci Resolve, CapCut, Adobe Premiere, and Final Cut Pro themes.
  - '/rpa' -> Visual Node RPA Automation Canvas (app/rpa_studio.html)
  - API Endpoints: /api/rpa/execute, /api/convert, /api/render, /api/voice-clone, /api/upscale
"""

import sys
import os
import json
import re
import subprocess
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
STUDIO = os.path.join(SCRIPTS_DIR, "studio.py")
REEL_MIMIC = os.path.join(SCRIPTS_DIR, "reel_mimic.py")
VOICE_CLONE = os.path.join(SCRIPTS_DIR, "voice_clone.py")
UPSCALER = os.path.join(SCRIPTS_DIR, "upscaler.py")
MODEL_ROUTER = os.path.join(SCRIPTS_DIR, "model_router.py")

def _is_safe_path(p: str) -> bool:
    """Defensive path traversal check to ensure file stays inside BASE_DIR."""
    if not p or not isinstance(p, str):
        return False
    try:
        abs_p = os.path.abspath(os.path.join(BASE_DIR, p) if not os.path.isabs(p) else p)
        return os.path.commonpath([abs_p, BASE_DIR]) == BASE_DIR
    except Exception:
        return False

def _sanitize_token(val: str, default: str = "") -> str:
    """Defensive input sanitization: allow only alphanumeric, dash, and underscore."""
    if not val or not isinstance(val, str):
        return default
    cleaned = re.sub(r"[^a-zA-Z0-9_\-:]", "", val)
    return cleaned or default

class RpaRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        if self.path in ["/", "/studio", "/pro", "/edit", "/ove"]:
            self.path = "/app/studio_pro.html"
        elif self.path == "/rpa":
            self.path = "/app/rpa_studio.html"
        elif self.path == "/api/copilot/status":
            self._handle_copilot_status()
            return
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        try:
            data = json.loads(body) if body.strip() else {}
        except Exception:
            data = {}

        if self.path == "/api/rpa/execute":
            try:
                raw_prompt = data.get("prompt", "Autonomous Video")
                prompt = str(raw_prompt)[:500]  # Bound max length
                mimic = _sanitize_token(data.get("mimic", "alex_hormozi_viral_reel"), "alex_hormozi_viral_reel")
                fmt = "9:16" if data.get("format") in ["9:16", "vertical"] else "16:9"

                print(f"🎬 [Studio RPA Job] Prompt: '{prompt[:60]}...', Mimic: {mimic}, Format: {fmt}")

                # If vertical format requested, ensure project is switched
                if fmt in ["9:16", "vertical"]:
                    subprocess.run([sys.executable, STUDIO, "convert", "9:16"], cwd=BASE_DIR)

                # Run Reel Mimic / Quickstart generator
                subprocess.run([sys.executable, REEL_MIMIC, mimic, prompt], cwd=BASE_DIR)

                self._send_json({
                    "status": "success",
                    "message": "Pipeline executed successfully",
                    "previewCommand": "npm run preview",
                    "renderCommand": "npm run render"
                })
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=500)

        elif self.path == "/api/convert":
            try:
                target_fmt = "9:16" if data.get("format") in ["9:16", "vertical"] else "16:9"
                print(f"🔄 [Studio Format Convert] Switching to {target_fmt}...")
                subprocess.run([sys.executable, STUDIO, "convert", target_fmt], cwd=BASE_DIR)
                self._send_json({"status": "success", "format": target_fmt})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=500)

        elif self.path == "/api/render":
            try:
                print("⚡ [Studio Render] Dispatched Remotion render...")
                subprocess.Popen([sys.executable, STUDIO, "render"], cwd=BASE_DIR)
                self._send_json({"status": "success", "message": "Render job dispatched to Remotion"})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=500)

        elif self.path == "/api/voice-clone":
            try:
                print("🎙️ [Studio Voice Clone] Triggered 5-second voice clone synthesis...")
                subprocess.Popen([sys.executable, STUDIO, "clone-voice"], cwd=BASE_DIR)
                self._send_json({"status": "success", "message": "5-Second voice clone started"})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=500)

        elif self.path == "/api/upscale":
            try:
                target_file = data.get("file", "")
                if not target_file or not _is_safe_path(target_file):
                    # Default to scene_01 if unspecified or unsafe
                    target_file = os.path.join("assets", "visuals", "scene_01.jpg")
                print(f"🔍 [Studio Upscaler] Upscaling {target_file} to 4K...")
                subprocess.Popen([sys.executable, STUDIO, "upscale", target_file], cwd=BASE_DIR)
                self._send_json({"status": "success", "message": "Upscale job launched", "file": target_file})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=500)

        elif self.path == "/api/copilot/chat":
            self._handle_copilot_chat(data)

        else:
            self.send_response(404)
            self.end_headers()

    def _handle_copilot_status(self):
        """Returns live pipeline status, scene count, format, and step progress."""
        timeline_path = os.path.join(BASE_DIR, "timeline.json")
        scene_count = 0
        project_title = "Untitled Production"
        is_vertical = False

        if os.path.exists(timeline_path):
            try:
                with open(timeline_path, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                    scene_count = len(tdata.get("scenes", []))
                    project_title = tdata.get("project", project_title)
                    is_vertical = tdata.get("height", 1080) > tdata.get("width", 1920)
            except Exception:
                pass

        current_step = 3 if scene_count > 0 else 1
        steps = [
            "1. Script & Premise",
            "2. Timeline & Beats",
            "3. Media Acquisition & 3D",
            "4. Neural Audio & Voice Clone",
            "5. Remotion Canvas Preview",
            "6. MP4 Broadcast Export"
        ]

        self._send_json({
            "currentStep": current_step,
            "stepName": steps[current_step - 1],
            "totalSteps": 6,
            "stepsRemaining": max(0, 6 - current_step),
            "project": project_title,
            "sceneCount": scene_count,
            "format": "9:16" if is_vertical else "16:9",
            "safeZone": is_vertical,
            "suggestions": [
                {"label": "⚡ Enable Safe-Zone Guide", "action": "safe_zone"},
                {"label": "📱 Switch to 9:16 Vertical Reel", "action": "convert_916"},
                {"label": "🎙️ Clone Voice (5-Sec Sample)", "action": "voice_clone"},
                {"label": "🔍 4K Super-Resolution", "action": "upscale_4k"}
            ]
        })

    def _handle_copilot_chat(self, data):
        """Interactive live copilot assistant for mid-flight customisation."""
        user_msg = str(data.get("message", "")).strip().lower()
        action_triggered = None
        reply = "I'm your OVE Production Assistant. How can I help fine-tune your video?"

        # Match natural user commands
        if any(k in user_msg for k in ["safe zone", "safezone", "tiktok guide"]):
            action_triggered = "toggle_safe_zone"
            reply = "📱 TikTok/Shorts safe-zone guides toggled! Subtitles and logos are protected within mobile app margins."
        elif any(k in user_msg for k in ["9:16", "vertical", "reel", "shorts"]):
            subprocess.run([sys.executable, STUDIO, "convert", "9:16"], cwd=BASE_DIR)
            action_triggered = "switch_916"
            reply = "📱 Switched active video canvas to 9:16 Vertical Reel format (1080x1920)."
        elif any(k in user_msg for k in ["16:9", "widescreen", "cinema", "youtube"]):
            subprocess.run([sys.executable, STUDIO, "convert", "16:9"], cwd=BASE_DIR)
            action_triggered = "switch_169"
            reply = "📺 Switched active video canvas to 16:9 Cinema Widescreen format (1920x1080)."
        elif any(k in user_msg for k in ["upscale", "4k", "super res"]):
            target = os.path.join("assets", "visuals", "scene_01.jpg")
            subprocess.Popen([sys.executable, STUDIO, "upscale", target], cwd=BASE_DIR)
            action_triggered = "upscale_4k"
            reply = "🔍 4K Super-Resolution upscaling dispatched for keyframe visual assets."
        elif any(k in user_msg for k in ["clone voice", "my voice", "voice clone"]):
            subprocess.Popen([sys.executable, STUDIO, "clone-voice"], cwd=BASE_DIR)
            action_triggered = "voice_clone"
            reply = "🎙️ 5-second voice clone synthesis job started! Generating scene narrations."
        elif any(k in user_msg for k in ["render", "export", "build mp4"]):
            subprocess.Popen([sys.executable, STUDIO, "render"], cwd=BASE_DIR)
            action_triggered = "render"
            reply = "⚡ Render job dispatched to Remotion engine! Final MP4 will be saved to out/."
        elif any(k in user_msg for k in ["theme", "style", "davinci", "capcut", "premiere", "vn", "filmora", "after effects"]):
            theme_choice = "vn" if "vn" in user_msg else ("capcut" if "capcut" in user_msg else ("filmora" if "filmora" in user_msg else "davinci"))
            action_triggered = f"theme_{theme_choice}"
            reply = f"🎨 UI Workspace theme updated to {theme_choice.upper()} mode!"
        else:
            # Query ModelRouter for smart film director suggestions
            try:
                from model_router import ModelRouter
                router = ModelRouter()
                res = router.generate_with_fallback(f"As a video director, answer briefly: {user_msg}")
                reply = str(res.get("content", ""))[:250] or "Ready to optimize your timeline! What change would you like to make?"
            except Exception:
                reply = "Ready to optimize your timeline! You can switch formats, toggle TikTok safe-zones, clone your voice, or trigger 4K upscaling."

        self._send_json({
            "status": "success",
            "reply": reply,
            "action": action_triggered,
            "currentStep": 3,
            "stepsRemaining": 3,
            "suggestions": [
                "📱 Enable 9:16 Safe-Zone",
                "⚡ Switch to CapCut / VN Theme",
                "🎙️ 5-Second Voice Clone",
                "🔍 4K Super-Resolution"
            ]
        })

    def _send_json(self, payload, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

def run_server(port=8080):
    server_address = ('127.0.0.1', port)
    try:
        httpd = HTTPServer(server_address, RpaRequestHandler)
    except OSError:
        # Fallback port if 8080 is in use
        port = 8888
        server_address = ('127.0.0.1', port)
        httpd = HTTPServer(server_address, RpaRequestHandler)

    pro_url = f"http://127.0.0.1:{port}/"
    rpa_url = f"http://127.0.0.1:{port}/rpa"
    print("=" * 70)
    print("🎬 ANTIGRAVITY UNIFIED VIDEO STUDIO PRO")
    print("=" * 70)
    print(f"✨ Pro Desktop NLE UI : {pro_url}")
    print(f"🤖 Visual RPA Canvas  : {rpa_url}")
    print("🎨 Themes: DaVinci Resolve | CapCut Neon | Premiere Pro | Final Cut")
    print("Press Ctrl+C to stop.")
    print("=" * 70)

    try:
        webbrowser.open(pro_url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Studio server.")
        httpd.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(p)
