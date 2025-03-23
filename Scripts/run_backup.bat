@echo off
echo Starting backup process...
powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0backup_script.ps1"
pause