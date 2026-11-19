#!/usr/bin/env python3
"""
Automated PDF Guide Compiler for Antigravity Video Studio
Renders docs/guide.html into Antigravity-Video-Free-Guide.pdf across:
  - macOS (Google Chrome / Chromium / Edge headless)
  - Windows (Chrome / Edge / Chromium headless)
  - Linux (Chromium / Google Chrome headless)
"""

import os
import sys
import shutil
import subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
HTML_SOURCE = os.path.join(BASE_DIR, "docs", "guide.html")
PDF_TARGET = os.path.join(BASE_DIR, "Antigravity-Video-Free-Guide.pdf")

def find_browser_binary():
    # Common binary paths
    candidates = [
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        # Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    # System PATH lookup
    for name in ["google-chrome", "chrome", "msedge", "chromium", "chromium-browser"]:
        found = shutil.which(name)
        if found:
            return found

    return None

def compile_pdf(source_html: str = HTML_SOURCE, target_pdf: str = PDF_TARGET):
    print("=" * 68)
    print("📄 ANTIGRAVITY AUTOMATED PDF GUIDE COMPILER")
    print(f"📖 Source HTML: {source_html}")
    print(f"🎯 Target PDF:  {target_pdf}")
    print("=" * 68)

    if not os.path.exists(source_html):
        print(f"❌ Error: Source file not found: {source_html}")
        return False

    browser = find_browser_binary()
    if not browser:
        print("❌ Error: No compatible Chrome/Edge/Chromium browser found.")
        print("💡 Please install Google Chrome or Microsoft Edge to compile PDFs.")
        return False

    print(f"⚡ Browser Engine: {browser}")
    print("🚀 Rendering document to PDF via Headless Chromium...")

    user_data_dir = os.path.join(os.environ.get("TMPDIR", "/tmp"), "chrome-pdf-builder")
    cmd = [
        browser,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        f"--user-data-dir={user_data_dir}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={target_pdf}",
        source_html
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if os.path.exists(target_pdf) and os.path.getsize(target_pdf) > 1000:
            size_kb = round(os.path.getsize(target_pdf) / 1024, 1)
            print(f"✅ Compilation Succeeded! ({size_kb} KB written to {target_pdf})")
            return True
        else:
            print(f"⚠️ Compilation failed: {res.stderr.decode()[:300]}")
            return False
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return False

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else HTML_SOURCE
    tgt = sys.argv[2] if len(sys.argv) > 2 else PDF_TARGET
    compile_pdf(src, tgt)
