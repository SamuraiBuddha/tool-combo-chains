@echo off
REM ========================================
REM Hybrid Memory Windows Installer Builder
REM ========================================

echo.
echo ========================================
echo   HYBRID MEMORY INSTALLER BUILDER
echo ========================================
echo.

REM Set working directory
cd /d "%~dp0"

REM Check if NSIS is installed
where makensis >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: NSIS (Nullsoft Scriptable Install System) is not installed or not in PATH!
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo Then add NSIS to your system PATH or run this script from NSIS directory.
    echo.
    pause
    exit /b 1
)

REM Create the icon
echo [1/4] Creating application icon...
powershell -ExecutionPolicy Bypass -File "create_icon.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Failed to create icon. Using default.
)
echo ✓ Icon created

REM Check if icon exists, create a dummy if not
if not exist "hybrid_memory_icon.ico" (
    echo Creating placeholder icon...
    copy /y nul "hybrid_memory_icon.ico" >nul
)

REM Build the installer
echo [2/4] Compiling installer with NSIS...
makensis hybrid_memory_installer.nsi
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to compile installer!
    pause
    exit /b 1
)
echo ✓ Installer compiled

REM Check if installer was created
if exist "HybridMemory_Setup.exe" (
    echo [3/4] Installer created successfully!
    
    REM Get file size
    for %%I in (HybridMemory_Setup.exe) do set FILESIZE=%%~zI
    set /a FILESIZE_MB=%FILESIZE% / 1024 / 1024
    
    echo ✓ File: HybridMemory_Setup.exe
    echo ✓ Size: %FILESIZE_MB% MB
    
    REM Optionally sign the installer (if certificate is available)
    if exist "code_signing_cert.pfx" (
        echo [4/4] Code signing installer...
        signtool sign /f "code_signing_cert.pfx" /t http://timestamp.digicert.com "HybridMemory_Setup.exe"
        echo ✓ Installer signed
    ) else (
        echo [4/4] Skipping code signing (no certificate found)
        echo ℹ Note: For distribution, consider code signing the installer
    )
    
    echo.
    echo ========================================
    echo   INSTALLER BUILD COMPLETE!
    echo ========================================
    echo.
    echo Installer: HybridMemory_Setup.exe
    echo Size: %FILESIZE_MB% MB
    echo.
    echo The installer includes:
    echo  • Hybrid Memory MCP Server
    echo  • Docker Compose configuration  
    echo  • PostgreSQL + Redis + Qdrant stack
    echo  • Automatic dependency checking
    echo  • Desktop and Start Menu shortcuts
    echo  • Uninstaller
    echo.
    echo Ready for distribution!
    echo.
    
    REM Ask if user wants to test the installer
    set /p test_installer="Test the installer now? (y/n): "
    if /i "%test_installer%"=="y" (
        echo.
        echo Launching installer...
        start "" "HybridMemory_Setup.exe"
    )
    
) else (
    echo ERROR: Installer was not created!
    pause
    exit /b 1
)

echo.
pause
