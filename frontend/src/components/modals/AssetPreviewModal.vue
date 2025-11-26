<template>
  <Modal
    :isOpen="isOpen"
    title="Asset preview"
    size="full"
    @close="handleClose"
  >
    <div class="asset-preview-modal">
      <div
        class="asset-preview-modal__viewer"
        ref="viewerRef"
        @wheel.prevent="handleWheel"
        @pointerdown.prevent="handlePointerDown"
        @touchstart.passive="handleTouchStart"
        @touchend.passive="handleTouchEnd"
      >
        <div class="asset-preview-modal__media-frame">
          <button
            type="button"
            class="asset-preview-modal__nav asset-preview-modal__nav--prev"
            :disabled="!hasPrevious"
            @click="previousAsset"
            aria-label="Previous asset"
          >
            <i class="icon icon-chevron-left" aria-hidden="true" />
          </button>
          <button
            type="button"
            class="asset-preview-modal__nav asset-preview-modal__nav--next"
            :disabled="!hasNext"
            @click="nextAsset"
            aria-label="Next asset"
          >
            <i class="icon icon-chevron-right" aria-hidden="true" />
          </button>

          <div
            class="asset-preview-modal__media-transform"
            :style="mediaTransform"
            @dblclick.prevent="resetView"
            ref="mediaWrapperRef"
          >
            <img
              v-if="isImage"
              :src="mediaUrl"
              :alt="currentAsset?.label || currentAsset?.filename || 'Asset preview'"
              class="asset-preview-modal__image"
              draggable="false"
              loading="lazy"
            />
            <video
              v-else-if="isVideo"
              ref="videoRef"
              :src="mediaUrl"
              class="asset-preview-modal__video"
              controls
              playsinline
              muted
            />
            <iframe
              v-else-if="isPdf"
              :src="mediaUrl"
              class="asset-preview-modal__pdf"
              frameborder="0"
              title="Document preview"
            />
            <div v-else class="asset-preview-modal__placeholder">
              <p>No preview available</p>
            </div>
          </div>
        </div>

        <div class="asset-preview-modal__toolbar" role="toolbar" aria-label="Zoom and rotation controls">
          <button
            type="button"
            class="asset-preview-modal__tool"
            :disabled="scale <= 1"
            @click="zoomOut"
            aria-label="Zoom out"
          >
            <i class="icon icon-search-minus" aria-hidden="true" />
          </button>
          <button
            type="button"
            class="asset-preview-modal__tool"
            :disabled="scale >= maxScale"
            @click="zoomIn"
            aria-label="Zoom in"
          >
            <i class="icon icon-search-plus" aria-hidden="true" />
          </button>
          <button type="button" class="asset-preview-modal__tool" @click="resetView" aria-label="Reset zoom">
            <i class="icon icon-reload" aria-hidden="true" />
          </button>
          <div class="asset-preview-modal__zoom-label">{{ zoomLabel }}</div>
          <button type="button" class="asset-preview-modal__tool" @click="rotateLeft" aria-label="Rotate left">
            <i class="icon icon-rotate-left" aria-hidden="true" />
          </button>
          <button type="button" class="asset-preview-modal__tool" @click="rotateRight" aria-label="Rotate right">
            <i class="icon icon-rotate-right" aria-hidden="true" />
          </button>
        </div>
      </div>

      <p class="sr-only" role="status" aria-live="polite">{{ assetStatusMessage }}</p>

      <section class="asset-preview-modal__details">
        <header class="asset-preview-modal__details-header">
          <div>
            <p class="asset-preview-modal__asset-name">
              {{ currentAsset?.label || currentAsset?.filename || 'Untitled asset' }}
            </p>
            <p class="asset-preview-modal__asset-meta">
              {{ assetTypeLabel }} · {{ formatBytes(currentAsset?.size) }}
            </p>
          </div>
          <span class="asset-preview-modal__asset-counter">{{ assetCounter }}</span>
        </header>

        <div class="asset-preview-modal__meta-grid">
          <div
            v-for="entry in metadataEntries"
            :key="entry.label"
            class="asset-preview-modal__meta-item"
          >
            <p class="asset-preview-modal__meta-label">{{ entry.label }}</p>
            <p class="asset-preview-modal__meta-value">{{ entry.value }}</p>
          </div>
        </div>

        <div v-if="exifEntries.length" class="asset-preview-modal__exif">
          <p class="asset-preview-modal__exif-title">EXIF data</p>
          <ul class="asset-preview-modal__exif-list">
            <li
              v-for="entry in exifEntries"
              :key="entry.label"
              class="asset-preview-modal__exif-item"
            >
              <span class="asset-preview-modal__exif-key">{{ entry.label }}</span>
              <span class="asset-preview-modal__exif-value">{{ entry.value }}</span>
            </li>
          </ul>
        </div>
      </section>

      <section class="asset-preview-modal__actions">
        <Button variant="ghost" size="md" @click="copyShareLink" :loading="isCopying">
          <i class="icon icon-link" aria-hidden="true" />
          <span>Copy share link</span>
        </Button>
        <span v-if="copyFeedback" class="asset-preview-modal__copy-feedback">{{ copyFeedback }}</span>
        <Button variant="primary" size="md" @click="downloadAsset">
          <i class="icon icon-download" aria-hidden="true" />
          <span>Download</span>
        </Button>
      </section>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import { useUIStore } from '@/stores/uiStore'
import type { Asset } from '@/types/api'

interface Props {
  isOpen: boolean
  assets: Asset[]
  startIndex?: number
}

const props = withDefaults(defineProps<Props>(), {
  startIndex: 0
})

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  close: []
}>()

const uiStore = useUIStore()

const currentIndex = ref(clamp(props.startIndex ?? 0, 0, props.assets.length - 1))
const scale = ref(1)
const rotation = ref(0)
const translate = ref({ x: 0, y: 0 })
const mediaWrapperRef = ref<HTMLElement | null>(null)
const viewerRef = ref<HTMLElement | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)
const pointerStart = ref<{ x: number; y: number } | null>(null)
const lastTranslate = ref({ x: 0, y: 0 })
const isPanning = ref(false)
const touchStartX = ref<number | null>(null)
const copyFeedback = ref('')
const isCopying = ref(false)

const minScale = 1
const maxScale = 4
const zoomStep = 0.25

const currentAsset = computed(() => props.assets[currentIndex.value] ?? null)
const hasNext = computed(() => props.assets.length > 0 && currentIndex.value < props.assets.length - 1)
const hasPrevious = computed(() => currentIndex.value > 0)
const assetCounter = computed(() => {
  if (!props.assets.length) return '0 of 0'
  return `${currentIndex.value + 1} of ${props.assets.length}`
})
const assetStatusMessage = computed(() => {
  if (!currentAsset.value) return 'No asset selected'
  return `Viewing asset ${currentIndex.value + 1} of ${props.assets.length}`
})
const assetTypeLabel = computed(() => {
  const mime = currentAsset.value?.mime_type ?? ''
  if (mime.startsWith('image/')) return 'Image'
  if (mime.startsWith('video/')) return 'Video'
  if (mime.includes('pdf')) return 'Document'
  return 'Asset'
})
const mediaUrl = computed(() => {
  return (
    currentAsset.value?.preview_url ||
    currentAsset.value?.thumbnail_url ||
    ''
  )
})
const isImage = computed(() => currentAsset.value?.mime_type.startsWith('image/') ?? false)
const isVideo = computed(() => currentAsset.value?.mime_type.startsWith('video/') ?? false)
const isPdf = computed(
  () => currentAsset.value?.mime_type?.includes('pdf') ?? false
)

const metadataEntries = computed(() => {
  const asset = currentAsset.value
  if (!asset) return []
  const list: Array<{ label: string; value: string }> = []
  if (asset.filename) {
    list.push({
      label: 'Filename',
      value: asset.filename
    })
  }
  if (asset.mime_type) {
    list.push({
      label: 'MIME type',
      value: asset.mime_type
    })
  }
  if (asset.size) {
    list.push({
      label: 'Size',
      value: formatBytes(asset.size)
    })
  }
  if (asset.date_added) {
    list.push({
      label: 'Added',
      value: formatDate(asset.date_added)
    })
  }
  const metadata = asset.metadata as Record<string, unknown> | undefined
  const dimensions = (metadata?.dimensions ?? {}) as {
    width?: number
    height?: number
  }
  if (dimensions.width && dimensions.height) {
    list.push({
      label: 'Dimensions',
      value: `${dimensions.width} × ${dimensions.height}`
    })
  }
  return list
})

const exifEntries = computed(() => {
  const asset = currentAsset.value
  if (!asset) return []
  const metadata = asset.metadata as Record<string, unknown> | undefined
  const exif = metadata?.exif
  if (!exif || typeof exif !== 'object') return []
  return Object.entries(exif)
    .slice(0, 6)
    .map(([key, value]) => ({
      label: startCase(key),
      value: String(value ?? '—')
    }))
})

const mediaTransform = computed(() => {
  return {
    transform: `translate(${translate.value.x}px, ${translate.value.y}px) scale(${scale.value}) rotate(${rotation.value}deg)`
  }
})

const zoomLabel = computed(() => `${Math.round(scale.value * 100)}%`)

watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      currentIndex.value = clamp(props.startIndex ?? 0, 0, props.assets.length - 1)
      resetView()
      window.addEventListener('keydown', handleKeydown)
    } else {
      window.removeEventListener('keydown', handleKeydown)
      stopPanning()
    }
  },
  { immediate: true }
)

watch(
  () => props.assets,
  (assets) => {
    if (!assets.length) {
      currentIndex.value = 0
      return
    }
    currentIndex.value = Math.min(currentIndex.value, assets.length - 1)
  }
)

watch(currentAsset, () => {
  resetView()
  copyFeedback.value = ''
})

function handleClose(): void {
  resetView()
  emit('update:isOpen', false)
  emit('close')
}

function nextAsset(): void {
  if (!hasNext.value) return
  currentIndex.value += 1
}

function previousAsset(): void {
  if (!hasPrevious.value) return
  currentIndex.value -= 1
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), Math.max(min, max))
}

function resetView(): void {
  scale.value = 1
  translationReset()
  rotation.value = 0
  pointerStart.value = null
  isPanning.value = false
  lastTranslate.value = { x: 0, y: 0 }
}

function translationReset(): void {
  translate.value = { x: 0, y: 0 }
}

function zoomIn(): void {
  scale.value = clamp(scale.value + zoomStep, minScale, maxScale)
}

function zoomOut(): void {
  scale.value = clamp(scale.value - zoomStep, minScale, maxScale)
  if (scale.value === 1) {
    translationReset()
  }
}

function rotateRight(): void {
  rotation.value = (rotation.value + 90) % 360
}

function rotateLeft(): void {
  rotation.value = (rotation.value - 90 + 360) % 360
}

function handleWheel(event: WheelEvent): void {
  if (event.deltaY === 0) return
  const direction = event.deltaY > 0 ? -1 : 1
  scale.value = clamp(scale.value + direction * zoomStep, minScale, maxScale)
  if (scale.value === 1) {
    translationReset()
  }
}

function handlePointerDown(event: PointerEvent): void {
  if (scale.value <= 1) return
  pointerStart.value = { x: event.clientX, y: event.clientY }
  lastTranslate.value = { ...translate.value }
  isPanning.value = true
  window.addEventListener('pointermove', handlePointerMove)
  window.addEventListener('pointerup', stopPanning)
}

function handlePointerMove(event: PointerEvent): void {
  if (!isPanning.value || !pointerStart.value) return
  const deltaX = event.clientX - pointerStart.value.x
  const deltaY = event.clientY - pointerStart.value.y
  translate.value = {
    x: lastTranslate.value.x + deltaX,
    y: lastTranslate.value.y + deltaY
  }
}

function stopPanning(): void {
  if (!isPanning.value) return
  isPanning.value = false
  pointerStart.value = null
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerup', stopPanning)
}

function handleTouchStart(event: TouchEvent): void {
  if (event.touches.length !== 1) return
  const touch = event.touches[0]
  if (!touch) return
  touchStartX.value = touch.clientX
}

function handleTouchEnd(event: TouchEvent): void {
  if (touchStartX.value === null || event.changedTouches.length !== 1) return
  const touch = event.changedTouches[0]
  if (!touch) {
    touchStartX.value = null
    return
  }
  const deltaX = touch.clientX - touchStartX.value
  const threshold = 40
  if (Math.abs(deltaX) < threshold) {
    touchStartX.value = null
    return
  }
  if (deltaX < 0) {
    nextAsset()
  } else {
    previousAsset()
  }
  touchStartX.value = null
}

function handleKeydown(event: KeyboardEvent): void {
  if (!props.isOpen) return
  const target = event.target as HTMLElement
  const ignoreTags = ['INPUT', 'TEXTAREA', 'SELECT']
  if (
    target &&
    (ignoreTags.includes(target.tagName) || target.isContentEditable)
  ) {
    return
  }

  switch (event.key) {
    case 'ArrowRight':
      event.preventDefault()
      nextAsset()
      break
    case 'ArrowLeft':
      event.preventDefault()
      previousAsset()
      break
    case 'Escape':
      handleClose()
      break
    case ' ':
      if (isVideo.value && videoRef.value) {
        event.preventDefault()
        toggleVideoPlayback()
      }
      break
    default:
  }
}

function toggleVideoPlayback(): void {
  if (!videoRef.value) return
  if (videoRef.value.paused) {
    videoRef.value.play().catch(() => {
      /* ignore */
    })
  } else {
    videoRef.value.pause()
  }
}

function resolveAssetUrl(asset: Asset): string {
  return (
    asset.preview_url ||
    asset.thumbnail_url ||
    `/api/v4/dam/assets/${asset.id}/download/`
  )
}

function downloadAsset(): void {
  if (!currentAsset.value) return
  const url = resolveAssetUrl(currentAsset.value)
  if (!url) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Download link is unavailable.'
    })
    return
  }
  const link = document.createElement('a')
  link.href = url
  link.download = currentAsset.value.filename || currentAsset.value.label || 'asset'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  uiStore.addNotification({
    type: 'success',
    title: 'Download started',
    message: 'The download should begin shortly.'
  })
}

async function copyShareLink(): Promise<void> {
  if (!currentAsset.value) return
  const url = resolveAssetUrl(currentAsset.value)
  if (!url) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'No shareable link available.'
    })
    return
  }
  isCopying.value = true
  try {
    await copyToClipboard(url)
    copyFeedback.value = 'Link copied!'
    uiStore.addNotification({
      type: 'success',
      message: 'Share link copied'
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to copy link.'
    })
    console.error('Copy share link failed', error)
  } finally {
    isCopying.value = false
  }
}

async function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(text)
    return
  }
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.top = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

function startCase(value: string): string {
  return value
    .replace(/_/g, ' ')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatBytes(bytes?: number): string {
  if (!bytes || bytes <= 0) return '—'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let value = bytes
  let index = 0
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024
    index += 1
  }
  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`
}

function formatDate(value?: string): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  stopPanning()
})
</script>

<style scoped lang="css">
:global(.sr-only) {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.asset-preview-modal {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.asset-preview-modal__viewer {
  position: relative;
  background: var(--color-bg-600, #0f172a);
  border-radius: 1rem;
  overflow: hidden;
  min-height: 60vh;
}

.asset-preview-modal__media-frame {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #020617;
}

.asset-preview-modal__media-transform {
  transition: transform 0.2s ease;
  will-change: transform;
  max-width: 100%;
  max-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.asset-preview-modal__image,
.asset-preview-modal__video,
.asset-preview-modal__pdf {
  max-width: 100%;
  max-height: 100%;
  display: block;
  border-radius: 0.5rem;
  user-select: none;
  pointer-events: none;
}

.asset-preview-modal__video,
.asset-preview-modal__pdf {
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: auto;
}

.asset-preview-modal__placeholder {
  color: #94a3b8;
  font-size: 1rem;
  text-align: center;
}

.asset-preview-modal__nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: rgba(15, 23, 42, 0.7);
  color: #fff;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease;
}

.asset-preview-modal__nav:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.asset-preview-modal__nav--prev {
  left: 1rem;
}

.asset-preview-modal__nav--next {
  right: 1rem;
}

.asset-preview-modal__toolbar {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.7);
  padding: 0.5rem 0.75rem;
  border-radius: 999px;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.5);
}

.asset-preview-modal__tool {
  border: none;
  background: transparent;
  color: #e2e8f0;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.asset-preview-modal__tool:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.asset-preview-modal__tool:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.asset-preview-modal__zoom-label {
  font-size: 0.85rem;
  color: #f8fafc;
  min-width: 48px;
  text-align: center;
}

.asset-preview-modal__details {
  padding: 0 0.5rem 0.25rem;
}

.asset-preview-modal__details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.asset-preview-modal__asset-name {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text, #0f172a);
}

.asset-preview-modal__asset-meta {
  margin: 0.25rem 0 0;
  color: #475569;
  font-size: 0.95rem;
}

.asset-preview-modal__asset-counter {
  font-size: 0.95rem;
  color: #64748b;
}

.asset-preview-modal__meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.asset-preview-modal__meta-item {
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: var(--color-bg-100, #f8fafc);
  border: 1px solid #e2e8f0;
}

.asset-preview-modal__meta-label {
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.asset-preview-modal__meta-value {
  margin: 0.25rem 0 0;
  font-size: 0.95rem;
  font-weight: 500;
  color: #0f172a;
}

.asset-preview-modal__exif {
  margin-top: 1rem;
  background: var(--color-bg-50, #fff);
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1rem;
}

.asset-preview-modal__exif-title {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
}

.asset-preview-modal__exif-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.asset-preview-modal__exif-item {
  flex: 1 1 180px;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  background: #0f172a;
  color: #f8fafc;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
}

.asset-preview-modal__exif-key {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #94a3b8;
}

.asset-preview-modal__exif-value {
  font-size: 0.85rem;
  font-weight: 500;
}

.asset-preview-modal__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.asset-preview-modal__copy-feedback {
  font-size: 0.9rem;
  color: #10b981;
}

.asset-preview-modal__actions .icon {
  margin-right: 0.35rem;
}

.asset-preview-modal__actions button {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}
</style>

