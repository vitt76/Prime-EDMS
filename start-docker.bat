@echo off
echo Starting Docker containers...
echo.

docker-compose up -d

echo.
echo Waiting for containers to start...
timeout /t 10 /nobreak > nul

echo.
echo Container status:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ====================================
echo BACKEND SHOULD BE AVAILABLE AT:
echo http://localhost:8080/
echo ====================================
echo.
echo To start frontend, run: start-frontend-windows.bat

pause
