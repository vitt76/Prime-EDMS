<!-- 263870e4-28a8-4905-b9b6-a46e0577a930 47728c77-f3bb-4974-bada-e9bc43e8da4a -->
# План стандартизации стилей: Tailwind + CSS-переменные

## Цель

Создать единую систему стилей с CSS-переменными как Single Source of Truth (SSOT) и интеграцией с Tailwind для консистентности и поддерживаемости.

## Архитектурные принципы

1. **CSS-переменные как SSOT**: Все значения цветов, типографики, spacing, shadows определяются в `index.css`
2. **Tailwind ссылается на переменные**: `tailwind.config.js` использует `var(--variable-name)` вместо хардкодных значений
3. **Tailwind для статики**: Layout, spacing, utilities через Tailwind классы
4. **CSS-переменные для динамики**: Runtime изменения, темы, сложные вычисления

## Этап 1: Аудит и дополнение CSS-переменных

### 1.1 Анализ используемых переменных

- Найти все используемые CSS-переменные в проекте (30 файлов)
- Выявить недостающие переменные:
  - `--color-surface`, `--color-border`, `--color-bg-1`
  - `--color-text`, `--color-text-secondary`, `--color-background`
  - `--font-size-*` (xs, sm, base, lg, xl, 2xl, 3xl)
  - `--radius-*` (sm, base, md, lg)
  - `--shadow-*` (sm, md, lg)

### 1.2 Обновление `frontend/src/styles/index.css`

- Добавить все недостающие переменные в `:root` и `.dark`
- Маппинг значений:
  - `--color-surface` → `--color-neutral-0`
  - `--color-border` → `--color-neutral-300`
  - `--color-bg-1` → `--color-neutral-50`
  - `--color-text` → `--color-neutral-900`
  - `--color-text-secondary` → `--color-neutral-600`
  - `--color-background` → `--color-neutral-50`
- Добавить типографику: `--font-size-xs` до `--font-size-3xl`
- Добавить радиусы: `--radius-sm`, `--radius-base`, `--radius-md`, `--radius-lg`
- Добавить тени: `--shadow-sm`, `--shadow-md`, `--shadow-lg`

## Этап 2: Интеграция Tailwind с CSS-переменными

### 2.1 Обновление `frontend/tailwind.config.js`

- Заменить хардкодные цвета на ссылки на CSS-переменные:
  ```js
  colors: {
    primary: {
      0: 'var(--color-primary-0)',
      50: 'var(--color-primary-50)',
      // ...
    }
  }
  ```

- Заменить fontSize на переменные:
  ```js
  fontSize: {
    xs: ['var(--font-size-xs)', { lineHeight: '1.5' }],
    // ...
  }
  ```

- Заменить borderRadius на переменные
- Заменить boxShadow на переменные
- Сохранить spacing, transitionDuration, transitionTimingFunction как есть (они не используются в CSS-переменных)

### 2.2 Проверка совместимости

- Убедиться, что Tailwind корректно обрабатывает `var()` в config
- Проверить работу dark mode через `.dark` класс

## Этап 3: Миграция компонентов

### 3.1 Приоритет 1: Common компоненты (уже используют Tailwind)

- Проверить корректность использования цветов
- Убедиться, что все цвета доступны через Tailwind классы
- Файлы: `Button.vue`, `Card.vue`, `Badge.vue`, `Input.vue`, `Modal.vue`, `Select.vue`

### 3.2 Приоритет 2: Компоненты с scoped styles

- `DataTable.vue`: Мигрировать простые стили на Tailwind классы
- Оставить CSS-переменные только для:
  - Сложных вычислений (scrollbar styles)
  - Динамических значений
  - Специфичных анимаций

### 3.3 Приоритет 3: Страницы

- `PublicationDetailPage.vue`: Мигрировать layout и spacing на Tailwind
- Оставить CSS-переменные для:
  - Skeleton animations
  - Сложных grid layouts с динамическими значениями
- Аналогично для других страниц (30 файлов)

## Этап 4: Документация и валидация

### 4.1 Создание Design Tokens документации

- Создать `frontend/docs/DESIGN-TOKENS.md`
- Описать все CSS-переменные и их использование
- Примеры использования Tailwind классов
- Guidelines когда использовать Tailwind vs CSS-переменные

### 4.2 Валидация изменений

- Проверить визуальную консистентность (light/dark mode)
- Убедиться, что все компоненты работают корректно
- Проверить производительность (Tailwind tree-shaking)

## Этап 5: Очистка и оптимизация

### 5.1 Удаление дублирования

- Убедиться, что нет хардкодных значений цветов в компонентах
- Удалить неиспользуемые CSS-переменные (если есть)

### 5.2 Оптимизация

- Проверить размер итогового CSS bundle
- Убедиться, что Tailwind правильно tree-shake неиспользуемые классы

## Критерии готовности

1. Все CSS-переменные определены в `index.css`
2. `tailwind.config.js` использует CSS-переменные через `var()`
3. Common компоненты используют Tailwind классы
4. Страницы мигрированы на Tailwind где возможно
5. CSS-переменные используются только для динамических значений
6. Документация создана и актуальна
7. Визуальная консистентность сохранена (light/dark mode)
8. Все тесты проходят

## Риски и митигация

**Риск 1**: Tailwind не поддерживает `var()` в config

- Митигация: Проверить в dev окружении перед массовой миграцией

**Риск 2**: Breaking changes в существующих компонентах

- Митигация: Поэтапная миграция, тестирование после каждого этапа

**Риск 3**: Увеличение размера bundle

- Митигация: Использовать Tailwind purge, проверять bundle size

## Порядок выполнения

1. Этап 1 (Аудит) - 1-2 часа
2. Этап 2 (Интеграция Tailwind) - 2-3 часа
3. Этап 3 (Миграция компонентов) - 1-2 дня (по приоритетам)
4. Этап 4 (Документация) - 2-3 часа
5. Этап 5 (Очистка) - 1-2 часа

**Общее время**: 2-3 рабочих дня

### To-dos

- [ ] Провести аудит всех используемых CSS-переменных в проекте (30 файлов), выявить недостающие переменные
- [ ] Обновить frontend/src/styles/index.css: добавить все недостающие переменные (--color-surface, --color-border, --font-size-*, --radius-*, --shadow-*) для light и dark mode
- [ ] Обновить frontend/tailwind.config.js: заменить хардкодные значения на ссылки на CSS-переменные через var() для colors, fontSize, borderRadius, boxShadow
- [ ] Проверить корректность работы Tailwind с CSS-переменными в dev окружении, убедиться что dark mode работает
- [ ] Проверить и обновить Common компоненты (Button, Card, Badge, Input, Modal, Select) - убедиться что используют Tailwind классы корректно
- [ ] Мигрировать DataTable.vue: простые стили на Tailwind, оставить CSS-переменные только для scrollbar и сложных случаев
- [ ] Мигрировать страницы (PublicationDetailPage, CollectionsPage и др.): layout/spacing на Tailwind, CSS-переменные для анимаций и динамики
- [ ] Создать frontend/docs/DESIGN-TOKENS.md с описанием всех CSS-переменных, примерами использования, guidelines
- [ ] Провести визуальную валидацию: проверить консистентность в light/dark mode, убедиться что все компоненты выглядят корректно
- [ ] Очистка: удалить дублирование, проверить bundle size, убедиться что Tailwind tree-shaking работает