# Скрипт проверки и настройки доступа к Prime-EDMS
# Запускать от имени администратора для настройки проброса портов

Write-Host "=== Проверка Prime-EDMS ===" -ForegroundColor Cyan
Write-Host ""

# 1. Проверка работы в WSL
Write-Host "1. Проверка работы приложения в WSL..." -ForegroundColor Yellow
$wslCheck = wsl -d Ubuntu-22.04 -- bash -c "cd /mnt/c/DAM/Prime-EDMS && curl -s -o /dev/null -w '%{http_code}' http://localhost:8080"
if ($wslCheck -eq "200") {
    Write-Host "   [OK] Приложение работает в WSL (HTTP $wslCheck)" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Приложение не работает в WSL (HTTP $wslCheck)" -ForegroundColor Red
    Write-Host "   Запустите: wsl -d Ubuntu-22.04 -- bash -c 'cd /mnt/c/DAM/Prime-EDMS && docker compose up -d'" -ForegroundColor Yellow
    exit 1
}

# 2. Получение IP адреса WSL
Write-Host ""
Write-Host "2. Получение IP адреса WSL..." -ForegroundColor Yellow
$wslIP = (wsl -d Ubuntu-22.04 hostname -I).Trim().Split()[0]
if ($wslIP) {
    Write-Host "   [OK] WSL IP: $wslIP" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Не удалось получить IP адрес WSL" -ForegroundColor Red
    exit 1
}

# 3. Проверка проброса портов
Write-Host ""
Write-Host "3. Проверка проброса портов..." -ForegroundColor Yellow
$portForward = netsh interface portproxy show all | Select-String "8080"
if ($portForward) {
    Write-Host "   [OK] Проброс портов настроен:" -ForegroundColor Green
    Write-Host "   $portForward" -ForegroundColor Gray
} else {
    Write-Host "   [WARNING] Проброс портов не настроен" -ForegroundColor Yellow
    
    # Попытка настроить проброс портов
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($isAdmin) {
        Write-Host "   Настройка проброса портов..." -ForegroundColor Yellow
        netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0 2>$null
        netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$wslIP
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   [OK] Проброс портов настроен!" -ForegroundColor Green
        } else {
            Write-Host "   [ERROR] Не удалось настроить проброс портов" -ForegroundColor Red
        }
    } else {
        Write-Host "   [INFO] Для настройки проброса портов запустите скрипт от имени администратора" -ForegroundColor Yellow
    }
}

# 4. Проверка доступности из Windows
Write-Host ""
Write-Host "4. Проверка доступности из Windows..." -ForegroundColor Yellow

# Проверка через localhost
$localhostTest = Test-NetConnection -ComputerName localhost -Port 8080 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($localhostTest) {
    Write-Host "   [OK] localhost:8080 доступен" -ForegroundColor Green
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "   [OK] HTTP $($response.StatusCode) - Приложение отвечает!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== УСПЕХ! ===" -ForegroundColor Green
        Write-Host "Откройте в браузере: http://localhost:8080" -ForegroundColor Cyan
    } catch {
        Write-Host "   [WARNING] Порт открыт, но приложение не отвечает: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [WARNING] localhost:8080 недоступен" -ForegroundColor Yellow
}

# Проверка через IP WSL
Write-Host ""
Write-Host "5. Проверка через IP адрес WSL..." -ForegroundColor Yellow
$ipTest = Test-NetConnection -ComputerName $wslIP -Port 8080 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($ipTest) {
    Write-Host "   [OK] $wslIP`:8080 доступен" -ForegroundColor Green
    try {
        $response = Invoke-WebRequest -Uri "http://$wslIP`:8080" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "   [OK] HTTP $($response.StatusCode) - Приложение отвечает!" -ForegroundColor Green
        Write-Host ""
        Write-Host "=== УСПЕХ! ===" -ForegroundColor Green
        Write-Host "Откройте в браузере: http://$wslIP`:8080" -ForegroundColor Cyan
    } catch {
        Write-Host "   [WARNING] Порт открыт, но приложение не отвечает: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "=== РЕШЕНИЕ ===" -ForegroundColor Yellow
        Write-Host "Попробуйте открыть в браузере: http://$wslIP`:8080" -ForegroundColor Cyan
    }
} else {
    Write-Host "   [ERROR] $wslIP`:8080 недоступен" -ForegroundColor Red
    Write-Host ""
    Write-Host "=== РЕШЕНИЕ ===" -ForegroundColor Yellow
    Write-Host "1. Проверьте firewall Windows" -ForegroundColor Cyan
    Write-Host "2. Попробуйте открыть в браузере: http://$wslIP`:8080" -ForegroundColor Cyan
    Write-Host "3. Или настройте проброс портов (запустите скрипт от администратора)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== ИТОГ ===" -ForegroundColor Cyan
Write-Host "Приложение работает в WSL" -ForegroundColor Green
Write-Host "IP адрес WSL: $wslIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "Попробуйте открыть:" -ForegroundColor Yellow
Write-Host "  - http://localhost:8080 (если настроен проброс портов)" -ForegroundColor White
Write-Host "  - http://$wslIP`:8080 (напрямую по IP)" -ForegroundColor White

