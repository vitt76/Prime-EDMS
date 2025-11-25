# 🚀 Quick Start Guide

## Первый запуск

1. **Установите зависимости:**
   ```bash
   cd frontend
   npm install
   ```

2. **Создайте файл окружения:**
   ```bash
   # Скопируйте пример (если файл не создан автоматически)
   # Windows PowerShell:
   Copy-Item .env.example .env
   
   # Linux/Mac:
   cp .env.example .env
   ```

3. **Запустите dev сервер:**
   ```bash
   npm run dev
   ```

   Приложение будет доступно по адресу: `http://localhost:5173`

## Проверка работоспособности

### Запуск тестов
```bash
# Unit тесты
npm run test

# E2E тесты (требует запущенный dev сервер)
npm run test:e2e
```

### Запуск Storybook
```bash
npm run storybook
```

Storybook будет доступен по адресу: `http://localhost:6006`

### Проверка типов
```bash
npm run type-check
```

### Линтинг
```bash
npm run lint
```

## Структура компонентов

Все компоненты находятся в `src/components/Common/`:

- **Button** - Кнопки с вариантами (primary, secondary, outline, ghost, danger)
- **Input** - Поля ввода с валидацией
- **Modal** - Модальные окна с анимациями
- **Card** - Карточки контента
- **Badge** - Бейджи статусов

## Использование компонентов

```vue
<template>
  <div>
    <Button variant="primary" @click="handleClick">
      Click me
    </Button>
    
    <Input 
      v-model="email" 
      label="Email" 
      type="email"
      :error="emailError"
    />
    
    <Modal v-model:is-open="isModalOpen" title="Example">
      <p>Modal content</p>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Button, Input, Modal } from '@/components/Common'

const email = ref('')
const emailError = ref('')
const isModalOpen = ref(false)

function handleClick() {
  console.log('Clicked!')
}
</script>
```

## Следующие шаги

1. ✅ Проект создан и настроен
2. ⏭️ Установите зависимости: `npm install`
3. ⏭️ Запустите dev сервер: `npm run dev`
4. ⏭️ Проверьте компоненты в Storybook: `npm run storybook`
5. ⏭️ Начните разработку новых компонентов согласно плану

## Troubleshooting

### Ошибка порта занят
Измените порт в `vite.config.ts` или используйте:
```bash
npm run dev -- --port 3000
```

### Ошибки TypeScript
Убедитесь, что все зависимости установлены:
```bash
npm install
npm run type-check
```

### Проблемы с Tailwind
Убедитесь, что `tailwind.config.js` правильно настроен и стили импортированы в `src/styles/index.css`


