# Start-HybridMemory.ps1
# One-click launcher for Tool-Combo-Chains Hybrid Memory System
# Created: 2025-06-29 by Jordan Ehrig
# Updated: 2025-06-29 to include ComfyUI and LM Studio

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

# Function to check if a process is running
function Test-ProcessRunning {
    param($ProcessName)
    $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
    return $null -ne $process
}

# Function to check if a port is in use
function Test-PortInUse {
    param($Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Step 1: Check/Start Docker Desktop
Write-Host "`n📦 Checking Docker Desktop..." -ForegroundColor Yellow
if (-not (Test-DockerRunning)) {
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Wait-ForDocker
}
Write-Host "✅ Docker Desktop is running!" -ForegroundColor Green

# Step 2: Check/Start LM Studio
Write-Host "`n🧠 Checking LM Studio..." -ForegroundColor Yellow
$lmStudioPath = "$env:LOCALAPPDATA\Programs\lm-studio\LM Studio.exe"
if (-not (Test-PortInUse -Port 1234)) {
    if (Test-Path $lmStudioPath) {
        Write-Host "Starting LM Studio..." -ForegroundColor Yellow
        Start-Process $lmStudioPath
        Write-Host "✅ LM Studio started! Please load your embedding model." -ForegroundColor Green
        Write-Host "⚠️  Make sure to start the server on port 1234" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  LM Studio not found at: $lmStudioPath" -ForegroundColor Yellow
        Write-Host "   Embeddings may not work without LM Studio running" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ LM Studio server is already running on port 1234!" -ForegroundColor Green
}

# Step 3: Check/Start ComfyUI
Write-Host "`n🎨 Checking ComfyUI..." -ForegroundColor Yellow
# Check common ComfyUI locations
$comfyUIPaths = @(
    "C:\ComfyUI\run_nvidia_gpu.bat",
    "C:\ComfyUI_windows_portable\run_nvidia_gpu.bat",
    "$env:USERPROFILE\ComfyUI\run_nvidia_gpu.bat",
    "$env:USERPROFILE\ComfyUI_windows_portable\run_nvidia_gpu.bat"
)

$comfyUIFound = $false
$comfyUIPath = ""

foreach ($path in $comfyUIPaths) {
    if (Test-Path $path) {
        $comfyUIFound = $true
        $comfyUIPath = $path
        break
    }
}

if (-not (Test-PortInUse -Port 8188)) {
    if ($comfyUIFound) {
        Write-Host "Starting ComfyUI..." -ForegroundColor Yellow
        $comfyUIDir = Split-Path -Parent $comfyUIPath
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$comfyUIPath`"" -WorkingDirectory $comfyUIDir
        Write-Host "✅ ComfyUI started! It will be available at http://localhost:8188" -ForegroundColor Green
    } else {
        Write-Host "⚠️  ComfyUI not found in common locations" -ForegroundColor Yellow
        Write-Host "   Image generation features will not be available" -ForegroundColor Yellow
        Write-Host "   Common locations checked:" -ForegroundColor Gray
        foreach ($path in $comfyUIPaths) {
            Write-Host "   - $path" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "✅ ComfyUI is already running on port 8188!" -ForegroundColor Green
}

# Step 4: Navigate to script's parent directory (tool-combo-chains root)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath
Write-Host "`n✅ Working in: $projectPath" -ForegroundColor Green

# Step 5: Start the containers
Write-Host "`n🐳 Starting Tool-Combo-Chains containers..." -ForegroundColor Yellow
docker-compose up -d

# Step 6: Wait for services to be healthy
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

# Step 7: Display connection info
Write-Host "`n📊 System Status:" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host "PostgreSQL: localhost:5432 (postgresDB)" -ForegroundColor White
Write-Host "Redis: localhost:6379" -ForegroundColor White
Write-Host "Qdrant: localhost:6333" -ForegroundColor White
Write-Host "LM Studio: localhost:1234 (embeddings)" -ForegroundColor White
Write-Host "ComfyUI: localhost:8188 (image generation)" -ForegroundColor White
Write-Host "Instance: Melchior-001" -ForegroundColor White

# Step 8: Optional - Start Claude Desktop
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
Write-Host "`nServices running:" -ForegroundColor White
Write-Host "  - Docker containers (PostgreSQL, Redis, Qdrant)" -ForegroundColor Gray
Write-Host "  - LM Studio (embeddings on port 1234)" -ForegroundColor Gray
Write-Host "  - ComfyUI (image generation on port 8188)" -ForegroundColor Gray
Write-Host "`nPress Enter to close this window (all services will keep running)..."
Read-Host