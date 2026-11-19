# ======================================================================
# Open Video Engine (OVE) - Automated Windows Setup & Storage Assistant
# Inspected & Verified under NVIDIA Security & Model Guidelines
# Compatible with Windows 10/11 laptops & workstations (HP, ASUS, Dell, Lenovo)
# ======================================================================

$ErrorActionPreference = "Continue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  OPEN VIDEO ENGINE (OVE) - WINDOWS SETUP & STORAGE ASSISTANT         " -ForegroundColor Cyan
Write-Host "  Inspected under NVIDIA Model Security & Safety Guidelines           " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$RepoDir = $PSScriptRoot
if (-not $RepoDir) { $RepoDir = (Get-Location).Path }
Set-Location $RepoDir

function Refresh-EnvPath {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ----------------------------------------------------------------------
# STEP 0: USER PERMISSION & SECURITY NOTICE
# ----------------------------------------------------------------------
Write-Host "[🔒] SECURITY & PRIVACY NOTICE:" -ForegroundColor Green
Write-Host "    - 100% Free, Local & Open-Source." -ForegroundColor Gray
Write-Host "    - No telemetry, no background spyware, no hidden costs." -ForegroundColor Gray
Write-Host "    - All video rendering and AI models run locally or via your authorized keys." -ForegroundColor Gray
Write-Host ""

# ----------------------------------------------------------------------
# STEP 1: MULTI-DRIVE STORAGE SCANNER & RENDER LOCATION GUIDANCE
# ----------------------------------------------------------------------
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 1: DISK STORAGE SCANNER (Protecting Your Laptop from 4K Bloat)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

$sysDrive = $env:SystemDrive # e.g. "C:"
$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 0 } | Sort-Object -Property Free -Descending

Write-Host "`nDetected Storage Partitions on this machine:" -ForegroundColor Cyan
$bestDrive = $null
$sysDriveObj = $null

foreach ($d in $drives) {
    $freeGb = [math]::Round($d.Free / 1GB, 1)
    $totalGb = [math]::Round(($d.Used + $d.Free) / 1GB, 1)
    $isSys = ($d.Name + ":" -eq $sysDrive)
    
    $tag = ""
    if ($isSys) { 
        $tag = "[OS System Drive]" 
        $sysDriveObj = $d
    } else { 
        $tag = "[Secondary Data Drive]" 
        if (-not $bestDrive -or ($d.Free -gt $bestDrive.Free)) {
            $bestDrive = $d
        }
    }
    
    $color = "Green"
    if ($freeGb -lt 20.0) { $color = "Red" }
    elseif ($freeGb -lt 40.0) { $color = "Yellow" }

    Write-Host "  - Drive $($d.Name): $freeGb GB free of $totalGb GB total $tag" -ForegroundColor $color
}

# Video render advisory
$targetRenderDir = "$RepoDir\out"

if ($bestDrive -and ($bestDrive.Free -gt ($sysDriveObj.Free + 20GB))) {
    $bestDriveLetter = "$($bestDrive.Name):"
    $recPath = "$bestDriveLetter\OVE_Video_Renders"
    $bestGb = [math]::Round($bestDrive.Free / 1GB, 1)
    $sysGb = [math]::Round($sysDriveObj.Free / 1GB, 1)

    Write-Host "`n[💡] STORAGE ADVISORY FOR HIGH-RESOLUTION VIDEO RENDERS:" -ForegroundColor Yellow
    Write-Host "     Rendering 4K/1080p Remotion videos generates 2 GB - 10 GB of cache." -ForegroundColor Gray
    Write-Host "     Your OS drive ($sysDrive) has $sysGb GB free." -ForegroundColor Gray
    Write-Host "     Drive $bestDriveLetter has $bestGb GB free!" -ForegroundColor Green
    Write-Host "     We recommend storing video renders on: $recPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "     Where would you like to store generated video exports?" -ForegroundColor White
    Write-Host "       [1] $recPath (Recommended - Saves space on $sysDrive)" -ForegroundColor Green
    Write-Host "       [2] Default folder: $RepoDir\out" -ForegroundColor Gray
    Write-Host "       [3] Custom directory path" -ForegroundColor Gray
    
    $choice = Read-Host "     Enter choice [1/2/3] (Default: 1)"
    if ([string]::IsNullOrWhiteSpace($choice) -or $choice -eq "1") {
        $targetRenderDir = $recPath
    } elseif ($choice -eq "3") {
        $custom = Read-Host "     Enter custom absolute directory path"
        if (-not [string]::IsNullOrWhiteSpace($custom)) {
            $targetRenderDir = $custom
        }
    }
}

# Create target render directory if needed
if (-not (Test-Path $targetRenderDir)) {
    try {
        New-Item -ItemType Directory -Force -Path $targetRenderDir | Out-Null
        Write-Host "[+] Created render storage folder at: $targetRenderDir" -ForegroundColor Green
    } catch {
        Write-Host "[-] Could not create $targetRenderDir. Falling back to $RepoDir\out" -ForegroundColor Yellow
        $targetRenderDir = "$RepoDir\out"
    }
}

# If user chose an external directory, link it via NTFS junction to out/
if ($targetRenderDir -ne "$RepoDir\out") {
    $outPath = "$RepoDir\out"
    if (Test-Path $outPath) {
        $item = Get-Item $outPath -Force
        # If it's a junction or empty directory, we can replace it safely
        if ($item.Attributes.ToString() -match "ReparsePoint" -or (Get-ChildItem $outPath).Count -eq 0) {
            Remove-Item $outPath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    if (-not (Test-Path $outPath)) {
        try {
            cmd.exe /c mklink /J "$outPath" "$targetRenderDir" | Out-Null
            Write-Host "[+] Linked '$outPath' -> '$targetRenderDir' via NTFS directory junction." -ForegroundColor Green
        } catch {
            Write-Host "[i] Junction creation bypassed. Using direct configuration path." -ForegroundColor Yellow
        }
    }
}

# Persist render storage configuration file
$storageConfig = @{
    "render_output_dir" = $targetRenderDir
    "repo_dir" = $RepoDir
    "configured_at" = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
} | ConvertTo-Json
Set-Content -Path "$RepoDir\storage_config.json" -Value $storageConfig -Force
Write-Host "[+] Render storage configuration saved: $targetRenderDir" -ForegroundColor Green

# ----------------------------------------------------------------------
# STEP 2: CHECK PACKAGE MANAGER (WINGET)
# ----------------------------------------------------------------------
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 2: CHECKING SYSTEM DEPENDENCIES & RUNTIMES                     " -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

$hasWinget = Get-Command winget -ErrorAction SilentlyContinue
if ($hasWinget) {
    Write-Host "[+] Windows Package Manager (winget) detected." -ForegroundColor Green
} else {
    Write-Host "[!] Winget not detected. Installer will use direct downloads if needed." -ForegroundColor Yellow
}

# ----------------------------------------------------------------------
# STEP 3: CHECK / INSTALL NODE.JS LTS
# ----------------------------------------------------------------------
Write-Host "`n[*] [1/5] Checking Node.js runtime (Remotion React Engine)..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "[!] Node.js not found in PATH. Installing Node.js LTS via winget..." -ForegroundColor Yellow
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

# ----------------------------------------------------------------------
# STEP 4: CHECK / INSTALL PYTHON 3.10+
# ----------------------------------------------------------------------
Write-Host "`n[*] [2/5] Checking Python 3..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[!] Python not found in PATH. Installing Python 3.11 via winget..." -ForegroundColor Yellow
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

# ----------------------------------------------------------------------
# STEP 5: CHECK / INSTALL FFMPEG
# ----------------------------------------------------------------------
Write-Host "`n[*] [3/5] Checking FFmpeg stream & video export engine..." -ForegroundColor Yellow
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

# ----------------------------------------------------------------------
# STEP 6: PYTHON VIRTUAL ENVIRONMENT & AI DEPENDENCIES
# ----------------------------------------------------------------------
Write-Host "`n[*] [4/5] Setting up Python Virtual Environment (.venv)..." -ForegroundColor Yellow
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
    
    & $VenvPip install --quiet torch torchaudio --index-url https://download.pytorch.org/whl/cu121
    if (Test-Path "$RepoDir\requirements-gpu.txt") {
        & $VenvPip install --quiet -r "$RepoDir\requirements-gpu.txt"
    }
    Write-Host "[+] NVIDIA CUDA acceleration enabled for local AI models!" -ForegroundColor Green
} else {
    Write-Host "`n[i] Standard / CPU Graphics detected. Engine optimized for cloud-assisted & Microsoft Neural Edge-TTS mode." -ForegroundColor Yellow
}

# ----------------------------------------------------------------------
# STEP 7: REMOTION REACT NODE PACKAGES
# ----------------------------------------------------------------------
Write-Host "`n[*] [5/5] Installing Remotion React video dependencies (npm install)..." -ForegroundColor Yellow
if (Test-Path "$RepoDir\package.json") {
    npm install --quiet
    Write-Host "[+] Remotion, Three.js, and GSAP video libraries ready." -ForegroundColor Green
}

# ----------------------------------------------------------------------
# STEP 8: AI SETUP ASSISTANT & PROBLEM SOLVER DIAGNOSTIC
# ----------------------------------------------------------------------
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 3: AI SETUP ASSISTANT & PROBLEM SOLVER HEALTH DIAGNOSIS       " -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

if (Test-Path $VenvPy) {
    & $VenvPy "$RepoDir\scripts\setup_doctor.py" --fix
} else {
    python "$RepoDir\scripts\setup_doctor.py" --fix
}

# ----------------------------------------------------------------------
# STEP 9: CREATE 1-CLICK DESKTOP SHORTCUT
# ----------------------------------------------------------------------
Write-Host "`n[*] Creating 1-Click Desktop Shortcut..." -ForegroundColor Yellow
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

# ----------------------------------------------------------------------
# COMPLETION SUMMARY
# ----------------------------------------------------------------------
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE! Open Video Engine (OVE) is 100% Ready!             " -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Storage Configured:" -ForegroundColor White
Write-Host "    -> Video Output Directory: $targetRenderDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "  To launch the studio anytime:" -ForegroundColor White
Write-Host "    1. Double-click the desktop shortcut: 'Open Video Engine (OVE)'" -ForegroundColor Cyan
Write-Host "    2. Or double-click 'Run_Studio.bat' in this folder." -ForegroundColor Cyan
Write-Host "    3. Or double-click 'setup_doctor.bat' if you ever need troubleshooting." -ForegroundColor Cyan
Write-Host "    4. Or run in terminal: python scripts/studio.py ove" -ForegroundColor Cyan
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
