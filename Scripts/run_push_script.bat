@echo off
echo Push changes to GitHub...
powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0push_to_github.ps1"
pause