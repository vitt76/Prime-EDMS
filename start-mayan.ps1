# Скрипт запуска Mayan EDMS для Windows с WSL2
# Использование: .\start-mayan.ps1

param(
    [switch]$Stop,
    [switch]$Restart,
    [switch]$Logs,
    [switch]$Status,
    [switch]$Clean
)

$WSL_DISTRO = "Ubuntu-22.04"
$PROJECT_PATH = "/mnt/c/Users/$env:USERNAME/PycharmProjects/Prime-EDMS"
$COMPOSE_FILE = "docker-compose.simple.yml"

function Write-Header {
    param([string]$Message)
    Write-Host "🔧 $Message" -ForegroundColor Cyan
}

function Execute-WSL {
    param([string]$Command)
    wsl --distribution $WSL_DISTRO -- bash -c "cd $PROJECT_PATH && $Command"
}

if ($Stop) {
    Write-Header "Остановка Mayan EDMS..."
    Execute-WSL "docker-compose -f $COMPOSE_FILE down"
    Write-Host "✅ Mayan EDMS остановлен" -ForegroundColor Green
    exit 0
}

if ($Restart) {
    Write-Header "Перезапуск Mayan EDMS..."
    Execute-WSL "docker-compose -f $COMPOSE_FILE down"
    Execute-WSL "docker-compose -f $COMPOSE_FILE up -d"
    Write-Host "✅ Mayan EDMS перезапущен" -ForegroundColor Green
    Write-Host "🌐 Доступен по адресу: http://localhost" -ForegroundColor Yellow
    exit 0
}

if ($Logs) {
    Write-Header "Просмотр логов Mayan EDMS..."
    Execute-WSL "docker-compose -f $COMPOSE_FILE logs -f"
    exit 0
}

if ($Status) {
    Write-Header "Статус контейнеров..."
    Execute-WSL "docker ps --filter name=prime-edms"
    exit 0
}

if ($Clean) {
    Write-Header "Очистка всех данных Mayan EDMS..."
    Write-Warning "Это действие удалит ВСЕ данные! Продолжить? (y/N)"
    $confirm = Read-Host
    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        Execute-WSL "docker-compose -f $COMPOSE_FILE down -v"
        Execute-WSL "docker volume rm prime-edms_app_data prime-edms_postgres_data prime-edms_redis_data prime-edms_rabbitmq_data 2>/dev/null || true"
        Write-Host "✅ Все данные удалены" -ForegroundColor Green
    } else {
        Write-Host "❌ Операция отменена" -ForegroundColor Red
    }
    exit 0
}

# Проверка наличия Docker
Write-Header "Проверка Docker..."
try {
    Execute-WSL "docker version" | Out-Null
} catch {
    Write-Error "Docker не запущен или не установлен в WSL2. Запустите setup-wsl.sh"
    exit 1
}

# Запуск Mayan EDMS
Write-Header "Запуск Mayan EDMS..."
Execute-WSL "docker-compose -f $COMPOSE_FILE up -d"

# Проверка статуса
Start-Sleep -Seconds 5
Write-Header "Проверка статуса..."
Execute-WSL "docker ps --filter name=prime-edms --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

Write-Host ""
Write-Host "✅ Mayan EDMS запущен!" -ForegroundColor Green
Write-Host "🌐 Доступен по адресу: http://localhost" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 Управление:" -ForegroundColor Cyan
Write-Host "  Остановить: .\start-mayan.ps1 -Stop"
Write-Host "  Перезапустить: .\start-mayan.ps1 -Restart"
Write-Host "  Логи: .\start-mayan.ps1 -Logs"
Write-Host "  Статус: .\start-mayan.ps1 -Status"
Write-Host "  Очистить данные: .\start-mayan.ps1 -Clean"
