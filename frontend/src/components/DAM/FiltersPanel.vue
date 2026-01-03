<template>
  <div class="filters-panel" role="region" aria-label="Панель фильтров">
    <!-- Type Filter with Facets -->
    <div class="mb-6">
      <label class="block text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        Тип файла
      </label>
      <div class="space-y-2" role="group" aria-label="Фильтр по типу файла">
        <label
          v-for="type in fileTypes"
          :key="type.value"
          class="flex items-center justify-between gap-2 cursor-pointer p-2 rounded-md hover:bg-neutral-50 dark:hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <input
              type="checkbox"
              :value="type.value"
              v-model="selectedTypes"
              class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500 min-w-[44px] min-h-[44px]"
              :aria-label="`Фильтр: ${type.label}`"
            />
            <span class="text-sm text-neutral-700 dark:text-neutral-700">{{ type.label }}</span>
          </div>
          <span
            v-if="facets?.type?.[type.value]"
            class="text-xs text-neutral-500 dark:text-neutral-500"
          >
            {{ facets.type[type.value] }}
          </span>
        </label>
      </div>
    </div>

    <!-- Date Range Filter -->
    <div class="mb-6">
      <label class="block text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        Дата добавления
      </label>
      <DateRangePicker v-model="dateRange" />
    </div>

    <!-- Size Filter -->
    <div class="mb-6">
      <label class="block text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        Размер файла
      </label>
      <div class="space-y-2">
        <div class="flex items-center gap-2">
          <input
            v-model.number="sizeMin"
            type="number"
            placeholder="Мин (MB)"
            class="flex-1 px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px]"
            aria-label="Минимальный размер файла в мегабайтах"
          />
          <span class="text-neutral-500" aria-hidden="true">—</span>
          <input
            v-model.number="sizeMax"
            type="number"
            placeholder="Макс (MB)"
            class="flex-1 px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-[44px]"
            aria-label="Максимальный размер файла в мегабайтах"
          />
        </div>
      </div>
    </div>

    <!-- Tags Filter with Autocomplete -->
    <div class="mb-6">
      <label class="block text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        Теги
      </label>
      <TagInput
        v-model="selectedTags"
        :suggestions="tagSuggestions"
        placeholder="Введите тег..."
        :allow-custom="true"
      />
      <!-- Facets for tags -->
      <div v-if="facets?.tags && Object.keys(facets.tags).length > 0" class="mt-2">
        <p class="text-xs text-neutral-500 dark:text-neutral-500 mb-2">Популярные теги:</p>
        <div class="flex flex-wrap gap-1">
          <button
            v-for="(count, tag) in facets.tags"
            :key="tag"
            :class="[
              'px-2 py-1 text-xs rounded-md transition-colors min-h-[44px]',
              selectedTags.includes(tag)
                ? 'bg-primary-500 text-white'
                : 'bg-neutral-100 dark:bg-neutral-100 text-neutral-700 dark:text-neutral-700 hover:bg-neutral-200 dark:hover:bg-neutral-200'
            ]"
            @click="toggleTag(tag)"
            type="button"
            :aria-label="`${selectedTags.includes(tag) ? 'Убрать' : 'Добавить'} тег ${tag}`"
            :aria-pressed="selectedTags.includes(tag)"
          >
            {{ tag }} ({{ count }})
          </button>
        </div>
      </div>
    </div>

    <!-- Custom Metadata Filters (Collapsible) -->
    <div class="mb-6">
      <button
        class="flex items-center justify-between w-full text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3"
        @click="showCustomMetadata = !showCustomMetadata"
      >
        <span>Дополнительные фильтры</span>
        <svg
          :class="['w-4 h-4 transition-transform', showCustomMetadata ? 'rotate-180' : '']"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
      <div v-if="showCustomMetadata" class="space-y-3">
        <div v-for="(filter, index) in customMetadataFilters" :key="index" class="space-y-1">
          <div class="flex gap-2">
            <input
              v-model="filter.key"
              type="text"
              placeholder="Ключ"
              class="flex-1 px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <input
              v-model="filter.value"
              type="text"
              placeholder="Значение"
              class="flex-1 px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              class="px-2 text-error hover:text-error-600 transition-colors"
              @click="removeCustomFilter(index)"
              aria-label="Удалить фильтр"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
        <button
          class="text-sm text-primary-500 hover:text-primary-600 transition-colors"
          @click="addCustomFilter"
        >
          + Добавить фильтр
        </button>
      </div>
    </div>

    <!-- Active Filters Summary -->
    <div v-if="hasActiveFilters" class="mb-4 p-3 bg-primary-50 dark:bg-primary-50 rounded-md">
      <p class="text-xs font-semibold text-neutral-900 dark:text-neutral-900 mb-2">
        Активные фильтры:
      </p>
      <div class="flex flex-wrap gap-1">
        <Badge
          v-for="(filter, key) in activeFiltersSummary"
          :key="key"
          variant="info"
          size="sm"
          class="cursor-pointer"
          @click="clearFilter(key)"
        >
          {{ filter }}
        </Badge>
      </div>
    </div>

    <!-- Actions (auto-apply; only reset) -->
    <div class="flex gap-2 pt-4 border-t border-neutral-300 dark:border-neutral-300">
      <Button
        variant="outline"
        size="sm"
        class="flex-1"
        :disabled="!hasActiveFilters"
        @click="handleReset"
      >
        Сбросить
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import Button from '@/components/Common/Button.vue'
import Badge from '@/components/Common/Badge.vue'
import TagInput from '@/components/Common/TagInput.vue'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'
import type { Facets, SearchFilters } from '@/types/api'

interface Props {
  facets?: Facets
  modelValue: SearchFilters
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [filters: SearchFilters]
  reset: []
}>()

const fileTypes = [
  { value: 'image', label: 'Изображения' },
  { value: 'video', label: 'Видео' },
  { value: 'document', label: 'Документы' },
  { value: 'audio', label: 'Аудио' }
]

const selectedTypes = ref<string[]>([])
const dateRange = ref<[string, string] | null>(null)
const sizeMin = ref<number | null>(null)
const sizeMax = ref<number | null>(null)
const selectedTags = ref<string[]>([])
const showCustomMetadata = ref(false)
const customMetadataFilters = ref<Array<{ key: string; value: string }>>([])
const isHydrating = ref(false)

function hydrateFromModel(filters: SearchFilters) {
  selectedTypes.value = filters.type || []
  dateRange.value = filters.date_range || null
  if (filters.size) {
    sizeMin.value = filters.size.min ? filters.size.min / (1024 * 1024) : null // bytes -> MB
    sizeMax.value = filters.size.max ? filters.size.max / (1024 * 1024) : null
  } else {
    sizeMin.value = null
    sizeMax.value = null
  }
  selectedTags.value = filters.tags || []
  if (filters.custom_metadata) {
    customMetadataFilters.value = Object.entries(filters.custom_metadata).map(([key, value]) => ({
      key,
      value: String(value)
    }))
  } else {
    customMetadataFilters.value = []
  }
}

// Initialize & keep in sync with external modelValue (e.g. URL back/forward)
watch(
  () => props.modelValue,
  (filters) => {
    isHydrating.value = true
    hydrateFromModel(filters || {})
    void nextTick(() => {
      isHydrating.value = false
    })
  },
  { immediate: true, deep: true }
)

const tagSuggestions = computed(() => {
  if (props.facets?.tags) {
    return Object.keys(props.facets.tags).sort((a, b) => {
      const countA = props.facets?.tags?.[a] || 0
      const countB = props.facets?.tags?.[b] || 0
      return countB - countA
    })
  }
  return []
})

const hasActiveFilters = computed(() => {
  return (
    selectedTypes.value.length > 0 ||
    dateRange.value !== null ||
    sizeMin.value !== null ||
    sizeMax.value !== null ||
    selectedTags.value.length > 0 ||
    customMetadataFilters.value.length > 0
  )
})

const activeFiltersSummary = computed(() => {
  const summary: Record<string, string> = {}
  if (selectedTypes.value.length > 0) {
    summary.type = `Тип: ${selectedTypes.value.join(', ')}`
  }
  if (dateRange.value) {
    summary.date = `Дата: ${dateRange.value[0]} - ${dateRange.value[1]}`
  }
  if (sizeMin.value !== null || sizeMax.value !== null) {
    summary.size = `Размер: ${sizeMin.value || 0} - ${sizeMax.value || '∞'} MB`
  }
  if (selectedTags.value.length > 0) {
    summary.tags = `Теги: ${selectedTags.value.join(', ')}`
  }
  return summary
})

function toggleTag(tag: string) {
  const index = selectedTags.value.indexOf(tag)
  if (index === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(index, 1)
  }
}

function addCustomFilter() {
  customMetadataFilters.value.push({ key: '', value: '' })
}

function removeCustomFilter(index: number) {
  customMetadataFilters.value.splice(index, 1)
}

function clearFilter(key: string) {
  switch (key) {
    case 'type':
      selectedTypes.value = []
      break
    case 'date':
      dateRange.value = null
      break
    case 'size':
      sizeMin.value = null
      sizeMax.value = null
      break
    case 'tags':
      selectedTags.value = []
      break
  }
}

function emitModelUpdate() {
  const filters: SearchFilters = {}

  if (selectedTypes.value.length > 0) {
    filters.type = selectedTypes.value
  }

  if (dateRange.value) {
    filters.date_range = dateRange.value
  }

  if (sizeMin.value !== null || sizeMax.value !== null) {
    filters.size = {
      min: sizeMin.value ? sizeMin.value * 1024 * 1024 : undefined, // Convert to bytes
      max: sizeMax.value ? sizeMax.value * 1024 * 1024 : undefined
    }
  }

  if (selectedTags.value.length > 0) {
    filters.tags = selectedTags.value
  }

  if (customMetadataFilters.value.length > 0) {
    const customMetadata: Record<string, unknown> = {}
    customMetadataFilters.value.forEach((filter) => {
      if (filter.key && filter.value) {
        customMetadata[filter.key] = filter.value
      }
    })
    if (Object.keys(customMetadata).length > 0) {
      filters.custom_metadata = customMetadata
    }
  }

  emit('update:modelValue', filters)
}

function handleReset() {
  selectedTypes.value = []
  dateRange.value = null
  sizeMin.value = null
  sizeMax.value = null
  selectedTags.value = []
  customMetadataFilters.value = []
  emitModelUpdate()
  emit('reset')
}

// Auto-apply (reactive). Debounce happens outside (in composable).
watch(
  () => [selectedTypes.value, dateRange.value, sizeMin.value, sizeMax.value, selectedTags.value, customMetadataFilters.value],
  () => {
    if (isHydrating.value) return
    emitModelUpdate()
  },
  { deep: true }
)
</script>

<style scoped>
.filters-panel {
  /* Additional styles if needed */
}
</style>

