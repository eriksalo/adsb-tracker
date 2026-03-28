# ADS-B Tracker - SDR Setup Script
# Downloads dump1090 for Windows and provides Zadig instructions

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BinDir = Join-Path $ProjectRoot "bin\dump1090"

Write-Host "=== ADS-B Tracker - SDR Setup ===" -ForegroundColor Cyan
Write-Host ""

# Create bin directory
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
    Write-Host "[+] Created $BinDir" -ForegroundColor Green
}

# Download dump1090 Windows build
$dump1090Url = "https://github.com/MalcolmRobb/dump1090/archive/refs/heads/master.zip"
$zipPath = Join-Path $BinDir "dump1090-src.zip"

Write-Host ""
Write-Host "=== Step 1: dump1090 ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "You need a Windows build of dump1090. Options:" -ForegroundColor White
Write-Host ""
Write-Host "  Option A: Download pre-built dump1090.exe" -ForegroundColor Green
Write-Host "    1. Go to: https://github.com/antirez/dump1090" -ForegroundColor White
Write-Host "    2. Or search for 'dump1090 windows exe' on GitHub" -ForegroundColor White
Write-Host "    3. Place dump1090.exe in: $BinDir" -ForegroundColor White
Write-Host ""
Write-Host "  Option B: Use rtl_sdr tools + dump1090-mutability" -ForegroundColor Green
Write-Host "    1. Download RTL-SDR release: https://ftp.osmocom.org/binaries/windows/rtl-sdr/" -ForegroundColor White
Write-Host "    2. Extract and add to PATH" -ForegroundColor White
Write-Host ""

# Check if dump1090 already exists
$dump1090Exe = Join-Path $BinDir "dump1090.exe"
if (Test-Path $dump1090Exe) {
    Write-Host "[OK] dump1090.exe found at $dump1090Exe" -ForegroundColor Green
} else {
    Write-Host "[!] dump1090.exe NOT found at $dump1090Exe" -ForegroundColor Red
    Write-Host "    Please download and place it there before running the tracker." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Step 2: Zadig USB Driver ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "Your Nooelec SDR needs the WinUSB driver (not the default DVB-T driver)." -ForegroundColor White
Write-Host ""
Write-Host "  1. Download Zadig: https://zadig.akeo.ie/" -ForegroundColor White
Write-Host "  2. Run Zadig as Administrator" -ForegroundColor White
Write-Host "  3. Options -> List All Devices" -ForegroundColor White
Write-Host "  4. Select 'Bulk-In, Interface (Interface 0)' or 'RTL2838UHIDIR'" -ForegroundColor White
Write-Host "  5. Verify USB ID is 0BDA:2838 or 0BDA:2832" -ForegroundColor White
Write-Host "  6. Select 'WinUSB' as the target driver" -ForegroundColor White
Write-Host "  7. Click 'Install Driver' or 'Replace Driver'" -ForegroundColor White
Write-Host ""
Write-Host "  WARNING: Do NOT install to 'Bulk-In, Interface 1' (IR receiver)!" -ForegroundColor Red
Write-Host ""

Write-Host "=== Step 3: Verify ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "  After installing the driver, test with:" -ForegroundColor White
Write-Host "    .\bin\dump1090\dump1090.exe --interactive --net" -ForegroundColor Cyan
Write-Host ""
Write-Host "  You should see aircraft appearing in the terminal if planes are overhead." -ForegroundColor White
Write-Host ""
Write-Host "Setup guide complete." -ForegroundColor Green
