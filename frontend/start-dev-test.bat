@echo off
cd /d "%~dp0"
echo Starting Vite dev server...
echo Current directory: %CD%
echo.
call npm run dev -- --host 0.0.0.0 --port 5173 2>&1
echo.
echo Exit code: %ERRORLEVEL%
pause

