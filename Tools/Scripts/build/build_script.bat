@echo off
rem ─────────────────────────────────────────────────────────────────────────────
rem 1) jump to project root (from Tools\Scripts\build)
cd /d "%~dp0\..\..\.."

echo Building Jammin' Eats executable...
echo.

rem ─────────────────────────────────────────────────────────────────────────────
rem 2) point at your python.exe
set "PYTHON_PATH=C:\Program Files\Python\Python313\python.exe"

echo Installing PyInstaller if needed...
"%PYTHON_PATH%" -m pip install pyinstaller

echo Building executable...
"%PYTHON_PATH%" -m PyInstaller --onefile --windowed ^
  --add-data "assets;assets" ^
  --add-data "Database;Database" ^
  --name "Jammin_Eats" main.py

echo.
if %errorlevel% neq 0 (
    echo Build failed.
    echo Check if your assets and Database folders exist and contain the required files.
) else (
    echo Build completed successfully!
    echo The executable can be found in the 'dist' folder.
    echo You can now share the Jammin_Eats.exe file with your music producer!
)

pause