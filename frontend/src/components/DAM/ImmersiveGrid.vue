<template>
  <div ref="gridContainerRef" class="immersive-grid-container">
    <div
      ref="scrollRef"
      class="immersive-grid-scroll"
      role="list"
      :aria-label="`Галерея активов (${density} density, виртуальная прокрутка)`"
      @scroll="onScroll"
      @mousedown="onGridMouseDown"
      @mousemove="onGridMouseMove"
      @mouseup="onGridMouseUp"
      @mouseleave="onGridMouseUp"
    >
      <div
        :style="{
          minHeight: hasMore ? `${virtualizer.getTotalSize() + 48}px` : `${virtualizer.getTotalSize()}px`,
          width: '100%',
        }"
      >
        <div
          :style="{
            height: `${virtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }"
        >
        <div
          v-for="row in virtualizer.getVirtualItems()"
          :key="String(row.key)"
          :data-index="row.index"
          :style="{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: `${row.size}px`,
            transform: `translateY(${row.start}px)`,
            display: 'grid',
            gridTemplateColumns: `repeat(${columns}, 1fr)`,
            gap: density === 'compact' ? '8px' : '24px',
          }"
          class="w-full h-full"
        >
          <template v-for="colIdx in columns" :key="colIdx">
            <div
              v-if="getAssetAtIndex(row.index * columns + (colIdx - 1))"
              :data-global-index="row.index * columns + (colIdx - 1)"
              class="immersive-grid-cell"
              role="listitem"
              @mousedown="onCellMouseDown($event, row.index * columns + (colIdx - 1))"
            >
              <AssetCard
                :asset="getAssetAtIndex(row.index * columns + (colIdx - 1))!"
                :is-selected="isAssetSelected(getAssetAtIndex(row.index * columns + (colIdx - 1))!)"
                :is-shared="isAssetShared(getAssetAtIndex(row.index * columns + (colIdx - 1))!.id)"
                :show-checkbox="true"
                :density="density"
                :data-index="row.index * columns + (colIdx - 1)"
                @select="(a: Asset, e?: MouseEvent) => handleAssetSelect(a, row.index * columns + (colIdx - 1), e)"
                @open="handleAssetOpen"
                @preview="handleAssetPreview"
                @download="handleAssetDownload"
                @share="handleAssetShare"
                @delete="handleAssetDelete"
                @add-tags="handleAssetAddTags"
                @move="handleAssetMove"
                @more="handleAssetMore"
                @contextmenu="(p) => emit('asset-contextmenu', p.asset, p.event)"
              />
            </div>
            <div
              v-else-if="row.index * columns + (colIdx - 1) < assets.length || (hasMore && isLoadingMore)"
              class="immersive-grid-cell"
              role="listitem"
            >
              <AssetCardSkeleton :density="density" />
            </div>
          </template>
        </div>
        </div>
      <!-- Infinite scroll sentinel (inside scroll so it appears when scrolling down) -->
      <div
        v-if="hasMore"
        ref="sentinelRef"
        class="w-full h-12 flex items-center justify-center flex-shrink-0"
        aria-live="polite"
      >
        <div
          v-if="isLoadingMore"
          class="flex items-center gap-2 text-sm text-neutral-500 dark:text-neutral-400"
        >
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600" />
          <span>Загрузка...</span>
        </div>
      </div>
      </div>
    </div>

    <!-- Drag-select overlay -->
    <div
      v-if="dragSelectRect"
      class="immersive-drag-select-overlay"
      :style="{
        left: `${dragSelectRect.x}px`,
        top: `${dragSelectRect.y}px`,
        width: `${dragSelectRect.width}px`,
        height: `${dragSelectRect.height}px`,
      }"
    />

    <!-- Scroll-to-top button -->
    <transition name="fade">
      <button
        v-if="showScrollTop"
        type="button"
        class="fixed bottom-6 right-6 z-40 p-3 rounded-full bg-primary-600 text-white
               shadow-lg hover:bg-primary-700 transition-colors focus:outline-none
               focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        aria-label="Наверх"
        @click="scrollToTop"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      </button>
    </transition>
  </div>
</template>

<script setup lang="ts">
/**
 * ImmersiveGrid: virtualized grid for 10k+ assets using @tanstack/vue-virtual.
 * Renders only visible rows; each row contains up to `columns` AssetCards.
 * Supports infinite scroll, Shift+Click range selection, and index-based drag-select.
 */

import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useVirtualizer } from '@tanstack/vue-virtual'
import { useElementSize } from '@vueuse/core'
import AssetCard from './AssetCard.vue'
import AssetCardSkeleton from './AssetCardSkeleton.vue'
import type { Asset } from '@/types/api'
import { useAssetStore } from '@/stores/assetStore'
import { useDistributionStore } from '@/stores/distributionStore'

const ROW_HEIGHT_COMPACT = 200
const ROW_HEIGHT_COMFORTABLE = 280
const GAP_COMPACT = 8
const GAP_COMFORTABLE = 24

interface Props {
  assets: Asset[]
  density?: 'compact' | 'comfortable'
  layout?: 'grid' | 'masonry'
  hasMore?: boolean
  isLoadingMore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  density: 'comfortable',
  layout: 'grid',
  hasMore: false,
  isLoadingMore: false,
})

const emit = defineEmits<{
  'asset-select': [asset: Asset, index: number]
  'asset-open': [asset: Asset]
  'asset-preview': [asset: Asset]
  'asset-download': [asset: Asset]
  'asset-share': [asset: Asset]
  'asset-delete': [asset: Asset]
  'asset-add-tags': [asset: Asset]
  'asset-move': [asset: Asset]
  'asset-more': [asset: Asset]
  'asset-contextmenu': [asset: Asset, event: MouseEvent]
  'load-more': []
}>()

const assetStore = useAssetStore()
const distributionStore = useDistributionStore()

const gridContainerRef = ref<HTMLElement | null>(null)
const scrollRef = ref<HTMLElement | null>(null)
const sentinelRef = ref<HTMLElement | null>(null)

const { width: containerWidth } = useElementSize(gridContainerRef, { width: 0, height: 0 })

const columns = computed(() => {
  const w = containerWidth.value || 800
  if (props.density === 'compact') {
    if (w >= 1536) return 8
    if (w >= 1280) return 6
    if (w >= 1024) return 5
    if (w >= 768) return 4
    if (w >= 640) return 3
    return 2
  }
  if (w >= 1280) return 5
  if (w >= 1024) return 4
  if (w >= 768) return 3
  if (w >= 640) return 2
  return 1
})

const rowHeight = computed(() => {
  const base = props.density === 'compact' ? ROW_HEIGHT_COMPACT : ROW_HEIGHT_COMFORTABLE
  const gap = props.density === 'compact' ? GAP_COMPACT : GAP_COMFORTABLE
  return base + gap
})

const rowCount = computed(() => Math.ceil(props.assets.length / columns.value))

const virtualizer = useVirtualizer({
  count: rowCount as unknown as number,
  getScrollElement: () => scrollRef.value,
  estimateSize: () => rowHeight.value,
  overscan: 3,
})

function getAssetAtIndex(index: number): Asset | undefined {
  return props.assets[index]
}

const lastSelectedIndex = ref<number | null>(null)

function isAssetSelected(asset: Asset): boolean {
  return assetStore.selectedAssets.has(asset.id)
}

function isAssetShared(assetId: number): boolean {
  return distributionStore.sharedAssetIds.has(assetId)
}

function handleAssetSelect(asset: Asset, index: number, event?: MouseEvent) {
  const isShiftClick = event?.shiftKey && lastSelectedIndex.value !== null

  if (isShiftClick) {
    const start = Math.min(lastSelectedIndex.value!, index)
    const end = Math.max(lastSelectedIndex.value!, index)
    for (let i = start; i <= end; i++) {
      const a = props.assets[i]
      if (a && !assetStore.selectedAssets.has(a.id)) {
        assetStore.toggleSelection(a.id)
      }
    }
  } else {
    assetStore.selectAsset(asset, true)
    lastSelectedIndex.value = index
  }
  emit('asset-select', asset, index)
}

function handleAssetOpen(asset: Asset) {
  emit('asset-open', asset)
}
function handleAssetPreview(asset: Asset) {
  emit('asset-preview', asset)
}
function handleAssetDownload(asset: Asset) {
  emit('asset-download', asset)
}
function handleAssetShare(asset: Asset) {
  emit('asset-share', asset)
}
function handleAssetDelete(asset: Asset) {
  emit('asset-delete', asset)
}
function handleAssetAddTags(asset: Asset) {
  emit('asset-add-tags', asset)
}
function handleAssetMove(asset: Asset) {
  emit('asset-move', asset)
}
function handleAssetMore(asset: Asset) {
  emit('asset-more', asset)
}

const showScrollTop = ref(false)
function onScroll() {
  if (!scrollRef.value) return
  showScrollTop.value = scrollRef.value.scrollTop > 600
}

function scrollToTop() {
  scrollRef.value?.scrollTo({ top: 0, behavior: 'smooth' })
}

let sentinelObserver: IntersectionObserver | null = null
function setupSentinelObserver() {
  sentinelObserver?.disconnect()
  if (!props.hasMore || !scrollRef.value) return
  sentinelObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting && !props.isLoadingMore) {
          emit('load-more')
        }
      }
    },
    { root: scrollRef.value, rootMargin: '300px 0px', threshold: 0 }
  )
  nextTick(() => {
    if (sentinelRef.value) sentinelObserver?.observe(sentinelRef.value)
  })
}

watch([() => props.hasMore, sentinelRef], () => {
  nextTick(() => setupSentinelObserver())
})

watch(
  () => [props.assets.length, columns.value, rowHeight.value],
  () => {
    nextTick(() => (virtualizer as { value?: { measure?: () => void } }).value?.measure?.())
  }
)

onMounted(() => {
  setupSentinelObserver()
})

onUnmounted(() => {
  sentinelObserver?.disconnect()
})

defineExpose({ scrollToTop })

// --- Drag-select (index-based) ---
interface DragRect {
  x: number
  y: number
  width: number
  height: number
  startX: number
  startY: number
}

const dragSelectRect = ref<DragRect | null>(null)
const dragSelectStartIndex = ref<number | null>(null)

function getGridBounds(): { top: number; left: number; cellWidth: number; cellHeight: number } | null {
  if (!scrollRef.value) return null
  const rect = scrollRef.value.getBoundingClientRect()
  const cellWidth = (scrollRef.value.clientWidth - 16) / columns.value
  return {
    top: rect.top - scrollRef.value.scrollTop,
    left: rect.left,
    cellWidth,
    cellHeight: rowHeight.value,
  }
}

function getIndexAtPoint(clientX: number, clientY: number): number | null {
  const bounds = getGridBounds()
  if (!bounds || !scrollRef.value) return null
  const localY = clientY - bounds.top
  const localX = clientX - bounds.left
  const col = Math.floor(localX / bounds.cellWidth)
  const row = Math.floor(localY / bounds.cellHeight)
  if (col < 0 || col >= columns.value || row < 0) return null
  const index = row * columns.value + col
  return index >= props.assets.length ? null : index
}

function onCellMouseDown(_e: MouseEvent, _index: number) {
  dragSelectStartIndex.value = null
  dragSelectRect.value = null
}

function onGridMouseDown(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.closest('.immersive-grid-cell') || target.closest('button')) return
  const index = getIndexAtPoint(e.clientX, e.clientY)
  dragSelectStartIndex.value = index
  dragSelectRect.value = {
    x: e.clientX,
    y: e.clientY,
    width: 0,
    height: 0,
    startX: e.clientX,
    startY: e.clientY,
  }
}

function onGridMouseMove(e: MouseEvent) {
  if (!dragSelectRect.value) return
  const rect = dragSelectRect.value
  let w = e.clientX - rect.startX
  let h = e.clientY - rect.startY
  let x = rect.startX
  let y = rect.startY
  if (w < 0) {
    x = e.clientX
    w = -w
  }
  if (h < 0) {
    y = e.clientY
    h = -h
  }
  dragSelectRect.value = { ...rect, x, y, width: w, height: h }
}

function onGridMouseUp() {
  if (!dragSelectRect.value || dragSelectStartIndex.value === null) {
    dragSelectRect.value = null
    dragSelectStartIndex.value = null
    return
  }
  const bounds = getGridBounds()
  if (!bounds || !scrollRef.value) {
    dragSelectRect.value = null
    dragSelectStartIndex.value = null
    return
  }
  const rect = dragSelectRect.value
  const scrollTop = scrollRef.value.scrollTop
  const top = Math.min(rect.y, rect.y + rect.height) - bounds.top + scrollTop
  const left = Math.min(rect.x, rect.x + rect.width) - bounds.left
  const bottom = top + rect.height
  const right = left + rect.width
  const startCol = Math.max(0, Math.floor(left / bounds.cellWidth))
  const endCol = Math.min(columns.value - 1, Math.floor(right / bounds.cellWidth))
  const startRow = Math.max(0, Math.floor(top / bounds.cellHeight))
  const endRow = Math.floor(bottom / bounds.cellHeight)
  for (let r = startRow; r <= endRow; r++) {
    for (let c = startCol; c <= endCol; c++) {
      const index = r * columns.value + c
      const asset = props.assets[index]
      if (asset && !assetStore.selectedAssets.has(asset.id)) {
        assetStore.toggleSelection(asset.id)
      }
    }
  }
  dragSelectRect.value = null
  dragSelectStartIndex.value = null
}
</script>

<style scoped>
.immersive-grid-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 0;
}

.immersive-grid-scroll {
  flex: 1;
  overflow: auto;
  height: calc(100vh - 200px);
  min-height: 400px;
}

.immersive-grid-cell {
  min-height: 0;
}

.immersive-drag-select-overlay {
  position: fixed;
  pointer-events: none;
  border: 2px solid theme('colors.primary.500');
  background: theme('colors.primary.500');
  opacity: 0.15;
  z-index: 30;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
