@echo off
REM ========================================
REM Hybrid Memory Cognitive Stack Launcher
REM Windows Installer Version
REM ========================================

title Hybrid Memory - Cognitive Amplification Stack

echo.
echo ========================================
echo   HYBRID MEMORY COGNITIVE STACK
echo   Windows Auto-Launcher v1.0
echo ========================================
echo.

REM Set working directory to script location
cd /d "%~dp0"
cd ..

REM Check if Docker is running
echo [1/5] Checking Docker status...
docker version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker is not running or not installed!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo ✓ Docker is running

REM Stop any existing containers
echo [2/5] Cleaning up existing containers...
docker-compose down >nul 2>&1
echo ✓ Cleaned up existing containers

REM Start PostgreSQL + Redis + Qdrant stack
echo [3/5] Starting database services...
docker-compose up -d --build
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start database services!
    pause
    exit /b 1
)
echo ✓ Database services started

REM Wait for services to be ready
echo [4/5] Waiting for services to initialize...
timeout /t 15 /nobreak >nul

REM Check if init-db.sql needs to be run
echo [5/5] Initializing database schema...
docker exec tool-combo-chains-postgres-1 psql -U cognitive -d cognitive -f /docker-entrypoint-initdb.d/init-db.sql >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Database schema initialized
) else (
    echo ⚠ Database schema may already exist
)

REM Start Python MCP server
echo.
echo ========================================
echo   STARTING HYBRID MEMORY MCP SERVER
echo ========================================
echo.
echo Server will start at: http://localhost:8080
echo Log files: logs/hybrid-memory.log
echo.
echo To stop: Press Ctrl+C or close this window
echo.

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start the MCP server with logging
python -m tool_combo_chains.mcp_hybrid_memory 2>&1 | tee logs/hybrid-memory.log

REM If we get here, the server stopped
echo.
echo ========================================
echo   HYBRID MEMORY SERVER STOPPED
echo ========================================
echo.
pause
