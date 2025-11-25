# 🚀 Как запускать команды Frontend

## ⚠️ ПРОБЛЕМА

Если вы находитесь в корневой директории `C:\DAM\Prime-EDMS` и запускаете:
```powershell
npm run test
npm run storybook
```

Вы получите ошибку:
```
npm error: Could not read package.json
```

## ✅ РЕШЕНИЕ 1: Использовать скрипт (РЕКОМЕНДУЕТСЯ)

Из корневой директории используйте скрипт `run-frontend.ps1`:

```powershell
# Из корневой директории C:\DAM\Prime-EDMS
.\run-frontend.ps1 test
.\run-frontend.ps1 storybook
.\run-frontend.ps1 dev
```

## ✅ РЕШЕНИЕ 2: Перейти в директорию frontend

```powershell
# Перейдите в frontend
cd frontend

# Теперь команды работают
npm run test
npm run storybook
npm run dev
```

## ✅ РЕШЕНИЕ 3: Использовать полный путь

```powershell
cd frontend; npm run test
cd frontend; npm run storybook
```

## 📋 Все доступные команды

### Через скрипт (из корня):
```powershell
.\run-frontend.ps1 dev              # Dev сервер
.\run-frontend.ps1 test              # Unit тесты
.\run-frontend.ps1 test:e2e          # E2E тесты
.\run-frontend.ps1 storybook         # Storybook
.\run-frontend.ps1 build             # Сборка
.\run-frontend.ps1 lint               # Линтинг
.\run-frontend.ps1 type-check        # Проверка типов
.\run-frontend.ps1 install           # Установка зависимостей
```

### Напрямую (из frontend/):
```powershell
cd frontend
npm run dev
npm run test
npm run test:e2e
npm run storybook
# и т.д.
```

## 💡 Совет: Создайте алиас

Добавьте в ваш PowerShell профиль (`$PROFILE`):

```powershell
function frontend { 
    param([string]$cmd)
    if ($cmd) {
        & "$PSScriptRoot\run-frontend.ps1" $cmd
    } else {
        cd "$PSScriptRoot\frontend"
    }
}
```

Тогда можно использовать:
```powershell
frontend test        # Запустит тесты
frontend             # Перейдет в frontend/
```

## ❓ Почему так?

`package.json` с npm скриптами находится в `frontend/`, а не в корне проекта. Корневая директория - это Django проект (Mayan EDMS), а frontend - это отдельный Vue.js проект.

