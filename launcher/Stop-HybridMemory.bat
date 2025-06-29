@echo off
REM Stop-HybridMemory.bat
REM Stop Tool-Combo-Chains containers

echo Stopping Tool-Combo-Chains Hybrid Memory System...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Stop-HybridMemory.ps1"
pause