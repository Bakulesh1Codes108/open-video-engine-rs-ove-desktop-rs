#!/usr/bin/env python3
"""
Master Studio CLI for Antigravity Video Studio
Unifies:
  - Interactive AI Film Copilot & Step-by-Step Controller (--until STEP)
  - Graphify Context Memory (<6 KB)
  - Pixabay / Pexels / Wikimedia Royalty-Free Stock Media Fetcher
  - Remotion + GSAP Deterministic Render Core
  - Open Higgsfield Camera Motion Rigs (Orbit 360, FPV Dive, Vertigo)
  - Three.js 3D Procedural Scenes (Globe, Particles, Isometric Chart)
  - Manim Mathematical & Scientific Animation Dispatcher
  - Blender Headless 3D Render Engine
  - Reel Mimic Viral Video Pacing Cloner (Hormozi, Vox, MrBeast)
  - Visual RPA Automation Pipeline & UI
  - DaVinci Resolve Color Science & OpenCut J-Cuts
"""

import sys
import os
import subprocess
import json
import re

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

GRAPH_MEMORY = os.path.join(SCRIPTS_DIR, "graph_memory.py")
GRAPH_EDITOR = os.path.join(SCRIPTS_DIR, "graph_editor.py")
VOICEOVER = os.path.join(SCRIPTS_DIR, "make_voiceovers.py")
MODEL_ROUTER = os.path.join(SCRIPTS_DIR, "model_router.py")
DIRECTOR_PRESETS = os.path.join(SCRIPTS_DIR, "director_presets.py")
DEVICE_ADVISOR = os.path.join(SCRIPTS_DIR, "device_advisor.py")
QUICKSTART = os.path.join(SCRIPTS_DIR, "quickstart.py")
REEL_MIMIC = os.path.join(SCRIPTS_DIR, "reel_mimic.py")
BLENDER_ENGINE = os.path.join(SCRIPTS_DIR, "blender_engine.py")
MANIM_ENGINE = os.path.join(SCRIPTS_DIR, "manim_engine.py")
RPA_SERVER = os.path.join(SCRIPTS_DIR, "rpa_server.py")
MEDIA_FETCHER = os.path.join(SCRIPTS_DIR, "media_fetcher.py")
COPILOT_AGENT = os.path.join(SCRIPTS_DIR, "copilot_agent.py")
VOICE_CLONE = os.path.join(SCRIPTS_DIR, "voice_clone.py")
FFMPEG_TOOLS = os.path.join(SCRIPTS_DIR, "ffmpeg_tools.py")
REVERSE_ENGINEER = os.path.join(SCRIPTS_DIR, "reverse_engineer.py")
ENGINE_HUB = os.path.join(SCRIPTS_DIR, "engine_hub.py")
UPSCALER = os.path.join(SCRIPTS_DIR, "upscaler.py")
PDF_COMPILER = os.path.join(SCRIPTS_DIR, "compile_pdf.py")
SETUP_DOCTOR = os.path.join(SCRIPTS_DIR, "setup_doctor.py")
AGENT_CREATOR = os.path.join(SCRIPTS_DIR, "agent_creator.py")
VIDEO_INSPECTOR = os.path.join(SCRIPTS_DIR, "video_inspector.py")
CREATOR_VAULT = os.path.join(SCRIPTS_DIR, "creator_vault.py")
TELEMETRY_LOGGER = os.path.join(SCRIPTS_DIR, "telemetry_logger.py")
LAB_REPORT = os.path.join(SCRIPTS_DIR, "lab_report.py")

def run_cmd(args):
    return subprocess.run(args, cwd=BASE_DIR)

def extract_json_from_llm(text: str) -> dict:
    if not text:
        return {}
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    return {}

def print_help():
    print("""
🎬 Antigravity Video Studio CLI (Multi-Engine & RPA Pipeline)

Usage:
  python3 scripts/studio.py app                         [Launch Pro Desktop NLE UI (DaVinci/CapCut/Premiere/FinalCut)]
  python3 scripts/studio.py copilot [topic] [--until STEP] [Interactive producer & step-by-step controller]
  python3 scripts/studio.py step <step_name> "<topic>"    [Execute strictly up to step: script|timeline|media|audio|preview|render]
  python3 scripts/studio.py rpa                         [Launch Visual RPA Automation UI]
  python3 scripts/studio.py quickstart "<story idea>"   [1-Click full film generator]
  python3 scripts/studio.py mimic <preset> "<topic>"    [Clone viral pacing: hormozi | vox | mrbeast]
  python3 scripts/studio.py fetch-media <id> "<query>" [Fetch Pixabay/Pexels stock media]
  python3 scripts/studio.py blender [type] [title]      [Headless 3D Blender render: 3d_chrome_title]
  python3 scripts/studio.py manim [type] [id]           [3Blue1Brown math render: neural_network]
  python3 scripts/studio.py inspect <URL_or_path>       [Forensic Video Deconstruction: cuts, audio cadence & best tools]
  python3 scripts/studio.py replicate <URL_or_path> "<topic>" [tweaks] [Replicate video skeleton with custom topic & tweaks]
  python3 scripts/studio.py styles                      [Creator Style Vault: MrBeast, Hormozi, Vox, Ali Abdaal, MKBHD]
  python3 scripts/studio.py apply-style <creator_id>    [Apply creator visual style signature to timeline]
  python3 scripts/studio.py scan-creator <id> "<Name>" <urls> [Scan multiple videos to learn creator editing DNA]
  python3 scripts/studio.py logs                        [Runtime Telemetry & Stuck-Agent Diagnostic Doctor]
  python3 scripts/studio.py agent "<prompt>"            [Prompt-to-Process Agent & Parallel Multi-Worker Pipeline]
  python3 scripts/studio.py cost "<prompt>"             [Token Optimizer & Cost Estimator ($0.00 Free vs Paid)]
  python3 scripts/studio.py budget [max_usd]            [View or set hard ceiling token budget limit]
  python3 scripts/studio.py doctor [--fix]              [AI Setup Assistant & Self-Healing Health Doctor]
  python3 scripts/studio.py storage                     [Multi-drive disk scanner & 4K render storage advisor]
  python3 scripts/studio.py advisor                     [Hardware, RAM & GPU advisor]
  python3 scripts/studio.py models                      [Check local Llama / OpenRouter / Gemini]
  python3 scripts/studio.py presets                     [List DaVinci cinematic color palettes]
  python3 scripts/studio.py clean "<noisy prompt>"      [Compress prompt & save 30-70% tokens]
  python3 scripts/studio.py edit "<edit command>"       [Prompt-driven graph memory editor]
  python3 scripts/studio.py director-scene <id> "<idea>" [preset] [Add scene with DaVinci grade & J-Cut]
  python3 scripts/studio.py smart-scene <id> "<prompt>" [Smart model router scene generation]
  python3 scripts/studio.py status                      [View live film reel report]
  python3 scripts/studio.py audio [voice_name]          [Generate free Microsoft Neural voiceovers]
  python3 scripts/studio.py clone-voice [sample_path]   [Clone creator 5s voice for all scenes]
  python3 scripts/studio.py vertical [hormozi|mrbeast] "<topic>" [1-Click 9:16 Vertical V3 viral reel generator]
  python3 scripts/studio.py convert [16:9|9:16]          [Switch active project between Widescreen & Vertical]
  python3 scripts/studio.py reverse-engineer <video.mp4> [OpenMotion + PySceneDetect video clone]
  python3 scripts/studio.py concat <file1> <file2> ...  [Lossless stream concatenation (0 re-encoding)]
  python3 scripts/studio.py cut <file> <start> <end>    [Lossless precision cut (LosslessCut pattern)]
  python3 scripts/studio.py upscale <image_path>        [4K super-resolution upscaler]
  python3 scripts/studio.py hub                         [On-demand engine catalog & JIT installer]
  python3 scripts/studio.py advise "<goal>"             [AI stack & model advisor for 5-min films]
  python3 scripts/studio.py lab                         [Run Monthly Laboratory Hardware & Token Benchmark Report]
  python3 scripts/studio.py pdf                         [Compile & render verified PDF production guide]
  python3 scripts/studio.py preview                     [Open in-editor Remotion Player]
  python3 scripts/studio.py render                      [Render broadcast MP4 (Auto-detects 16:9 or 9:16)]
  python3 scripts/studio.py render-vertical             [Render 9:16 Vertical V3 reel to out/vertical_reel.mp4]
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd in ["app", "ui", "pro", "desktop", "ove", "openvideo"]:
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        run_cmd([sys.executable, RPA_SERVER, str(port)])
    elif cmd in ["copilot", "producer", "interview"]:
        args = [sys.executable, COPILOT_AGENT] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["step", "until"]:
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/studio.py step <step_name_or_number> '<topic>'")
            print("Steps available: 1=script, 2=timeline, 3=media, 4=audio, 5=preview, 6=render")
            sys.exit(1)
        step_target = sys.argv[2]
        topic = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "Autonomous AI Video"
        run_cmd([sys.executable, COPILOT_AGENT, topic, "--until", step_target])
    elif cmd == "rpa":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        run_cmd([sys.executable, RPA_SERVER, str(port)])
    elif cmd in ["fetch-media", "stock", "pixabay"]:
        if len(sys.argv) < 4:
            print("Usage: python3 scripts/studio.py fetch-media <scene_id> '<search query>' [orientation: horizontal|vertical]")
            sys.exit(1)
        sid = sys.argv[2]
        query = sys.argv[3]
        ori = sys.argv[4] if len(sys.argv) > 4 else "horizontal"
        run_cmd([sys.executable, MEDIA_FETCHER, sid, query, ori])
    elif cmd == "mimic":
        pname = sys.argv[2] if len(sys.argv) > 2 else "alex_hormozi_viral_reel"
        topic = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "AI Video Revolution"
        run_cmd([sys.executable, REEL_MIMIC, pname, topic])
    elif cmd == "blender":
        stype = sys.argv[2] if len(sys.argv) > 2 else "3d_chrome_title"
        title = sys.argv[3] if len(sys.argv) > 3 else "FUTURE CINEMA"
        run_cmd([sys.executable, BLENDER_ENGINE, stype, title])
    elif cmd == "manim":
        stype = sys.argv[2] if len(sys.argv) > 2 else "neural_network"
        sid = sys.argv[3] if len(sys.argv) > 3 else "manim_01"
        run_cmd([sys.executable, MANIM_ENGINE, stype, sid])
    elif cmd in ["styles", "creators", "vault"]:
        run_cmd([sys.executable, CREATOR_VAULT, "list"])
    elif cmd in ["apply-style", "style"]:
        cid = sys.argv[2] if len(sys.argv) > 2 else "alex_hormozi"
        run_cmd([sys.executable, CREATOR_VAULT, "apply", cid])
    elif cmd == "scan-creator":
        args = [sys.executable, CREATOR_VAULT, "scan"] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["logs", "telemetry", "stuck"]:
        run_cmd([sys.executable, TELEMETRY_LOGGER])
    elif cmd in ["inspect", "analyze-video", "forensic"]:
        target = sys.argv[2] if len(sys.argv) > 2 else "examples/vox_k_shape_recovery_ai_geopolitics_explainer.mp4"
        run_cmd([sys.executable, VIDEO_INSPECTOR, "inspect", target])
    elif cmd in ["replicate", "clone-video", "copy-video"]:
        args = [sys.executable, VIDEO_INSPECTOR, "replicate"] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["skeleton", "recipe"]:
        skel = os.path.join(BASE_DIR, "graphify-out", "video_skeleton.json")
        if os.path.exists(skel):
            with open(skel, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("No video skeleton loaded yet. Run: python3 scripts/studio.py inspect <URL_or_path>")
    elif cmd in ["cost", "tokens", "pricing"]:
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "A cinematic 3-act documentary scene about underwater hydrothermal vents"
        run_cmd([sys.executable, MODEL_ROUTER, "cost", prompt])
    elif cmd == "budget":
        args = [sys.executable, MODEL_ROUTER, "budget"] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["agent", "parallel", "prompt-to-process"]:
        args = [sys.executable, AGENT_CREATOR] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["doctor", "health", "fix"]:
        args = [sys.executable, SETUP_DOCTOR] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["advisor", "storage", "disk", "sysinfo"]:
        args = [sys.executable, DEVICE_ADVISOR] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["quickstart", "generate"]:
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "The mystery of deep space radio bursts"
        run_cmd([sys.executable, QUICKSTART, prompt])
    elif cmd == "init":
        title = sys.argv[2] if len(sys.argv) > 2 else "Autonomous AI Documentary"
        run_cmd([sys.executable, GRAPH_MEMORY, "init", title])
    elif cmd == "status":
        run_cmd([sys.executable, GRAPH_MEMORY, "status"])
    elif cmd == "models":
        run_cmd([sys.executable, MODEL_ROUTER, "status"])
    elif cmd == "presets":
        run_cmd([sys.executable, DIRECTOR_PRESETS])
    elif cmd == "clean":
        raw = " ".join(sys.argv[2:])
        run_cmd([sys.executable, MODEL_ROUTER, "clean", raw])
    elif cmd == "edit":
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/studio.py edit '<natural language edit command>'")
            print("Examples:")
            print("  python3 scripts/studio.py edit 'make scene_01 8 seconds and zoom-in'")
            print("  python3 scripts/studio.py edit 'change subtitle of scene_02 to The world changed forever'")
            print("  python3 scripts/studio.py edit 'switch global style to netflix-doc'")
            sys.exit(1)
        instruction = " ".join(sys.argv[2:])
        run_cmd([sys.executable, GRAPH_EDITOR, "prompt", instruction])
    elif cmd == "director-scene":
        if len(sys.argv) < 4:
            print("Usage: python3 scripts/studio.py director-scene <id> '<rough concept>' [preset_name]")
            sys.exit(1)
        sid = sys.argv[2]
        raw_concept = sys.argv[3]
        preset = sys.argv[4] if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else "netflix-doc"
        skip_media = "--no-media" in sys.argv

        from model_router import PromptCompressor
        compressor = PromptCompressor()
        cleaned = compressor.clean_noisy_prompt(raw_concept)
        print(f"🧹 Cleaned Concept ({cleaned['estimated_token_savings']} token savings): '{cleaned['cleaned_prompt']}'")

        from director_presets import enhance_prompt
        enhanced = enhance_prompt(cleaned['cleaned_prompt'], preset)
        print(f"🎨 Applied DaVinci Preset: {enhanced['preset_title']} ({enhanced['colorGrade']}, J-Cut: {enhanced['jCutFrames']} frames)")

        title = sid.replace("_", " ").title()
        narration = cleaned['cleaned_prompt']
        dur = cleaned['detected_duration']
        motion = cleaned['detected_motion']
        vp = enhanced['enhanced_visual_prompt']

        if not skip_media:
            import media_fetcher
            media_fetcher.acquire_media_for_scene(sid, cleaned['cleaned_prompt'], orientation="horizontal")

        run_cmd([sys.executable, GRAPH_MEMORY, "add-scene", sid, title, narration, str(dur), vp, motion])
        run_cmd([sys.executable, GRAPH_MEMORY, "export-timeline"])
        print(f"✨ Scene [{sid}] saved with {preset} cinematic color grade and J-Cut pacing!")

    elif cmd == "smart-scene":
        if len(sys.argv) < 4:
            print("Usage: python3 scripts/studio.py smart-scene <id> '<rough noisy prompt>'")
            sys.exit(1)
        sid = sys.argv[2]
        raw_prompt = " ".join(sys.argv[3:])
        
        from model_router import PromptCompressor, ModelRouter
        compressor = PromptCompressor()
        router = ModelRouter()
        
        cleaned = compressor.clean_noisy_prompt(raw_prompt)
        print(f"🧹 Cleaned noisy prompt ({cleaned['estimated_token_savings']} token savings): '{cleaned['cleaned_prompt']}'")
        
        suggestion = router.suggest_tier(cleaned['cleaned_prompt'])
        print(f"💡 Suggested Model: {suggestion['recommended_provider']} ({suggestion['model']}) | Cost: {suggestion['estimated_cost']}")
        
        gen_result = router.generate_with_fallback(cleaned['cleaned_prompt'])
        
        title = sid.replace("_", " ").title()
        narration = cleaned['cleaned_prompt']
        duration = cleaned['detected_duration']
        motion = cleaned['detected_motion']
        visual_prompt = f"Cinematic photorealistic documentary shot: {cleaned['cleaned_prompt']}, 35mm lens, 8k"
        
        parsed = extract_json_from_llm(str(gen_result.get("content", "")))
        if parsed:
            title = parsed.get("title", title)
            narration = parsed.get("narration", narration)
            visual_prompt = parsed.get("visualPrompt", visual_prompt)
            duration = parsed.get("duration", duration)
            motion = parsed.get("motion", motion)

        import media_fetcher
        media_fetcher.acquire_media_for_scene(sid, narration, orientation="horizontal")

        run_cmd([sys.executable, GRAPH_MEMORY, "add-scene", sid, title, narration, str(duration), visual_prompt, motion])
        run_cmd([sys.executable, GRAPH_MEMORY, "export-timeline"])
        print(f"✨ Successfully integrated [{sid}] via smart router into Graphify Memory & Remotion Timeline!")

    elif cmd == "add-scene":
        if len(sys.argv) < 5:
            print("Usage: python3 scripts/studio.py add-scene <id> <title> <narration> [dur] [prompt] [motion]")
            sys.exit(1)
        sid = sys.argv[2]
        title = sys.argv[3]
        narr = sys.argv[4]
        dur = sys.argv[5] if len(sys.argv) > 5 else "5"
        vp = sys.argv[6] if len(sys.argv) > 6 else ""
        motion = sys.argv[7] if len(sys.argv) > 7 else "zoom-in"

        import media_fetcher
        media_fetcher.acquire_media_for_scene(sid, narr or title, orientation="horizontal")

        run_cmd([sys.executable, GRAPH_MEMORY, "add-scene", sid, title, narr, dur, vp, motion])
        run_cmd([sys.executable, GRAPH_MEMORY, "export-timeline"])
    elif cmd == "sync":
        run_cmd([sys.executable, GRAPH_MEMORY, "export-timeline"])
    elif cmd in ["convert", "switch-format", "format"]:
        if len(sys.argv) < 3:
            print("Usage: python3 scripts/studio.py convert <16:9|9:16>")
            sys.exit(1)
        target_fmt = sys.argv[2]
        run_cmd([sys.executable, GRAPH_EDITOR, "prompt", f"convert to {target_fmt}"])
    elif cmd in ["clone-voice", "voice-clone", "clone"]:
        args = [sys.executable, VOICE_CLONE] + sys.argv[2:]
        run_cmd(args)
    elif cmd == "audio":
        args = [sys.executable, VOICEOVER] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["vertical", "vertical-v3", "reel", "short"]:
        preset = "alex_hormozi_viral_reel"
        topic = "The AI Revolution in 2026"
        if len(sys.argv) > 2:
            arg2 = sys.argv[2].lower()
            if any(k in arg2 for k in ["hormozi", "mrbeast", "vox"]):
                preset = "alex_hormozi_viral_reel" if "hormozi" in arg2 else ("mrbeast_retention_hook" if "mrbeast" in arg2 else "vox_highlighter_explainer")
                topic = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else topic
            else:
                topic = " ".join(sys.argv[2:])
        run_cmd([sys.executable, REEL_MIMIC, preset, topic])
    elif cmd in ["reverse-engineer", "reverse", "openmotion"]:
        args = [sys.executable, REVERSE_ENGINEER] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["concat", "join", "merge"]:
        files = sys.argv[2:]
        args = [sys.executable, FFMPEG_TOOLS, "concat"] + files
        run_cmd(args)
    elif cmd in ["cut", "slice", "trim"]:
        args = [sys.executable, FFMPEG_TOOLS, "cut"] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["upscale", "4k"]:
        args = [sys.executable, UPSCALER] + sys.argv[2:]
        run_cmd(args)
    elif cmd in ["hub", "engines", "models-hub"]:
        run_cmd([sys.executable, ENGINE_HUB])
    elif cmd in ["advise", "suggest-stack"]:
        goal = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Generate a 5-minute short film"
        run_cmd([sys.executable, ENGINE_HUB, "advise", goal])
    elif cmd in ["pdf", "compile-pdf"]:
        run_cmd([sys.executable, PDF_COMPILER])
    elif cmd in ["lab", "lab-report", "moth-lab", "benchmark"]:
        run_cmd([sys.executable, LAB_REPORT])
    elif cmd in ["render-vertical", "render-reel"]:
        run_cmd(["npx", "remotion", "render", "src/index.ts", "VerticalV3", "out/vertical_reel.mp4"])
    elif cmd == "preview":
        run_cmd(["npx", "remotion", "preview", "src/index.ts"])
    elif cmd == "render":
        comp_id = "Documentary"
        out_file = "out/documentary.mp4"
        timeline_path = os.path.join(BASE_DIR, "timeline.json")
        if os.path.exists(timeline_path):
            try:
                with open(timeline_path, "r", encoding="utf-8") as f:
                    tdata = json.load(f)
                    if tdata.get("height", 1080) > tdata.get("width", 1920):
                        comp_id = "VerticalV3"
                        out_file = "out/vertical_reel.mp4"
            except Exception:
                pass
        run_cmd(["npx", "remotion", "render", "src/index.ts", comp_id, out_file])
    else:
        print_help()
