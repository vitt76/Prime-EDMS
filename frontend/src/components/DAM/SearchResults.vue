<template>
  <div class="search-results">
    <!-- Results List -->
    <div
      v-for="(result, index) in results"
      :key="result.id"
      :data-result-index="index"
      :class="[
        'flex items-center gap-3 p-3 cursor-pointer transition-colors',
        'hover:bg-neutral-100 dark:hover:bg-neutral-100',
        index === selectedIndex ? 'bg-primary-50 dark:bg-primary-50' : ''
      ]"
      @click="$emit('select', result.id)"
      @mouseenter="$emit('hover', index)"
      role="option"
      :aria-selected="index === selectedIndex"
    >
      <!-- Thumbnail -->
      <div class="flex-shrink-0 w-12 h-12 bg-neutral-100 dark:bg-neutral-100 rounded-md overflow-hidden">
        <img
          v-if="result.thumbnail_url"
          :src="result.thumbnail_url"
          :alt="result.label"
          class="w-full h-full object-cover"
          @error="handleImageError"
        />
        <div
          v-else
          class="w-full h-full flex items-center justify-center bg-neutral-200 dark:bg-neutral-200"
        >
          <svg class="w-6 h-6 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      </div>

      <!-- Metadata -->
      <div class="flex-1 min-w-0">
        <div class="text-sm font-medium text-neutral-900 dark:text-neutral-900 truncate">
          {{ result.label }}
        </div>
        <div class="flex items-center gap-2 mt-1 text-xs text-neutral-600 dark:text-neutral-600">
          <span>{{ formatFileSize(result.size) }}</span>
          <span>•</span>
          <span>{{ formatDate(result.date_added) }}</span>
          <span v-if="result.mime_type" class="ml-1">
            {{ getFileTypeLabel(result.mime_type) }}
          </span>
        </div>
      </div>

      <!-- Arrow Icon -->
      <svg
        class="flex-shrink-0 w-5 h-5 text-neutral-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 5l7 7-7 7"
        />
      </svg>
    </div>

    <!-- View All Results Link -->
    <div
      v-if="totalCount > results.length"
      class="border-t border-neutral-300 dark:border-neutral-300 p-3"
    >
      <button
        class="w-full text-center text-sm text-primary-500 hover:text-primary-600 font-medium transition-colors"
        @click="$emit('view-all')"
      >
        Показать все результаты ({{ totalCount }})
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Asset } from '@/types/api'
import { formatFileSize, formatDate } from '@/utils/formatters'

interface Props {
  results: Asset[]
  selectedIndex: number
  totalCount: number
}

defineProps<Props>()

const emit = defineEmits<{
  select: [assetId: number]
  'view-all': []
  hover: [index: number]
}>()

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

function getFileTypeLabel(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'Изображение'
  if (mimeType.startsWith('video/')) return 'Видео'
  if (mimeType.startsWith('audio/')) return 'Аудио'
  if (mimeType.includes('pdf')) return 'PDF'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'Документ'
  return 'Файл'
}
</script>

<style scoped>
.search-results {
  max-height: 400px;
  overflow-y: auto;
}
</style>

