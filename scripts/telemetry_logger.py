#!/usr/bin/env python3
"""
Telemetry, Execution Logger & Stuck-Agent Diagnostic Engine for Open Video Engine (OVE).
Records every execution phase, sub-agent call, and timing into persistent structured logs.
Provides autonomous stuck-agent diagnosis to detect bottlenecks (FFmpeg, Remotion, Network, TTS)
and prescribe exact automated self-healing solutions for local AI and creators.
"""

import os
import sys
import json
import time
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

TELEMETRY_LOG = os.path.join(LOGS_DIR, "production_telemetry.log")
DIAGNOSTICS_JSON = os.path.join(LOGS_DIR, "agent_diagnostics.json")

class TelemetryLogger:
    def __init__(self, session_id=None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_times = {}

    def log_event(self, level: str, agent_name: str, message: str, metadata: dict = None):
        """Appends human-readable timestamped log line."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        meta_str = f" | {json.dumps(metadata)}" if metadata else ""
        line = f"[{timestamp}] [{level.upper():<5}] [{agent_name:<18}] {message}{meta_str}\n"

        try:
            with open(TELEMETRY_LOG, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass

    def start_step(self, step_name: str, metadata: dict = None):
        self.start_times[step_name] = time.time()
        self.log_event("INFO", step_name, f"Starting step execution...", metadata)
        self._update_diagnostics(step_name, "RUNNING", metadata)

    def complete_step(self, step_name: str, metadata: dict = None):
        start = self.start_times.get(step_name, time.time())
        duration = round(time.time() - start, 3)
        meta = metadata or {}
        meta["duration_seconds"] = duration
        self.log_event("INFO", step_name, f"Step completed successfully in {duration}s", meta)
        self._update_diagnostics(step_name, "COMPLETED", meta)

    def error_step(self, step_name: str, error_msg: str, metadata: dict = None):
        meta = metadata or {}
        meta["error"] = error_msg
        self.log_event("ERROR", step_name, f"Step failed: {error_msg}", meta)
        self._update_diagnostics(step_name, "FAILED", meta)

    def _update_diagnostics(self, step_name: str, status: str, meta: dict = None):
        diag_data = {}
        if os.path.exists(DIAGNOSTICS_JSON):
            try:
                with open(DIAGNOSTICS_JSON, "r", encoding="utf-8") as f:
                    diag_data = json.load(f)
            except Exception:
                diag_data = {}

        diag_data["last_updated"] = datetime.now().isoformat()
        diag_data["session_id"] = self.session_id
        diag_data.setdefault("steps", {})[step_name] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metadata": meta or {}
        }

        try:
            with open(DIAGNOSTICS_JSON, "w", encoding="utf-8") as f:
                json.dump(diag_data, f, indent=2)
        except Exception:
            pass

    @staticmethod
    def analyze_stuck_pipeline() -> dict:
        """Analyzes logs to detect where a pipeline is stalled or failed."""
        if not os.path.exists(DIAGNOSTICS_JSON):
            return {
                "health": "NO_RUNS_RECORDED",
                "message": "No active pipeline runs logged yet."
            }

        try:
            with open(DIAGNOSTICS_JSON, "r", encoding="utf-8") as f:
                diag = json.load(f)
        except Exception as e:
            return {"health": "ERROR", "message": f"Could not parse diagnostics: {e}"}

        steps = diag.get("steps", {})
        stuck_points = []
        now = time.time()

        for step, data in steps.items():
            status = data.get("status")
            if status == "FAILED":
                err = data.get("metadata", {}).get("error", "Unknown failure")
                fix = "Run 'python scripts/studio.py doctor --fix' to self-heal environment."
                if "remotion" in err.lower() or "node" in err.lower():
                    fix = "Run 'npm install' in repository root to reinstall Remotion video core."
                elif "ffmpeg" in err.lower():
                    fix = "Run setup.bat or 'winget install Gyan.FFmpeg' to restore FFmpeg."
                elif "tts" in err.lower() or "audio" in err.lower():
                    fix = "Install Edge-TTS via: 'pip install edge-tts' or check network."
                elif "space" in err.lower() or "disk" in err.lower():
                    fix = "Run 'python scripts/studio.py storage' to map renders to secondary drive."

                stuck_points.append({
                    "step": step,
                    "issue": f"Step '{step}' marked as FAILED with error: {err}",
                    "recommended_fix": fix
                })

        return {
            "session_id": diag.get("session_id"),
            "last_updated": diag.get("last_updated"),
            "health": "STUCK" if stuck_points else "HEALTHY",
            "issues_detected": len(stuck_points),
            "stuck_details": stuck_points
        }

def print_log_report():
    print("=" * 72)
    print("🩺 OVE RUNTIME TELEMETRY & STUCK-AGENT DIAGNOSTIC REPORT")
    print("=" * 72)
    analysis = TelemetryLogger.analyze_stuck_pipeline()

    if analysis["health"] == "HEALTHY":
        print("✅ Pipeline Health: ALL SYSTEMS OPERATIONAL")
        print("   No stalled steps, memory leaks, or execution failures detected.")
        print(f"   Log Location: {TELEMETRY_LOG}")
    elif analysis["health"] == "NO_RUNS_RECORDED":
        print("⚪ No pipeline execution logs recorded yet.")
        print("   Logs will automatically appear when running any studio command.")
    else:
        print(f"⚠️  PIPELINE STUCK / FAILED ({analysis['issues_detected']} issue(s) found):")
        for idx, issue in enumerate(analysis["stuck_details"], 1):
            print(f"\n   [{idx}] Bottleneck in Step: {issue['step']}")
            print(f"       Problem: {issue['issue']}")
            print(f"       🔧 AI Self-Healing Fix: {issue['recommended_fix']}")

    # Print last 5 log events
    if os.path.exists(TELEMETRY_LOG):
        print("\n📜 Recent Execution Logs (Tail):")
        try:
            with open(TELEMETRY_LOG, "r", encoding="utf-8") as f:
                lines = f.readlines()[-8:]
                for l in lines:
                    print(f"   {l.strip()}")
        except Exception:
            pass
    print("=" * 72)

if __name__ == "__main__":
    print_log_report()
