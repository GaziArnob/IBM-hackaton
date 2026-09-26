# LegacyLift Converter launcher.
# First run: checks JDKs, Python and Git, creates the virtual environment and installs
# dependencies. Every run: starts the web app at http://localhost:8501.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Test-Jdk($major) {
    $roots = "$env:ProgramFiles\Eclipse Adoptium", "$env:ProgramFiles\Java", "$env:ProgramFiles\Microsoft"
    foreach ($root in $roots) {
        if (Test-Path $root) {
            foreach ($d in Get-ChildItem $root -Directory) {
                $release = Join-Path $d.FullName "release"
                if ((Test-Path $release) -and (Select-String -Path $release -Pattern "JAVA_VERSION=`"(1\.)?$major[\.`"]" -Quiet)) {
                    return $true
                }
            }
        }
    }
    return $false
}

Write-Host "`n== LegacyLift Converter ==`n" -ForegroundColor Cyan

# 1. Requirements -------------------------------------------------------------
$missing = @()
foreach ($jdk in 17, 21) {
    if (Test-Jdk $jdk) { Write-Host "[ok] JDK $jdk" -ForegroundColor Green }
    else { Write-Host "[missing] JDK $jdk" -ForegroundColor Red; $missing += "winget install --id EclipseAdoptium.Temurin.$jdk.JDK -e" }
}
if (Get-Command python -ErrorAction SilentlyContinue) { Write-Host "[ok] Python" -ForegroundColor Green }
else { Write-Host "[missing] Python" -ForegroundColor Red; $missing += "winget install --id Python.Python.3.12 -e" }
if (Get-Command git -ErrorAction SilentlyContinue) { Write-Host "[ok] Git" -ForegroundColor Green }
else { Write-Host "[missing] Git" -ForegroundColor Red; $missing += "winget install --id Git.Git -e" }

if ($missing.Count -gt 0) {
    Write-Host "`nInstall the missing tools, then close and reopen PowerShell and run this script again:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  $_" }
    Read-Host "`nPress Enter to exit"
    exit 1
}

# 2. Virtual environment (first run only) --------------------------------------
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "`nFirst run: creating the Python environment..." -ForegroundColor Cyan
    python -m venv .venv
    & $py -m pip install --quiet --upgrade pip
    & $py -m pip install --quiet -r requirements.txt
    Write-Host "[ok] Dependencies installed" -ForegroundColor Green
}

# 3. Start ------------------------------------------------------------------------
Write-Host "`nStarting the web app at http://localhost:8501  (press Ctrl+C here to stop)`n" -ForegroundColor Cyan
& $py -m streamlit run app.py --browser.gatherUsageStats false
