# Start dump1090 and the ADS-B Tracker web app together
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$dump1090 = Join-Path $ProjectRoot "bin\dump1090\dump1090.exe"

if (-not (Test-Path $dump1090)) {
    Write-Host "ERROR: dump1090.exe not found at $dump1090" -ForegroundColor Red
    Write-Host "Run setup_sdr.ps1 first to get installation instructions." -ForegroundColor Yellow
    exit 1
}

Write-Host "=== Starting ADS-B Tracker ===" -ForegroundColor Cyan

# Start dump1090 in background
Write-Host "Starting dump1090..." -ForegroundColor Yellow
$dump1090Process = Start-Process -FilePath $dump1090 `
    -ArgumentList "--net", "--net-sbs-port", "30003", "--net-bo-port", "30005", "--gain", "-10" `
    -PassThru -WindowStyle Minimized

Write-Host "dump1090 started (PID: $($dump1090Process.Id))" -ForegroundColor Green

# Give dump1090 a moment to initialize
Start-Sleep -Seconds 2

# Start Python app
Write-Host "Starting web app..." -ForegroundColor Yellow
Write-Host "Open http://localhost:8080 in your browser" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

try {
    Set-Location $ProjectRoot
    python -m adsb_tracker
} finally {
    # Clean up dump1090 on exit
    Write-Host ""
    Write-Host "Stopping dump1090..." -ForegroundColor Yellow
    if (-not $dump1090Process.HasExited) {
        Stop-Process -Id $dump1090Process.Id -Force
    }
    Write-Host "All processes stopped." -ForegroundColor Green
}
