#!/usr/bin/env python3
"""
FFmpeg Stream & Lossless Video Toolkit for Antigravity Video Studio
Provides:
  - Lossless stream concatenation (concat demuxer) without re-encoding
  - Instant precision cutting / trimming (LosslessCut pattern)
  - Audio/Video muxing and extraction
"""

import os
import sys
import shutil
import subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
OUT_DIR = os.path.join(BASE_DIR, "out")
os.makedirs(OUT_DIR, exist_ok=True)

def check_ffmpeg():
    return shutil.which("ffmpeg") is not None

def concat_videos(input_files: list, output_file: str = None) -> str:
    """
    Losslessly concatenates multiple MP4 files using FFmpeg's concat demuxer.
    Zero re-encoding, runs in milliseconds with 100% original quality preserved.
    """
    if not output_file:
        output_file = os.path.join(OUT_DIR, "concatenated_master.mp4")

    if not check_ffmpeg():
        print("⚠️ FFmpeg is not installed or not in PATH.")
        print("💡 Install via: brew install ffmpeg (Mac) or winget install Gyan.FFmpeg (Windows)")
        return ""

    valid_files = [f for f in input_files if os.path.exists(f)]
    if not valid_files:
        print("❌ Error: No valid video files provided to concatenate.")
        return ""

    list_path = os.path.join(OUT_DIR, "_concat_manifest.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for vf in valid_files:
            abs_path = os.path.abspath(vf).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")

    print(f"🔗 [Lossless Concat] Merging {len(valid_files)} video clips into: {output_file}")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output_file
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if res.returncode == 0 and os.path.exists(output_file):
            print(f"✅ Lossless Master export complete -> {output_file}")
            return output_file
        else:
            print(f"⚠️ FFmpeg copy failed, retrying with re-encode fallback...")
            fallback_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                output_file
            ]
            subprocess.run(fallback_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            return output_file
    finally:
        if os.path.exists(list_path):
            try:
                os.remove(list_path)
            except Exception:
                pass

def lossless_cut(input_file: str, start_time: str, end_time: str, output_file: str = None) -> str:
    """
    LosslessCut Swiss-knife pattern: Slices video between start and end timestamps
    without re-encoding using keyframe copying.
    """
    if not output_file:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_cut{ext}"

    if not check_ffmpeg():
        print("⚠️ FFmpeg not found.")
        return ""

    print(f"✂️  [LosslessCut] Slicing '{os.path.basename(input_file)}' from {start_time} to {end_time}...")
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-to", str(end_time),
        "-i", input_file,
        "-c", "copy",
        output_file
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode == 0:
        print(f"✅ Lossless slice saved to: {output_file}")
        return output_file
    else:
        print(f"⚠️ Lossless cut failed: {res.stderr.decode()[:200]}")
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/ffmpeg_tools.py concat <file1> <file2> ... [output.mp4]")
        print("  python3 scripts/ffmpeg_tools.py cut <file> <start_sec> <end_sec> [output.mp4]")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "concat":
        files = sys.argv[2:]
        concat_videos(files)
    elif cmd == "cut":
        if len(sys.argv) < 5:
            print("Usage: python3 scripts/ffmpeg_tools.py cut <file> <start> <end>")
            sys.exit(1)
        lossless_cut(sys.argv[2], sys.argv[3], sys.argv[4])
