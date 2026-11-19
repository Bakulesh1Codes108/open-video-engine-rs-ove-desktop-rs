#!/usr/bin/env python3
"""
Renders the Ecosystem Capability Matrix into a High-Definition (HD) Retina PNG image.
"""

import os
import sys
import shutil
import subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
HTML_SOURCE = os.path.join(BASE_DIR, "docs", "capability_matrix.html")
IMG_TARGET = os.path.join(BASE_DIR, "assets", "images", "ecosystem_capability_matrix.png")
os.makedirs(os.path.dirname(IMG_TARGET), exist_ok=True)

def find_browser():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    for name in ["google-chrome", "chrome", "msedge", "chromium"]:
        found = shutil.which(name)
        if found:
            return found
    return None

def render_image():
    browser = find_browser()
    if not browser:
        print("❌ Error: No Chrome/Edge/Chromium browser found.")
        return False

    user_data_dir = os.path.join(os.environ.get("TMPDIR", "/tmp"), "chrome-img-builder")
    cmd = [
        browser,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        f"--user-data-dir={user_data_dir}",
        "--hide-scrollbars",
        "--window-size=1920,1080",
        "--device-scale-factor=2",
        f"--screenshot={IMG_TARGET}",
        HTML_SOURCE
    ]

    print(f"🚀 Rendering HD Matrix Image from {HTML_SOURCE}...")
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if os.path.exists(IMG_TARGET) and os.path.getsize(IMG_TARGET) > 5000:
        size_kb = round(os.path.getsize(IMG_TARGET) / 1024, 1)
        print(f"✅ HD Image Generated Successfully! ({size_kb} KB written to {IMG_TARGET})")
        return True
    else:
        print(f"⚠️ Screenshot failed: {res.stderr.decode()[:300]}")
        return False

if __name__ == "__main__":
    render_image()
