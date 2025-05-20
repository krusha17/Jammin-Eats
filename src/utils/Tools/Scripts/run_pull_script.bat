@echo off
echo Pull changes from GitHub...
powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0pull_from_github.ps1"
pause