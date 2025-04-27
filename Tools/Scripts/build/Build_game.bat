@echo off
rem ─────────────────────────────────────────────────────────────────────────────
rem 1) Jump to project root (from Tools\Scripts\build)
cd /d "%~dp0\..\..\.."

echo Building Jammin' Eats executable...
echo.

rem ─────────────────────────────────────────────────────────────────────────────
rem 2) Point at your python.exe (no surrounding quotes in the SET)
set "PYTHON_PATH=C:\Program Files\Python\Python313\python.exe"

echo Installing PyInstaller if needed...
"%PYTHON_PATH%" -m pip install pyinstaller

echo Building console-mode executable…
"%PYTHON_PATH%" -m PyInstaller --onefile --console ^
  --hidden-import pytmx ^
  --hidden-import pytmx.util_pygame ^
  --add-data "assets;assets" ^
  --name "Jammin_Eats" ^
  main.py

echo.
if %errorlevel% neq 0 (
    echo.
    echo Build failed.
    echo Check that your assets and Database folders exist and contain the required files.
) else (
    echo.
    echo Build completed successfully!
    echo You can run dist\Jammin_Eats.exe from a Command Prompt to see any runtime output.
)

pause