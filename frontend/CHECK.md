# ✅ Проверка установки

## Проблема: команды запускаются из неправильной директории

Если вы находитесь в корневой директории `C:\DAM\Prime-EDMS`, команды нужно запускать из директории `frontend/`.

## Решение 1: Перейти в директорию frontend

```powershell
cd frontend
npm run storybook
npm run test
```

## Решение 2: Использовать полный путь

```powershell
cd frontend; npm run storybook
cd frontend; npm run test
```

## Решение 3: Использовать скрипт run.ps1

Из корневой директории:
```powershell
.\frontend\run.ps1 storybook
.\frontend\run.ps1 test
```

## Проверка установки зависимостей

1. Перейдите в директорию frontend:
   ```powershell
   cd frontend
   ```

2. Проверьте, установлены ли зависимости:
   ```powershell
   Test-Path node_modules
   ```

3. Если `node_modules` не существует, установите зависимости:
   ```powershell
   npm install
   ```

4. После установки попробуйте снова:
   ```powershell
   npm run storybook
   npm run test
   ```

## Возможные проблемы

### Ошибка: "Could not read package.json"
- **Причина**: Вы находитесь не в директории `frontend/`
- **Решение**: Перейдите в `cd frontend` перед запуском команд

### Ошибка: "Module not found"
- **Причина**: Зависимости не установлены
- **Решение**: Выполните `npm install` в директории `frontend/`

### Ошибка Storybook: "Cannot find module"
- **Причина**: Зависимости Storybook не установлены
- **Решение**: Выполните `npm install` - все зависимости должны установиться

