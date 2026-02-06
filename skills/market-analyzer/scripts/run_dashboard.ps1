# Market Analyzer - Lancer le dashboard (Windows)
# Usage: .\run_dashboard.ps1  ou  .\run_dashboard.ps1 -Port 8080

param([int]$Port = 8080)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Windows: python ou py selon l'installation
$python = $null
if (Get-Command python -ErrorAction SilentlyContinue) { $python = "python" }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $python = "py" }
else {
    Write-Host "Python introuvable. Installez Python depuis https://www.python.org/ ou Microsoft Store." -ForegroundColor Red
    exit 1
}

Write-Host "Demarrage du dashboard sur http://localhost:$Port" -ForegroundColor Green
& $python dashboard_advanced.py --port $Port
