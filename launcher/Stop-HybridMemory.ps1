# Stop-HybridMemory.ps1
# Gracefully stop Tool-Combo-Chains Hybrid Memory System
# Created: 2025-06-29 by Jordan Ehrig

Write-Host "🛑 Stopping Tool-Combo-Chains Hybrid Memory System..." -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow

# Navigate to script's parent directory (tool-combo-chains root)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

Write-Host "`n📦 Stopping containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "`n✅ All containers stopped!" -ForegroundColor Green
Write-Host "`nPress Enter to close..."
Read-Host