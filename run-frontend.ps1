# Скрипт для запуска frontend команд из корневой директории
# Использование: .\run-frontend.ps1 [команда]
# Примеры:
#   .\run-frontend.ps1 dev
#   .\run-frontend.ps1 test
#   .\run-frontend.ps1 storybook

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

$frontendDir = Join-Path $PSScriptRoot "frontend"

if (-not (Test-Path $frontendDir)) {
    Write-Host "❌ Ошибка: директория frontend не найдена!" -ForegroundColor Red
    Write-Host "Текущая директория: $PSScriptRoot" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path (Join-Path $frontendDir "package.json"))) {
    Write-Host "❌ Ошибка: package.json не найден в директории frontend!" -ForegroundColor Red
    exit 1
}

Push-Location $frontendDir

try {
    Write-Host "🚀 Запуск команды '$Command' в директории frontend..." -ForegroundColor Green
    Write-Host ""
    
    switch ($Command) {
        "dev" { npm run dev }
        "build" { npm run build }
        "test" { npm run test }
        "test:coverage" { npm run test:coverage }
        "test:e2e" { npm run test:e2e }
        "storybook" { npm run storybook }
        "lint" { npm run lint }
        "type-check" { npm run type-check }
        "install" { npm install }
        default {
            Write-Host "❌ Неизвестная команда: $Command" -ForegroundColor Red
            Write-Host ""
            Write-Host "Доступные команды:" -ForegroundColor Yellow
            Write-Host "  dev              - Запуск dev сервера"
            Write-Host "  build            - Сборка для production"
            Write-Host "  test             - Запуск unit тестов"
            Write-Host "  test:coverage    - Запуск тестов с coverage"
            Write-Host "  test:e2e         - Запуск E2E тестов"
            Write-Host "  storybook        - Запуск Storybook"
            Write-Host "  lint             - Проверка кода ESLint"
            Write-Host "  type-check       - Проверка типов TypeScript"
            Write-Host "  install          - Установка зависимостей"
            exit 1
        }
    }
} finally {
    Pop-Location
}

