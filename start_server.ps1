:: Script to start Contabiliza.IA (FastAPI) on local network
:: Run as Administrator on first run to create the firewall rule

Write-Host "Starting Contabiliza.IA (FastAPI) on local network..." -ForegroundColor Cyan

# Get local IPv4
$IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress

Write-Host "Server accessible at: http://${IP}:8000" -ForegroundColor Green
Write-Host "API docs: http://${IP}:8000/docs" -ForegroundColor Green

# Configure firewall (first run)
try {
    $firewallRule = Get-NetFirewallRule -DisplayName "Contabiliza.IA" -ErrorAction SilentlyContinue
    if (-not $firewallRule) {
        Write-Host "Creating firewall rule..." -ForegroundColor Yellow
        New-NetFirewallRule -DisplayName "Contabiliza.IA" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
        Write-Host "Firewall ready" -ForegroundColor Green
    }
} catch {
    Write-Host "Run as Administrator to create the firewall rule" -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
python backend\scripts\init_database.py

# Start server
Write-Host "`nServer started! Press Ctrl+C to stop.`n" -ForegroundColor Green
Write-Host "Devices on the network can access: http://${IP}:8000`n" -ForegroundColor Cyan

# Start Uvicorn with host 0.0.0.0 (allow external access)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
