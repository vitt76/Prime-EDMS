<template>
  <div ref="gridContainerRef" class="asset-grid-container">
    <div
      :class="gridClasses"
      role="list"
      :aria-label="`Галерея активов (${density} density)`"
    >
      <template v-for="(asset, index) in visibleAssets" :key="asset.id">
        <div
          ref="cardRefs"
          :data-asset-id="asset.id"
          :data-index="index"
          class="asset-grid-item"
          role="listitem"
        >
          <AssetCard
            v-if="observedSet.has(asset.id)"
            :asset="asset"
            :is-selected="isAssetSelected(asset)"
            :is-shared="isAssetShared(asset.id)"
            :show-checkbox="true"
            :density="density"
            :data-index="index"
            @select="(asset: Asset, event: MouseEvent) => handleAssetSelect(asset, index, event)"
            @open="handleAssetOpen"
            @preview="handleAssetPreview"
            @download="handleAssetDownload"
            @share="handleAssetShare"
            @delete="handleAssetDelete"
            @add-tags="handleAssetAddTags"
            @move="handleAssetMove"
            @contextmenu="(p) => emit('asset-contextmenu', p.asset, p.event)"
          />
          <!-- Skeleton placeholder for cards not yet observed -->
          <div
            v-else
            class="asset-grid-skeleton rounded-lg bg-neutral-200 dark:bg-neutral-700 animate-pulse"
            :class="density === 'compact' ? 'h-36' : 'h-52'"
          />
        </div>
      </template>
    </div>

    <!-- Infinite scroll sentinel -->
    <div
      v-if="hasMore"
      ref="sentinelRef"
      class="w-full h-12 flex items-center justify-center"
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

    <!-- Scroll-to-top button -->
    <transition name="fade">
      <button
        v-if="showScrollTop"
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
 * AssetGrid with Intersection Observer-based lazy rendering.
 *
 * For large collections (>100 assets), cards are only rendered when they
 * enter the viewport (with a generous rootMargin buffer). This keeps the
 * DOM lightweight while preserving the native CSS Grid layout.
 *
 * For infinite scroll, a sentinel element at the bottom triggers loading
 * of additional pages when it comes into view.
 */

import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import AssetCard from './AssetCard.vue'
import type { Asset } from '@/types/api'
import { useAssetStore } from '@/stores/assetStore'

interface Props {
  assets: Asset[]
  density?: 'compact' | 'comfortable'
  layout?: 'grid' | 'masonry'
  /** Enable lazy rendering via IntersectionObserver (auto-enabled for >50 assets) */
  lazyRender?: boolean
  /** Whether there are more assets to load */
  hasMore?: boolean
  /** Whether additional assets are currently loading */
  isLoadingMore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  density: 'comfortable',
  layout: 'grid',
  lazyRender: true,
  hasMore: false,
  isLoadingMore: false
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
  'asset-contextmenu': [asset: Asset, event: MouseEvent]
  'load-more': []
}>()

const assetStore = useAssetStore()

// Refs
const gridContainerRef = ref<HTMLElement>()
const sentinelRef = ref<HTMLElement>()
const cardRefs = ref<HTMLElement[]>([])

// Selection state for Shift+Click range selection
const lastSelectedIndex = ref<number | null>(null)

// Intersection Observer state
const observedSet = ref<Set<number>>(new Set())
let cardObserver: IntersectionObserver | null = null
let sentinelObserver: IntersectionObserver | null = null

// Scroll-to-top visibility
const showScrollTop = ref(false)
let scrollListener: (() => void) | null = null

// Determine if lazy rendering should be active
const isLazy = computed(() => props.lazyRender && props.assets.length > 50)

// Visible assets — all of them, rendering is controlled per-card via observedSet
const visibleAssets = computed(() => props.assets)

// Grid classes based on density
const gridClasses = computed(() => {
  const base = ['w-full']

  if (props.layout === 'masonry') {
    base.push('columns-auto')
    if (props.density === 'compact') {
      base.push('columns-[180px]', 'gap-2')
    } else {
      base.push('columns-[240px]', 'gap-4')
    }
  } else {
    base.push('grid')
    if (props.density === 'compact') {
      base.push(
        'grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 2xl:grid-cols-8',
        'gap-2'
      )
    } else {
      base.push(
        'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6',
        'gap-4 sm:gap-6'
      )
    }
  }

  return base.join(' ')
})

// --- Intersection Observer setup ---

function setupCardObserver() {
  if (!isLazy.value) {
    // When not lazy, mark all assets as observed immediately
    observedSet.value = new Set(props.assets.map(a => a.id))
    return
  }

  // Disconnect existing observer
  cardObserver?.disconnect()

  cardObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const assetId = Number((entry.target as HTMLElement).dataset.assetId)
          if (assetId && !observedSet.value.has(assetId)) {
            observedSet.value = new Set([...observedSet.value, assetId])
          }
          // Once observed, stop watching this element (it stays rendered)
          cardObserver?.unobserve(entry.target)
        }
      }
    },
    {
      // Buffer: start rendering cards 600px before they enter the viewport
      rootMargin: '600px 0px 600px 0px',
      threshold: 0
    }
  )

  // Observe all card wrapper elements
  nextTick(() => {
    const container = gridContainerRef.value
    if (!container) return

    const items = container.querySelectorAll('.asset-grid-item')
    items.forEach(el => cardObserver?.observe(el))
  })
}

function setupSentinelObserver() {
  sentinelObserver?.disconnect()

  if (!props.hasMore) return

  sentinelObserver = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting && !props.isLoadingMore) {
          emit('load-more')
        }
      }
    },
    { rootMargin: '300px 0px', threshold: 0 }
  )

  nextTick(() => {
    if (sentinelRef.value) {
      sentinelObserver?.observe(sentinelRef.value)
    }
  })
}

function setupScrollListener() {
  const onScroll = () => {
    showScrollTop.value = window.scrollY > 600
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  scrollListener = onScroll
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// --- Selection ---

function isAssetSelected(asset: Asset): boolean {
  return assetStore.selectedAssets.has(asset.id)
}

function isAssetShared(_assetId: number): boolean {
  return false
}

function handleAssetSelect(asset: Asset, index: number, event?: MouseEvent) {
  const isShiftClick = event?.shiftKey && lastSelectedIndex.value !== null

  if (isShiftClick) {
    const start = Math.min(lastSelectedIndex.value!, index)
    const end = Math.max(lastSelectedIndex.value!, index)

    for (let i = start; i <= end; i++) {
      const rangeAsset = props.assets[i]
      if (rangeAsset && !assetStore.selectedAssets.has(rangeAsset.id)) {
        assetStore.toggleSelection(rangeAsset.id)
      }
    }
  } else {
    assetStore.selectAsset(asset, true)
    lastSelectedIndex.value = index
  }

  emit('asset-select', asset, index)
}

function handleAssetOpen(asset: Asset) { emit('asset-open', asset) }
function handleAssetPreview(asset: Asset) { emit('asset-preview', asset) }
function handleAssetDownload(asset: Asset) { emit('asset-download', asset) }
function handleAssetShare(asset: Asset) { emit('asset-share', asset) }
function handleAssetDelete(asset: Asset) { emit('asset-delete', asset) }
function handleAssetAddTags(asset: Asset) { emit('asset-add-tags', asset) }
function handleAssetMove(asset: Asset) { emit('asset-move', asset) }

// --- Lifecycle ---

onMounted(() => {
  setupCardObserver()
  setupSentinelObserver()
  setupScrollListener()
})

onUnmounted(() => {
  cardObserver?.disconnect()
  sentinelObserver?.disconnect()
  if (scrollListener) {
    window.removeEventListener('scroll', scrollListener)
  }
})

// Re-observe when assets change
watch(() => props.assets.length, () => {
  nextTick(() => {
    setupCardObserver()
    setupSentinelObserver()
  })
})

watch(() => props.hasMore, () => {
  nextTick(() => setupSentinelObserver())
})

// Expose for parent
defineExpose({ scrollToTop })
</script>

<style scoped>
/* Masonry layout fallback using CSS columns */
.columns-auto {
  column-fill: balance;
}

.columns-auto > * {
  break-inside: avoid;
  margin-bottom: var(--gap, 1rem);
}

.columns-auto > * {
  page-break-inside: avoid;
  break-inside: avoid;
}

/* Skeleton cards */
.asset-grid-skeleton {
  aspect-ratio: 4/3;
}

/* Scroll-to-top fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

