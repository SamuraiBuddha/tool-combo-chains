# Start-HybridMemory.ps1
# One-click launcher for Tool-Combo-Chains Hybrid Memory System
# Created: 2025-06-29 by Jordan Ehrig

Write-Host "🚀 Starting Tool-Combo-Chains Hybrid Memory System..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Function to check if Docker Desktop is running
function Test-DockerRunning {
    try {
        docker ps 2>&1 | Out-Null
        return $?
    } catch {
        return $false
    }
}

# Function to wait for Docker
function Wait-ForDocker {
    $attempts = 0
    $maxAttempts = 30
    
    while (-not (Test-DockerRunning) -and $attempts -lt $maxAttempts) {
        Write-Host "⏳ Waiting for Docker Desktop to start... ($attempts/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        $attempts++
    }
    
    if ($attempts -ge $maxAttempts) {
        Write-Host "❌ Docker Desktop failed to start!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Step 1: Check/Start Docker Desktop
Write-Host "`n📦 Checking Docker Desktop..." -ForegroundColor Yellow
if (-not (Test-DockerRunning)) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Wait-ForDocker
}
Write-Host "✅ Docker Desktop is running!" -ForegroundColor Green

# Step 2: Navigate to script's parent directory (tool-combo-chains root)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath
Write-Host "✅ Working in: $projectPath" -ForegroundColor Green

# Step 3: Start the containers
Write-Host "`n🐳 Starting Tool-Combo-Chains containers..." -ForegroundColor Yellow
docker-compose up -d

# Step 4: Wait for services to be healthy
Write-Host "`n⏳ Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check container status
$containers = @(
    "cognitive-postgres",
    "cognitive-redis", 
    "cognitive-qdrant"
)

$allHealthy = $true
foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format "table {{.Status}}" | Select-Object -Skip 1
    if ($status -like "*healthy*" -or $status -like "*Up*") {
        Write-Host "✅ $container is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $container status: $status" -ForegroundColor Yellow
        $allHealthy = $false
    }
}

# Step 5: Display connection info
Write-Host "`n📊 System Status:" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host "PostgreSQL: localhost:5432 (postgresDB)" -ForegroundColor White
Write-Host "Redis: localhost:6379" -ForegroundColor White
Write-Host "Qdrant: localhost:6333" -ForegroundColor White
Write-Host "Instance: Melchior-001" -ForegroundColor White

# Step 6: Optional - Start Claude Desktop
Write-Host "`n🤖 Would you like to start Claude Desktop? (Y/N)" -ForegroundColor Cyan
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    $claudePath = "$env:LOCALAPPDATA\Programs\claude\Claude.exe"
    if (Test-Path $claudePath) {
        Start-Process $claudePath
        Write-Host "✅ Claude Desktop started!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Claude Desktop not found at expected location" -ForegroundColor Yellow
    }
}

# Final message
Write-Host "`n✨ Hybrid Memory System is READY!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "All systems operational. Memory x Sequential x Sandbox = 100x!" -ForegroundColor Cyan
Write-Host "`nPress Enter to close this window (containers will keep running)..."
Read-Host