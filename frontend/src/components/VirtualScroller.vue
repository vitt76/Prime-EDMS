<template>
  <div
    ref="scrollerRef"
    class="virtual-scroller"
    role="list"
    :aria-label="ariaLabel"
    tabindex="0"
    @scroll="handleScroll"
    @keydown="handleKeydown"
  >
    <!-- Spacer for total height -->
    <div
      class="virtual-scroller__spacer"
      :style="{ height: `${totalHeight}px` }"
      aria-hidden="true"
    />

    <!-- Visible items container -->
    <div
      class="virtual-scroller__items"
      :style="{ transform: `translateY(${offsetY}px)` }"
    >
      <!-- Rendered items -->
      <div
        v-for="(item, index) in visibleItems"
        :key="getItemKey(item, startIndex + index)"
        class="virtual-scroller__item"
        :style="{ height: `${itemHeight}px` }"
        role="listitem"
      >
        <slot
          :item="item"
          :index="startIndex + index"
          :is-visible="true"
        />
      </div>

      <!-- Loading skeletons for upcoming items -->
      <div
        v-for="i in loadingItemsCount"
        :key="`skeleton-${startIndex + visibleItems.length + i}`"
        class="virtual-scroller__item virtual-scroller__item--skeleton"
        :style="{ height: `${itemHeight}px` }"
        role="listitem"
        aria-hidden="true"
      >
        <slot
          name="skeleton"
          :index="startIndex + visibleItems.length + i"
        />
      </div>
    </div>

    <!-- Loading indicator at bottom -->
    <div
      v-if="showBottomLoader"
      class="virtual-scroller__bottom-loader"
      role="status"
      aria-live="polite"
    >
      <slot name="loading">
        <div class="flex items-center justify-center py-4">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
          <span class="ml-2 text-sm text-neutral-600 dark:text-neutral-400">
            Loading more items...
          </span>
        </div>
      </slot>
    </div>

    <!-- Empty state -->
    <div
      v-if="totalItems === 0 && !isLoading"
      class="virtual-scroller__empty"
      role="status"
    >
      <slot name="empty">
        <div class="flex flex-col items-center justify-center py-12 text-center">
          <svg class="w-12 h-12 text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m8-5v2m0 0v2m0-2h2m-2 0h-2" />
          </svg>
          <h3 class="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
            No items found
          </h3>
          <p class="text-sm text-neutral-600 dark:text-neutral-400">
            Try adjusting your filters or search terms.
          </p>
        </div>
      </slot>
    </div>

    <!-- Error state -->
    <div
      v-if="error && !isLoading"
      class="virtual-scroller__error"
      role="alert"
    >
      <slot name="error" :error="error" :retry="handleRetry">
        <div class="flex flex-col items-center justify-center py-8 text-center">
          <svg class="w-10 h-10 text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
            Failed to load items
          </h3>
          <p class="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
            {{ error }}
          </p>
          <button
            @click="handleRetry"
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Virtual Scroller Component
 *
 * High-performance infinite scrolling with buffer management for large datasets.
 * Supports keyboard navigation, accessibility, and smooth scrolling.
 */

import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { throttle } from 'lodash-es'

// Types
export interface VirtualScrollerItem {
  id: string | number
  [key: string]: any
}

export interface VirtualScrollerProps {
  /** Array of items to render */
  items: VirtualScrollerItem[]
  /** Total number of items (for infinite scroll) */
  totalItems: number
  /** Height of each item in pixels */
  itemHeight: number
  /** Number of items to render above/below visible area */
  bufferSize?: number
  /** Container height in pixels */
  containerHeight?: number
  /** Enable infinite scroll */
  infiniteScroll?: boolean
  /** Distance from bottom to trigger load more */
  loadMoreThreshold?: number
  /** Current loading state */
  isLoading?: boolean
  /** Error message */
  error?: string | null
  /** ARIA label for the scroller */
  ariaLabel?: string
  /** Function to get unique key for each item */
  itemKey?: (item: VirtualScrollerItem, index: number) => string | number
}

// Props
const props = withDefaults(defineProps<VirtualScrollerProps>(), {
  bufferSize: 5,
  containerHeight: 600,
  infiniteScroll: true,
  loadMoreThreshold: 200,
  isLoading: false,
  error: null,
  ariaLabel: 'Virtual list',
  itemKey: (item: VirtualScrollerItem, index: number) => item.id ?? index
})

// Emits
const emit = defineEmits<{
  'load-more': []
  'item-focus': [item: VirtualScrollerItem, index: number]
  'scroll': [scrollTop: number, scrollHeight: number]
  'retry': []
}>()

// Refs
const scrollerRef = ref<HTMLElement>()
const scrollTop = ref(0)

// Computed properties
const visibleRange = computed(() => {
  const start = Math.max(0, Math.floor(scrollTop.value / props.itemHeight) - props.bufferSize)
  const end = Math.min(
    props.totalItems,
    Math.ceil((scrollTop.value + props.containerHeight) / props.itemHeight) + props.bufferSize
  )
  return { start, end }
})

const startIndex = computed(() => visibleRange.value.start)

const endIndex = computed(() => visibleRange.value.end)

const visibleItems = computed(() => {
  const { start, end } = visibleRange.value
  return props.items.slice(start, end)
})

const offsetY = computed(() => startIndex.value * props.itemHeight)

const totalHeight = computed(() => props.totalItems * props.itemHeight)

const loadingItemsCount = computed(() => {
  if (!props.infiniteScroll || !props.isLoading) return 0

  const visibleEnd = endIndex.value
  const bufferEnd = Math.min(props.totalItems, visibleEnd + props.bufferSize)
  return Math.max(0, bufferEnd - visibleEnd)
})

const showBottomLoader = computed(() => {
  if (!props.infiniteScroll || props.error) return false

  const scrolledToBottom = scrollTop.value + props.containerHeight >= totalHeight.value - props.loadMoreThreshold
  return scrolledToBottom && (props.isLoading || loadingItemsCount.value > 0)
})

// Methods
const getItemKey = (item: VirtualScrollerItem, index: number): string | number => {
  return props.itemKey(item, index)
}

const handleScroll = throttle(() => {
  if (!scrollerRef.value) return

  const newScrollTop = scrollerRef.value.scrollTop
  scrollTop.value = newScrollTop

  // Emit scroll event
  emit('scroll', newScrollTop, scrollerRef.value.scrollHeight)

  // Check if we need to load more items
  if (props.infiniteScroll && !props.isLoading && !props.error) {
    const scrolledToBottom = newScrollTop + props.containerHeight >= totalHeight.value - props.loadMoreThreshold

    if (scrolledToBottom && visibleRange.value.end >= props.items.length) {
      emit('load-more')
    }
  }
}, 16) // ~60fps

const handleRetry = () => {
  emit('retry')
}

const handleKeydown = (event: KeyboardEvent) => {
  if (!scrollerRef.value) return

  const { key } = event
  const scrollAmount = props.itemHeight * 3 // Scroll 3 items at a time

  switch (key) {
    case 'ArrowDown':
      event.preventDefault()
      scrollerRef.value.scrollTop += scrollAmount
      break
    case 'ArrowUp':
      event.preventDefault()
      scrollerRef.value.scrollTop -= scrollAmount
      break
    case 'PageDown':
      event.preventDefault()
      scrollerRef.value.scrollTop += props.containerHeight
      break
    case 'PageUp':
      event.preventDefault()
      scrollerRef.value.scrollTop -= props.containerHeight
      break
    case 'Home':
      event.preventDefault()
      scrollerRef.value.scrollTop = 0
      break
    case 'End':
      event.preventDefault()
      scrollerRef.value.scrollTop = totalHeight.value - props.containerHeight
      break
  }
}

// Scroll to specific item
const scrollToItem = (index: number, align: 'start' | 'center' | 'end' = 'start') => {
  if (!scrollerRef.value) return

  const itemTop = index * props.itemHeight
  let scrollTop = itemTop

  switch (align) {
    case 'center':
      scrollTop = itemTop - props.containerHeight / 2 + props.itemHeight / 2
      break
    case 'end':
      scrollTop = itemTop - props.containerHeight + props.itemHeight
      break
  }

  scrollerRef.value.scrollTo({
    top: Math.max(0, scrollTop),
    behavior: 'smooth'
  })
}

// Scroll to top
const scrollToTop = () => {
  if (scrollerRef.value) {
    scrollerRef.value.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Get visible item indices
const getVisibleRange = () => visibleRange.value

// Watch for prop changes that affect scrolling
watch(() => props.items.length, () => {
  // Recalculate visible range when items change
  nextTick(() => handleScroll())
})

watch(() => props.totalItems, () => {
  // Update total height when total items change
  nextTick(() => handleScroll())
})

// Lifecycle
onMounted(() => {
  if (scrollerRef.value) {
    // Set initial scroll position
    scrollerRef.value.scrollTop = scrollTop.value
  }
})

onUnmounted(() => {
  // Cleanup throttled function
  handleScroll.cancel()
})

// Expose methods for parent components
defineExpose({
  scrollToItem,
  scrollToTop,
  getVisibleRange
})
</script>

<style scoped>
.virtual-scroller {
  @apply relative overflow-auto bg-neutral-50 dark:bg-neutral-900;
  height: v-bind('`${containerHeight}px`');
  scrollbar-width: thin;
  scrollbar-color: rgb(156 163 175) transparent;
}

.virtual-scroller:focus {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
}

/* Webkit scrollbar styling */
.virtual-scroller::-webkit-scrollbar {
  width: 8px;
}

.virtual-scroller::-webkit-scrollbar-track {
  background: transparent;
}

.virtual-scroller::-webkit-scrollbar-thumb {
  background: rgb(156 163 175);
  border-radius: 4px;
}

.virtual-scroller::-webkit-scrollbar-thumb:hover {
  background: rgb(107 114 128);
}

.virtual-scroller__spacer {
  @apply pointer-events-none;
}

.virtual-scroller__items {
  @apply relative;
}

.virtual-scroller__item {
  @apply absolute left-0 right-0;
  will-change: transform;
}

.virtual-scroller__item--skeleton {
  @apply opacity-50;
}

.virtual-scroller__bottom-loader {
  @apply flex justify-center py-4;
}

.virtual-scroller__empty,
.virtual-scroller__error {
  @apply absolute inset-0 flex items-center justify-center;
}

/* Smooth scrolling */
.virtual-scroller {
  scroll-behavior: smooth;
}

/* Focus styles for keyboard navigation */
.virtual-scroller:focus-visible {
  @apply ring-2 ring-primary-500 ring-offset-2;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .virtual-scroller {
    border: 2px solid;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .virtual-scroller {
    scroll-behavior: auto;
  }

  .virtual-scroller__item {
    transition: none;
  }
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .virtual-scroller {
    -webkit-overflow-scrolling: touch;
  }

  .virtual-scroller::-webkit-scrollbar {
    display: none;
  }
}
</style>











