@echo off
REM Windows batch script for Mayan EDMS setup
REM This script sets up WSL2 and Docker for Windows

echo 🚀 Setting up Mayan EDMS for Windows + WSL2...
echo.

REM Check if WSL2 is installed
wsl --list --verbose >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ WSL2 is not installed. Please install WSL2 first:
    echo    https://docs.microsoft.com/en-us/windows/wsl/install
    pause
    exit /b 1
)

echo ✅ WSL2 is installed
echo.

REM Install Ubuntu if not present
wsl --list | findstr /C:"Ubuntu" >nul
if %errorlevel% neq 0 (
    echo 📦 Installing Ubuntu for WSL2...
    wsl --install -d Ubuntu-22.04
    echo.
    echo ⚠️  Ubuntu installed. Please restart your computer and run this script again.
    pause
    exit /b 0
)

echo ✅ Ubuntu is installed
echo.

REM Set WSL2 as default version
echo 🔧 Setting WSL2 as default version...
wsl --set-default-version 2
echo ✅ WSL2 set as default
echo.

REM Start Ubuntu and run setup
echo 🐧 Starting Ubuntu and running setup script...
echo This will open a new Ubuntu window. Please run the following commands there:
echo.
echo cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS
echo ./setup-wsl.sh
echo.
echo Press any key to continue...
pause

REM Try to run setup automatically
echo Attempting automatic setup...
wsl --distribution Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS && chmod +x setup-wsl.sh && ./setup-wsl.sh"

echo.
echo ✅ Setup completed! Please restart WSL2:
echo    wsl --shutdown
echo    wsl
echo.
echo Then run: start-windows.bat
echo.
pause
