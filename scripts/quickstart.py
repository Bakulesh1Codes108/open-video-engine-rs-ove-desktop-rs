#!/usr/bin/env python3
"""
1-Click Quickstart Generator for Antigravity Video Studio
Enables anyone to clone the repo and immediately generate a full 3-scene
cinematic documentary from a single sentence prompt.
"""

import sys
import os
import subprocess
import json

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
DEVICE_ADVISOR = os.path.join(SCRIPTS_DIR, "device_advisor.py")
STUDIO = os.path.join(SCRIPTS_DIR, "studio.py")

def run_quickstart(concept_prompt: str, preset: str = "netflix-doc", generate_audio: bool = True, fetch_media: bool = True):
    print("=" * 65)
    print("🎬 ANTIGRAVITY 1-CLICK AUTONOMOUS VIDEO QUICKSTART")
    print("=" * 65)

    # 1. Device & Storage Advisor Check
    print("🔍 Analyzing hardware & available storage...")
    subprocess.run([sys.executable, DEVICE_ADVISOR], cwd=BASE_DIR)
    print("")

    # 2. Reset or Initialize project
    title = concept_prompt[:45].strip().title()
    subprocess.run([sys.executable, STUDIO, "init", title], cwd=BASE_DIR)

    # 3. Create a 3-Beat Cinematic Documentary Arc
    print("\n🎥 Generating 3-Act Cinematic Documentary Story Arc...")

    beats = [
        {
            "id": "scene_01",
            "title": "Act I: The Hook",
            "concept": f"{concept_prompt} - The mysterious beginning and initial catalyst.",
            "duration": 5.5,
            "motion": "zoom-in"
        },
        {
            "id": "scene_02",
            "title": "Act II: The Journey",
            "concept": f"{concept_prompt} - Venturing deeper into the unknown, facing immense scale and challenge.",
            "duration": 6.5,
            "motion": "pan-right"
        },
        {
            "id": "scene_03",
            "title": "Act III: The Revelation",
            "concept": f"{concept_prompt} - Reaching the breakthrough, a breathtaking perspective of what lies ahead.",
            "duration": 6.0,
            "motion": "zoom-out"
        }
    ]

    for b in beats:
        cmd = [
            sys.executable, STUDIO, "director-scene",
            b["id"], b["concept"], preset
        ]
        if not fetch_media:
            cmd.append("--no-media")
        subprocess.run(cmd, cwd=BASE_DIR)

    # 4. Generate Voiceovers (if edge-tts installed)
    if generate_audio:
        print("\n🎙️ Generating voiceovers...")
        subprocess.run([sys.executable, STUDIO, "audio"], cwd=BASE_DIR)

        print("\n" + "=" * 65)
        print("✨ PRODUCTION READY!")
        print("=" * 65)
        print("To preview your documentary in the video player, run:")
        print("  npm install")
        print("  npm run preview")
        print("\nTo export the final high-speed MP4, run:")
        print("  npm run render")
        print("=" * 65)

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "The launch of Voyager 1 into the vast cosmic interstellar void"
    preset = "netflix-doc"
    run_quickstart(prompt, preset)
