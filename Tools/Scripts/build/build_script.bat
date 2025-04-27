@echo off
rem ─────────────────────────────────────────────────────────────────────────────
rem 1) Jump to project root (from Tools\Scripts\build)
cd /d "%~dp0\..\..\.."

echo Building Jammin' Eats executable...
echo.

rem ─────────────────────────────────────────────────────────────────────────────
rem 2) Point at your venv’s python.exe
set "PYTHON_PATH=%CD%\venv\Scripts\python.exe"

echo Installing PyInstaller if needed...
"%PYTHON_PATH%" -m pip install pyinstaller

echo Building console-mode executable…
"%PYTHON_PATH%" -m PyInstaller --onefile --console ^
  --add-data "assets;assets" ^
  --add-data "Database;Database" ^
  --hidden-import pytmx ^
  --name "Jammin_Eats" main.py

echo.
if %errorlevel% neq 0 (
    echo.
    echo Build failed.  
    echo Check that your assets and Database folders exist and contain the required files.
) else (
    echo.
    echo Build completed successfully!
    echo You can run the new exe from the 'dist' folder:  
    echo     cd dist && .\Jammin_Eats.exe
)

pause