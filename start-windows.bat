@echo off
REM Windows batch script for Mayan EDMS management

if "%1"=="help" goto help
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="clean" goto clean

REM Default action: start
goto start

:help
echo Mayan EDMS Management Script for Windows
echo.
echo Usage: %0 [command]
echo.
echo Commands:
echo   start    - Start Mayan EDMS
echo   stop     - Stop Mayan EDMS
echo   restart  - Restart Mayan EDMS
echo   logs     - Show logs
echo   status   - Show status
echo   clean    - Clean all data (DANGER!)
echo   help     - Show this help
echo.
echo Examples:
echo   %0 start
echo   %0 logs
echo   %0 status
goto end

:start
echo 🚀 Starting Mayan EDMS...
wsl --distribution Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS && docker-compose -f docker-compose.simple.yml up -d"
echo.
echo ✅ Mayan EDMS started!
echo 🌐 Access at: http://localhost
echo.
echo Use '%0 status' to check status
echo Use '%0 logs' to view logs
goto end

:stop
echo 🛑 Stopping Mayan EDMS...
wsl --distribution Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS && docker-compose -f docker-compose.simple.yml down"
echo ✅ Mayan EDMS stopped
goto end

:restart
echo 🔄 Restarting Mayan EDMS...
wsl --distribution Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS && docker-compose -f docker-compose.simple.yml restart"
echo ✅ Mayan EDMS restarted
goto end

:logs
echo 📋 Showing Mayan EDMS logs (Ctrl+C to exit)...
wsl --distribution Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS && docker-compose -f docker-compose.simple.yml logs -f"
goto end

:status
echo 📊 Mayan EDMS Status:
echo.
wsl --distribution Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS && docker-compose -f docker-compose.simple.yml ps"
echo.
echo Docker containers:
wsl --distribution Ubuntu-22.04 -- docker ps --filter name=prime-edms --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
goto end

:clean
echo ⚠️  WARNING: This will delete ALL Mayan EDMS data!
echo.
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" goto end

echo 🧹 Cleaning all data...
wsl --distribution Ubuntu-22.04 -- bash -c "cd /mnt/c/Users/%USERNAME%/Projects/Prime-EDMS && docker-compose -f docker-compose.simple.yml down -v"
wsl --distribution Ubuntu-22.04 -- bash -c "docker volume rm prime-edms_app_data prime-edms_postgres_data prime-edms_redis_data prime-edms_rabbitmq_data 2>/dev/null || true"
echo ✅ All data cleaned
goto end

:end
