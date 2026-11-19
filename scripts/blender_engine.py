#!/usr/bin/env python3
"""
Blender Headless 3D Render Engine for Antigravity Video Studio.
Enables programmatic generation and background rendering of 3D titles,
product turntables, and cinematic 3D environments.
"""

import sys
import os
import subprocess
import shutil
import glob

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
BLENDER_PROJECTS_DIR = os.path.join(BASE_DIR, "projects", "blender-renders")
os.makedirs(BLENDER_PROJECTS_DIR, exist_ok=True)

BLENDER_SCENE_SCRIPTS = {
    "3d_chrome_title": """
import bpy
import math

# Clear existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# Scene setup
scene = bpy.context.scene
scene.render.engine = 'CYCLES' if bpy.context.preferences.addons.get('cycles') else 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 90

# Camera
cam_data = bpy.data.cameras.new("StudioCamera")
cam_obj = bpy.data.objects.new("StudioCamera", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Camera Animation (Crane Down & Dolly In)
cam_obj.location = (0, -6.5, 3.2)
cam_obj.rotation_euler = (math.radians(65), 0, 0)
cam_obj.keyframe_insert(data_path="location", frame=1)
cam_obj.location = (0, -4.8, 1.2)
cam_obj.rotation_euler = (math.radians(80), 0, 0)
cam_obj.keyframe_insert(data_path="location", frame=90)

# 3D Extruded Text
font_curve = bpy.data.curves.new(type="FONT", name="TitleCurve")
font_curve.body = "{TITLE_TEXT}"
font_curve.extrude = 0.15
font_curve.bevel_depth = 0.03
font_curve.align_x = 'CENTER'
font_curve.align_y = 'CENTER'

text_obj = bpy.data.objects.new("TitleObject", font_curve)
bpy.context.collection.objects.link(text_obj)
text_obj.location = (0, 0, 0)

# Metallic Chrome Material
mat = bpy.data.materials.new(name="ChromeMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs["Metallic"].default_value = 0.95
    principled.inputs["Roughness"].default_value = 0.15
    if "Base Color" in principled.inputs:
        principled.inputs["Base Color"].default_value = (0.75, 0.85, 1.0, 1.0)
text_obj.data.materials.append(mat)

# Studio Lighting (Three-Point)
# Key Light
key_light = bpy.data.lights.new(name="KeyLight", type='AREA')
key_light.energy = 450
key_obj = bpy.data.objects.new(name="KeyLight", object_data=key_light)
key_obj.location = (4, -4, 4)
bpy.context.collection.objects.link(key_obj)

# Rim Light
rim_light = bpy.data.lights.new(name="RimLight", type='SPOT')
rim_light.energy = 750
rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_light)
rim_obj.location = (-3, 3, 3)
bpy.context.collection.objects.link(rim_obj)

# Render Output
scene.render.filepath = "{OUTPUT_PATH}"
bpy.ops.render.render(write_still=True)
print("✅ Blender render complete: {OUTPUT_PATH}")
"""
}

def find_blender_binary():
    """Locates Blender executable across macOS, Windows, and Linux."""
    # 1. System PATH
    found = shutil.which("blender")
    if found:
        return found

    # 2. macOS Application Directory
    mac_paths = [
        "/Applications/Blender.app/Contents/MacOS/Blender",
        os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender")
    ]
    for p in mac_paths:
        if os.path.exists(p):
            return p

    # 3. Windows Standard Paths
    win_paths = glob.glob(r"C:\Program Files\Blender Foundation\Blender *\blender.exe")
    if win_paths:
        return win_paths[0]

    return None

def render_blender_scene(scene_type="3d_chrome_title", title_text="ANTIGRAVITY", output_filename="blender_scene.png"):
    blender_bin = find_blender_binary()
    out_path = os.path.join(BASE_DIR, "assets", "visuals", output_filename)
    script_path = os.path.join(BLENDER_PROJECTS_DIR, f"{scene_type}.py")

    template = BLENDER_SCENE_SCRIPTS.get(scene_type, BLENDER_SCENE_SCRIPTS["3d_chrome_title"])
    code = template.replace("{TITLE_TEXT}", title_text).replace("{OUTPUT_PATH}", out_path)

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"🎬 Generated Blender Python script at: {script_path}")

    if blender_bin:
        print(f"⚡ Launching headless Blender render via: {blender_bin}")
        cmd = [blender_bin, "-b", "-P", script_path]
        subprocess.run(cmd, cwd=BASE_DIR)
        print(f"✅ Rendered Blender 3D scene to: {out_path}")
        return out_path
    else:
        print("💡 Blender is not currently detected on this machine.")
        print("   To enable native 3D Blender rendering:")
        print("     • macOS:   brew install blender (or download from blender.org)")
        print("     • Windows: winget install BlenderFoundation.Blender")
        print("   Using Three.js 3D Procedural Engine inside Remotion as zero-overhead alternative.")
        return None

if __name__ == "__main__":
    stype = sys.argv[1] if len(sys.argv) > 1 else "3d_chrome_title"
    ttext = sys.argv[2] if len(sys.argv) > 2 else "FUTURE CINEMA"
    out_name = sys.argv[3] if len(sys.argv) > 3 else "scene_blender.png"
    render_blender_scene(stype, ttext, out_name)
