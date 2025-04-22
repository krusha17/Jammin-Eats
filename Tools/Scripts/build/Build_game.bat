@echo off
REM === Jammin' Eats Build Script ===
echo Building JamminEats.exe...

REM Replace with your correct path to python.exe if needed
set PYTHON_EXE = "C:\Users\jerom\AppData\Local\Programs\Python\Python313\python.exe"

REM Run PyInstaller to create a one-file, no-console executable
%PYTHON_EXE% -m PyInstaller main.py --onefile --noconsole --name JamminEats

echo Done! Check the "dist" folder for JamminEats.exe
pause
