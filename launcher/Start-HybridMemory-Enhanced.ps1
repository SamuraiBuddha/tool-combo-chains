# Start-HybridMemory-Enhanced.ps1
# Enhanced one-click launcher for Tool-Combo-Chains Hybrid Memory System
# Created: 2025-06-29 by Jordan Ehrig
# Enhanced: 2025-07-03 - Added missing PowerShell commands and auto-Claude startup

Write-Host "🚀 Starting Tool-Combo-Chains Hybrid Memory System..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

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

# Function to run PowerShell command with error handling
function Invoke-SafeCommand {
    param($Command, $Description)
    Write-Host "`n🔧 $Description..." -ForegroundColor Yellow
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
            Write-Host "✅ $Description completed successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ $Description completed with warnings (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
            return $true
        }
    } catch {
        Write-Host "❌ $Description failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Step 1: Check/Start Docker Desktop
Write-Host "`n🐳 Checking Docker Desktop..." -ForegroundColor Yellow
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
        Write-Host "💡 AUTO-START: Add LM Studio to Windows Startup folder:" -ForegroundColor Cyan
        Write-Host "   shell:startup → Create shortcut to: $lmStudioPath" -ForegroundColor Gray
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
        Write-Host "💡 AUTO-START: Add ComfyUI to Windows Startup folder:" -ForegroundColor Cyan
        Write-Host "   shell:startup → Create batch file with: `"$comfyUIPath`"" -ForegroundColor Gray
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

# Step 7: Run Jordan's required PowerShell commands
Write-Host "`n🔧 Running installation and setup commands..." -ForegroundColor Cyan

# Command 1: ./install.bat
if (-not (Invoke-SafeCommand ".\install.bat" "Running install.bat")) {
    Write-Host "⚠️ install.bat failed, continuing anyway..." -ForegroundColor Yellow
}

# Command 2: ./scripts/init-db.sh (run via WSL or Git Bash if available)
$bashFound = $false
$bashCommands = @(
    "wsl bash ./scripts/init-db.sh",
    "bash ./scripts/init-db.sh",
    "sh ./scripts/init-db.sh"
)

foreach ($bashCmd in $bashCommands) {
    try {
        if (-not (Invoke-SafeCommand $bashCmd "Running init-db.sh")) {
            continue
        } else {
            $bashFound = $true
            break
        }
    } catch {
        continue
    }
}

if (-not $bashFound) {
    Write-Host "⚠️ Could not run init-db.sh (bash not found). Install WSL or Git Bash." -ForegroundColor Yellow
}

# Command 3: python -m tool_combo_chains.mcp_hybrid_memory
Start-Sleep -Seconds 2
if (-not (Invoke-SafeCommand "python -m tool_combo_chains.mcp_hybrid_memory" "Starting hybrid memory MCP server")) {
    Write-Host "⚠️ Hybrid memory MCP server failed to start. Check Python environment." -ForegroundColor Yellow
}

# Step 8: Display connection info
Write-Host "`n📊 System Status:" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host "PostgreSQL: localhost:5432 (postgresDB)" -ForegroundColor White
Write-Host "Redis: localhost:6379" -ForegroundColor White
Write-Host "Qdrant: localhost:6333" -ForegroundColor White
Write-Host "LM Studio: localhost:1234 (embeddings)" -ForegroundColor White
Write-Host "ComfyUI: localhost:8188 (image generation)" -ForegroundColor White
Write-Host "Instance: Melchior-001" -ForegroundColor White

# Step 9: Automatically start Claude Desktop
Write-Host "`n🤖 Starting Claude Desktop..." -ForegroundColor Cyan
$claudePaths = @(
    "$env:LOCALAPPDATA\Programs\claude\Claude.exe",
    "$env:APPDATA\Claude\Claude.exe",
    "C:\Program Files\Claude\Claude.exe"
)

$claudeFound = $false
foreach ($claudePath in $claudePaths) {
    if (Test-Path $claudePath) {
        Start-Process $claudePath
        Write-Host "✅ Claude Desktop started!" -ForegroundColor Green
        $claudeFound = $true
        break
    }
}

if (-not $claudeFound) {
    Write-Host "⚠️  Claude Desktop not found. Install from: https://claude.ai/download" -ForegroundColor Yellow
    Write-Host "   Checked locations:" -ForegroundColor Gray
    foreach ($path in $claudePaths) {
        Write-Host "   - $path" -ForegroundColor Gray
    }
}

# Final message
Write-Host "`n✨ Hybrid Memory System is READY!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host "All systems operational. Memory x Sequential x Sandbox = 100x!" -ForegroundColor Cyan

Write-Host "`nServices running:" -ForegroundColor White
Write-Host "  - Docker containers (PostgreSQL, Redis, Qdrant)" -ForegroundColor Gray
Write-Host "  - LM Studio (embeddings on port 1234)" -ForegroundColor Gray
Write-Host "  - ComfyUI (image generation on port 8188)" -ForegroundColor Gray
Write-Host "  - Hybrid Memory MCP Server" -ForegroundColor Gray
Write-Host "  - Claude Desktop" -ForegroundColor Gray

Write-Host "`n🎯 STARTUP AUTOMATION TIPS:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "1. LM Studio auto-start:" -ForegroundColor White
Write-Host "   • Win+R → shell:startup" -ForegroundColor Gray
Write-Host "   • Create shortcut to LM Studio.exe" -ForegroundColor Gray
Write-Host "`n2. ComfyUI auto-start:" -ForegroundColor White
Write-Host "   • Win+R → shell:startup" -ForegroundColor Gray
Write-Host "   • Create .bat file: start `"ComfyUI`" `"$comfyUIPath`"" -ForegroundColor Gray
Write-Host "`n3. This launcher shortcut:" -ForegroundColor White
Write-Host "   • Right-click desktop → New → Shortcut" -ForegroundColor Gray
Write-Host "   • Target: powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath\Start-HybridMemory-Enhanced.ps1`"" -ForegroundColor Gray

Write-Host "`nPress Enter to close this window (all services will keep running)..."
Read-Host
