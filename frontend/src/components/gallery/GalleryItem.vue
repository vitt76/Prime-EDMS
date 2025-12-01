<template>
  <div
    class="gallery-item"
    :class="{
      'gallery-item--selected': isSelected,
      'gallery-item--list': viewMode === 'list',
      'gallery-item--grid': viewMode === 'grid'
    }"
    role="listitem"
    :tabindex="0"
    @click="handleClick"
    @keydown="handleKeydown"
    @focus="handleFocus"
    @blur="handleBlur"
    :aria-selected="isSelected"
    :aria-label="getAriaLabel()"
  >
    <!-- Selection checkbox (grid mode) -->
    <div
      v-if="viewMode === 'grid' && showSelection"
      class="gallery-item__checkbox"
    >
      <input
        type="checkbox"
        :checked="isSelected"
        class="gallery-item__checkbox-input"
        @change.stop="handleSelect"
        @click.stop
        :aria-label="`Select ${item.name}`"
      />
    </div>

    <!-- Item content -->
    <div class="gallery-item__content">
      <!-- Image/video preview -->
      <div class="gallery-item__preview">
        <div
          v-if="item.type?.startsWith('image/')"
          class="gallery-item__image-container"
        >
          <img
            v-if="item.thumbnail_url"
            :src="item.thumbnail_url"
            :alt="`Preview of ${item.name}`"
            class="gallery-item__image"
            loading="lazy"
            @error="handleImageError"
          />
          <div
            v-else
            class="gallery-item__image-placeholder"
          >
            <svg class="w-8 h-8 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        <!-- Video preview -->
        <div
          v-else-if="item.type?.startsWith('video/')"
          class="gallery-item__video-container"
        >
          <video
            v-if="item.thumbnail_url"
            :src="item.thumbnail_url"
            class="gallery-item__video"
            muted
            preload="metadata"
            @loadeddata="handleVideoLoad"
            @error="handleVideoError"
          />
          <div
            v-else
            class="gallery-item__video-placeholder"
          >
            <svg class="w-8 h-8 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="gallery-item__play-icon">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>

        <!-- Document/other file type -->
        <div
          v-else
          class="gallery-item__file-container"
        >
          <div class="gallery-item__file-icon">
            {{ getFileIcon(item.type) }}
          </div>
        </div>

        <!-- Status badges -->
        <div class="gallery-item__badges">
          <span
            v-if="item.status === 'processing'"
            class="gallery-item__badge gallery-item__badge--processing"
          >
            Processing
          </span>
          <span
            v-if="item.is_favorite"
            class="gallery-item__badge gallery-item__badge--favorite"
          >
            ★
          </span>
        </div>
      </div>

      <!-- Item info -->
      <div class="gallery-item__info">
        <!-- List mode: checkbox and filename -->
        <div v-if="viewMode === 'list'" class="gallery-item__list-header">
          <input
            type="checkbox"
            :checked="isSelected"
            class="gallery-item__checkbox-input"
            @change.stop="handleSelect"
            @click.stop
            :aria-label="`Select ${item.name}`"
          />
          <div class="gallery-item__filename" :title="item.name">
            {{ item.name }}
          </div>
        </div>

        <!-- Grid mode: filename -->
        <div
          v-else
          class="gallery-item__filename"
          :title="item.name"
        >
          {{ item.name }}
        </div>

        <!-- Metadata -->
        <div class="gallery-item__metadata">
          <span class="gallery-item__size">{{ formatFileSize(item.size) }}</span>
          <span class="gallery-item__date">{{ formatDate(item.date_added) }}</span>
          <span
            v-if="item.tags?.length"
            class="gallery-item__tags"
          >
            {{ item.tags.slice(0, 2).join(', ') }}{{ item.tags.length > 2 ? '...' : '' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Hover actions (grid mode) -->
    <div
      v-if="viewMode === 'grid' && showActions"
      class="gallery-item__actions"
    >
      <button
        @click.stop="handleFavorite"
        class="gallery-item__action-btn"
        :class="{ 'gallery-item__action-btn--active': item.is_favorite }"
        :aria-label="item.is_favorite ? 'Remove from favorites' : 'Add to favorites'"
      >
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
        </svg>
      </button>

      <button
        @click.stop="handleShare"
        class="gallery-item__action-btn"
        aria-label="Share asset"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
        </svg>
      </button>

      <button
        @click.stop="handleDownload"
        class="gallery-item__action-btn"
        aria-label="Download asset"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </button>

      <button
        @click.stop="handleDelete"
        class="gallery-item__action-btn gallery-item__action-btn--danger"
        aria-label="Delete asset"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Gallery Item Component
 *
 * Individual asset item in the virtualized gallery grid/list view.
 * Supports selection, hover actions, and keyboard navigation.
 */

import { computed } from 'vue'
import type { GalleryItem } from '@/stores/galleryStore'

// Props
const props = withDefaults(defineProps<{
  item: GalleryItem
  index: number
  viewMode: 'grid' | 'list'
  isSelected: boolean
  showSelection?: boolean
  showActions?: boolean
}>(), {
  showSelection: true,
  showActions: true
})

// Emits
const emit = defineEmits<{
  select: [item: GalleryItem, index: number]
  open: [item: GalleryItem]
  favorite: [item: GalleryItem]
  share: [item: GalleryItem]
  download: [item: GalleryItem]
  delete: [item: GalleryItem]
}>()

// Computed
const fileExtension = computed(() => {
  const name = props.item.name || ''
  const lastDot = name.lastIndexOf('.')
  return lastDot > 0 ? name.substring(lastDot + 1).toLowerCase() : ''
})

// Methods
const handleClick = (event: MouseEvent) => {
  // If clicking on checkbox or action buttons, don't open item
  if ((event.target as HTMLElement).closest('.gallery-item__checkbox, .gallery-item__actions')) {
    return
  }

  emit('open', props.item)
}

const handleKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault()
      if (event.ctrlKey || event.metaKey) {
        handleSelect()
      } else {
        emit('open', props.item)
      }
      break
  }
}

const handleSelect = () => {
  emit('select', props.item, props.index)
}

const handleFavorite = () => {
  emit('favorite', props.item)
}

const handleShare = () => {
  emit('share', props.item)
}

const handleDownload = () => {
  emit('download', props.item)
}

const handleDelete = () => {
  emit('delete', props.item)
}

const handleFocus = () => {
  // Could emit focus event for virtual scroller
}

const handleBlur = () => {
  // Could emit blur event for virtual scroller
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'

  // Show placeholder
  const placeholder = img.parentElement?.querySelector('.gallery-item__image-placeholder') as HTMLElement
  if (placeholder) {
    placeholder.style.display = 'flex'
  }
}

const handleVideoLoad = (event: Event) => {
  // Video loaded successfully
}

const handleVideoError = (event: Event) => {
  const video = event.target as HTMLVideoElement
  video.style.display = 'none'

  // Show placeholder
  const placeholder = video.parentElement?.querySelector('.gallery-item__video-placeholder') as HTMLElement
  if (placeholder) {
    placeholder.style.display = 'flex'
  }
}

const getFileIcon = (mimeType: string): string => {
  if (!mimeType) return '📄'

  if (mimeType.startsWith('image/')) return '🖼️'
  if (mimeType.startsWith('video/')) return '🎥'
  if (mimeType.startsWith('audio/')) return '🎵'

  // Documents
  if (mimeType.includes('pdf')) return '📄'
  if (mimeType.includes('word') || mimeType.includes('document')) return '📝'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return '📊'
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return '📽️'

  // Archives
  if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('7z')) return '📦'

  // Text files
  if (mimeType.startsWith('text/')) return '📄'

  return '📄'
}

const formatFileSize = (bytes: number): string => {
  if (!bytes || bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (dateString: string): string => {
  if (!dateString) return ''

  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return 'Today'
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
      })
    }
  } catch (error) {
    return dateString
  }
}

const getAriaLabel = (): string => {
  const parts = [
    props.item.name,
    formatFileSize(props.item.size),
    `Created ${formatDate(props.item.date_added)}`
  ]

  if (props.item.tags?.length) {
    parts.push(`Tags: ${props.item.tags.join(', ')}`)
  }

  if (props.isSelected) {
    parts.unshift('Selected')
  }

  return parts.join(', ')
}
</script>

<style scoped>
.gallery-item {
  @apply relative cursor-pointer transition-all duration-200;
  @apply bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700;
}

.gallery-item--grid {
  @apply rounded-lg overflow-hidden hover:shadow-lg hover:scale-[1.02];
}

.gallery-item--list {
  @apply rounded-none border-b border-l-0 border-r-0 first:border-t;
  @apply hover:bg-neutral-50 dark:hover:bg-neutral-700/50;
}

.gallery-item--selected {
  @apply ring-2 ring-primary-500 ring-offset-2;
}

.gallery-item:focus {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
}

.gallery-item__checkbox {
  @apply absolute top-2 left-2 z-10;
}

.gallery-item__checkbox-input {
  @apply w-5 h-5 text-primary-600 bg-white border-neutral-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-neutral-800 focus:ring-2 dark:bg-neutral-700 dark:border-neutral-600;
}

.gallery-item__content {
  @apply relative;
}

.gallery-item__preview {
  @apply relative overflow-hidden;
}

.gallery-item--grid .gallery-item__preview {
  @apply aspect-square;
}

.gallery-item--list .gallery-item__preview {
  @apply w-16 h-16 flex-shrink-0;
}

.gallery-item__image-container,
.gallery-item__video-container,
.gallery-item__file-container {
  @apply w-full h-full flex items-center justify-center bg-neutral-100 dark:bg-neutral-700;
}

.gallery-item__image {
  @apply w-full h-full object-cover;
}

.gallery-item__image-placeholder,
.gallery-item__video-placeholder {
  @apply w-full h-full flex items-center justify-center;
}

.gallery-item__video {
  @apply w-full h-full object-cover;
}

.gallery-item__play-icon {
  @apply absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 text-white opacity-0 transition-opacity;
}

.gallery-item:hover .gallery-item__play-icon {
  @apply opacity-100;
}

.gallery-item__file-icon {
  @apply text-4xl;
}

.gallery-item__badges {
  @apply absolute top-2 right-2 flex flex-col space-y-1;
}

.gallery-item__badge {
  @apply px-2 py-1 text-xs font-medium rounded;
}

.gallery-item__badge--processing {
  @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400;
}

.gallery-item__badge--favorite {
  @apply bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400;
}

.gallery-item__info {
  @apply p-3;
}

.gallery-item--list .gallery-item__info {
  @apply flex-1 flex items-center space-x-3 p-4;
}

.gallery-item__list-header {
  @apply flex items-center space-x-3 mb-2;
}

.gallery-item__filename {
  @apply text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate;
}

.gallery-item--grid .gallery-item__filename {
  @apply text-sm;
}

.gallery-item--list .gallery-item__filename {
  @apply flex-1 text-base;
}

.gallery-item__metadata {
  @apply flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-neutral-500 dark:text-neutral-400;
}

.gallery-item--list .gallery-item__metadata {
  @apply flex-col items-start gap-x-0 gap-y-1;
}

.gallery-item__size,
.gallery-item__date,
.gallery-item__tags {
  @apply truncate;
}

.gallery-item__actions {
  @apply absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center space-x-3 opacity-0 transition-opacity;
}

.gallery-item:hover .gallery-item__actions {
  @apply opacity-100;
}

.gallery-item__action-btn {
  @apply p-3 rounded-full bg-white hover:bg-neutral-100 text-neutral-700 transition-colors;
  @apply focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-black;
}

.gallery-item__action-btn--active {
  @apply text-red-600;
}

.gallery-item__action-btn--danger {
  @apply text-red-600 hover:bg-red-50;
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .gallery-item {
    @apply border-2;
  }

  .gallery-item--selected {
    @apply ring-4;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .gallery-item {
    @apply transition-none;
  }

  .gallery-item__actions {
    @apply transition-none;
  }

  .gallery-item__play-icon {
    @apply transition-none;
  }
}

/* Focus visible */
.gallery-item:focus-visible {
  @apply ring-2 ring-primary-500 ring-offset-2;
}
</style>




