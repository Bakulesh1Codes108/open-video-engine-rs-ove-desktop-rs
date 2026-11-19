#!/usr/bin/env python3
"""
On-Demand Engine Hub & Model Advisor for Antigravity Video Studio
Enforces the Zero-Bloat Principle:
  - Keeps repository featherweight (<20 MB)
  - Manages external heavy engines (MiniMax H3 FreeVideo, LTX-Video 2.5,
    PySceneDetect, WhisperX, Kokoro-82M, LosslessCut, Real-ESRGAN, Ollama)
  - Provides just-in-time AI suggestions and 1-click installation commands
    only when explicitly needed for production.
"""

import os
import sys
import shutil
import subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import device_advisor

ENGINES_CATALOG = {
    "ltx-video": {
        "name": "Lightricks LTX-Video 2.5 (Fast 5-Min Short Film Generator)",
        "type": "Text/Image-to-Video",
        "vram": "4 GB - 8 GB VRAM",
        "description": "Ultra-fast diffusion transformer for generating 5-second cinematic b-roll clips and short films under 5 minutes.",
        "recommended_for": "Cinematic short films, sci-fi documentaries, nature b-roll",
        "install_cmd": "pip install ltx-video diffusers torch --index-url https://download.pytorch.org/whl/cu121"
    },
    "freevideo": {
        "name": "FlashML-org/FreeVideo (MiniMax H3 Low-VRAM)",
        "type": "MiniMax H3 Video Inference",
        "vram": "8 GB VRAM / 16 GB RAM",
        "description": "Quantized consumer-grade runner for MiniMax H3 (Video DeltaNet with layer offloading).",
        "recommended_for": "High-fidelity photorealistic human motion & complex storytelling",
        "install_cmd": "git clone https://github.com/FlashML-org/FreeVideo.git && cd FreeVideo && pip install -r requirements.txt"
    },
    "kokoro": {
        "name": "Kokoro-82M Neural TTS (Ultra-Lightweight)",
        "type": "Local Voice Synthesizer",
        "vram": "<100 MB RAM (CPU Friendly)",
        "description": "82M parameter open-weights TTS. Runs in real-time on CPU or GPU with near ElevenLabs natural expressiveness.",
        "recommended_for": "Offline narration, privacy-focused voice synthesis, 8GB Mac CPU",
        "install_cmd": "pip install kokoro-onnx soundfile"
    },
    "pyscenedetect": {
        "name": "PySceneDetect (Video Cut Boundary Extractor)",
        "type": "Video Analysis & Rhythm Extraction",
        "vram": "CPU mode (<50 MB RAM)",
        "description": "Automatically analyzes reference videos and finds exact cut timestamps to clone viral pacing.",
        "recommended_for": "Reverse-engineering TikTok/Reel videos, automatic pacing extraction",
        "install_cmd": "pip install scenedetect[opencv]"
    },
    "whisperx": {
        "name": "WhisperX (Forced Alignment Word Timestamps)",
        "type": "Speech Alignment",
        "vram": "1 GB - 2 GB VRAM (or CPU)",
        "description": "Generates word-level millisecond timestamps to power Hormozi-style kinetic bouncing highlight subtitles.",
        "recommended_for": "Vertical V3 kinetic active-word subtitle synchronization",
        "install_cmd": "pip install whisperx"
    },
    "real-esrgan": {
        "name": "Real-ESRGAN / Compact Upscaler (4K Upscaling)",
        "type": "Super-Resolution",
        "vram": "2 GB - 4 GB VRAM",
        "description": "Upscales 1080p stills and video clips into crystal-clear 4K without storing 60GB raw files.",
        "recommended_for": "Broadcast 4K export from lightweight 1080p source assets",
        "install_cmd": "pip install realesrgan"
    },
    "lossless-cut": {
        "name": "LosslessCut / FFmpeg Concat Swiss-Knife",
        "type": "Lossless Video Editor",
        "vram": "Zero VRAM / Instant FFmpeg stream copy",
        "description": "Merges multiple scenes and trims clips in milliseconds without re-encoding.",
        "recommended_for": "Instant clip concatenation, lossless trimming, rapid export",
        "install_cmd": "brew install ffmpeg (Mac) or winget install Gyan.FFmpeg (Windows)"
    },
    "ollama": {
        "name": "Ollama (Open-Source Local LLM Hub)",
        "type": "Local LLM Host",
        "vram": "4 GB - 8 GB VRAM",
        "description": "Runs Llama 3.2, Mistral, Qwen locally on your NVIDIA GPU without manual weight management.",
        "recommended_for": "Offline scripting, character generation, prompt compression",
        "install_cmd": "curl -fsSL https://ollama.com/install.sh | sh (or download from ollama.com)"
    }
}

def check_engine_installed(engine_key: str) -> bool:
    if engine_key == "lossless-cut":
        return shutil.which("ffmpeg") is not None
    elif engine_key == "ollama":
        return shutil.which("ollama") is not None
    elif engine_key == "pyscenedetect":
        try:
            import scenedetect
            return True
        except ImportError:
            return shutil.which("scenedetect") is not None
    elif engine_key == "kokoro":
        try:
            import kokoro
            return True
        except ImportError:
            return False
    elif engine_key == "whisperx":
        try:
            import whisperx
            return True
        except ImportError:
            return False
    elif engine_key == "real-esrgan":
        try:
            import realesrgan
            return True
        except ImportError:
            return False
    elif engine_key == "ltx-video":
        try:
            import ltx_video
            return True
        except ImportError:
            return False
    elif engine_key == "freevideo":
        return os.path.exists(os.path.join(BASE_DIR, "FreeVideo"))
    return False

def show_hub_status():
    print("=" * 72)
    print("📦 ANTIGRAVITY ON-DEMAND ENGINE HUB & MODEL ADVISOR")
    print("Zero-Bloat Principle: Heavy engines install JIT only when ordered.")
    print("=" * 72)

    hw = device_advisor.analyze_system()
    print(f"🖥️  Host System: {hw['os']} | RAM: {hw['ram_gb']} GB | Disk Free: {hw['disk']['free_gb']} GB")
    print(f"🎮 GPU Compute: {hw['gpu']['name']} ({hw['gpu']['type']})")
    print("-" * 72)

    for k, info in ENGINES_CATALOG.items():
        is_inst = check_engine_installed(k)
        status_badge = "🟢 [INSTALLED & READY]" if is_inst else "⚪ [ON-DEMAND (NOT INSTALLED)]"
        print(f"\n{status_badge} {info['name']}")
        print(f"   Category: {info['type']} | Compute Need: {info['vram']}")
        print(f"   Purpose:  {info['description']}")
        if not is_inst:
            print(f"   👉 To Install: {info['install_cmd']}")
    print("\n" + "=" * 72)

def advise_best_engines(goal: str):
    print("=" * 72)
    print(f"🤖 AI ENGINE ADVISOR: Tailoring optimal stack for: '{goal}'")
    print("=" * 72)
    g = goal.lower()

    if any(w in g for w in ["short film", "5 min", "5 minutes", "movie", "cinema", "story"]):
        print("🎯 Recommended Production Stack for Short Films (< 5 Mins):")
        print("  1. Visuals: Lightricks LTX-Video 2.5 (Fast clip generation) or Cloud Imagen 3 stills")
        print("  2. Camera: Open Higgsfield Rigs (Orbit 360, FPV Dive, 35mm grain)")
        print("  3. Audio: Edge-TTS (ChristopherNeural) or Kokoro-82M")
        print("  4. Stitching: FFmpeg Lossless Concat (scripts/ffmpeg_tools.py concat)")
        print("\n💡 Why? Keeps device cool, exports under 5 minutes without downloading 68GB models.")

    elif any(w in g for w in ["reverse", "clone", "tiktok", "reel", "mrbeast", "hormozi"]):
        print("🎯 Recommended Production Stack for Viral Video Reverse-Engineering:")
        print("  1. Cut Detection: PySceneDetect (pip install scenedetect[opencv])")
        print("  2. Word Timing: WhisperX for kinetic word highlighting")
        print("  3. Composition: Antigravity Vertical V3 (src/compositions/VerticalComposition.tsx)")
        print("  4. Quick Execution: python3 scripts/studio.py reverse-engineer reference.mp4")

    elif any(w in g for w in ["voice", "audio", "clone"]):
        print("🎯 Recommended Audio Stack:")
        print("  1. Zero-Cost Cloud: Edge-TTS (pip install edge-tts) -> Zero RAM/Disk cost")
        print("  2. 5-Second Voice Cloning: F5-TTS on HP Pavilion GPU (pip install f5-tts)")
        print("  3. Ultra-Light Offline: Kokoro-82M (pip install kokoro-onnx)")

    else:
        print("🎯 Standard Antigravity Unified Studio Stack:")
        print("  • Remotion + Three.js + Open Higgsfield (Built-in, zero external weight)")
        print("  • Pixabay/Pexels stock media fetcher (Built-in)")
        print("  • Graphify Memory (<15 KB footprint)")
    print("=" * 72)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["suggest", "advise"]:
        goal_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Generate a 5-minute short film"
        advise_best_engines(goal_text)
    else:
        show_hub_status()
