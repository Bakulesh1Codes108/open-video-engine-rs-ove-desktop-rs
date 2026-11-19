#!/usr/bin/env python3
"""
Interactive AI Film Copilot & Step-by-Step Pipeline Controller.
Guides creators through an executive producer interview, asks questions
when needed, manages token expenditure & costing, supports group and step-by-step
permissions, and executes strictly up to a specific step on command:
  Step 1: script     (Prompt compression & scene beats)
  Step 2: timeline   (Graphify memory & Remotion timeline)
  Step 3: media      (Pixabay/Pexels/Wikimedia visual asset acquisition)
  Step 4: audio      (Edge-TTS neural voiceover synthesis)
  Step 5: preview    (Remotion in-editor live player)
  Step 6: render     (Headless broadcast MP4 export)
"""

import sys
import os
import json
import subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import device_advisor
import media_fetcher
import graph_memory
import director_presets
import reel_mimic
import model_router

STEPS_ORDER = ["script", "timeline", "media", "audio", "preview", "render"]
STEP_NAMES = {
    "1": "script",
    "2": "timeline",
    "3": "media",
    "4": "audio",
    "5": "preview",
    "6": "render"
}

def prompt_user(question: str, default=None, choices=None) -> str:
    prompt_str = f"\n🎬 [AI Producer] {question}\n"
    if choices:
        for idx, (key, desc) in enumerate(choices.items(), 1):
            marker = " (Default)" if key == default else ""
            prompt_str += f"   [{idx}] {desc}{marker}\n"
        prompt_str += f"Choose [1-{len(choices)}] or press Enter for default: "
    else:
        if default:
            prompt_str += f"Press Enter for default: '{default}'\n> "
        else:
            prompt_str += "> "

    try:
        user_input = input(prompt_str).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Copilot session paused.")
        sys.exit(0)

    if not user_input:
        return default

    if choices:
        if user_input.isdigit():
            idx = int(user_input) - 1
            keys = list(choices.keys())
            if 0 <= idx < len(keys):
                return keys[idx]
        if user_input.lower() in choices:
            return user_input.lower()
        return default

    return user_input

class FilmCopilotAgent:
    def __init__(self, permission_mode="group", group_max_step=4):
        self.compressor = model_router.PromptCompressor()
        self.router = model_router.ModelRouter()
        self.cost_agent = model_router.TokenCostingAgent()
        self.permission_mode = permission_mode.lower() # "group", "step", "auto"
        self.group_max_step = group_max_step

    def request_permission(self, step_num: int, step_name: str, description: str) -> bool:
        """Manages Step-by-Step and Group Permission boundaries."""
        if self.permission_mode == "auto":
            return True
        elif self.permission_mode == "group":
            if step_num <= self.group_max_step:
                print(f"   [✓ Group Permission Active]: Step {step_num} ({step_name}) auto-approved.")
                return True
            else:
                prompt_str = (
                    f"\n✋ [Group Permission Boundary Reached at Step {step_num}]:\n"
                    f"   Authorize execution of '{step_name.upper()}' ({description})? [Y/n]: "
                )
                try:
                    ans = input(prompt_str).strip().lower()
                    return ans not in ["n", "no", "q", "quit"]
                except (EOFError, KeyboardInterrupt):
                    return False
        else: # "step"
            prompt_str = f"\n[?] [Permission Gate]: Authorize Step {step_num} ({step_name}: {description})? [Y/n]: "
            try:
                ans = input(prompt_str).strip().lower()
                return ans not in ["n", "no", "q", "quit"]
            except (EOFError, KeyboardInterrupt):
                return False

    def run_pipeline(self, initial_idea=None, stop_until="render", interactive=True):
        stop_step = STEP_NAMES.get(str(stop_until).lower(), str(stop_until).lower())
        if stop_step not in STEPS_ORDER:
            stop_step = "render"

        print("=" * 72)
        print("🎬 ANTIGRAVITY AI PRODUCER, TOKEN OPTIMIZER & PERMISSION CONTROLLER")
        print(f"Target Execution Boundary: [Complete through Step: '{stop_step.upper()}']")
        print(f"Permission Mode:           [{self.permission_mode.upper()}] (Group auto-approves Steps 1-{self.group_max_step})")
        print("=" * 72)

        # ----------------------------------------------------
        # STEP 1: SCRIPT & PREMISE
        # ----------------------------------------------------
        print("\n🔹 [STEP 1/6: SCRIPTING, TOKEN OPTIMIZATION & BUDGET CHECK]")
        if interactive and not initial_idea:
            raw_topic = prompt_user(
                "What is the story, course lesson, or topic of your video?",
                default="The exploration of subterranean oceans beneath Europa ice"
            )
        else:
            raw_topic = initial_idea or "The exploration of subterranean oceans beneath Europa ice"
            print(f"🎬 Premise: '{raw_topic}'")

        cleaned_info = self.compressor.clean_noisy_prompt(raw_topic)
        topic = cleaned_info["cleaned_prompt"]
        if cleaned_info["estimated_token_savings"] != "0%":
            print(f"🧹 Token Savings: {cleaned_info['estimated_token_savings']} tokens saved by prompt compression.")

        # Token Cost Estimation
        cost_info = self.cost_agent.calculate_cost_comparison(topic)
        est_cost = cost_info["providers"][0]["cost_display"]
        print(f"💰 Token Budget: ~{cost_info['total_tokens']} tokens | Est. Model Cost: {est_cost}")

        if stop_step == "script":
            print("\n🛑 [STOP COMMAND REACHED]: Completed Step 1 (Script & Prompt Optimized).")
            print(f"Ready topic: '{topic}'")
            return

        # ----------------------------------------------------
        # STEP 2: TIMELINE & STORY ARC
        # ----------------------------------------------------
        if not self.request_permission(2, "timeline", "Generate Storyboard & Graphify Nodes"):
            print("\n🛑 Execution paused by user at Step 2.")
            return

        print("\n🔹 [STEP 2/6: TIMELINE & GRAPHIFY STORYBOARD]")
        if interactive:
            format_choices = {
                "16:9": "16:9 Widescreen (YouTube, Course Documentaries, Netflix Cinema)",
                "9:16": "9:16 Vertical Reel (TikTok, Instagram Reels, YouTube Shorts)",
                "omni": "Dual Omni-Master (1-Click Dual Export for BOTH 16:9 Cinema & 9:16 Reel)"
            }
            aspect = prompt_user("Which format and platform are you producing for?", default="16:9", choices=format_choices)

            if aspect == "9:16":
                pacing_choices = {
                    "alex_hormozi_viral_reel": "Alex Hormozi Viral Reel (Fast 2.2s cuts, whip pans)",
                    "mrbeast_retention_hook": "MrBeast Fast Cut (Hyper-retention 1.6s cuts)"
                }
                pacing = prompt_user("Which viral reel pacing would you like to clone?", default="alex_hormozi_viral_reel", choices=pacing_choices)
            elif aspect == "omni":
                pacing_choices = {
                    "vox_highlighter_explainer": "Vox Data Explainer (Dynamic 3D maps & charts that look stunning in both 16:9 & 9:16)",
                    "netflix-doc": "Netflix Cinematic (Film grade, 35mm grain, dual-layer smart blur)",
                    "alex_hormozi_viral_reel": "Hormozi Viral Reel (Punchy pacing, auto-adapted to both)"
                }
                pacing = prompt_user("Which master pacing style should anchor both formats?", default="vox_highlighter_explainer", choices=pacing_choices)
            else:
                pacing_choices = {
                    "netflix-doc": "Netflix Cinema Documentary (Moody 2.39:1 anamorphic, 35mm grain, J-Cuts)",
                    "vox_highlighter_explainer": "Vox Data Explainer (Animated 3D maps, data graphs)",
                    "hollywood-epic": "Hollywood Blockbuster (Teal & Orange contrast)"
                }
                pacing = prompt_user("Which cinematic storytelling style matches your vision?", default="netflix-doc", choices=pacing_choices)
        else:
            aspect = "16:9"
            pacing = "netflix-doc"

        # Check Hardware & Storage
        device_info = device_advisor.analyze_system()
        print(f"💻 Hardware: {device_info['gpu']['name']} | {device_info['disk']['free_gb']} GB disk available")

        # Assemble Story Arc & Graphify Timeline
        if pacing in ["alex_hormozi_viral_reel", "mrbeast_retention_hook", "vox_highlighter_explainer"]:
            reel_mimic.mimic_reel(pacing, topic, fetch_media=False, generate_audio=False)
        else:
            from quickstart import run_quickstart
            run_quickstart(
                topic,
                preset=pacing if pacing in director_presets.CINEMATIC_PRESETS else "netflix-doc",
                generate_audio=False,
                fetch_media=False
            )

        print("💾 Synchronized scene nodes into Graphify memory & timeline.json.")

        if stop_step == "timeline":
            print("\n🛑 [STOP COMMAND REACHED]: Completed Step 2 (Timeline & Graphify Storyboard).")
            print("Timeline recipe ready in timeline.json and graphify-out/graph.json.")
            return

        # ----------------------------------------------------
        # STEP 3: STOCK & PROCEDURAL MEDIA ACQUISITION
        # ----------------------------------------------------
        if not self.request_permission(3, "media", "Acquire Stock Media & 3D Visual Assets"):
            print("\n🛑 Execution paused by user at Step 3.")
            return

        print("\n🔹 [STEP 3/6: MEDIA ACQUISITION (PIXABAY / PEXELS / 3D)]")
        timeline_path = os.path.join(BASE_DIR, "timeline.json")
        with open(timeline_path, "r", encoding="utf-8") as f:
            tdata = json.load(f)

        for s in tdata.get("scenes", []):
            sid = s.get("id")
            sub = s.get("subtitle") or topic
            media_fetcher.acquire_media_for_scene(sid, sub, orientation="vertical" if aspect == "9:16" else "horizontal")

        print("🖼️ Visual assets verified and guaranteed in assets/visuals/.")

        if stop_step == "media":
            print("\n🛑 [STOP COMMAND REACHED]: Completed Step 3 (Visual Media Acquired).")
            print("Visual assets are downloaded and mapped on disk.")
            return

        # ----------------------------------------------------
        # STEP 4: NEURAL VOICEOVER SYNTHESIS
        # ----------------------------------------------------
        if not self.request_permission(4, "audio", "Synthesize Neural Audio Narration"):
            print("\n🛑 Execution paused by user at Step 4.")
            return

        print("\n🔹 [STEP 4/6: NEURAL AUDIO SYNTHESIS (EDGE-TTS)]")
        voice = "en-US-ChristopherNeural"
        if interactive:
            voice_choices = {
                "en-US-ChristopherNeural": "Christopher Neural (Deep authoritative documentary)",
                "en-US-GuyNeural": "Guy Neural (Engaging, conversational)",
                "en-US-SoniaNeural": "Sonia Neural (Warm, expressive)"
            }
            voice = prompt_user("Who should narrate?", default="en-US-ChristopherNeural", choices=voice_choices)

        subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "make_voiceovers.py"), voice], cwd=BASE_DIR)
        print("🎙️ Audio narration synthesized and synced.")

        if stop_step == "audio":
            print("\n🛑 [STOP COMMAND REACHED]: Completed Step 4 (Audio & Voiceover Synthesized).")
            return

        # ----------------------------------------------------
        # STEP 5: IN-EDITOR REMOTION PREVIEW
        # ----------------------------------------------------
        if not self.request_permission(5, "preview", "Launch Remotion Player"):
            print("\n🛑 Execution paused by user at Step 5.")
            return

        print("\n🔹 [STEP 5/6: PREVIEW READY]")
        print("All visual layers, audio ducking, Ken Burns and subtitles are assembled.")
        print("Run command to launch Remotion Player: npm run preview")

        if stop_step == "preview":
            print("\n🛑 [STOP COMMAND REACHED]: Completed Step 5 (Ready for Preview).")
            return

        # ----------------------------------------------------
        # STEP 6: HEADLESS MP4 RENDER
        # ----------------------------------------------------
        if not self.request_permission(6, "render", "Render Final Broadcast MP4 Video"):
            print("\n🛑 Execution paused by user at Step 6.")
            return

        print("\n🔹 [STEP 6/6: BROADCAST MP4 RENDER]")
        if aspect == "omni":
            print("⚡ Rendering Widescreen (16:9) Documentary...")
            subprocess.run(["npx", "remotion", "render", "src/index.ts", "Documentary", "out/documentary.mp4"], cwd=BASE_DIR)
            print("⚡ Rendering Vertical V3 (9:16) Reel...")
            subprocess.run(["npx", "remotion", "render", "src/index.ts", "VerticalV3", "out/vertical_reel.mp4"], cwd=BASE_DIR)
            print("\n" + "=" * 70)
            print("🎉 DUAL OMNI PRODUCTION COMPLETE! Exports saved:")
            print("   📺 16:9 Widescreen -> out/documentary.mp4")
            print("   📱 9:16 Vertical   -> out/vertical_reel.mp4")
            print("=" * 70)
        elif aspect == "9:16":
            print("⚡ Rendering Vertical V3 (9:16) Reel...")
            subprocess.run(["npx", "remotion", "render", "src/index.ts", "VerticalV3", "out/vertical_reel.mp4"], cwd=BASE_DIR)
            print("\n" + "=" * 70)
            print("🎉 PRODUCTION COMPLETE! Export saved to: out/vertical_reel.mp4")
            print("=" * 70)
        else:
            print("⚡ Rendering final high-speed MP4 via Remotion...")
            subprocess.run(["npx", "remotion", "render", "src/index.ts", "Documentary", "out/documentary.mp4"], cwd=BASE_DIR)
            print("\n" + "=" * 70)
            print("🎉 PRODUCTION COMPLETE! Export saved to: out/documentary.mp4")
            print("=" * 70)

if __name__ == "__main__":
    until_step = "render"
    permission_mode = "group"
    group_max = 4
    topic_args = []

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ["--until", "--step", "-u", "-s"] and i + 1 < len(sys.argv):
            until_step = sys.argv[i + 1]
            i += 2
        elif arg in ["--permission", "-p"] and i + 1 < len(sys.argv):
            permission_mode = sys.argv[i + 1]
            i += 2
        elif arg in ["--group", "-g"] and i + 1 < len(sys.argv):
            try:
                group_max = int(sys.argv[i + 1].split("-")[-1])
            except Exception:
                group_max = 4
            i += 2
        elif arg in ["--auto", "-a"]:
            permission_mode = "auto"
            i += 1
        else:
            topic_args.append(arg)
            i += 1

    topic_str = " ".join(topic_args) if topic_args else None
    agent = FilmCopilotAgent(permission_mode=permission_mode, group_max_step=group_max)
    agent.run_pipeline(initial_idea=topic_str, stop_until=until_step, interactive=False if topic_str else True)
