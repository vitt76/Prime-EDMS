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
    <!-- Google Photos Style Checkbox (top-left, appears on hover or when selected) -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 scale-90"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-90"
    >
      <div
        v-if="showCheckbox && (isHovered || isSelected)"
        class="absolute top-2 left-2 z-30"
        data-selection-zone
        @click.stop="handleSelect"
      >
        <div
          :class="[
            'w-6 h-6 rounded-full flex items-center justify-center transition-all duration-200',
            isSelected
              ? 'bg-primary-500 ring-2 ring-white ring-offset-1'
              : 'bg-white/90 backdrop-blur-sm shadow-md hover:bg-white hover:scale-110'
          ]"
        >
          <svg
            v-if="isSelected"
            class="w-4 h-4 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="3"
              d="M5 13l4 4L19 7"
            />
          </svg>
          <div
            v-else
            class="w-3 h-3 rounded-full border-2 border-neutral-400"
          />
        </div>
      </div>
    </Transition>

    <!-- Thumbnail Container (no fixed aspect ratio, adapts to content) -->
    <div
      ref="thumbnailRef"
      class="relative w-full bg-neutral-50 overflow-hidden"
      :class="thumbnailAspectClass"
    >
      <!-- Favorite (top-right, appears on hover; always visible when favorited) -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 scale-90"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-90"
      >
        <button
          v-if="isHovered || isFavorite"
          type="button"
          data-favorite
          class="absolute top-2 right-2 z-30 w-9 h-9 rounded-full
                 bg-white/90 backdrop-blur-sm shadow-md
                 hover:bg-white active:scale-95
                 transition-all duration-200 flex items-center justify-center
                 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          :class="isHeartPulsing ? 'scale-125' : 'hover:scale-110'"
          :aria-label="isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'"
          @click.stop="handleToggleFavorite"
        >
          <component
            :is="isFavorite ? HeartSolidIcon : HeartOutlineIcon"
            class="w-5 h-5"
            :class="isFavorite ? 'text-red-500' : 'text-neutral-700'"
          />
        </button>
      </Transition>

      <!-- Optimized Image with smart object-fit -->
      <img
        v-if="!props.isLoading && shouldLoadImage && !imageError"
        :src="imageSrc"
        :alt="props.asset.label"
        loading="lazy"
        :class="imageObjectFitClass"
        class="w-full h-full transition-transform duration-500 ease-out"
        :style="{ transform: isHovered && !isSelected ? 'scale(1.05)' : 'scale(1)' }"
        @error="handleImageError"
      />
      
      <!-- Loading Skeleton -->
      <div
        v-else-if="isLoading || !shouldLoadImage"
        class="w-full h-full flex items-center justify-center bg-gradient-to-br from-neutral-100 to-neutral-200 animate-pulse"
      >
        <div class="w-12 h-12 rounded-full bg-neutral-300" />
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

      <!-- Quick Actions (bottom-right, appears on hover)
           IMPORTANT: metadata overlay reserves space (padding-right/padding-bottom),
           so action buttons never cover filename/size/date/tags. -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-2"
      >
        <div
          v-if="isHovered && !isLoading && !isSelected"
          class="absolute bottom-3 right-3 z-30 flex items-center gap-2 pointer-events-auto"
          data-quick-actions
          @click.stop
        >
          <button
            class="w-9 h-9 rounded-full bg-white/95 backdrop-blur-sm shadow-lg 
                   hover:bg-white hover:scale-110 active:scale-95
                   transition-all duration-200 flex items-center justify-center
                   focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
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
            class="w-9 h-9 rounded-full bg-white/95 backdrop-blur-sm shadow-lg 
                   hover:bg-white hover:scale-110 active:scale-95
                   transition-all duration-200 flex items-center justify-center
                   focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
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
            ref="moreBtnRef"
            class="w-9 h-9 rounded-full bg-white/95 backdrop-blur-sm shadow-lg 
                   hover:bg-white hover:scale-110 active:scale-95
                   transition-all duration-200 flex items-center justify-center
                   focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            @click.stop="toggleActionsMenu"
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

      <!-- Metadata Overlay (bottom, appears on hover with gradient background) -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-4"
      >
        <div
          v-if="isHovered && !isLoading"
          class="absolute inset-x-0 bottom-0 z-20 
                 bg-gradient-to-t from-black/80 via-black/60 to-transparent 
                 px-3 pt-3 pointer-events-none"
          :class="!isSelected ? 'pb-16 pr-36' : 'pb-4 pr-3'"
        >
          <h3 
            class="text-sm font-semibold text-white truncate mb-1 drop-shadow-lg"
            :title="asset.label"
          >
            {{ asset.label }}
          </h3>
          <div class="flex items-center justify-between text-xs text-white/90">
            <span class="font-medium drop-shadow">
              {{ formatFileSize(asset.file_details?.size ?? asset.size) }}
            </span>
            <span class="drop-shadow">{{ formatDate(asset.date_added) }}</span>
          </div>
          <!-- Tags (show first 2) -->
          <div v-if="displayTags.length > 0" class="flex flex-wrap gap-1.5 mt-2">
            <span
              v-for="tag in displayTags"
              :key="tag"
              class="px-2 py-0.5 text-[10px] font-medium bg-white/20 backdrop-blur-sm text-white 
                     rounded-md truncate max-w-[100px]"
              :title="tag"
            >
              {{ tag }}
            </span>
            <span
              v-if="allTags.length > 2"
              class="px-2 py-0.5 text-[10px] font-medium text-white/70"
            >
              +{{ allTags.length - 2 }}
            </span>
          </div>
        </div>
      </Transition>

      <!-- Status Badges (top-right, always visible) -->
      <div class="absolute top-2 right-2 z-20 flex flex-col gap-1.5 items-end pointer-events-none">
        <!-- Shared Badge -->
        <span
          v-if="props.isShared"
          class="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider 
                 bg-primary-500/90 text-white rounded backdrop-blur-sm shadow-md"
          title="Актив расшарен"
        >
          Shared
        </span>
        <!-- AI Analyzed Indicator -->
        <span
          v-if="asset.ai_analysis?.status === 'completed'"
          class="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium 
                 bg-purple-500/90 text-white rounded backdrop-blur-sm shadow-md"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z"/>
          </svg>
          AI
        </span>
      </div>

      <!-- Actions Dropdown Menu -->
      <Teleport to="body">
        <Transition
          enter-active-class="transition ease-out duration-150"
          enter-from-class="opacity-0 translate-y-1 scale-95"
          enter-to-class="opacity-100 translate-y-0 scale-100"
          leave-active-class="transition ease-in duration-100"
          leave-from-class="opacity-100 translate-y-0 scale-100"
          leave-to-class="opacity-0 translate-y-1 scale-95"
        >
          <div
            v-if="showActionsMenu"
            ref="actionsMenuRef"
            class="fixed bg-white shadow-2xl rounded-xl border border-neutral-200 z-[2000] overflow-hidden ring-1 ring-black/5 backdrop-blur max-h-[70vh] min-w-[200px]"
            :style="menuStyle"
          >
            <div class="py-1">
              <button
                class="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-neutral-800 hover:bg-neutral-50 text-left transition-colors"
                @click.stop="handleAddTags"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h10M7 12h10M7 17h6" />
                </svg>
                Теги
              </button>
              <button
                class="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-neutral-800 hover:bg-neutral-50 text-left transition-colors"
                @click.stop="handleMove"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h6m0 0v6m0-6L10 16l-4-4-5 5" />
                </svg>
                Переместить
              </button>
              <div class="border-t border-neutral-100 my-1" />
              <button
                class="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 text-left transition-colors"
                @click.stop="handleDelete"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Удалить
              </button>
            </div>
          </div>
        </Transition>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import type { Asset } from '@/types/api'
import { formatFileSize, formatDate } from '@/utils/formatters'
import { useIntersectionObserver } from '@/composables/useIntersectionObserver'
import { useAssetStore } from '@/stores/assetStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { resolveAssetImageUrl } from '@/utils/imageUtils'
import { apiService } from '@/services/apiService'
import { HeartIcon as HeartOutlineIcon } from '@heroicons/vue/24/outline'
import { HeartIcon as HeartSolidIcon } from '@heroicons/vue/24/solid'

interface Props {
  asset: Asset
  isSelected?: boolean
  isLoading?: boolean
  showCheckbox?: boolean
  isShared?: boolean
  density?: 'compact' | 'comfortable'
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  isLoading: false,
  showCheckbox: true,
  isShared: false,
  density: 'comfortable'
})

const emit = defineEmits<{
  select: [asset: Asset, event?: MouseEvent]
  open: [asset: Asset]
  preview: [asset: Asset]
  download: [asset: Asset]
  share: [asset: Asset]
  addTags: [asset: Asset]
  move: [asset: Asset]
  delete: [asset: Asset]
  'toggle-favorite': [asset: Asset]
}>()

const isHovered = ref(false)
const imageError = ref(false)
const thumbnailRef = ref<HTMLElement | null>(null)
const isDragging = ref(false)
const favoritesStore = useFavoritesStore()
const imageSrc = computed(() => resolveAssetImageUrl(props.asset))
const showActionsMenu = ref(false)
const moreBtnRef = ref<HTMLElement | null>(null)
const actionsMenuRef = ref<HTMLElement | null>(null)
const menuStyle = ref<Record<string, string>>({})
const isDownloading = ref(false)
const assetStore = useAssetStore()
const isHeartPulsing = ref(false)

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

// Determine image object-fit based on file type
const imageObjectFitClass = computed(() => {
  const mime = props.asset.mime_type || ''
  const label = props.asset.label?.toLowerCase() || ''
  
  // For logos, icons, and documents: use 'contain' to show full content
  if (
    mime.includes('svg') ||
    label.includes('logo') ||
    label.includes('icon') ||
    mime.includes('pdf') ||
    mime.includes('document')
  ) {
    return 'object-contain'
  }
  
  // For photos and images: use 'cover' for better visual impact
  return 'object-cover'
})

// Aspect ratio based on density
const thumbnailAspectClass = computed(() => {
  if (props.density === 'compact') {
    return 'aspect-square'
  }
  // Comfortable: use 16:9 for photos, square for others
  const mime = props.asset.mime_type || ''
  if (mime.startsWith('image/') && !mime.includes('svg')) {
    return 'aspect-video'
  }
  return 'aspect-square'
})

// Card classes: Immersive design (no borders/shadows in rest state)
const cardClasses = computed(() => {
  const base = [
    'group',
    'relative',
    'overflow-hidden',
    'cursor-pointer',
    'transition-all',
    'duration-300',
    'ease-out',
    'rounded-lg',
  ]
  
  // Dragging state
  if (isDragging.value) {
    base.push('opacity-50', 'scale-95', 'ring-2', 'ring-primary-400', 'ring-dashed')
  }
  // Selected state: scale down with blue ring
  else if (props.isSelected) {
    base.push('scale-95', 'ring-2', 'ring-primary-500', 'ring-offset-2')
  }
  // Rest state: completely clean, no borders, no shadows
  // Only subtle hover effect
  else {
    base.push('hover:scale-[1.02]')
  }
  
  return base.join(' ')
})

const isFavorite = computed(() => favoritesStore.isFavorite(props.asset.id))

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

function handleClick(event: MouseEvent | KeyboardEvent) {
  // If clicking on checkbox or quick actions, don't trigger preview
  const target = event.target as HTMLElement
  if (
    target.closest('[data-selection-zone]') ||
    target.closest('[data-quick-actions]') ||
    target.closest('[data-favorite]')
  ) {
    return
  }
  emit('preview', props.asset)
}

function handleDoubleClick() {
  emit('open', props.asset)
}

function handleSelect(event?: MouseEvent) {
  emit('select', props.asset, event)
}

async function handleToggleFavorite() {
  // pulse animation
  isHeartPulsing.value = true
  window.setTimeout(() => {
    isHeartPulsing.value = false
  }, 220)

  emit('toggle-favorite', props.asset)

  try {
    await favoritesStore.toggleFavorite(props.asset.id, props.asset as any)
  } catch {
    // ignore; store will revert on error
  }
}

async function handleDownload() {
  if (isDownloading.value) return
  isDownloading.value = true

  const assetAny = props.asset as any
  let directUrl = assetAny.download_url as string | undefined
  let fileId =
    assetAny.file_latest_id ||
    assetAny.file_latest?.id ||
    (props.asset as any)?.file_latest?.id

  const extractIdFromUrl = (url?: string | null) => {
    if (!url) return undefined
    const match = String(url).match(/files\/(\d+)\//)
    return match?.[1] ? Number(match[1]) : undefined
  }

  if (!directUrl && !fileId) {
    try {
      const detail: any = await apiService.get(`/api/v4/documents/${props.asset.id}/`)
      directUrl = detail?.data?.file_latest?.download_url
      fileId = detail?.data?.file_latest?.id || extractIdFromUrl(detail?.data?.file_latest?.url)
    } catch (e) {
      console.warn('Failed to fetch asset detail for download', props.asset.id)
    }
  }

  if (!directUrl && !fileId) {
    isDownloading.value = false
    return
  }

  let urlToFetch: string | null = directUrl || null
  if (!urlToFetch && fileId) {
    urlToFetch = `/api/v4/documents/${props.asset.id}/files/${fileId}/download/`
  }

  if (urlToFetch && urlToFetch.startsWith('/')) {
    const base = import.meta.env.VITE_API_URL || window.location.origin
    urlToFetch = `${base}${urlToFetch}`
  }

  const filename = props.asset.label || `asset-${props.asset.id}`

  try {
    const response: any = await apiService.get(urlToFetch as string, {
      responseType: 'blob',
      headers: { Accept: '*/*' } as any
    })
    const blobUrl = URL.createObjectURL(response.data as Blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(blobUrl)
  } catch (error) {
    emit('download', props.asset)
  } finally {
    isDownloading.value = false
  }
}

function handleShare() {
  emit('share', props.asset)
}

function toggleActionsMenu() {
  if (showActionsMenu.value) {
    showActionsMenu.value = false
    return
  }
  const btn = moreBtnRef.value
  if (btn) {
    const rect = btn.getBoundingClientRect()
    const menuWidth = Math.min(200, window.innerWidth - 16)
    const left = Math.min(
      Math.max(8, rect.left),
      window.innerWidth - menuWidth - 8
    )
    const top = rect.bottom + 8
    menuStyle.value = {
      top: `${top}px`,
      left: `${left}px`,
      width: `${menuWidth}px`
    }
  }
  showActionsMenu.value = true
}

function handleAddTags() {
  showActionsMenu.value = false
  emit('addTags', props.asset)
}

function handleMove() {
  showActionsMenu.value = false
  emit('move', props.asset)
}

function handleDelete() {
  showActionsMenu.value = false
  setTimeout(() => {
    emit('delete', props.asset)
  }, 100)
}

function handleGlobalClick(event: MouseEvent) {
  if (!showActionsMenu.value) return
  const target = event.target as Node
  if (
    actionsMenuRef.value?.contains(target) ||
    moreBtnRef.value?.contains(target)
  ) {
    return
  }
  showActionsMenu.value = false
}

function handleGlobalEscape(event: KeyboardEvent) {
  if (event.key === 'Escape' && showActionsMenu.value) {
    showActionsMenu.value = false
  }
}

function handleGlobalResizeScroll() {
  if (showActionsMenu.value) {
    toggleActionsMenu()
  }
}

// Drag & Drop
function handleDragStart(event: DragEvent) {
  if (!event.dataTransfer) return
  
  isDragging.value = true
  
  let assetIds: number[]
  if (props.isSelected && assetStore.selectedAssets.size > 0) {
    assetIds = Array.from(assetStore.selectedAssets)
  } else {
    assetIds = [props.asset.id]
  }
  
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('application/json', JSON.stringify({
    type: 'asset',
    assetIds: assetIds,
    label: assetIds.length > 1 ? `${assetIds.length} файлов` : props.asset.label
  }))
}

function handleDragEnd() {
  isDragging.value = false
}

onMounted(() => {
  // IMPORTANT: do not use capture here.
  // Capture-phase listener can close the teleported menu before Vue click handlers run.
  window.addEventListener('click', handleGlobalClick)
  window.addEventListener('keydown', handleGlobalEscape)
  window.addEventListener('resize', handleGlobalResizeScroll)
  window.addEventListener('scroll', handleGlobalResizeScroll, true)

  const size = (props.asset as any)?.file_details?.size ?? props.asset.size
  if (!size || size === 0) {
    assetStore.getAssetDetail(props.asset.id, true).catch(() => {
      // Silently ignore errors
    })
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleGlobalClick)
  window.removeEventListener('keydown', handleGlobalEscape)
  window.removeEventListener('resize', handleGlobalResizeScroll)
  window.removeEventListener('scroll', handleGlobalResizeScroll, true)
})
</script>
