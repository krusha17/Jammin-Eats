@echo off
echo ========================================
echo         JAMMIN' EATS BUILDER
echo ========================================
echo.

REM Set title for console window
title Building Jammin' Eats Game

REM Display version and timestamp
echo Build started at: %date% %time%
echo.

REM Create a clean build environment (optional - remove comment if you want to clean before building)
echo Cleaning up previous build files...
if exist build\ (
    rmdir /S /Q build
    echo - Removed build folder
)
if exist dist\ (
    rmdir /S /Q dist
    echo - Removed dist folder
)
echo.

REM Check for Python environment
echo Checking Python environment...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Make sure Python is installed and in your PATH.
    goto :error
)

REM Check for PyInstaller
echo Checking for PyInstaller...
python -c "import PyInstaller" > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller not found! Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller.
        goto :error
    )
)

REM Create the executable
echo.
echo Building executable with PyInstaller...
echo (This may take a few minutes)
echo.
python -m PyInstaller --onefile --windowed --add-data "assets;assets" --add-data "src;src" --hidden-import pygame --hidden-import pytmx --name "Jammin_Eats" main.py
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    goto :error
)

REM Build completed successfully
echo.
echo ========================================
echo       BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Your game executable is ready at:
echo %CD%\dist\Jammin_Eats.exe
echo.
echo To play your game, run the executable above.
echo.
goto :end

:error
echo.
echo ========================================
echo            BUILD FAILED!
echo ========================================
echo.
echo Please check the error messages above.
pause
exit /b 1

:end
echo Build process completed at: %date% %time%
echo Press any key to exit...
pause > nul
exit /b 0
