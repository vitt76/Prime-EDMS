@echo off
echo Starting DAM Frontend Dev Server...
echo.

cd /d %~dp0frontend

echo Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found! Please install Node.js from https://nodejs.org/
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
echo Open browser at: http://localhost:5173/login
echo.
npm run dev -- --host 0.0.0.0 --port 5173

pause
