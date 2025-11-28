<template>
  <div
    :class="cardClasses"
    role="button"
    tabindex="0"
    :aria-label="`Актив: ${asset.label}`"
    :draggable="true"
    @click="handleClick"
    @dblclick="handleDoubleClick"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false; isDragging = false"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
  >
    <!-- Checkbox (shown on hover or when selected) -->
    <Transition
      enter-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showCheckbox && (isHovered || isSelected)"
        class="absolute top-3 left-3 z-20"
        @click.stop="handleSelect"
      >
        <div class="relative">
          <input
            type="checkbox"
            :checked="isSelected"
            class="peer w-5 h-5 rounded border-2 border-white/80 bg-black/20 text-primary-500 
                   focus:ring-2 focus:ring-primary-500 focus:ring-offset-0 cursor-pointer
                   checked:bg-primary-500 checked:border-primary-500
                   hover:border-white transition-colors"
            @click.stop
            @change="handleSelect"
            :aria-label="`Выбрать актив ${asset.label}`"
          />
        </div>
      </div>
    </Transition>

    <!-- Thumbnail Container with 16:9 Aspect Ratio -->
    <div
      ref="thumbnailRef"
      class="relative w-full aspect-video bg-neutral-100 rounded-t-lg overflow-hidden"
    >
      <!-- Optimized Image with WebP support and lazy loading -->
      <img
        v-if="props.asset.thumbnail_url && !props.isLoading && shouldLoadImage"
        :src="props.asset.thumbnail_url"
        :alt="props.asset.label"
        loading="lazy"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        @error="handleImageError"
      />
      
      <!-- Loading Spinner -->
      <div
        v-else-if="isLoading || !shouldLoadImage"
        class="w-full h-full flex items-center justify-center bg-neutral-100"
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
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      
      <!-- Placeholder for missing images -->
      <div
        v-else-if="imageError || !props.asset.thumbnail_url"
        class="w-full h-full flex items-center justify-center bg-gradient-to-br from-neutral-100 to-neutral-200"
      >
        <div class="text-center">
          <svg
            class="w-12 h-12 mx-auto text-neutral-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p class="mt-1 text-xs text-neutral-400">{{ getFileTypeLabel() }}</p>
        </div>
      </div>

      <!-- Hover Overlay with Quick Actions -->
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="isHovered && !isLoading"
          class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent 
                 flex items-end justify-center pb-4 gap-2"
          @click.stop
        >
          <button
            class="p-2.5 bg-white/95 rounded-full hover:bg-white hover:scale-110 
                   transition-all duration-200 shadow-lg"
            @click.stop="handlePreview"
            aria-label="Предпросмотр актива"
            type="button"
          >
            <svg class="w-5 h-5 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            class="p-2.5 bg-white/95 rounded-full hover:bg-white hover:scale-110 
                   transition-all duration-200 shadow-lg"
            @click.stop="handleDownload"
            aria-label="Скачать актив"
            type="button"
          >
            <svg class="w-5 h-5 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
          </button>
          <button
            class="p-2.5 bg-white/95 rounded-full hover:bg-white hover:scale-110 
                   transition-all duration-200 shadow-lg"
            @click.stop="handleShare"
            aria-label="Поделиться"
            type="button"
          >
            <svg class="w-5 h-5 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
              />
            </svg>
          </button>
          <button
            class="p-2.5 bg-white/95 rounded-full hover:bg-white hover:scale-110 
                   transition-all duration-200 shadow-lg"
            @click.stop="handleMore"
            aria-label="Дополнительные действия"
            type="button"
          >
            <svg class="w-5 h-5 text-neutral-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
              />
            </svg>
          </button>
        </div>
      </Transition>

      <!-- File Type Badge (top right) -->
      <div class="absolute top-3 right-3 flex gap-1.5">
        <!-- Shared Badge -->
        <span
          v-if="props.isShared"
          class="flex items-center gap-1 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider 
                 bg-primary-500 text-white rounded backdrop-blur-sm"
          title="Актив расшарен"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          Shared
        </span>
        <!-- Status Badge -->
        <span
          v-if="asset.metadata?.status"
          :class="statusBadgeClasses"
        >
          {{ getStatusLabel(asset.metadata.status as string) }}
        </span>
        <!-- File Type Badge -->
        <span
          v-if="asset.metadata?.type"
          class="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider 
                 bg-black/50 text-white rounded backdrop-blur-sm"
        >
          {{ asset.metadata.type }}
        </span>
      </div>

      <!-- AI Analyzed Indicator -->
      <div 
        v-if="asset.ai_analysis?.status === 'completed'"
        class="absolute bottom-3 left-3"
      >
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium 
                     bg-purple-500/90 text-white rounded backdrop-blur-sm">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z"/>
          </svg>
          AI
        </span>
      </div>
    </div>

    <!-- Metadata Footer -->
    <div class="p-3 space-y-1.5">
      <!-- Title with truncation -->
      <h3 
        class="text-sm font-medium text-neutral-800 truncate"
        :title="asset.label"
      >
        {{ asset.label }}
      </h3>
      
      <!-- File info row -->
      <div class="flex items-center justify-between text-xs text-neutral-500">
        <span class="font-medium">{{ formatFileSize(asset.size) }}</span>
        <span>{{ formatDate(asset.date_added) }}</span>
      </div>
      
      <!-- Tags (show first 2) -->
      <div v-if="displayTags.length > 0" class="flex flex-wrap gap-1 mt-1.5">
        <span
          v-for="tag in displayTags"
          :key="tag"
          class="px-1.5 py-0.5 text-[10px] font-medium bg-neutral-100 text-neutral-600 
                 rounded hover:bg-neutral-200 transition-colors cursor-pointer truncate max-w-[80px]"
          :title="tag"
        >
          {{ tag }}
        </span>
        <span
          v-if="allTags.length > 2"
          class="px-1.5 py-0.5 text-[10px] font-medium text-neutral-400"
        >
          +{{ allTags.length - 2 }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Asset } from '@/types/api'
import { formatFileSize, formatDate } from '@/utils/formatters'
import { useIntersectionObserver } from '@/composables/useIntersectionObserver'
import { useAssetStore } from '@/stores/assetStore'

interface Props {
  asset: Asset
  isSelected?: boolean
  isLoading?: boolean
  showCheckbox?: boolean
  isShared?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  isLoading: false,
  showCheckbox: true,
  isShared: false
})

const emit = defineEmits<{
  select: [asset: Asset]
  open: [asset: Asset]
  preview: [asset: Asset]
  download: [asset: Asset]
  share: [asset: Asset]
  more: [asset: Asset]
}>()

const isHovered = ref(false)
const imageError = ref(false)
const thumbnailRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)

// Intersection Observer for lazy loading
const { hasIntersected } = useIntersectionObserver(thumbnailRef, {
  rootMargin: '100px'
})

const shouldLoadImage = computed(() => {
  return hasIntersected.value || props.isLoading
})

// Combine custom tags and AI tags
const allTags = computed(() => {
  const tags = [...(props.asset.tags || [])]
  if (props.asset.ai_analysis?.tags) {
    props.asset.ai_analysis.tags.forEach(t => {
      if (!tags.includes(t)) tags.push(t)
    })
  }
  return tags
})

const displayTags = computed(() => allTags.value.slice(0, 2))

const cardClasses = computed(() => {
  const base = [
    'group',
    'relative',
    'bg-white',
    'rounded-xl',
    'overflow-hidden',
    'cursor-pointer',
    'transition-all',
    'duration-300',
    'ease-out',
  ]
  
  // Dragging state
  if (isDragging.value) {
    base.push('opacity-50', 'scale-95', 'ring-2', 'ring-primary-400', 'ring-dashed')
  }
  // Hover & selection states
  else if (props.isSelected) {
    base.push('ring-2', 'ring-primary-500', 'ring-offset-2', 'shadow-lg')
  } else {
    base.push(
      'border',
      'border-neutral-200',
      'hover:border-neutral-300',
      'hover:shadow-xl',
      'hover:-translate-y-1'
    )
  }
  
  return base.join(' ')
})

const statusBadgeClasses = computed(() => {
  const status = props.asset.metadata?.status as string
  const base = 'px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded backdrop-blur-sm'
  
  switch (status?.toLowerCase()) {
    case 'approved':
      return `${base} bg-emerald-500/90 text-white`
    case 'pending':
      return `${base} bg-amber-500/90 text-white`
    case 'rejected':
      return `${base} bg-red-500/90 text-white`
    case 'draft':
      return `${base} bg-neutral-500/90 text-white`
    default:
      return `${base} bg-neutral-500/90 text-white`
  }
})

function handleImageError() {
  imageError.value = true
}

function getFileTypeLabel(): string {
  const type = props.asset.metadata?.type as string
  const mime = props.asset.mime_type
  
  if (type) return type.toUpperCase()
  if (mime?.startsWith('image/')) return 'IMAGE'
  if (mime?.startsWith('video/')) return 'VIDEO'
  if (mime?.startsWith('audio/')) return 'AUDIO'
  if (mime?.includes('pdf')) return 'PDF'
  return 'FILE'
}

function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    approved: 'Одобрен',
    pending: 'Ожидает',
    rejected: 'Отклонен',
    draft: 'Черновик'
  }
  return labels[status.toLowerCase()] || status
}

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

function handleShare() {
  emit('share', props.asset)
}

function handleMore() {
  emit('more', props.asset)
}

// ============================================================================
// DRAG & DROP HANDLERS
// ============================================================================

const assetStore = useAssetStore()

function handleDragStart(event: DragEvent) {
  if (!event.dataTransfer) return
  
  isDragging.value = true
  
  // Collect IDs - if this asset is selected, drag all selected assets
  // Otherwise, drag only this asset
  let assetIds: number[]
  
  if (props.isSelected && assetStore.selectedAssets.size > 0) {
    assetIds = Array.from(assetStore.selectedAssets)
  } else {
    assetIds = [props.asset.id]
  }
  
  // Set drag data
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('application/json', JSON.stringify({
    type: 'asset',
    assetIds: assetIds,
    label: assetIds.length > 1 
      ? `${assetIds.length} файлов` 
      : props.asset.label
  }))
  
  // Create custom drag image
  const dragImage = document.createElement('div')
  dragImage.className = 'px-3 py-2 bg-primary-500 text-white text-sm font-medium rounded-lg shadow-lg'
  dragImage.textContent = assetIds.length > 1 
    ? `${assetIds.length} файлов`
    : props.asset.label
  dragImage.style.position = 'absolute'
  dragImage.style.top = '-1000px'
  document.body.appendChild(dragImage)
  event.dataTransfer.setDragImage(dragImage, 0, 0)
  
  // Remove drag image after a short delay
  setTimeout(() => {
    document.body.removeChild(dragImage)
  }, 0)
}

function handleDragEnd() {
  isDragging.value = false
}
</script>
