#!/usr/bin/env python3
"""
Prompt-Driven Graphify Memory Editor & Knowledge Cache
Allows natural language prompt editing of cached film knowledge, scenes,
character consistency, and cinematic styles without consuming storage (<15 KB).
"""

import sys
import os
import json
import re

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
GRAPH_FILE = os.path.join(BASE_DIR, "graphify-out", "graph.json")
TIMELINE_FILE = os.path.join(BASE_DIR, "timeline.json")

def load_graph():
    if not os.path.exists(GRAPH_FILE):
        return {"project": {}, "nodes": [], "edges": []}
    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_graph(data):
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    export_timeline(data)

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def export_timeline(data):
    proj = data.get("project", {})
    scenes = [n for n in data.get("nodes", []) if n.get("type") == "Scene"]
    scenes.sort(key=lambda x: natural_sort_key(x["id"]))

    timeline = {
        "project": proj.get("title", "Autonomous Documentary"),
        "fps": proj.get("fps", 30),
        "width": proj.get("width", 1920),
        "height": proj.get("height", 1080),
        "letterbox": proj.get("letterbox", True),
        "defaultColorGrade": proj.get("defaultColorGrade", "moody-documentary"),
        "scenes": [
            {
                "id": s["id"],
                "durationInFrames": s["properties"].get("durationInFrames", 150),
                "voiceover": s["properties"].get("voiceoverAsset"),
                "visual": s["properties"].get("visualAsset"),
                "subtitle": s["properties"].get("narration"),
                "motion": s["properties"].get("motionType", "zoom-in"),
                "colorGrade": s["properties"].get("colorGrade", proj.get("defaultColorGrade", "moody-documentary")),
                "jCutFrames": s["properties"].get("jCutFrames", 12)
            }
            for s in scenes
        ]
    }
    with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)

def edit_scene_field(scene_id: str, field: str, value: str):
    data = load_graph()
    found = False
    for node in data.get("nodes", []):
        if node.get("id") == scene_id and node.get("type") == "Scene":
            props = node.setdefault("properties", {})
            if field in ["duration", "durationSeconds"]:
                val_sec = float(value)
                props["durationSeconds"] = val_sec
                props["durationInFrames"] = int(val_sec * data["project"].get("fps", 30))
            elif field in ["subtitle", "narration"]:
                props["narration"] = value
            elif field in ["motion", "motionType"]:
                props["motionType"] = value
            elif field in ["colorGrade", "preset"]:
                props["colorGrade"] = value
            elif field in ["title"]:
                props["title"] = value
            else:
                props[field] = value
            found = True
            break

    if found:
        save_graph(data)
        print(f"✅ Updated [{scene_id}] field '{field}' -> '{value}' in Graphify cache.")
    else:
        print(f"❌ Scene [{scene_id}] not found in graph memory.")

def edit_with_natural_prompt(prompt_instruction: str):
    data = load_graph()
    instruction = prompt_instruction.strip()
    updated = False

    # 1. Global format switch (16:9 vs 9:16)
    if re.search(r"\b(?:switch|convert|change|set|make)\b.*?\b(?:9:16|vertical|reel|tiktok|short|shorts)\b", instruction, re.IGNORECASE):
        data["project"]["width"] = 1080
        data["project"]["height"] = 1920
        data["project"]["letterbox"] = False
        save_graph(data)
        print("📱 Project format converted to: 9:16 Vertical Reel (1080x1920) with Vertical V3 active.")
        return

    if re.search(r"\b(?:switch|convert|change|set|make)\b.*?\b(?:16:9|horizontal|widescreen|cinema|documentary|youtube)\b", instruction, re.IGNORECASE):
        data["project"]["width"] = 1920
        data["project"]["height"] = 1080
        data["project"]["letterbox"] = True
        save_graph(data)
        print("🎬 Project format converted to: 16:9 Widescreen Cinema (1920x1080) with 2.39:1 letterbox.")
        return

    # 2. Global style switch
    style_match = re.search(r"(?:switch|change|set)\s+(?:global\s+)?(?:style|preset|color\s*grade)\s+to\s+([a-zA-Z0-9_\-]+)", instruction, re.IGNORECASE)
    if style_match:
        new_style = style_match.group(1).lower()
        data["project"]["defaultColorGrade"] = new_style
        for n in data.get("nodes", []):
            if n.get("type") == "Scene":
                n.setdefault("properties", {})["colorGrade"] = new_style
        save_graph(data)
        print(f"🎬 Global film style updated to '{new_style}' across all scenes in memory graph.")
        return

    # 2. Target specific scene ID
    scene_match = re.search(r"\b(scene_\d+|scene\d+)\b", instruction, re.IGNORECASE)
    if not scene_match:
        print("💡 Tip: Specify which scene to edit (e.g. 'make scene_01 7 seconds')")
        return

    sid = scene_match.group(1).lower()
    if "_" not in sid:
        sid = sid.replace("scene", "scene_")

    target_scene = None
    for n in data.get("nodes", []):
        if n.get("id").lower() == sid and n.get("type") == "Scene":
            target_scene = n
            break

    if not target_scene:
        print(f"❌ Scene [{sid}] not found in Graphify memory.")
        return

    props = target_scene.setdefault("properties", {})

    # Check for duration edit
    dur_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:sec|seconds|s\b)", instruction, re.IGNORECASE)
    if dur_match:
        new_dur = float(dur_match.group(1))
        props["durationSeconds"] = new_dur
        props["durationInFrames"] = int(new_dur * data["project"].get("fps", 30))
        print(f"⏱️ Updated [{sid}] duration to {new_dur}s ({props['durationInFrames']} frames).")
        updated = True

    # Check for motion edit
    for m in ["zoom-in", "zoom-out", "pan-left", "pan-right", "static"]:
        if re.search(rf"\b{m}\b", instruction, re.IGNORECASE):
            props["motionType"] = m
            print(f"🎥 Updated [{sid}] motion to '{m}'.")
            updated = True
            break

    # Check for narration / subtitle edit
    sub_match = re.search(r"(?:subtitle|narration|text)\s+(?:(?:of|for)\s+\S+\s+)?(?:to|is|=|as)\s+[\"']?([^\"']+)[\"']?", instruction, re.IGNORECASE)
    if sub_match:
        new_sub = sub_match.group(1).strip()
        props["narration"] = new_sub
        print(f"📝 Updated [{sid}] subtitle to: '{new_sub}'")
        updated = True

    if updated:
        save_graph(data)
        print(f"💾 Changes successfully committed to Graphify knowledge cache & Remotion timeline!")
    else:
        print(f"⚠️ Could not parse specific edit parameters from: '{instruction}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/graph_editor.py prompt '<natural language edit command>'")
        print("  python3 scripts/graph_editor.py set <scene_id> <field> '<value>'")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "prompt":
        prompt_str = " ".join(sys.argv[2:])
        edit_with_natural_prompt(prompt_str)
    elif cmd == "set":
        if len(sys.argv) < 5:
            print("Usage: python3 scripts/graph_editor.py set <scene_id> <field> <value>")
            sys.exit(1)
        edit_scene_field(sys.argv[2], sys.argv[3], sys.argv[4])
