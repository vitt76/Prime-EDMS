@echo off
echo Starting DAM System...
echo.

echo Stopping old containers...
docker-compose down

echo.
echo Starting new containers...
docker-compose up -d

echo.
echo Waiting for containers to start...
timeout /t 10 /nobreak > nul

echo.
echo Checking container status...
docker ps

echo.
echo System should be running at:
echo - Backend: http://localhost:8080
echo - Frontend: Will start after running start-frontend-wsl.sh in WSL
echo.
echo To start frontend, run in WSL terminal:
echo   cd /mnt/host/c/DAM/Prime-EDMS
echo   ./start-frontend-wsl.sh

pause
