# Скрипт для перезапуска Docker контейнера Prime-EDMS
# После добавления volume mount для dynamic_search

Write-Host "Перезапуск контейнера Prime-EDMS..." -ForegroundColor Cyan

# Попытка 1: Через docker-compose напрямую
Write-Host "`nПопытка 1: docker-compose restart app" -ForegroundColor Yellow
try {
    docker-compose restart app
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Контейнер успешно перезапущен!" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "Ошибка: $_" -ForegroundColor Red
}

# Попытка 2: Через docker restart
Write-Host "`nПопытка 2: Поиск контейнера и перезапуск через docker restart" -ForegroundColor Yellow
try {
    $containerName = docker ps -a --format "{{.Names}}" | Select-String "prime-edms.*app" | Select-Object -First 1
    if ($containerName) {
        Write-Host "Найден контейнер: $containerName" -ForegroundColor Cyan
        docker restart $containerName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Контейнер успешно перезапущен!" -ForegroundColor Green
            exit 0
        }
    } else {
        Write-Host "Контейнер не найден" -ForegroundColor Red
    }
} catch {
    Write-Host "Ошибка: $_" -ForegroundColor Red
}

# Попытка 3: Через WSL
Write-Host "`nПопытка 3: Перезапуск через WSL" -ForegroundColor Yellow
try {
    $wslCommand = "cd /mnt/c/DAM/Prime-EDMS && docker-compose restart app"
    wsl bash -c $wslCommand
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Контейнер успешно перезапущен через WSL!" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "Ошибка WSL: $_" -ForegroundColor Red
}

Write-Host "`nНе удалось автоматически перезапустить контейнер." -ForegroundColor Red
Write-Host "Пожалуйста, выполните вручную:" -ForegroundColor Yellow
Write-Host "  1. Откройте Docker Desktop" -ForegroundColor White
Write-Host "  2. Найдите контейнер 'prime-edms-app' (или похожий)" -ForegroundColor White
Write-Host "  3. Нажмите кнопку 'Restart'" -ForegroundColor White
Write-Host "`nИли выполните в WSL терминале:" -ForegroundColor Yellow
Write-Host "  cd /mnt/c/DAM/Prime-EDMS" -ForegroundColor White
Write-Host "  docker-compose restart app" -ForegroundColor White

