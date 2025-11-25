# Скрипт для запуска команд из корневой директории проекта
param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

$frontendDir = Join-Path $PSScriptRoot "frontend"

if (-not (Test-Path $frontendDir)) {
    Write-Host "Ошибка: директория frontend не найдена!" -ForegroundColor Red
    exit 1
}

Push-Location $frontendDir

try {
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
            Write-Host "Неизвестная команда: $Command" -ForegroundColor Red
            Write-Host "Доступные команды: dev, build, test, test:coverage, test:e2e, storybook, lint, type-check, install"
            exit 1
        }
    }
} finally {
    Pop-Location
}

