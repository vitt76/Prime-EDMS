<template>
  <div class="metadata-panel">
    <!-- File Details Section -->
    <section class="mb-6">
      <h3 class="text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        Информация о файле
      </h3>
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Название:</span>
          <span class="text-neutral-900 dark:text-neutral-900 font-medium">{{ asset?.label || 'N/A' }}</span>
        </div>
        <div v-if="fileDetails" class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Имя файла:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ fileDetails.filename }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Размер:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ asset ? formatFileSize(asset.size) : 'N/A' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Тип:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ asset?.mime_type || 'N/A' }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Добавлено:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ asset ? formatDate(asset.date_added) : 'N/A' }}</span>
        </div>
        <div v-if="fileDetails?.checksum" class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Checksum:</span>
          <span class="text-neutral-900 dark:text-neutral-900 font-mono text-xs">
            {{ truncate(fileDetails.checksum, 16) }}
          </span>
        </div>
      </div>
    </section>

    <!-- Image Info (EXIF) Section -->
    <section v-if="isImage && imageMetadata" class="mb-6">
      <h3 class="text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        Информация об изображении
      </h3>
      <div class="space-y-2 text-sm">
        <div v-if="imageMetadata.dimensions" class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Размеры:</span>
          <span class="text-neutral-900 dark:text-neutral-900">
            {{ imageMetadata.dimensions.width }} × {{ imageMetadata.dimensions.height }} px
          </span>
        </div>
        <div v-if="imageMetadata.dpi" class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">DPI:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ imageMetadata.dpi }}</span>
        </div>
        <div v-if="imageMetadata.color_space" class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Цветовое пространство:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ imageMetadata.color_space }}</span>
        </div>
        <div v-if="imageMetadata.camera" class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Камера:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ imageMetadata.camera }}</span>
        </div>
        <div v-if="imageMetadata.exposure" class="flex justify-between">
          <span class="text-neutral-600 dark:text-neutral-600">Экспозиция:</span>
          <span class="text-neutral-900 dark:text-neutral-900">{{ imageMetadata.exposure }}</span>
        </div>
      </div>
    </section>

    <!-- AI Analysis Section -->
    <section v-if="aiAnalysis" class="mb-6">
      <h3 class="text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        AI Анализ
      </h3>
      <div v-if="aiAnalysis.status === 'completed'" class="space-y-3">
        <!-- Tags -->
        <div v-if="aiAnalysis.tags && aiAnalysis.tags.length > 0">
          <div class="text-xs font-medium text-neutral-600 dark:text-neutral-600 mb-2">
            Теги:
          </div>
          <div class="flex flex-wrap gap-2">
            <Badge
              v-for="tag in aiAnalysis.tags"
              :key="tag"
              variant="info"
              size="sm"
            >
              {{ tag }}
            </Badge>
          </div>
        </div>

        <!-- Description -->
        <div v-if="aiAnalysis.ai_description">
          <div class="text-xs font-medium text-neutral-600 dark:text-neutral-600 mb-2">
            Описание:
          </div>
          <p class="text-sm text-neutral-900 dark:text-neutral-900">
            {{ aiAnalysis.ai_description }}
          </p>
        </div>

        <!-- Dominant Colors -->
        <div v-if="aiAnalysis.colors && aiAnalysis.colors.length > 0">
          <div class="text-xs font-medium text-neutral-600 dark:text-neutral-600 mb-2">
            Доминирующие цвета:
          </div>
          <div class="flex gap-2">
            <div
              v-for="(color, index) in aiAnalysis.colors"
              :key="index"
              class="w-8 h-8 rounded border border-neutral-300 dark:border-neutral-300"
              :style="{ backgroundColor: color }"
              :title="color"
            ></div>
          </div>
        </div>

        <!-- Objects Detected -->
        <div v-if="aiAnalysis.objects_detected && aiAnalysis.objects_detected.length > 0">
          <div class="text-xs font-medium text-neutral-600 dark:text-neutral-600 mb-2">
            Обнаруженные объекты:
          </div>
          <div class="space-y-1">
            <div
              v-for="(obj, index) in aiAnalysis.objects_detected"
              :key="index"
              class="flex items-center justify-between text-sm"
            >
              <span class="text-neutral-900 dark:text-neutral-900">{{ obj.name }}</span>
              <span class="text-neutral-600 dark:text-neutral-600">
                {{ Math.round(obj.confidence * 100) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="aiAnalysis.status === 'processing'" class="text-sm text-neutral-600 dark:text-neutral-600">
        <div class="flex items-center gap-2">
          <div class="animate-spin h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full"></div>
          <span>Анализ выполняется...</span>
        </div>
      </div>
      <div v-else class="text-sm text-neutral-600 dark:text-neutral-600">
        AI анализ недоступен
      </div>
    </section>

    <!-- Version History Section -->
    <section v-if="versionHistory && versionHistory.length > 0" class="mb-6">
      <h3 class="text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        История версий
      </h3>
      <div class="space-y-2">
        <button
          v-for="(version, index) in versionHistory"
          :key="version.id"
          :class="[
            'w-full text-left p-2 rounded-md text-sm transition-colors',
            'hover:bg-neutral-100 dark:hover:bg-neutral-100',
            index === 0 ? 'bg-primary-50 dark:bg-primary-50' : ''
          ]"
          @click="$emit('version-select', version.id)"
        >
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-neutral-900 dark:text-neutral-900">
                {{ version.filename }}
              </div>
              <div class="text-xs text-neutral-600 dark:text-neutral-600 mt-1">
                {{ formatDate(version.uploaded_date) }}
                <span v-if="version.uploaded_by"> • {{ version.uploaded_by }}</span>
              </div>
            </div>
            <div class="text-xs text-neutral-600 dark:text-neutral-600">
              {{ formatFileSize(version.size) }}
            </div>
          </div>
        </button>
      </div>
    </section>

    <!-- Comments Section -->
    <section v-if="comments && comments.length > 0" class="mb-6">
      <h3 class="text-sm font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
        Комментарии ({{ comments.length }})
      </h3>
      <div class="space-y-3 max-h-64 overflow-y-auto">
        <div
          v-for="comment in comments"
          :key="comment.id"
          class="p-3 bg-neutral-50 dark:bg-neutral-50 rounded-md"
        >
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm font-medium text-neutral-900 dark:text-neutral-900">
              {{ comment.author }}
            </span>
            <span class="text-xs text-neutral-600 dark:text-neutral-600">
              {{ formatRelativeTime(comment.created_date) }}
            </span>
          </div>
          <p class="text-sm text-neutral-700 dark:text-neutral-700">
            {{ comment.text }}
          </p>
        </div>
      </div>
    </section>

    <!-- Actions Section -->
    <section class="border-t border-neutral-300 dark:border-neutral-300 pt-4">
      <div class="flex flex-col gap-2">
        <Button
          variant="primary"
          size="md"
          class="w-full"
          @click="$emit('download')"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          Скачать
        </Button>
        <Button
          variant="outline"
          size="md"
          class="w-full"
          @click="$emit('share')"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.552 3.546a2 2 0 002.938-2.187l.546-2.59A4.998 4.998 0 0017 12c0-.482-.114-.938-.316-1.342m0 2.684L12.448 8.454a2 2 0 00-2.938-2.187l-.546 2.59A4.998 4.998 0 007 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684"
            />
          </svg>
          Поделиться
        </Button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Asset, AssetDetailResponse, FileDetails, AIAnalysis, Comment, Version } from '@/types/api'
import { formatFileSize, formatDate, formatRelativeTime, truncate } from '@/utils/formatters'
import Button from '@/components/Common/Button.vue'
import Badge from '@/components/Common/Badge.vue'

interface Props {
  asset: Asset | AssetDetailResponse | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  download: []
  share: []
  'version-select': [versionId: number]
}>()

// Extract data from asset
const fileDetails = computed<FileDetails | null>(() => {
  if (!props.asset) return null
  if ('file_details' in props.asset) {
    return props.asset.file_details
  }
  return null
})

const aiAnalysis = computed<AIAnalysis | null>(() => {
  if (!props.asset) return null
  if ('ai_analysis' in props.asset && props.asset.ai_analysis) {
    return props.asset.ai_analysis
  }
  return null
})

const comments = computed<Comment[]>(() => {
  if (!props.asset) return []
  if ('comments' in props.asset && props.asset.comments) {
    return props.asset.comments
  }
  return []
})

const versionHistory = computed<Version[]>(() => {
  if (!props.asset) return []
  if ('version_history' in props.asset && props.asset.version_history) {
    return props.asset.version_history
  }
  return []
})

const isImage = computed(() => {
  return props.asset?.mime_type?.startsWith('image/') || false
})

const imageMetadata = computed(() => {
  if (!isImage.value || !props.asset) return null

  // Extract image metadata from asset metadata or file_details
  const metadata = props.asset.metadata || {}
  const details = fileDetails.value

  // Try to extract dimensions from various sources
  let dimensions = null
  if (metadata.dimensions) {
    dimensions = metadata.dimensions
  } else if (metadata.width && metadata.height) {
    dimensions = { width: metadata.width, height: metadata.height }
  } else if (details && 'width' in details && 'height' in details) {
    dimensions = { width: details.width, height: details.height }
  }

  return {
    dimensions,
    dpi: metadata.dpi || metadata.resolution || null,
    color_space: metadata.color_space || metadata.colorProfile || null,
    camera: metadata.camera || metadata.make || null,
    exposure: metadata.exposure || metadata.exposureTime || null
  }
})
</script>

<style scoped>
.metadata-panel {
  height: 100%;
  overflow-y: auto;
  padding: 1.5rem;
}
</style>

