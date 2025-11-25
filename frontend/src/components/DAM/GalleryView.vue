<template>
  <div class="gallery-view">
    <!-- Loading State -->
    <div v-if="assetStore.isLoading && assetStore.assets.length === 0" class="p-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="i in 8"
          :key="i"
          class="bg-neutral-100 dark:bg-neutral-100 rounded-lg animate-pulse"
          style="height: 260px"
        ></div>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="assetStore.error && assetStore.assets.length === 0"
      class="p-8 text-center"
    >
      <div class="max-w-md mx-auto">
        <svg
          class="mx-auto h-12 w-12 text-error"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-neutral-900 dark:text-neutral-900">
          Ошибка загрузки
        </h3>
        <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-600">
          {{ assetStore.error }}
        </p>
        <button
          class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors min-h-[44px] min-w-[120px]"
          @click="handleRetry"
          type="button"
          aria-label="Повторить загрузку активов"
        >
          Попробовать снова
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="assetStore.assets.length === 0 && !assetStore.isLoading"
      class="p-8 text-center"
    >
      <div class="max-w-md mx-auto">
        <svg
          class="mx-auto h-12 w-12 text-neutral-400"
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
        <h3 class="mt-4 text-lg font-medium text-neutral-900 dark:text-neutral-900">
          Нет активов
        </h3>
        <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-600">
          Загрузите первый актив, чтобы начать работу
        </p>
      </div>
    </div>

    <!-- Gallery Grid -->
    <div v-else class="gallery-content">
      <!-- Gallery Toolbar with Select All -->
      <div
        v-if="assetStore.assets.length > 0"
        class="flex items-center justify-between px-4 py-2 border-b border-neutral-300 dark:border-neutral-300 bg-neutral-0 dark:bg-neutral-0 sticky top-0 z-30"
      >
        <div class="flex items-center gap-4">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              :checked="isAllSelected"
              :indeterminate="isIndeterminate"
              class="w-5 h-5 rounded border-neutral-300 text-primary-500 focus:ring-primary-500 min-w-[44px] min-h-[44px]"
              @change="handleSelectAllToggle"
              aria-label="Выбрать все активы"
            />
            <span class="text-sm font-medium text-neutral-900 dark:text-neutral-900">
              {{ isAllSelected ? 'Снять выделение' : 'Выбрать все' }}
            </span>
          </label>
          <span
            v-if="assetStore.selectedCount > 0"
            class="text-sm text-neutral-600 dark:text-neutral-600"
          >
            Выбрано: <strong>{{ assetStore.selectedCount }}</strong> из {{ assetStore.assets.length }}
          </span>
        </div>
      </div>

      <!-- Bulk Actions Toolbar -->
      <BulkActions
        :selected-count="assetStore.selectedCount"
        @tag="handleBulkTag"
        @move="handleBulkMove"
        @download="handleBulkDownload"
        @share="handleBulkShare"
        @delete="handleBulkDelete"
        @clear-selection="handleClearSelection"
      />

      <!-- Assets Grid (regular for small lists) -->
      <div
        v-if="assetStore.assets.length < 100"
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 p-4"
        role="grid"
        aria-label="Галерея активов"
      >
        <AssetCard
          v-for="asset in assetStore.assets"
          :key="asset.id"
          :asset="asset"
          :is-selected="isAssetSelected(asset)"
          :show-checkbox="true"
          @select="handleAssetSelect"
          @open="handleAssetOpen"
          @preview="handleAssetPreview"
          @download="handleAssetDownload"
          @more="handleAssetMore"
        />
      </div>

      <!-- Virtual Scrolling for large lists (100+ items) -->
      <div
        v-else
        ref="virtualScrollContainer"
        class="virtual-scroll-container p-4"
        style="height: calc(100vh - 200px); overflow-y: auto;"
        role="grid"
        aria-label="Галерея активов (виртуальная прокрутка)"
        tabindex="0"
        @scroll="handleScroll"
      >
        <div
          :style="{ height: `${totalHeight}px`, position: 'relative' }"
        >
          <div
            :style="{ transform: `translateY(${offsetY}px)` }"
          >
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              <AssetCard
                v-for="asset in visibleAssets"
                :key="asset.id"
                :asset="asset"
                :is-selected="isAssetSelected(asset)"
                :show-checkbox="true"
                @select="handleAssetSelect"
                @open="handleAssetOpen"
                @preview="handleAssetPreview"
                @download="handleAssetDownload"
                @more="handleAssetMore"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <Pagination
        v-if="assetStore.totalCount > 0"
        :current-page="assetStore.currentPage"
        :total-items="assetStore.totalCount"
        :page-size="assetStore.pageSize"
        @page-change="handlePageChange"
        class="mb-20"
      />
    </div>

    <!-- Bulk Operation Modals -->
    <BulkTagModal
      :is-open="showBulkTagModal"
      :selected-ids="selectedAssetIds"
      @close="showBulkTagModal = false"
      @success="handleBulkOperationSuccess"
    />
    <BulkMoveModal
      :is-open="showBulkMoveModal"
      :selected-ids="selectedAssetIds"
      @close="showBulkMoveModal = false"
      @success="handleBulkOperationSuccess"
    />
    <BulkDeleteModal
      :is-open="showBulkDeleteModal"
      :selected-ids="selectedAssetIds"
      @close="showBulkDeleteModal = false"
      @success="handleBulkOperationSuccess"
    />
    <BulkDownloadModal
      :is-open="showBulkDownloadModal"
      :selected-ids="selectedAssetIds"
      @close="showBulkDownloadModal = false"
      @success="handleBulkOperationSuccess"
    />
    <BulkShareModal
      :is-open="showBulkShareModal"
      :selected-ids="selectedAssetIds"
      @close="showBulkShareModal = false"
      @success="handleBulkOperationSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assetStore'
import AssetCard from './AssetCard.vue'
import BulkActions from './BulkActions.vue'
import BulkTagModal from './BulkTagModal.vue'
import BulkMoveModal from './BulkMoveModal.vue'
import BulkDeleteModal from './BulkDeleteModal.vue'
import BulkDownloadModal from './BulkDownloadModal.vue'
import BulkShareModal from './BulkShareModal.vue'
import Pagination from '@/components/Common/Pagination.vue'
import type { Asset } from '@/types/api'

const router = useRouter()
const assetStore = useAssetStore()
const virtualScrollContainer = ref<HTMLElement | null>(null)

// Virtual scrolling state
const scrollTop = ref(0)
const itemHeight = 280 // Height of each asset card + gap
const itemsPerRow = ref(4) // Will be calculated based on screen size
const containerHeight = ref(600)
const bufferSize = 2 // Number of rows to render outside viewport

// Calculate visible items for virtual scrolling
const visibleAssets = computed(() => {
  if (assetStore.assets.length < 100) {
    return assetStore.assets
  }

  const rowsPerViewport = Math.ceil(containerHeight.value / itemHeight)
  const startRow = Math.max(0, Math.floor(scrollTop.value / itemHeight) - bufferSize)
  const endRow = Math.min(
    Math.ceil(assetStore.assets.length / itemsPerRow.value),
    startRow + rowsPerViewport + bufferSize * 2
  )
  
  const startIndex = startRow * itemsPerRow.value
  const endIndex = endRow * itemsPerRow.value

  return assetStore.assets.slice(
    Math.max(0, startIndex),
    Math.min(assetStore.assets.length, endIndex)
  )
})

const totalHeight = computed(() => {
  if (assetStore.assets.length < 100) return 0
  const rows = Math.ceil(assetStore.assets.length / itemsPerRow.value)
  return rows * itemHeight
})

const offsetY = computed(() => {
  if (assetStore.assets.length < 100) return 0
  const startRow = Math.max(0, Math.floor(scrollTop.value / itemHeight) - bufferSize)
  return startRow * itemHeight
})

// Handle scroll for virtual scrolling (throttled for performance)
let scrollTimeout: number | null = null
function handleScroll(event: Event) {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
  
  // Throttle scroll updates for better performance
  if (scrollTimeout) {
    cancelAnimationFrame(scrollTimeout)
  }
  scrollTimeout = requestAnimationFrame(() => {
    // Scroll position already updated above
  })
}

// Load assets on mount and setup virtual scrolling
let resizeHandler: (() => void) | null = null

onMounted(() => {
  // Load assets
  if (assetStore.assets.length === 0) {
    assetStore.fetchAssets()
  }

  // Setup virtual scrolling
  if (virtualScrollContainer.value) {
    // Calculate items per row based on container width
    const updateItemsPerRow = () => {
      if (virtualScrollContainer.value) {
        const width = virtualScrollContainer.value.clientWidth
        // Responsive breakpoints: xl(1280px), lg(1024px), md(768px), sm(640px)
        if (width >= 1280) itemsPerRow.value = 5
        else if (width >= 1024) itemsPerRow.value = 4
        else if (width >= 768) itemsPerRow.value = 3
        else if (width >= 640) itemsPerRow.value = 2
        else itemsPerRow.value = 1
        
        // Update container height for virtual scrolling calculations
        containerHeight.value = virtualScrollContainer.value.clientHeight || 600
      }
    }
    
    updateItemsPerRow()
    resizeHandler = () => {
      updateItemsPerRow()
      // Debounce resize for better performance
      if (scrollTimeout) {
        cancelAnimationFrame(scrollTimeout)
      }
      scrollTimeout = requestAnimationFrame(updateItemsPerRow)
    }
    window.addEventListener('resize', resizeHandler, { passive: true })
  }
})

onUnmounted(() => {
  if (virtualScrollContainer.value) {
    virtualScrollContainer.value.removeEventListener('scroll', handleScroll)
  }
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
  if (scrollTimeout) {
    cancelAnimationFrame(scrollTimeout)
  }
})

// Watch for page changes
watch(
  () => assetStore.currentPage,
  () => {
    assetStore.fetchAssets()
  }
)

function isAssetSelected(asset: Asset): boolean {
  return assetStore.selectedAssets.some((a) => a.id === asset.id)
}

const isAllSelected = computed(() => {
  return (
    assetStore.assets.length > 0 &&
    assetStore.selectedAssets.length === assetStore.assets.length
  )
})

const isIndeterminate = computed(() => {
  return (
    assetStore.selectedAssets.length > 0 &&
    assetStore.selectedAssets.length < assetStore.assets.length
  )
})

function handleSelectAllToggle() {
  if (isAllSelected.value) {
    assetStore.clearSelection()
  } else {
    assetStore.selectAll()
  }
}

function handleAssetSelect(asset: Asset) {
  assetStore.selectAsset(asset, true) // Multi-select enabled
}

function handleAssetOpen(asset: Asset) {
  router.push(`/dam/assets/${asset.id}`)
}

function handleAssetPreview(asset: Asset) {
  // TODO: Open preview modal
  console.log('Preview asset:', asset.id)
}

function handleAssetDownload(asset: Asset) {
  // TODO: Implement download
  console.log('Download asset:', asset.id)
}

function handleAssetMore(asset: Asset) {
  // TODO: Open more actions menu
  console.log('More actions for asset:', asset.id)
}

function handlePageChange(page: number) {
  assetStore.setPage(page)
}

function handleRetry() {
  assetStore.fetchAssets()
}

// Bulk Operations
const showBulkTagModal = ref(false)
const showBulkMoveModal = ref(false)
const showBulkDeleteModal = ref(false)
const showBulkDownloadModal = ref(false)
const showBulkShareModal = ref(false)

const selectedAssetIds = computed(() => assetStore.selectedAssets.map((a) => a.id))

function handleBulkTag() {
  showBulkTagModal.value = true
}

function handleBulkMove() {
  showBulkMoveModal.value = true
}

function handleBulkDelete() {
  showBulkDeleteModal.value = true
}

function handleBulkDownload() {
  showBulkDownloadModal.value = true
}

function handleBulkShare() {
  showBulkShareModal.value = true
}

function handleClearSelection() {
  assetStore.clearSelection()
}

function handleBulkOperationSuccess() {
  // Refresh assets after bulk operation
  assetStore.fetchAssets()
  assetStore.clearSelection()
}
</script>

<style scoped>
.gallery-view {
  min-height: 400px;
}

.gallery-content {
  display: flex;
  flex-direction: column;
  min-height: 400px;
}
</style>

