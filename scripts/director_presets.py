#!/usr/bin/env python3
"""
Director's Cinematic Presets & Prompt Guide for Antigravity Video Studio.
Bakes DaVinci Resolve color science (LUTs, Grain, 2.39:1 Letterbox)
and OpenCut pacing (J-Cuts, 4-Second Rule) directly into prompts.
"""

import sys
import json

CINEMATIC_PRESETS = {
    "netflix-doc": {
        "name": "Netflix High-End Documentary",
        "aspectRatio": "2.39:1",
        "letterbox": True,
        "colorGrade": "moody-documentary",
        "jCutFrames": 12,
        "lighting": "Chiaroscuro moody side-lighting, deep shadows with soft fill",
        "lens": "35mm prime lens, shallow depth of field, subtle film grain",
        "musicDucking": 0.16
    },
    "hollywood-epic": {
        "name": "Hollywood Blockbuster (Teal & Orange)",
        "aspectRatio": "2.39:1",
        "letterbox": True,
        "colorGrade": "teal-and-orange",
        "jCutFrames": 15,
        "lighting": "High-contrast rim lighting, anamorphic horizontal lens flare",
        "lens": "Anamorphic widescreen 50mm, rich saturated highlights",
        "musicDucking": 0.20
    },
    "historical-investigation": {
        "name": "Historical Investigation / Archive",
        "aspectRatio": "2.39:1",
        "letterbox": True,
        "colorGrade": "kodak-portra",
        "jCutFrames": 10,
        "lighting": "Warm tungsten museum lighting, atmospheric dust motes",
        "lens": "Vintage 1960s Leica glass, organic Kodachrome texture",
        "musicDucking": 0.14
    },
    "noir-crime": {
        "name": "True Crime / Neo-Noir Monochrome",
        "aspectRatio": "2.39:1",
        "letterbox": True,
        "colorGrade": "noir-monochrome",
        "jCutFrames": 14,
        "lighting": "Venetian blind hard shadows, high-contrast silhouette",
        "lens": "28mm wide lens, stark monochromatic contrast",
        "musicDucking": 0.15
    },
    "modern-explainer": {
        "name": "Vox / Modern Explainer",
        "aspectRatio": "16:9",
        "letterbox": False,
        "colorGrade": "clean",
        "jCutFrames": 6,
        "lighting": "High-key crisp studio lighting, neutral color accuracy",
        "lens": "Clean digital sensor, sharp graphics overlays",
        "musicDucking": 0.22
    },
    "aftereffects-motion": {
        "name": "Adobe After Effects Motion Graphics",
        "aspectRatio": "16:9",
        "letterbox": False,
        "colorGrade": "teal-and-orange",
        "jCutFrames": 8,
        "lighting": "Dynamic volumetric edge lighting, glowing neon highlights",
        "lens": "50mm prime with depth of field, 3D motion motion blur",
        "musicDucking": 0.20
    },
    "vidyo-repurpose": {
        "name": "vidyo.ai / Social Reel Repurpose",
        "aspectRatio": "9:16",
        "letterbox": False,
        "colorGrade": "clean",
        "jCutFrames": 4,
        "lighting": "Crisp ring-light studio illumination, vibrant skin tones",
        "lens": "24mm wide angle, vertical safe-zone composition",
        "musicDucking": 0.24
    },
    "vlog-pop": {
        "name": "KineMaster / InShot / VN Vibrant Vlog",
        "aspectRatio": "9:16",
        "letterbox": False,
        "colorGrade": "clean",
        "jCutFrames": 5,
        "lighting": "Bright natural daylight, punchy saturated colors",
        "lens": "35mm vlog perspective, snappy cuts and transitions",
        "musicDucking": 0.22
    }
}

def enhance_prompt(raw_concept: str, preset_name: str = "netflix-doc") -> dict:
    """
    Takes a raw concept and automatically applies DaVinci color directives
    and OpenCut cutting parameters.
    """
    preset = CINEMATIC_PRESETS.get(preset_name, CINEMATIC_PRESETS["netflix-doc"])

    visual_prompt = (
        f"Cinematic photorealistic documentary frame: {raw_concept}. "
        f"Cinematography: {preset['lens']}. "
        f"Lighting: {preset['lighting']}. "
        f"Color: {preset['colorGrade']} palette, film texture, 8k resolution, award-winning cinematography."
    )

    return {
        "preset": preset_name,
        "preset_title": preset["name"],
        "enhanced_visual_prompt": visual_prompt,
        "colorGrade": preset["colorGrade"],
        "letterbox": preset["letterbox"],
        "jCutFrames": preset["jCutFrames"],
        "musicDucking": preset["musicDucking"]
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Available Cinematic Presets:")
        for k, v in CINEMATIC_PRESETS.items():
            print(f"  • {k:25} -> {v['name']} ({v['colorGrade']}, Letterbox: {v['letterbox']})")
        print("\nUsage:")
        print("  python3 scripts/director_presets.py enhance '<raw scene idea>' [preset_name]")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "list":
        for k, v in CINEMATIC_PRESETS.items():
            print(f"  • {k:25} -> {v['name']}")
    elif cmd == "enhance":
        concept = sys.argv[2] if len(sys.argv) > 2 else "A scientist discovering a glowing bioluminescent deep-sea organism"
        preset = sys.argv[3] if len(sys.argv) > 3 else "netflix-doc"
        res = enhance_prompt(concept, preset)
        print(json.dumps(res, indent=2))
