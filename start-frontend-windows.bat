@echo off
echo Starting DAM Frontend in Windows...
echo.

cd /d "%~dp0frontend"

echo Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo Checking npm...
npm --version
if %errorlevel% neq 0 (
    echo ERROR: npm not found!
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Starting Vite dev server...
echo.
echo ====================================
echo FRONTEND WILL BE AVAILABLE AT:
echo http://localhost:5173/login
echo http://localhost:5173/test.html
echo ====================================
echo.
echo Press Ctrl+C to stop the server
echo.

npm run dev -- --host 0.0.0.0 --port 5173
