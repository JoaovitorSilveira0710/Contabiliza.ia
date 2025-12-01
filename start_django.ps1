# Start Django server for Contabiliza.IA (local network)
# Run as Administrator to auto-create firewall rule

Write-Host "Starting Contabiliza.IA (Django) on local network..." -ForegroundColor Cyan

# Resolve local IPv4
$IP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress

Write-Host "Server accessible at: http://${IP}:8000" -ForegroundColor Green
Write-Host "API base: http://${IP}:8000/api/" -ForegroundColor Green

# Configure firewall (first run)
try {
    $firewallRule = Get-NetFirewallRule -DisplayName "Contabiliza.IA (Django)" -ErrorAction SilentlyContinue
    if (-not $firewallRule) {
        Write-Host "Creating firewall rule for port 8000..." -ForegroundColor Yellow
        New-NetFirewallRule -DisplayName "Contabiliza.IA (Django)" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow | Out-Null
        Write-Host "Firewall ready" -ForegroundColor Green
    }
} catch {
    Write-Host "Run as Administrator to create firewall rule (optional)" -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Apply migrations
Write-Host "Applying database migrations..." -ForegroundColor Yellow
Push-Location "${PSScriptRoot}\django_backend"; 
python manage.py makemigrations; 
python manage.py migrate; 
Pop-Location

# Start Django server bound to all interfaces
Write-Host "`nDjango server started! Press Ctrl+C to stop.`n" -ForegroundColor Green
Write-Host "Devices on the network can access: http://${IP}:8000`n" -ForegroundColor Cyan

Push-Location "${PSScriptRoot}\django_backend"; 
python manage.py runserver 0.0.0.0:8000; 
Pop-Location
