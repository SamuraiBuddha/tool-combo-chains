@echo off
echo ==================================================
echo Tool Combo Chains - Installation Script
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/5] Installing package in development mode...
pip install -e .

echo.
echo [4/5] Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo Created .env file - please update with your passwords!
) else (
    echo .env file already exists - skipping
)

echo.
echo [5/5] Checking services...
docker-compose ps

echo.
echo ==================================================
echo Installation Complete!
echo ==================================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Start services: docker-compose up -d
echo 3. Initialize database: scripts\init-db.sh
echo 4. Add to Claude Desktop config (see docs\claude-desktop-config.md)
echo 5. Restart Claude Desktop
echo.
echo To test the MCP server:
echo   python -m tool_combo_chains
echo.
pause
