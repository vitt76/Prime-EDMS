<template>
  <div class="gallery-view">
    <!-- Loading State - Skeleton Grid -->
    <div v-if="assetStore.isLoading && assetStore.assets.length === 0" class="p-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
        <div
          v-for="i in 12"
          :key="i"
          class="bg-white rounded-xl border border-neutral-200 overflow-hidden animate-pulse"
        >
          <div class="aspect-video bg-neutral-200" />
          <div class="p-3 space-y-2">
            <div class="h-4 bg-neutral-200 rounded w-3/4" />
            <div class="flex justify-between">
              <div class="h-3 bg-neutral-200 rounded w-16" />
              <div class="h-3 bg-neutral-200 rounded w-20" />
            </div>
          </div>
        </div>
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
      class="flex items-center justify-center min-h-[60vh] p-8"
    >
      <div class="max-w-md text-center">
        <div class="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-primary-100 to-primary-50 flex items-center justify-center mb-6">
          <svg
            class="w-12 h-12 text-primary-500"
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
        </div>
        <h3 class="text-xl font-semibold text-neutral-800 mb-2">
          Библиотека пуста
        </h3>
        <p class="text-neutral-500 mb-6">
          Начните работу с загрузки первых файлов в вашу DAM-систему
        </p>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-xl
                 hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                 transition-all shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30"
          @click="$emit('open-upload')"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Загрузить файлы
        </button>
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

      <!-- Assets Grid (regular for small lists) -->
      <div
        v-if="assetStore.assets.length < 100"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6 p-6"
        role="grid"
        aria-label="Галерея активов"
      >
        <AssetCard
          v-for="asset in assetStore.assets"
          :key="asset.id"
          :asset="asset"
          :is-selected="isAssetSelected(asset)"
          :is-shared="isAssetShared(asset.id)"
          :show-checkbox="true"
          @select="handleAssetSelect"
          @open="handleAssetOpen"
          @preview="handleAssetPreview"
          @download="handleAssetDownload"
          @share="handleAssetShare"
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
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
              <AssetCard
                v-for="asset in visibleAssets"
                :key="asset.id"
                :asset="asset"
                :is-selected="isAssetSelected(asset)"
                :is-shared="isAssetShared(asset.id)"
                :show-checkbox="true"
                @select="handleAssetSelect"
                @open="handleAssetOpen"
                @preview="handleAssetPreview"
                @download="handleAssetDownload"
                @share="handleAssetShare"
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
      :selected-count="selectedAssetIds.length"
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
    <ShareModal
      :is-open="showBulkShareModal"
      :assets="selectedAssetsList"
      @close="showBulkShareModal = false"
      @success="handleShareSuccess"
    />

    <!-- Floating Bulk Actions Bar (New Glassmorphism Version) -->
    <BulkActionsBar
      @share="handleBulkShare"
      @download="handleBulkDownload"
      @move="handleBulkMove"
      @campaign="handleBulkCampaign"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/apiService'
import { useAssetStore } from '@/stores/assetStore'
import { useDistributionStore } from '@/stores/distributionStore'
import AssetCard from './AssetCard.vue'
import BulkActionsBar from './BulkActionsBar.vue'
import BulkTagModal from './BulkTagModal.vue'
import BulkMoveModal from './BulkMoveModal.vue'
import BulkDeleteModal from './BulkDeleteModal.vue'
import BulkDownloadModal from './BulkDownloadModal.vue'
import ShareModal from './ShareModal.vue'
import Pagination from '@/components/Common/Pagination.vue'
import type { Asset } from '@/types/api'

// Emits
defineEmits<{
  'open-upload': []
}>()

const router = useRouter()
const assetStore = useAssetStore()
const distributionStore = useDistributionStore()
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

  // Load shared links for shared badges
  distributionStore.fetchSharedLinks()

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
  return assetStore.selectedAssets.has(asset.id)
}

function isAssetShared(assetId: number): boolean {
  return distributionStore.sharedAssetIds.has(assetId)
}

const isAllSelected = computed(() => {
  return (
    assetStore.assets.length > 0 &&
    assetStore.selectedAssets.size === assetStore.assets.length
  )
})

const isIndeterminate = computed(() => {
  return (
    assetStore.selectedAssets.size > 0 &&
    assetStore.selectedAssets.size < assetStore.assets.length
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

async function handleAssetDownload(asset: Asset) {
  try {
    let fileId = (asset as any).file_latest_id
    let downloadUrl = (asset as any).download_url as string | undefined

    // If no download_url provided, try to fetch latest file id
    if (!downloadUrl) {
      if (!fileId) {
        // Fetch latest file via API as fallback
        const filesResp = await apiService.get<any>(
          `/api/v4/documents/${asset.id}/files/`,
          { params: { page_size: 1, ordering: '-timestamp' } }
        )
        fileId = filesResp?.results?.[0]?.id
      }
      if (fileId) {
        downloadUrl = `/api/v4/documents/${asset.id}/files/${fileId}/download/`
      } else {
        downloadUrl = `/api/v4/documents/${asset.id}/files/latest/download/`
      }
    }

    const filename =
      asset.file_details?.filename ||
      asset.filename ||
      asset.label ||
      `document-${asset.id}`

    const blob = await apiService.get<Blob>(downloadUrl, {
      responseType: 'blob'
    } as any)

    const objectUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(objectUrl)
  } catch (error) {
    console.error('[GalleryView] Download failed', error)
  }
}

function handleAssetShare(asset: Asset) {
  // Select this asset and open share modal
  assetStore.clearSelection()
  assetStore.toggleSelection(asset.id)
  showBulkShareModal.value = true
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

const selectedAssetIds = computed(() => Array.from(assetStore.selectedAssets))
const selectedAssetsList = computed(() => 
  assetStore.assets.filter(asset => assetStore.selectedAssets.has(asset.id))
)

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

function handleBulkCampaign() {
  // Переходим на вкладку кампаний, SharingPage возьмет выбранные активы из assetStore
  router.push({ path: '/sharing', query: { tab: 'campaigns', from: 'assets' } })
}

function handleShareSuccess() {
  showBulkShareModal.value = false
  assetStore.clearSelection()
  // Refresh assets to update shared badges
  assetStore.fetchAssets()
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

