# =============================================================================
# START BACKEND - FastAPI Backend Launcher
# =============================================================================
# This script starts the FastAPI backend on port 8000
# =============================================================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Starting FastAPI Backend" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check requirements
if (-not (Test-Path "requirements.txt")) {
    Write-Host "[ERROR] requirements.txt not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Checking Python packages..." -ForegroundColor Yellow

# Optional: Install/update requirements
$install = Read-Host "Do you want to install/update requirements? (y/N)"
if ($install -eq "y" -or $install -eq "Y") {
    Write-Host "Installing requirements..." -ForegroundColor Gray
    python -m pip install -r requirements.txt
    Write-Host ""
}

# Get local IP
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "10.*" -or $_.IPAddress -like "192.168.*" }).IPAddress | Select-Object -First 1

Write-Host "Network Configuration:" -ForegroundColor Cyan
Write-Host "   * Local IP:    $localIP" -ForegroundColor White
Write-Host "   * Backend URL: http://${localIP}:8000" -ForegroundColor White
Write-Host "   * API Docs:    http://${localIP}:8000/docs" -ForegroundColor White
Write-Host ""

Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Start the server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
