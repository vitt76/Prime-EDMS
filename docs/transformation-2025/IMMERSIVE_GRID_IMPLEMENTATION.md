# Immersive Grid Implementation Guide

**Дата:** 2025-01-XX  
**Версия:** 1.0  
**Статус:** Реализация Immersive Grid для DAM-системы

---

## 📋 Обзор

Реализован профессиональный "Immersive Grid" дизайн для DAM-системы в стиле Pinterest, Google Photos и Figma. Компоненты переработаны для создания "премиального" пользовательского опыта с фокусом на контент, а не на UI-элементы.

---

## 🎨 Ключевые Улучшения

### 1. Immersive Card Design (Visual)

#### ✅ Убраны границы и тени в покое
- **Было:** `border border-neutral-200`, `shadow-lg` всегда видимы
- **Стало:** Чистый вид без границ и теней в состоянии покоя
- **Hover:** Только легкий `scale-[1.02]` для интерактивности

#### ✅ Умный Aspect Ratio
- **Логотипы и SVG:** `object-contain` для полного отображения без обрезки
- **Фотографии:** `object-cover` для визуального воздействия
- **Определение:** Автоматическое на основе MIME-типа и имени файла

#### ✅ Metadata on Hover
- **Было:** Метаданные всегда видны в footer карточки
- **Стало:** Метаданные появляются только при hover с градиентной подложкой
- **Градиент:** `from-black/80 via-black/60 to-transparent` для читаемости на любом фоне

---

### 2. Interaction Models (Behavior)

#### ✅ Google Photos Style Selection
- **Чекбокс:** Круглый, в левом верхнем углу
- **Появление:** Только при hover или когда выбран
- **Выбранное состояние:** `scale-95` + синяя обводка (`ring-2 ring-primary-500`)
- **Анимация:** Плавное появление/исчезновение с `scale` эффектом

#### ✅ Quick Actions
- **Расположение:** Правый нижний угол при hover
- **Действия:** Download, Share, More (три точки)
- **Стиль:** Круглые кнопки с `backdrop-blur-sm` и `shadow-lg`
- **Анимация:** `scale-110` на hover, `scale-95` на active

---

### 3. Density Control (Architecture)

#### ✅ Prop `density` в `AssetGrid`
- **`'compact'`:** Меньше отступы (`gap-2`), больше колонок (до 8 на 2xl), квадратные превью
- **`'comfortable'`:** Больше отступы (`gap-4 sm:gap-6`), меньше колонок (до 6 на 2xl), 16:9 для фото

#### ✅ Layout Options
- **`'grid'`:** Стандартный CSS Grid (рекомендуется)
- **`'masonry'`:** CSS Columns fallback (для будущей реализации настоящего masonry)

---

## 💻 Компоненты

### `AssetCard.vue`

**Основные изменения:**

1. **Убраны границы и тени:**
```vue
<!-- Было -->
<div class="border border-neutral-200 shadow-lg ...">

<!-- Стало -->
<div class="..."> <!-- Чистый вид -->
```

2. **Metadata overlay на hover:**
```vue
<Transition>
  <div
    v-if="isHovered"
    class="absolute inset-x-0 bottom-0 
           bg-gradient-to-t from-black/80 via-black/60 to-transparent 
           px-3 py-3 pb-4"
  >
    <h3 class="text-sm font-semibold text-white truncate">
      {{ asset.label }}
    </h3>
    <!-- ... -->
  </div>
</Transition>
```

3. **Google Photos style checkbox:**
```vue
<div
  v-if="showCheckbox && (isHovered || isSelected)"
  class="absolute top-2 left-2 z-30"
>
  <div
    :class="[
      'w-6 h-6 rounded-full',
      isSelected
        ? 'bg-primary-500 ring-2 ring-white'
        : 'bg-white/90 backdrop-blur-sm shadow-md'
    ]"
  >
    <!-- Checkmark или пустой круг -->
  </div>
</div>
```

4. **Quick actions в правом нижнем углу:**
```vue
<div
  v-if="isHovered && !isSelected"
  class="absolute bottom-3 right-3 z-30 flex items-center gap-2"
>
  <!-- Download, Share, More buttons -->
</div>
```

5. **Умный object-fit:**
```typescript
const imageObjectFitClass = computed(() => {
  const mime = props.asset.mime_type || ''
  const label = props.asset.label?.toLowerCase() || ''
  
  // Логотипы и документы: contain
  if (mime.includes('svg') || label.includes('logo') || mime.includes('pdf')) {
    return 'object-contain'
  }
  
  // Фотографии: cover
  return 'object-cover'
})
```

---

### `AssetGrid.vue`

**Основные возможности:**

1. **Density control:**
```vue
<AssetGrid
  :assets="assets"
  density="comfortable"
  layout="grid"
/>
```

2. **Grid classes на основе density:**
```typescript
const gridClasses = computed(() => {
  if (props.density === 'compact') {
    return 'grid-cols-2 sm:grid-cols-3 ... xl:grid-cols-6 2xl:grid-cols-8 gap-2'
  } else {
    return 'grid-cols-1 sm:grid-cols-2 ... xl:grid-cols-5 2xl:grid-cols-6 gap-4 sm:gap-6'
  }
})
```

3. **Shift+Click range selection:**
```typescript
function handleAssetSelect(asset: Asset, index: number, event?: MouseEvent) {
  const isShiftClick = event?.shiftKey && lastSelectedIndex.value !== null
  
  if (isShiftClick) {
    // Select range
    const start = Math.min(lastSelectedIndex.value!, index)
    const end = Math.max(lastSelectedIndex.value!, index)
    for (let i = start; i <= end; i++) {
      assetStore.selectedAssets.add(props.assets[i].id)
    }
  } else {
    // Toggle single
    // ...
  }
}
```

---

### `useAssetSelection.ts` (Composable)

**Логика выбора в Composition API:**

```typescript
import { useAssetSelection } from '@/composables/useAssetSelection'

const assets = ref<Asset[]>([])
const {
  selectedAssets,
  isSelected,
  toggleSelection,
  selectRange,
  selectAll,
  clearSelection,
  handleKeydown
} = useAssetSelection(assets, {
  enableKeyboardShortcuts: true,
  onSelectionChange: (selectedIds) => {
    console.log('Selection changed:', selectedIds.size)
  }
})
```

**Использование в компоненте:**

```vue
<template>
  <div @keydown="handleKeydown">
    <AssetCard
      v-for="(asset, index) in assets"
      :key="asset.id"
      :is-selected="isSelected(asset.id)"
      @select="(asset, event) => toggleSelection(asset, index, event)"
    />
  </div>
</template>
```

**Keyboard shortcuts:**
- **Ctrl+A / Cmd+A:** Выбрать все
- **Delete / Backspace:** Удалить выбранные (требует обработчика в родителе)
- **Escape:** Очистить выбор

---

## 🔄 Интеграция с GalleryView

**Пример обновления `GalleryView.vue`:**

```vue
<template>
  <div class="gallery-view">
    <!-- ... toolbar ... -->
    
    <!-- Использование нового AssetGrid -->
    <AssetGrid
      :assets="assetStore.assets"
      :density="viewDensity"
      layout="grid"
      @asset-select="handleAssetSelect"
      @asset-open="handleAssetOpen"
      @asset-preview="handleAssetPreview"
      @asset-download="handleAssetDownload"
      @asset-share="handleAssetShare"
      @asset-delete="handleAssetDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AssetGrid from '@/components/DAM/AssetGrid.vue'
import { useAssetStore } from '@/stores/assetStore'

const assetStore = useAssetStore()
const viewDensity = ref<'compact' | 'comfortable'>('comfortable')

function handleAssetSelect(asset: Asset, index: number) {
  // Логика уже обработана в AssetGrid
  // Можно добавить дополнительную логику (например, analytics)
}

// ... другие handlers ...
</script>
```

---

## 🎯 Selection Model (Composition API)

### Логика выбора

**1. Одиночный выбор:**
```typescript
function toggleSelection(asset: Asset, index: number, event?: MouseEvent) {
  if (selectedAssets.value.has(asset.id)) {
    selectedAssets.value.delete(asset.id)
  } else {
    selectedAssets.value.add(asset.id)
  }
  lastSelectedIndex.value = index
}
```

**2. Диапазонный выбор (Shift+Click):**
```typescript
function selectRange(startIndex: number, endIndex: number) {
  const start = Math.min(startIndex, endIndex)
  const end = Math.max(startIndex, endIndex)
  
  for (let i = start; i <= end; i++) {
    const asset = assets.value[i]
    if (asset) {
      selectedAssets.value.add(asset.id)
    }
  }
  
  lastSelectedIndex.value = endIndex
}
```

**3. Выбрать все:**
```typescript
function selectAll() {
  assets.value.forEach(asset => {
    selectedAssets.value.add(asset.id)
  })
}
```

**4. Очистить выбор:**
```typescript
function clearSelection() {
  selectedAssets.value.clear()
  lastSelectedIndex.value = null
}
```

---

## 📐 Стили и Классы

### Density: Compact

```css
/* Grid */
grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8
gap-2

/* Card */
aspect-square  /* Все карточки квадратные */
```

### Density: Comfortable

```css
/* Grid */
grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6
gap-4 sm:gap-6

/* Card */
aspect-video  /* Для фото */
aspect-square  /* Для логотипов/документов */
```

---

## 🚀 Использование

### Базовое использование

```vue
<template>
  <AssetGrid
    :assets="assets"
    density="comfortable"
  />
</template>
```

### С обработчиками событий

```vue
<template>
  <AssetGrid
    :assets="assetStore.assets"
    density="comfortable"
    @asset-select="handleSelect"
    @asset-open="handleOpen"
    @asset-delete="handleDelete"
  />
</template>

<script setup lang="ts">
function handleSelect(asset: Asset, index: number) {
  console.log('Selected:', asset.label, 'at index', index)
}

function handleOpen(asset: Asset) {
  router.push(`/dam/assets/${asset.id}`)
}

function handleDelete(asset: Asset) {
  // Показать confirmation modal
  // Вызвать assetStore.deleteAsset(asset.id)
}
</script>
```

### С keyboard shortcuts

```vue
<template>
  <div @keydown="selection.handleKeydown">
    <AssetGrid
      :assets="assets"
      @asset-delete="handleBulkDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { useAssetSelection } from '@/composables/useAssetSelection'

const assets = ref<Asset[]>([])
const selection = useAssetSelection(assets, {
  enableKeyboardShortcuts: true
})

function handleBulkDelete(asset: Asset) {
  // Обработка удаления (может быть bulk, если выбрано несколько)
  const selectedIds = Array.from(selection.selectedAssets.value)
  if (selectedIds.length > 1) {
    // Bulk delete
  } else {
    // Single delete
  }
}
</script>
```

---

## 🎨 Визуальные Состояния

### Rest State (Покой)
- ✅ Нет границ
- ✅ Нет теней
- ✅ Чистый вид, фокус на контенте

### Hover State
- ✅ Легкий `scale-[1.02]`
- ✅ Появляется checkbox (левый верхний угол)
- ✅ Появляются quick actions (правый нижний угол)
- ✅ Появляется metadata overlay (снизу с градиентом)

### Selected State
- ✅ `scale-95` (карточка уменьшается)
- ✅ `ring-2 ring-primary-500` (синяя обводка)
- ✅ Checkbox всегда виден с галочкой
- ✅ Quick actions скрыты (чтобы не мешать)

### Dragging State
- ✅ `opacity-50`
- ✅ `scale-95`
- ✅ `ring-2 ring-primary-400 ring-dashed`

---

## 🔧 Кастомизация

### Изменение цветов

В `AssetCard.vue` можно изменить:
- **Primary color:** Заменить `primary-500` на другой цвет из Tailwind
- **Checkbox:** Изменить `bg-primary-500` на другой цвет
- **Ring color:** Изменить `ring-primary-500` на другой цвет

### Изменение размеров

В `AssetGrid.vue` можно настроить:
- **Gap:** Изменить `gap-2` (compact) или `gap-4 sm:gap-6` (comfortable)
- **Columns:** Изменить количество колонок в `gridClasses`

### Изменение анимаций

В `AssetCard.vue` можно настроить:
- **Transition duration:** Изменить `duration-200`, `duration-300`
- **Scale values:** Изменить `scale-[1.02]`, `scale-95`, `scale-110`

---

## 📊 Производительность

### Оптимизации

1. **Lazy Loading:** Используется `IntersectionObserver` для загрузки изображений только при видимости
2. **Virtual Scrolling:** Для больших списков (100+ элементов) рекомендуется использовать виртуальную прокрутку
3. **Reactivity:** Используется `Set` для эффективного управления выбором

### Рекомендации

- Для списков < 100 элементов: используйте обычный `AssetGrid`
- Для списков >= 100 элементов: используйте виртуальную прокрутку (см. `GalleryView.vue`)

---

## 🐛 Известные Ограничения

1. **Masonry Layout:** Текущая реализация использует CSS Columns как fallback. Для настоящего masonry рекомендуется использовать библиотеку `vue-masonry-css` или `@vueuse/core`.

2. **Touch Devices:** На мобильных устройствах hover эффекты не работают. Рекомендуется показывать metadata всегда на touch-устройствах.

3. **Keyboard Navigation:** Требуется дополнительная реализация для полноценной навигации с клавиатуры (Tab, Arrow keys).

---

## 📝 TODO

- [ ] Реализовать настоящий Masonry layout через библиотеку
- [ ] Добавить touch-friendly режим (показывать metadata всегда на мобильных)
- [ ] Улучшить keyboard navigation (Tab, Arrow keys, Home, End)
- [ ] Добавить drag selection (lasso tool) для выбора множества файлов
- [ ] Оптимизировать для очень больших списков (1000+ элементов)

---

**Автор:** Lead Frontend Engineer  
**Дата:** 2025-01-XX  
**Версия:** 1.0

