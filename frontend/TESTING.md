# 🧪 Руководство по тестированию

## Типы тестов

Проект использует два типа тестов:

### 1. Unit тесты (Vitest)
- **Команда:** `npm run test`
- **Директория:** `tests/unit/`
- **Что тестируется:** Компоненты, утилиты, stores
- **Среда:** jsdom (браузерная среда в Node.js)

### 2. E2E тесты (Playwright)
- **Команда:** `npm run test:e2e`
- **Директория:** `tests/e2e/`
- **Что тестируется:** Полные пользовательские сценарии
- **Среда:** Реальные браузеры (Chrome, Firefox, Safari)

## ⚠️ Важно

**Unit тесты и E2E тесты запускаются РАЗНЫМИ командами!**

```powershell
# ✅ Unit тесты (Vitest)
npm run test

# ✅ E2E тесты (Playwright)
npm run test:e2e

# ❌ НЕ запускайте E2E тесты через npm run test
# Они автоматически исключены из Vitest
```

## Запуск тестов

### Unit тесты

```powershell
cd frontend

# Запуск всех unit тестов
npm run test

# Запуск с UI
npm run test:ui

# Запуск с coverage
npm run test:coverage

# Запуск в watch режиме (автоматический перезапуск)
npm run test -- --watch
```

### E2E тесты

```powershell
cd frontend

# Запуск E2E тестов
# Playwright автоматически запустит dev сервер если нужно
npm run test:e2e

# Запуск с UI (интерактивный режим)
npm run test:e2e:ui

# Запуск в конкретном браузере
npx playwright test --project=chromium
```

## Структура тестов

```
tests/
├── unit/              # Unit тесты (Vitest)
│   ├── components/   # Тесты компонентов
│   └── utils/        # Тесты утилит
├── e2e/              # E2E тесты (Playwright)
│   └── *.spec.ts     # E2E сценарии
└── setup/            # Настройка тестов
    └── vitest.setup.ts
```

## Написание тестов

### Unit тест (пример)

```typescript
// tests/unit/components/Button.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/Common/Button.vue'

describe('Button', () => {
  it('renders correctly', () => {
    const wrapper = mount(Button, {
      slots: { default: 'Click me' }
    })
    expect(wrapper.text()).toBe('Click me')
  })
})
```

### E2E тест (пример)

```typescript
// tests/e2e/home.spec.ts
import { test, expect } from '@playwright/test'

test('home page loads correctly', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/DAM System/)
})
```

## Coverage

Для просмотра coverage unit тестов:

```powershell
npm run test:coverage
```

Отчет будет доступен в `coverage/index.html`

## Troubleshooting

### Ошибка: "Playwright Test did not expect test() to be called here"
**Причина:** Vitest пытается запустить Playwright тесты  
**Решение:** Убедитесь, что используете правильную команду:
- `npm run test` - только unit тесты
- `npm run test:e2e` - только E2E тесты

### E2E тесты не запускаются
**Причина:** Dev сервер не запущен  
**Решение:** Playwright автоматически запустит сервер, но можно запустить вручную:
```powershell
# Терминал 1
npm run dev

# Терминал 2
npm run test:e2e
```

### Тесты падают из-за импортов
**Причина:** Неправильные пути алиасов  
**Решение:** Убедитесь, что в `vitest.config.ts` и `vite.config.ts` настроены алиасы `@/`

## CI/CD

В GitHub Actions:
- Unit тесты запускаются автоматически
- E2E тесты запускаются отдельным job
- Coverage загружается в Codecov

См. `.github/workflows/ci.yml`

