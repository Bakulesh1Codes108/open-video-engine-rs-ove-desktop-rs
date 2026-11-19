#!/usr/bin/env python3
"""
Automated Voiceover Generator for Antigravity Video Studio
Reads timeline.json / graph.json and batch-synthesizes studio narration via Edge-TTS.
Automatically syncs speech duration to Remotion frame counts.
"""

import asyncio
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMELINE_FILE = os.path.join(BASE_DIR, "timeline.json")
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
GRAPH_FILE = os.path.join(BASE_DIR, "graphify-out", "graph.json")

os.makedirs(AUDIO_DIR, exist_ok=True)

DEFAULT_VOICE = "en-US-ChristopherNeural"  # Alternatives: en-US-GuyNeural, en-US-SoniaNeural

async def generate_scene_audio(scene_id, text, voice=DEFAULT_VOICE):
    import edge_tts
    out_file = os.path.join(AUDIO_DIR, f"{scene_id}.mp3")
    print(f"🎙️  Synthesizing [{scene_id}] with {voice}...")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_file)
    print(f"✅ Saved voiceover to: {out_file}")
    return out_file

def estimate_duration_frames(text, fps=30):
    # Average speaking rate: ~2.5 words per second + 0.5s breathing pad
    word_count = len(text.split())
    estimated_seconds = max(3.0, (word_count / 2.5) + 0.5)
    return int(estimated_seconds * fps), round(estimated_seconds, 1)

async def batch_generate_from_timeline(voice=DEFAULT_VOICE):
    if not os.path.exists(TIMELINE_FILE):
        print(f"❌ Error: {TIMELINE_FILE} not found. Run graph_memory.py export-timeline first.")
        return

    with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    scenes = timeline.get("scenes", [])
    fps = timeline.get("fps", 30)

    try:
        import edge_tts
    except ImportError:
        print("⚠️ edge-tts is not installed in current python environment.")
        print("💡 You can install it via: pip install edge-tts")
        print("Creating placeholder audio entries...")
        return

    for scene in scenes:
        sid = scene.get("id")
        text = scene.get("subtitle", "")
        if text:
            await generate_scene_audio(sid, text, voice)
            frames, sec = estimate_duration_frames(text, fps)
            scene["durationInFrames"] = frames
            scene["voiceover"] = f"assets/audio/{sid}.mp3"

    # Save synced durations back to timeline.json
    with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    print(f"✨ Synced speech durations and voiceovers back to {TIMELINE_FILE}")

if __name__ == "__main__":
    if "--clone" in sys.argv:
        import voice_clone
        custom_sample = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
        voice_clone.batch_clone_from_timeline(custom_sample)
    else:
        voice = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else DEFAULT_VOICE
        asyncio.run(batch_generate_from_timeline(voice))
