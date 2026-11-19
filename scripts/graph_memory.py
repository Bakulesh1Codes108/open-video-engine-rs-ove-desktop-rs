#!/usr/bin/env python3
"""
Graphify Memory Engine for Antigravity Video Studio
Enables token-efficient context recall for AI Film & Documentary production.
"""

import json
import os
import sys
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_OUT_DIR = os.path.join(BASE_DIR, "graphify-out")
GRAPH_FILE = os.path.join(GRAPH_OUT_DIR, "graph.json")
REPORT_FILE = os.path.join(GRAPH_OUT_DIR, "GRAPH_REPORT.md")

os.makedirs(GRAPH_OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "assets", "audio"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "assets", "visuals"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "assets", "broll"), exist_ok=True)

def natural_sort_key(node):
    """Sorts scene IDs naturally so scene_2 precedes scene_10"""
    sid = node.get("id", "")
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', sid)]

def load_graph():
    if not os.path.exists(GRAPH_FILE):
        return {
            "version": "1.0.0",
            "updatedAt": datetime.utcnow().isoformat() + "Z",
            "project": {
                "id": "proj_01",
                "title": "Untitled AI Documentary",
                "fps": 30,
                "width": 1920,
                "height": 1080,
                "aspectRatio": "16:9",
                "fontFamily": "Inter, sans-serif"
            },
            "nodes": [],
            "edges": []
        }
    with open(GRAPH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_graph(data):
    data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    generate_report(data)

def generate_report(data):
    proj = data.get("project", {})
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    
    scenes = [n for n in nodes if n.get("type") == "Scene"]
    scenes.sort(key=natural_sort_key)
    entities = [n for n in nodes if n.get("type") == "Entity"]
    visuals = [n for n in nodes if n.get("type") == "VisualAsset"]
    audios = [n for n in nodes if n.get("type") == "AudioAsset"]

    lines = [
        f"# Graphify Film Memory Report: {proj.get('title', 'Documentary')}",
        f"*Generated: {data.get('updatedAt')}*",
        "",
        "## 1. Project Specifications",
        f"- **Resolution:** {proj.get('width', 1920)}x{proj.get('height', 1080)} @ {proj.get('fps', 30)} FPS",
        f"- **Aspect Ratio:** {proj.get('aspectRatio', '16:9')}",
        f"- **Total Scenes:** {len(scenes)}",
        f"- **Registered Entities:** {len(entities)}",
        f"- **Visual Assets:** {len(visuals)}",
        f"- **Audio Assets:** {len(audios)}",
        "",
        "## 2. Narrative Timeline & Continuity",
        "| Scene ID | Beat / Title | Duration (s) | Visual Style | Voiceover Status |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]

    for sc in scenes:
        props = sc.get("properties", {})
        sid = sc.get("id")
        beat = props.get("title", "Untitled Beat")
        dur = props.get("durationSeconds", 5)
        style = props.get("style", "Cinematic 35mm")
        vo_text = props.get("narration", "")
        vo_status = "Ready" if vo_text else "Missing"
        lines.append(f"| `{sid}` | {beat} | {dur}s | {style} | {vo_status} |")

    lines.append("")
    lines.append("## 3. Structural Graph Connections (Edges)")
    for edge in edges:
        lines.append(f"- `[{edge.get('from')}]` --**{edge.get('type')}**--> `[{edge.get('to')}]`")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def cmd_init(title="Autonomous AI Documentary"):
    data = load_graph()
    data["project"]["title"] = title
    data["nodes"] = []
    data["edges"] = []
    save_graph(data)
    print(f"Initialized Graphify memory for '{title}' at {GRAPH_FILE}")

def cmd_add_scene(scene_id, title, narration, duration_sec=5, visual_prompt="", motion_type="zoom-in"):
    data = load_graph()
    data["nodes"] = [n for n in data["nodes"] if n["id"] != scene_id]
    
    scene_node = {
        "id": scene_id,
        "type": "Scene",
        "properties": {
            "title": title,
            "narration": narration,
            "durationSeconds": float(duration_sec),
            "durationInFrames": int(float(duration_sec) * data["project"].get("fps", 30)),
            "visualPrompt": visual_prompt,
            "motionType": motion_type,
            "voiceoverAsset": f"assets/audio/{scene_id}.mp3",
            "visualAsset": f"assets/visuals/{scene_id}.jpg"
        }
    }
    data["nodes"].append(scene_node)
    
    # Natural sort scenes
    scenes = [n for n in data["nodes"] if n["type"] == "Scene"]
    scenes.sort(key=natural_sort_key)
    
    # Refresh TRANSITIONS_TO edges
    data["edges"] = [e for e in data["edges"] if e["type"] != "TRANSITIONS_TO"]
    for i in range(len(scenes) - 1):
        data["edges"].append({
            "from": scenes[i]["id"],
            "to": scenes[i+1]["id"],
            "type": "TRANSITIONS_TO",
            "properties": {"transition": "crossfade", "durationFrames": 15}
        })

    save_graph(data)
    print(f"Scene [{scene_id}] '{title}' added to Graphify memory.")

def cmd_get_compact_context():
    data = load_graph()
    proj = data.get("project", {})
    scenes = [n for n in data.get("nodes", []) if n.get("type") == "Scene"]
    scenes.sort(key=natural_sort_key)
    compact = {
        "project": proj.get("title"),
        "totalScenes": len(scenes),
        "timeline": [
            {
                "id": s["id"],
                "beat": s["properties"].get("title"),
                "duration": s["properties"].get("durationSeconds"),
                "narrationSummary": (s["properties"].get("narration", "")[:60] + "...") if len(s["properties"].get("narration", "")) > 60 else s["properties"].get("narration")
            }
            for s in scenes
        ]
    }
    print(json.dumps(compact, indent=2))

def cmd_export_remotion_timeline(output_json=None):
    data = load_graph()
    proj = data.get("project", {})
    scenes = [n for n in data.get("nodes", []) if n.get("type") == "Scene"]
    scenes.sort(key=natural_sort_key)

    timeline = {
        "project": proj.get("title", "Autonomous AI Documentary"),
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
                "motion": s["properties"].get("motionType", "zoom-in")
            }
            for s in scenes
        ]
    }
    out_path = output_json or os.path.join(BASE_DIR, "timeline.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    print(f"Exported Remotion timeline to: {out_path}")

# Direct API exports
init_graph = cmd_init
add_scene_node = cmd_add_scene
export_remotion_timeline = cmd_export_remotion_timeline
get_compact_context = cmd_get_compact_context

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 graph_memory.py [init | add-scene | compact-context | export-timeline | status]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        title = sys.argv[2] if len(sys.argv) > 2 else "Autonomous AI Documentary"
        cmd_init(title)
    elif cmd == "add-scene":
        if len(sys.argv) < 5:
            print("Usage: python3 graph_memory.py add-scene <id> <title> <narration> [duration_sec] [visual_prompt] [motion]")
            sys.exit(1)
        sid = sys.argv[2]
        title = sys.argv[3]
        narr = sys.argv[4]
        dur = sys.argv[5] if len(sys.argv) > 5 else 5
        vp = sys.argv[6] if len(sys.argv) > 6 else ""
        motion = sys.argv[7] if len(sys.argv) > 7 else "zoom-in"
        cmd_add_scene(sid, title, narr, dur, vp, motion)
    elif cmd == "compact-context":
        cmd_get_compact_context()
    elif cmd == "export-timeline":
        cmd_export_remotion_timeline()
    elif cmd == "status":
        data = load_graph()
        scenes = [n for n in data.get("nodes", []) if n.get("type") == "Scene"]
        print(f"Project: {data.get('project', {}).get('title')}")
        print(f"Total Scenes: {len(scenes)}")
        print(f"Graph file: {GRAPH_FILE}")
        print(f"Report: {REPORT_FILE}")
    else:
        print(f"Unknown command: {cmd}")
