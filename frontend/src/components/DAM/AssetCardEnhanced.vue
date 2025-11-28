<template>
  <div
    :class="cardClasses"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click="handleClick"
    @dblclick="handleDoubleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
    role="button"
    tabindex="0"
    :aria-label="`Актив: ${asset.label}`"
    :aria-selected="isSelected"
  >
    <!-- Selection Checkbox -->
    <transition name="fade">
      <div
        v-if="isHovered || isSelected"
        class="asset-card__checkbox"
        @click.stop="emit('select', asset)"
      >
        <input
          type="checkbox"
          :checked="isSelected"
          class="asset-card__checkbox-input"
          @click.stop
          @change="emit('select', asset)"
          :aria-label="`Выбрать ${asset.label}`"
        />
      </div>
    </transition>
    
    <!-- Thumbnail Container -->
    <div class="asset-card__thumbnail">
      <!-- Image -->
      <img
        v-if="asset.thumbnail_url"
        :src="asset.thumbnail_url"
        :alt="asset.label"
        class="asset-card__image"
        loading="lazy"
        @error="handleImageError"
      />
      
      <!-- Fallback Icon -->
      <div v-else class="asset-card__fallback">
        <component :is="fileTypeIcon" class="asset-card__fallback-icon" />
      </div>
      
      <!-- File Type Badge -->
      <div class="asset-card__type-badge">
        <component :is="fileTypeIcon" class="w-3.5 h-3.5" />
      </div>
      
      <!-- Status Badge -->
      <div v-if="asset.metadata?.status" class="asset-card__status-badge">
        <span :class="['asset-card__status', `asset-card__status--${asset.metadata.status}`]">
          {{ statusLabel }}
        </span>
      </div>
      
      <!-- AI Badge -->
      <div v-if="hasAIAnalysis" class="asset-card__ai-badge" title="AI Analyzed">
        <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
        </svg>
      </div>
      
      <!-- Hover Overlay -->
      <transition name="fade">
        <div v-if="isHovered" class="asset-card__overlay">
          <div class="asset-card__actions">
            <button
              @click.stop="emit('preview', asset)"
              class="asset-card__action-btn"
              title="Просмотр"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </button>
            <button
              @click.stop="emit('download', asset)"
              class="asset-card__action-btn"
              title="Скачать"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
            </button>
            <button
              @click.stop="emit('share', asset)"
              class="asset-card__action-btn"
              title="Поделиться"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"/>
              </svg>
            </button>
          </div>
        </div>
      </transition>
      
      <!-- Video Duration -->
      <div v-if="isVideo && asset.metadata?.duration" class="asset-card__duration">
        {{ formatDuration(asset.metadata.duration as number) }}
      </div>
    </div>
    
    <!-- Info Section -->
    <div class="asset-card__info">
      <h3 class="asset-card__title" :title="asset.label">
        {{ asset.label }}
      </h3>
      
      <div class="asset-card__meta">
        <span class="asset-card__size">{{ formatFileSize(asset.size) }}</span>
        <span class="asset-card__date">{{ formatRelativeDate(asset.date_added) }}</span>
      </div>
      
      <!-- Tags Preview -->
      <div v-if="displayTags.length" class="asset-card__tags">
        <span
          v-for="tag in displayTags.slice(0, 2)"
          :key="tag"
          class="asset-card__tag"
        >
          {{ tag }}
        </span>
        <span v-if="displayTags.length > 2" class="asset-card__tag asset-card__tag--more">
          +{{ displayTags.length - 2 }}
        </span>
      </div>
    </div>
    
    <!-- List View Layout -->
    <template v-if="viewMode === 'list'">
      <div class="asset-card__list-actions">
        <button
          @click.stop="emit('preview', asset)"
          class="asset-card__list-action"
          title="Просмотр"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
        </button>
        <button
          @click.stop="emit('download', asset)"
          class="asset-card__list-action"
          title="Скачать"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
          </svg>
        </button>
        <button
          @click.stop="emit('delete', asset)"
          class="asset-card__list-action asset-card__list-action--danger"
          title="Удалить"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import type { Asset } from '@/types/api'
import { formatFileSize } from '@/utils/formatters'

// ============================================================================
// PROPS & EMITS
// ============================================================================

interface Props {
  asset: Asset
  isSelected?: boolean
  viewMode?: 'grid' | 'list'
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  viewMode: 'grid',
})

const emit = defineEmits<{
  select: [asset: Asset]
  open: [asset: Asset]
  preview: [asset: Asset]
  download: [asset: Asset]
  share: [asset: Asset]
  delete: [asset: Asset]
}>()

// ============================================================================
// STATE
// ============================================================================

const isHovered = ref(false)
const imageError = ref(false)

// ============================================================================
// COMPUTED
// ============================================================================

const cardClasses = computed(() => [
  'asset-card',
  props.viewMode === 'list' && 'asset-card--list',
  props.isSelected && 'asset-card--selected',
  isHovered.value && 'asset-card--hovered',
])

const fileType = computed(() => {
  const type = props.asset.metadata?.type as string
  if (type) return type
  
  const mime = props.asset.mime_type
  if (mime.startsWith('image/')) return 'image'
  if (mime.startsWith('video/')) return 'video'
  if (mime.startsWith('audio/')) return 'audio'
  if (mime.includes('pdf') || mime.includes('document') || mime.includes('spreadsheet') || mime.includes('presentation')) return 'document'
  return 'other'
})

const isVideo = computed(() => fileType.value === 'video')

const hasAIAnalysis = computed(() => 
  props.asset.ai_analysis?.status === 'completed'
)

const displayTags = computed(() => {
  const tags: string[] = []
  if (props.asset.tags) tags.push(...props.asset.tags)
  if (props.asset.ai_analysis?.tags) tags.push(...props.asset.ai_analysis.tags)
  return [...new Set(tags)]
})

const statusLabel = computed(() => {
  const statusMap: Record<string, string> = {
    approved: 'Одобрено',
    pending: 'На проверке',
    draft: 'Черновик',
    rejected: 'Отклонено',
  }
  const status = props.asset.metadata?.status as string
  return statusMap[status] || status
})

// File type icons as render functions
const fileTypeIcon = computed(() => {
  const icons: Record<string, any> = {
    image: () => h('svg', { class: 'w-full h-full', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' })
    ]),
    video: () => h('svg', { class: 'w-full h-full', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
    ]),
    audio: () => h('svg', { class: 'w-full h-full', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3' })
    ]),
    document: () => h('svg', { class: 'w-full h-full', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
    ]),
    other: () => h('svg', { class: 'w-full h-full', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z' })
    ]),
  }
  return icons[fileType.value] || icons.other
})

// ============================================================================
// METHODS
// ============================================================================

function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Сегодня'
  if (diffDays === 1) return 'Вчера'
  if (diffDays < 7) return `${diffDays} дн. назад`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} нед. назад`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} мес. назад`
  return `${Math.floor(diffDays / 365)} г. назад`
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function handleClick(): void {
  emit('select', props.asset)
}

function handleDoubleClick(): void {
  emit('open', props.asset)
}

function handleImageError(): void {
  imageError.value = true
}
</script>

<style scoped>
/* ============================================================================
   BASE CARD
   ============================================================================ */

.asset-card {
  @apply relative bg-white rounded-xl overflow-hidden;
  @apply border border-neutral-200 cursor-pointer;
  @apply transition-all duration-200 ease-out;
}

.asset-card:hover {
  @apply shadow-lg border-neutral-300;
  transform: translateY(-2px);
}

.asset-card:focus {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
}

.asset-card--selected {
  @apply ring-2 ring-primary-500 border-primary-500;
}

/* ============================================================================
   CHECKBOX
   ============================================================================ */

.asset-card__checkbox {
  @apply absolute top-3 left-3 z-20;
}

.asset-card__checkbox-input {
  @apply w-5 h-5 rounded border-2 border-white bg-white/80 backdrop-blur-sm;
  @apply text-primary-600 cursor-pointer;
  @apply focus:ring-2 focus:ring-primary-500 focus:ring-offset-0;
  @apply shadow-sm;
}

/* ============================================================================
   THUMBNAIL
   ============================================================================ */

.asset-card__thumbnail {
  @apply relative aspect-square bg-neutral-100 overflow-hidden;
}

.asset-card__image {
  @apply w-full h-full object-cover;
  @apply transition-transform duration-300;
}

.asset-card:hover .asset-card__image {
  @apply scale-105;
}

.asset-card__fallback {
  @apply w-full h-full flex items-center justify-center bg-neutral-100;
}

.asset-card__fallback-icon {
  @apply w-12 h-12 text-neutral-400;
}

/* ============================================================================
   BADGES
   ============================================================================ */

.asset-card__type-badge {
  @apply absolute bottom-3 left-3 z-10;
  @apply w-7 h-7 rounded-lg bg-white/90 backdrop-blur-sm shadow-sm;
  @apply flex items-center justify-center text-neutral-600;
}

.asset-card__status-badge {
  @apply absolute top-3 right-3 z-10;
}

.asset-card__status {
  @apply inline-flex px-2 py-0.5 rounded-full text-xs font-medium;
  @apply bg-white/90 backdrop-blur-sm shadow-sm;
}

.asset-card__status--approved { @apply text-green-700; }
.asset-card__status--pending { @apply text-yellow-700; }
.asset-card__status--draft { @apply text-neutral-600; }
.asset-card__status--rejected { @apply text-red-700; }

.asset-card__ai-badge {
  @apply absolute bottom-3 right-3 z-10;
  @apply w-6 h-6 rounded-full bg-purple-500 text-white;
  @apply flex items-center justify-center shadow-sm;
}

.asset-card__duration {
  @apply absolute bottom-3 right-3 z-10;
  @apply px-2 py-0.5 rounded bg-black/70 text-white text-xs font-medium;
}

/* ============================================================================
   OVERLAY & ACTIONS
   ============================================================================ */

.asset-card__overlay {
  @apply absolute inset-0 z-10;
  @apply bg-gradient-to-t from-black/60 via-black/20 to-transparent;
  @apply flex items-center justify-center;
}

.asset-card__actions {
  @apply flex items-center gap-2;
}

.asset-card__action-btn {
  @apply w-10 h-10 rounded-full bg-white/90 backdrop-blur-sm;
  @apply flex items-center justify-center text-neutral-700;
  @apply hover:bg-white hover:text-primary-600 hover:scale-110;
  @apply transition-all duration-200 shadow-lg;
}

/* ============================================================================
   INFO SECTION
   ============================================================================ */

.asset-card__info {
  @apply p-3;
}

.asset-card__title {
  @apply text-sm font-medium text-neutral-900 truncate mb-1;
}

.asset-card__meta {
  @apply flex items-center justify-between text-xs text-neutral-500;
}

.asset-card__tags {
  @apply flex items-center gap-1 mt-2 overflow-hidden;
}

.asset-card__tag {
  @apply inline-flex px-1.5 py-0.5 bg-neutral-100 text-neutral-600 rounded text-xs;
  @apply truncate max-w-[80px];
}

.asset-card__tag--more {
  @apply bg-primary-100 text-primary-600 flex-shrink-0;
}

/* ============================================================================
   LIST VIEW
   ============================================================================ */

.asset-card--list {
  @apply flex items-center gap-4 p-3;
}

.asset-card--list .asset-card__thumbnail {
  @apply w-16 h-16 flex-shrink-0 rounded-lg aspect-auto;
}

.asset-card--list .asset-card__info {
  @apply flex-1 p-0 min-w-0;
}

.asset-card--list .asset-card__type-badge,
.asset-card--list .asset-card__status-badge,
.asset-card--list .asset-card__ai-badge,
.asset-card--list .asset-card__duration,
.asset-card--list .asset-card__overlay {
  @apply hidden;
}

.asset-card__list-actions {
  @apply flex items-center gap-1 flex-shrink-0;
}

.asset-card__list-action {
  @apply w-8 h-8 rounded-lg text-neutral-400;
  @apply hover:bg-neutral-100 hover:text-neutral-700;
  @apply flex items-center justify-center transition-colors;
}

.asset-card__list-action--danger {
  @apply hover:bg-red-50 hover:text-red-600;
}

/* ============================================================================
   TRANSITIONS
   ============================================================================ */

.fade-enter-active,
.fade-leave-active {
  @apply transition-opacity duration-200;
}

.fade-enter-from,
.fade-leave-to {
  @apply opacity-0;
}
</style>

