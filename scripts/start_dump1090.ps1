# Start dump1090 with network output enabled
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$dump1090 = Join-Path $ProjectRoot "bin\dump1090\dump1090.exe"

if (-not (Test-Path $dump1090)) {
    Write-Host "ERROR: dump1090.exe not found at $dump1090" -ForegroundColor Red
    Write-Host "Run setup_sdr.ps1 first to get installation instructions." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting dump1090 with network output..." -ForegroundColor Cyan
Write-Host "  SBS output: port 30003" -ForegroundColor White
Write-Host "  dump1090 web UI: http://localhost:8081" -ForegroundColor White
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

& $dump1090 --interactive --net
