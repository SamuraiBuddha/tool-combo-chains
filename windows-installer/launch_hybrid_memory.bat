@echo off
REM ===============================================
REM Hybrid Memory Quick Launcher
REM Portable launcher for any directory
REM ===============================================

REM Check if running from installation directory
if exist "tool_combo_chains\mcp_hybrid_memory.py" (
    echo Starting from current directory...
    call start_hybrid_memory.bat
    exit /b 0
)

REM Check standard installation path
set INSTALL_PATH=%PROGRAMFILES%\Hybrid Memory Cognitive Stack
if exist "%INSTALL_PATH%\start_hybrid_memory.bat" (
    echo Starting from installation directory...
    cd /d "%INSTALL_PATH%"
    call start_hybrid_memory.bat
    exit /b 0
)

REM Check user profile installation
set USER_INSTALL_PATH=%USERPROFILE%\AppData\Local\Hybrid Memory Cognitive Stack
if exist "%USER_INSTALL_PATH%\start_hybrid_memory.bat" (
    echo Starting from user installation...
    cd /d "%USER_INSTALL_PATH%"
    call start_hybrid_memory.bat
    exit /b 0
)

REM Check if git repository is available
if exist ".git" (
    echo Starting from Git repository...
    call run_hybrid_memory.bat
    exit /b 0
)

REM If nothing found, show help
echo.
echo ========================================
echo   HYBRID MEMORY NOT FOUND
echo ========================================
echo.
echo Hybrid Memory installation not found in:
echo  • Current directory
echo  • %PROGRAMFILES%\Hybrid Memory Cognitive Stack
echo  • %USERPROFILE%\AppData\Local\Hybrid Memory Cognitive Stack
echo.
echo Please either:
echo  1. Run the installer: HybridMemory_Setup.exe
echo  2. Clone from Git: git clone https://github.com/SamuraiBuddha/tool-combo-chains.git
echo  3. Place this script in your Hybrid Memory directory
echo.
pause
exit /b 1
