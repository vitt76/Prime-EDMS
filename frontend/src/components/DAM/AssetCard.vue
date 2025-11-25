<template>
  <div
    :class="cardClasses"
    @click="handleClick"
    @dblclick="handleDoubleClick"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- Checkbox (shown on hover or when selected) -->
    <div
      v-if="showCheckbox && (isHovered || isSelected)"
      class="absolute top-2 left-2 z-10"
      @click.stop="handleSelect"
    >
      <input
        type="checkbox"
        :checked="isSelected"
        class="w-5 h-5 rounded border-neutral-300 text-primary-500 focus:ring-primary-500 cursor-pointer"
        @click.stop
        @change="handleSelect"
      />
    </div>

    <!-- Thumbnail -->
    <div
      ref="thumbnailRef"
      class="relative w-full h-48 bg-neutral-100 dark:bg-neutral-100 rounded-t-lg overflow-hidden"
    >
      <img
        v-if="asset.thumbnail_url && !isLoading && shouldLoadImage"
        :src="asset.thumbnail_url"
        :alt="asset.label"
        class="w-full h-full object-cover"
        @error="handleImageError"
      />
      <div
        v-else-if="isLoading"
        class="w-full h-full flex items-center justify-center"
      >
        <svg
          class="animate-spin h-8 w-8 text-neutral-400"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      </div>
      <div
        v-else
        class="w-full h-full flex items-center justify-center bg-neutral-200 dark:bg-neutral-200"
      >
        <svg
          class="w-12 h-12 text-neutral-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>

      <!-- Quick Actions (shown on hover) -->
      <div
        v-if="isHovered && !isLoading"
        class="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center gap-2 opacity-0 transition-opacity duration-fast hover:opacity-100"
        @click.stop
      >
        <button
          class="p-2 bg-white rounded-full hover:bg-neutral-100 transition-colors"
          @click.stop="handlePreview"
          aria-label="Preview"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
            />
          </svg>
        </button>
        <button
          class="p-2 bg-white rounded-full hover:bg-neutral-100 transition-colors"
          @click.stop="handleDownload"
          aria-label="Download"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
        </button>
        <button
          class="p-2 bg-white rounded-full hover:bg-neutral-100 transition-colors"
          @click.stop="handleMore"
          aria-label="More options"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
            />
          </svg>
        </button>
      </div>

      <!-- Status Badge -->
      <div
        v-if="asset.metadata?.status"
        class="absolute top-2 right-2"
      >
        <Badge
          :variant="getStatusVariant(asset.metadata.status as string)"
          size="sm"
        >
          {{ asset.metadata.status }}
        </Badge>
      </div>
    </div>

    <!-- Metadata -->
    <div class="p-3">
      <h3 class="text-sm font-medium text-neutral-900 dark:text-neutral-900 truncate mb-1">
        {{ asset.label }}
      </h3>
      <div class="flex items-center justify-between text-xs text-neutral-600 dark:text-neutral-600">
        <span>{{ formatFileSize(asset.size) }}</span>
        <span>{{ formatDate(asset.date_added) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Asset } from '@/types/api'
import Badge from '@/components/Common/Badge.vue'
import { formatFileSize, formatDate } from '@/utils/formatters'
import { useIntersectionObserver } from '@/composables/useIntersectionObserver'
import type { BadgeVariant } from '@/types'

interface Props {
  asset: Asset
  isSelected?: boolean
  isLoading?: boolean
  showCheckbox?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  isLoading: false,
  showCheckbox: true
})

const emit = defineEmits<{
  select: [asset: Asset]
  open: [asset: Asset]
  preview: [asset: Asset]
  download: [asset: Asset]
  more: [asset: Asset]
}>()

const isHovered = ref(false)
const imageError = ref(false)
const thumbnailRef = ref<HTMLElement | null>(null)

// Intersection Observer for lazy loading
const { hasIntersected } = useIntersectionObserver(thumbnailRef, {
  rootMargin: '100px'
})

const shouldLoadImage = computed(() => {
  return hasIntersected.value || props.isLoading
})

const cardClasses = computed(() => {
  return [
    'relative',
    'bg-neutral-0',
    'dark:bg-neutral-0',
    'rounded-lg',
    'border',
    'border-neutral-300',
    'dark:border-neutral-300',
    'overflow-hidden',
    'cursor-pointer',
    'transition-all',
    'duration-fast',
    'hover:shadow-lg',
    props.isSelected ? 'ring-2 ring-primary-500' : ''
  ].filter(Boolean).join(' ')
})

function handleClick() {
  emit('select', props.asset)
}

function handleDoubleClick() {
  emit('open', props.asset)
}

function handleSelect() {
  emit('select', props.asset)
}

function handlePreview() {
  emit('preview', props.asset)
}

function handleDownload() {
  emit('download', props.asset)
}

function handleMore() {
  emit('more', props.asset)
}

function handleImageError() {
  imageError.value = true
}

function getStatusVariant(status: string): BadgeVariant {
  const statusMap: Record<string, BadgeVariant> = {
    approved: 'success',
    pending: 'warning',
    rejected: 'error',
    draft: 'neutral'
  }
  return statusMap[status.toLowerCase()] || 'neutral'
}
</script>

