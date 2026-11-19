#!/usr/bin/env python3
"""
AI Hardware, Disk Space & Cloud Advisor Agent
Automatically detects host hardware (Mac, Windows HP Gaming, Linux),
calculates free disk space, RAM, GPU acceleration (NVIDIA CUDA vs Metal vs CPU),
and advises the optimal zero-cost studio configuration before rendering.
"""

import sys
import os
import shutil
import platform
import subprocess

def get_disk_space_gb(path="."):
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "path": os.path.abspath(path),
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_free": round((free / total) * 100, 1)
        }
    except Exception:
        return {
            "path": path,
            "total_gb": 0.0,
            "used_gb": 0.0,
            "free_gb": 0.0,
            "percent_free": 0.0
        }

def scan_all_drives():
    """Scans all available storage volumes on Windows, Mac, or Linux to recommend optimal video render storage."""
    drives = []
    system = platform.system()

    if system == "Windows":
        import string
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                space = get_disk_space_gb(drive_path)
                drives.append({
                    "drive": f"{letter}:",
                    "path": drive_path,
                    "free_gb": space["free_gb"],
                    "total_gb": space["total_gb"],
                    "is_system": letter.upper() == "C"
                })
    elif system == "Darwin":
        # Root volume
        root_space = get_disk_space_gb("/")
        drives.append({
            "drive": "Macintosh HD",
            "path": "/",
            "free_gb": root_space["free_gb"],
            "total_gb": root_space["total_gb"],
            "is_system": True
        })
        # External volumes (guard against permission restrictions)
        vols_dir = "/Volumes"
        try:
            if os.path.exists(vols_dir):
                for v in os.listdir(vols_dir):
                    v_path = os.path.join(vols_dir, v)
                    if os.path.isdir(v_path) and not os.path.islink(v_path) and v != "Macintosh HD":
                        space = get_disk_space_gb(v_path)
                        drives.append({
                            "drive": v,
                            "path": v_path,
                            "free_gb": space["free_gb"],
                            "total_gb": space["total_gb"],
                            "is_system": False
                        })
        except Exception:
            pass
    else:
        # Linux
        root_space = get_disk_space_gb("/")
        drives.append({
            "drive": "/",
            "path": "/",
            "free_gb": root_space["free_gb"],
            "total_gb": root_space["total_gb"],
            "is_system": True
        })

    # Sort drives by free space descending
    drives.sort(key=lambda d: d["free_gb"], reverse=True)
    return drives

def recommend_storage_location():
    """Determines the best drive to store rendered 1080p/4K MP4 videos without filling OS drive."""
    drives = scan_all_drives()
    if not drives:
        return {"drive": ".", "path": "out", "reason": "Default workspace output folder"}

    # Find drive with maximum free space
    best_drive = drives[0]
    system_drive = next((d for d in drives if d.get("is_system")), drives[-1])

    warning = None
    if system_drive["free_gb"] < 15.0:
        warning = f"⚠️ Primary OS drive ({system_drive['drive']}) is tight on space ({system_drive['free_gb']} GB free). Highly recommend using an alternate drive!"

    target_dir = os.path.join(best_drive["path"], "OVE_Video_Renders") if best_drive["is_system"] is False else os.path.abspath("out")

    return {
        "recommended_drive": best_drive["drive"],
        "recommended_path": target_dir,
        "free_space_gb": best_drive["free_gb"],
        "drives": drives,
        "warning": warning
    }

def get_ram_gb():
    system = platform.system()
    try:
        if system == "Darwin":
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"]).decode().strip()
            return round(int(out) / (1024**3), 1)
        elif system == "Linux":
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        return round(kb / (1024**2), 1)
        elif system == "Windows":
            out = subprocess.check_output(["wmic", "OS", "get", "TotalVisibleMemorySize", "/Value"]).decode()
            for line in out.splitlines():
                if "=" in line:
                    return round(int(line.split("=")[1]) / (1024**2), 1)
    except Exception:
        pass
    return None

def detect_gpu():
    # 1. Check NVIDIA GPU via nvidia-smi
    try:
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=gpu_name,memory.total", "--format=csv,noheader,nounits"], stderr=subprocess.DEVNULL).decode().strip()
        if out:
            lines = out.splitlines()
            gpus = [line.split(",")[0].strip() for line in lines]
            return {"type": "NVIDIA_CUDA", "name": gpus[0], "status": "Ready for high-speed local AI & hardware render"}
    except Exception:
        pass

    # 2. Check Apple Silicon Metal
    if platform.system() == "Darwin" and platform.machine() in ["arm64", "aarch64"]:
        return {"type": "APPLE_SILICON_METAL", "name": "Apple M-Series GPU", "status": "Hardware Metal acceleration active"}

    # 3. Default CPU / Integrated Graphics
    return {"type": "INTEGRATED_CPU", "name": platform.processor() or "CPU", "status": "Standard compute (Recommend Cloud AI for generation)"}

def analyze_system():
    disk = get_disk_space_gb()
    ram = get_ram_gb()
    gpu = detect_gpu()
    os_name = f"{platform.system()} {platform.release()} ({platform.machine()})"

    # Safety Render Estimate
    # Average 1080p 30fps Remotion / MP4 export needs ~150-300MB
    safe_to_render = disk["free_gb"] >= 1.0

    # Optimal Strategy Selection
    if gpu["type"] == "NVIDIA_CUDA":
        strategy = "LOCAL_GPU_POWERHOUSE"
        recommendation = (
            "🚀 High-Performance NVIDIA Setup Detected!\n"
            "  • Run Fooocus locally for unlimited Midjourney-quality SDXL frames (0 API cost).\n"
            "  • Run Ollama (Llama 3.2 / Qwen 2.5) locally with CUDA acceleration.\n"
            "  • Export MP4s with NVIDIA NVENC hardware encoder."
        )
    elif gpu["type"] == "APPLE_SILICON_METAL":
        strategy = "APPLE_SILICON_STUDIO"
        recommendation = (
            "🍏 Apple Silicon Detected!\n"
            "  • Unified memory allows smooth local MLX / Draw Things image generation.\n"
            "  • Use Edge-TTS and Remotion for clean local documentary rendering."
        )
    else:
        strategy = "CLOUD_FREE_TIER_OPTIMAL"
        recommendation = (
            "☁️ Cloud-Assisted Mode Recommended (Keeps device cool and fast)!\n"
            "  • Use Google AI Pro (Jio Gemini 2.0 Flash) or OpenRouter Free Gateway for LLM planning.\n"
            "  • Use Imagen 3 / Pollinations.ai for photorealistic stills.\n"
            "  • Remotion will render clean 1080p video without overloading your CPU."
        )

    return {
        "os": os_name,
        "disk": disk,
        "ram_gb": ram,
        "gpu": gpu,
        "safe_to_render": safe_to_render,
        "strategy": strategy,
        "recommendation": recommendation
    }

def print_report():
    info = analyze_system()
    storage = recommend_storage_location()

    print("=" * 68)
    print("🤖 OVE & ANTIGRAVITY AI HARDWARE & MULTI-DRIVE STORAGE ADVISOR")
    print("=" * 68)
    print(f"🖥️  OS Platform:     {info['os']}")
    print(f"🧠 RAM Available:   {info['ram_gb']} GB" if info['ram_gb'] else "🧠 RAM:             Detected")
    print(f"🎮 GPU Compute:     {info['gpu']['name']} [{info['gpu']['type']}]")
    print(f"   Status:          {info['gpu']['status']}")
    print("-" * 68)
    print("💾 Detected Storage Volumes & Render Space:")
    for d in storage["drives"]:
        tag = "[OS Drive]" if d.get("is_system") else "[Secondary / External]"
        status_flag = "🟢 Plenty of Space" if d["free_gb"] > 40 else ("🟡 Moderate Space" if d["free_gb"] > 10 else "🔴 Low Space")
        print(f"   • {d['drive']:<16} : {d['free_gb']:>6.1f} GB free / {d['total_gb']:>6.1f} GB total  {tag:<22} {status_flag}")

    if storage.get("warning"):
        print(f"\n{storage['warning']}")

    print(f"\n📂 Recommended Render Output Location:")
    print(f"   -> {storage['recommended_path']} ({storage['free_space_gb']} GB available)")
    print("-" * 68)

    if not info["safe_to_render"]:
        print("⚠️  WARNING: Disk space is critically low (<1 GB free). Clean disk before rendering!")
    else:
        print("✅ Storage Check:   Sufficient space for video renders & audio assets.")
    print("-" * 68)
    print(f"🎯 Recommended Production Profile: [{info['strategy']}]")
    print(info["recommendation"])
    print("=" * 68)

if __name__ == "__main__":
    print_report()
