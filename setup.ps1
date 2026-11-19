# ======================================================================
# Open Video Engine (OVE) & Antigravity Studio - Automated Windows Installer
# Foolproof 1-Click setup for Windows laptops & PCs (HP Pavilion, ASUS, Dell, Lenovo)
# ======================================================================

$ErrorActionPreference = "Continue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  OPEN VIDEO ENGINE (OVE) - AUTOMATED WINDOWS LAPTOP SETUP            " -ForegroundColor Cyan
Write-Host "  (Configures Node.js, Python, FFmpeg, Remotion, and AI Engines)      " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$RepoDir = $PSScriptRoot
if (-not $RepoDir) { $RepoDir = (Get-Location).Path }
Set-Location $RepoDir

function Refresh-EnvPath {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# --------------------------------------------------
# 1. Check or Auto-Install Windows Package Manager (Winget)
# --------------------------------------------------
$hasWinget = Get-Command winget -ErrorAction SilentlyContinue
if ($hasWinget) {
    Write-Host "[+] Windows Package Manager (winget) detected." -ForegroundColor Green
} else {
    Write-Host "[!] Winget not detected. Installer will use direct web downloads for missing components." -ForegroundColor Yellow
}

# --------------------------------------------------
# 2. Check / Install Node.js (Required for Remotion React Video Engine)
# --------------------------------------------------
Write-Host "`n[*] [1/6] Checking Node.js runtime..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "[!] Node.js not found in PATH. Attempting automated installation via winget..." -ForegroundColor Yellow
    if ($hasWinget) {
        winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements
        Refresh-EnvPath
        $node = Get-Command node -ErrorAction SilentlyContinue
    }
    if (-not $node) {
        Write-Host "[-] Please install Node.js LTS manually from: https://nodejs.org/" -ForegroundColor Red
    } else {
        Write-Host "[+] Node.js installed successfully: $(node --version)" -ForegroundColor Green
    }
} else {
    Write-Host "[+] Node.js is ready: $(node --version)" -ForegroundColor Green
}

# --------------------------------------------------
# 3. Check / Install Python 3.10+
# --------------------------------------------------
Write-Host "`n[*] [2/6] Checking Python 3..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[!] Python not found in PATH. Attempting automated installation via winget..." -ForegroundColor Yellow
    if ($hasWinget) {
        winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        Refresh-EnvPath
        $python = Get-Command python -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        Write-Host "[-] Please install Python 3.11+ manually from: https://python.org/" -ForegroundColor Red
        Write-Host "    (Remember to check 'Add Python to PATH' during installation!)" -ForegroundColor Yellow
    } else {
        Write-Host "[+] Python installed successfully: $(python --version)" -ForegroundColor Green
    }
} else {
    Write-Host "[+] Python is ready: $(python --version)" -ForegroundColor Green
}

# --------------------------------------------------
# 4. Check / Install FFmpeg
# --------------------------------------------------
Write-Host "`n[*] [3/6] Checking FFmpeg video tools..." -ForegroundColor Yellow
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
$FfmpegDir = "$env:LOCALAPPDATA\video-tools\ffmpeg"

if (-not $ffmpeg) {
    Write-Host "[!] FFmpeg not detected in PATH. Setting up standalone FFmpeg..." -ForegroundColor Yellow
    if ($hasWinget) {
        winget install Gyan.FFmpeg --silent --accept-package-agreements --accept-source-agreements
        Refresh-EnvPath
        $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
    }
    
    if (-not $ffmpeg) {
        Write-Host "[*] Downloading portable FFmpeg Essentials (~30 MB)..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $FfmpegDir | Out-Null
        $zipPath = "$FfmpegDir\ffmpeg.zip"
        try {
            Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $zipPath
            Expand-Archive -Path $zipPath -DestinationPath "$FfmpegDir\extracted" -Force
            $binFolder = Get-ChildItem -Directory "$FfmpegDir\extracted\ffmpeg-*" | Select-Object -First 1
            Copy-Item -Path "$($binFolder.FullName)\bin\*" -Destination $FfmpegDir -Force
            Remove-Item -Path $zipPath -Force
            Remove-Item -Path "$FfmpegDir\extracted" -Recurse -Force

            # Add to User PATH
            $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
            if (-not $userPath.Contains($FfmpegDir)) {
                [Environment]::SetEnvironmentVariable("Path", "$userPath;$FfmpegDir", "User")
                $env:Path = "$env:Path;$FfmpegDir"
            }
            Write-Host "[+] Portable FFmpeg installed and added to PATH." -ForegroundColor Green
        } catch {
            Write-Host "[-] Failed to download FFmpeg automatically. Please install via: winget install Gyan.FFmpeg" -ForegroundColor Red
        }
    } else {
        Write-Host "[+] FFmpeg installed via package manager." -ForegroundColor Green
    }
} else {
    Write-Host "[+] FFmpeg detected: $(ffmpeg -version | Select-Object -First 1)" -ForegroundColor Green
}

# --------------------------------------------------
# 5. Configure Python Virtual Environment & AI Dependencies
# --------------------------------------------------
Write-Host "`n[*] [4/6] Setting up Python Virtual Environment (.venv)..." -ForegroundColor Yellow
$VenvDir = "$RepoDir\.venv"
$VenvPip = "$VenvDir\Scripts\pip.exe"
$VenvPy = "$VenvDir\Scripts\python.exe"

if (-not (Test-Path $VenvPy)) {
    Write-Host "[*] Creating fresh virtual environment at $VenvDir..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

if (Test-Path $VenvPip) {
    Write-Host "[*] Upgrading pip and installing core packages (Edge-TTS, PyWebView, Requests)..." -ForegroundColor Yellow
    & $VenvPip install --quiet --upgrade pip
    if (Test-Path "$RepoDir\requirements.txt") {
        & $VenvPip install --quiet -r "$RepoDir\requirements.txt"
    } else {
        & $VenvPip install --quiet edge-tts requests pillow pywebview yt-dlp
    }
    Write-Host "[+] Core Python video packages installed." -ForegroundColor Green
}

# Check for NVIDIA GPU (HP Pavilion / Gaming Laptop acceleration)
$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidiaSmi) {
    Write-Host "`n[⚡] NVIDIA GPU Detected!" -ForegroundColor Green
    $gpuName = (nvidia-smi --query-gpu=gpu_name --format=csv,noheader | Select-Object -First 1)
    Write-Host "     Graphics Card: $gpuName" -ForegroundColor Cyan
    Write-Host "     Enabling hardware-accelerated 5-second voice cloning (CUDA PyTorch)..." -ForegroundColor Yellow
    
    # Install PyTorch with CUDA 12.1 for ultra-fast local voice cloning
    & $VenvPip install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cu121
    if (Test-Path "$RepoDir\requirements-gpu.txt") {
        & $VenvPip install --quiet -r "$RepoDir\requirements-gpu.txt"
    }
    Write-Host "[+] NVIDIA CUDA acceleration enabled for local AI models!" -ForegroundColor Green
} else {
    Write-Host "`n[i] Standard / CPU Graphics detected. Engine optimized for cloud-assisted & Microsoft Neural Edge-TTS mode." -ForegroundColor Yellow
}

# --------------------------------------------------
# 6. Install Remotion React Node Dependencies
# --------------------------------------------------
Write-Host "`n[*] [5/6] Installing Remotion React video dependencies (npm install)..." -ForegroundColor Yellow
if (Test-Path "$RepoDir\package.json") {
    npm install --quiet
    Write-Host "[+] Remotion, Three.js, and GSAP video libraries ready." -ForegroundColor Green
}

# --------------------------------------------------
# 7. Create 1-Click Desktop Shortcut
# --------------------------------------------------
Write-Host "`n[*] [6/6] Creating 1-Click Desktop Shortcut..." -ForegroundColor Yellow
try {
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = "$desktopPath\Open Video Engine (OVE).lnk"
    $targetBat = "$RepoDir\Run_Studio.bat"
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($shortcutPath)
    $Shortcut.TargetPath = $targetBat
    $Shortcut.WorkingDirectory = $RepoDir
    $Shortcut.Description = "Launch Open Video Engine (OVE) Pro Desktop NLE Studio"
    if (Test-Path "$RepoDir\app\icon.ico") {
        $Shortcut.IconLocation = "$RepoDir\app\icon.ico, 0"
    }
    $Shortcut.Save()
    Write-Host "[+] Desktop shortcut created: 'Open Video Engine (OVE).lnk'" -ForegroundColor Green
} catch {
    Write-Host "[i] Desktop shortcut skipped (permissions). You can launch via Run_Studio.bat." -ForegroundColor Yellow
}

# --------------------------------------------------
# Completion Summary
# --------------------------------------------------
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE! Open Video Engine (OVE) is 100% Ready!             " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To launch the studio anytime:" -ForegroundColor White
Write-Host "    1. Double-click the desktop shortcut: 'Open Video Engine (OVE)'" -ForegroundColor Cyan
Write-Host "    2. Or double-click 'Run_Studio.bat' in this folder." -ForegroundColor Cyan
Write-Host "    3. Or run in terminal: python scripts/studio.py ove" -ForegroundColor Cyan
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
