<template>
  <div class="gallery-view">
    <!-- Loading State - Skeleton Grid -->
    <div v-if="assetStore.isLoading && assetStore.assets.length === 0" class="p-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
        <AssetCardSkeleton
          v-for="i in 12"
          :key="i"
          :density="gridDensity"
        />
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

    <!-- Empty State: filters active — nothing found -->
    <div
      v-else-if="assetStore.assets.length === 0 && !assetStore.isLoading && activeFiltersCount > 0"
      class="flex items-center justify-center min-h-[60vh] p-8"
    >
      <div class="max-w-md text-center">
        <div class="mx-auto w-24 h-24 rounded-full bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center mb-6">
          <svg
            class="w-12 h-12 text-neutral-400 dark:text-neutral-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-neutral-800 dark:text-neutral-200 mb-2">
          Ничего не найдено
        </h3>
        <p class="text-neutral-500 dark:text-neutral-400 mb-6">
          По выбранным фильтрам активов нет. Попробуйте изменить условия поиска.
        </p>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-xl
                 hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                 transition-all"
          @click="handleFiltersReset"
        >
          Сбросить фильтры
        </button>
      </div>
    </div>

    <!-- Empty State: library empty (no filters) -->
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
      <!-- Context-Aware Header Actions -->
      <Teleport to="#header-actions">
        <GalleryHeaderActions
          variant="controls"
          :density="gridDensity"
          :layout="gridLayout"
          :sort="gridSort"
          :active-filters-count="activeFiltersCount"
          @update:density="handleDensityChange"
          @update:layout="handleLayoutChange"
          @update:sort="handleSortChange"
          @toggle-filters="openFilters"
        />
      </Teleport>
      <Teleport to="#header-search-actions">
        <SavedSearchesDropdown
          ref="savedSearchesDropdownRef"
          @save-current="openSaveSearchModal"
          @run="handleSavedSearchRun"
          @edit="openRenameSavedSearchModal"
          @delete="handleSavedSearchDelete"
        />
        <GalleryHeaderActions
          variant="filter"
          :density="gridDensity"
          :layout="gridLayout"
          :sort="gridSort"
          :active-filters-count="activeFiltersCount"
          @toggle-filters="openFilters"
        />
      </Teleport>

      <!-- Recently Viewed (Sprint 1 Discovery UX) -->
      <div class="px-6 pt-4 pb-2">
        <RecentlyViewedBlock :limit="12" />
      </div>

      <!-- Assets Grid (regular for small lists, threshold 80) -->
      <section
        v-if="!isVirtual"
        class="p-6"
        aria-label="Галерея активов"
      >
        <div class="group">
          <!-- Select All (ABOVE grid, no overlay) -->
          <div
            v-if="assetStore.assets.length > 0"
            class="flex items-center justify-between mb-3"
          >
            <button
              type="button"
              class="flex items-center gap-2
                     bg-white/95 backdrop-blur-md border border-gray-200 shadow-sm
                     rounded-xl px-3 py-2 text-sm font-medium
                     text-gray-700 hover:text-gray-900 hover:bg-gray-50
                     transition-all duration-150"
              :class="assetStore.selectedCount > 0 ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'"
              @click="handleSelectAllToggle"
              aria-label="Выбрать все активы"
            >
              <span
                class="w-4 h-4 rounded border border-gray-300 bg-white flex items-center justify-center"
                aria-hidden="true"
              >
                <svg v-if="isAllSelected" class="w-3.5 h-3.5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                </svg>
                <svg v-else-if="isIndeterminate" class="w-3.5 h-3.5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 12h14" />
                </svg>
              </span>
              <span>{{ isAllSelected ? 'Снять выделение' : 'Выбрать все' }}</span>
            </button>

            <div v-if="assetStore.selectedCount > 0" class="text-sm text-gray-600">
              Выбрано: <span class="font-semibold text-gray-900">{{ assetStore.selectedCount }}</span> из {{ assetStore.assets.length }}
            </div>
          </div>

          <AssetGrid
            :assets="assetStore.assets"
            :density="gridDensity"
            :layout="gridLayout"
            :has-more="assetStore.hasNextPage"
            :is-loading-more="assetStore.isLoadingMore"
            @asset-open="handleAssetOpen"
            @asset-preview="handleAssetPreview"
            @asset-download="handleAssetDownload"
            @asset-share="handleAssetShare"
            @asset-delete="handleAssetDelete"
            @asset-add-tags="handleAssetAddTags"
            @asset-move="handleAssetMove"
            @asset-contextmenu="handleAssetContextMenu"
            @load-more="assetStore.loadMore"
          />
        </div>
      </section>

      <!-- Immersive Grid (virtualized for 80+ items) -->
      <div
        v-else
        class="p-4 relative group"
      >
        <!-- Select All (above grid) -->
        <div
          v-if="assetStore.assets.length > 0"
          class="flex items-center justify-between mb-3"
        >
          <button
            type="button"
            class="flex items-center gap-2
                   bg-white/95 backdrop-blur-md border border-gray-200 shadow-sm
                   rounded-xl px-3 py-2 text-sm font-medium
                   text-gray-700 hover:text-gray-900 hover:bg-gray-50
                   transition-all duration-150"
            :class="assetStore.selectedCount > 0 ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'"
            @click="handleSelectAllToggle"
            aria-label="Выбрать все активы"
          >
            <span
              class="w-4 h-4 rounded border border-gray-300 bg-white flex items-center justify-center"
              aria-hidden="true"
            >
              <svg v-if="isAllSelected" class="w-3.5 h-3.5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else-if="isIndeterminate" class="w-3.5 h-3.5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 12h14" />
              </svg>
            </span>
            <span>{{ isAllSelected ? 'Снять выделение' : 'Выбрать все' }}</span>
          </button>

          <div v-if="assetStore.selectedCount > 0" class="text-sm text-gray-600">
            Выбрано: <span class="font-semibold text-gray-900">{{ assetStore.selectedCount }}</span> из {{ assetStore.assets.length }}
          </div>
        </div>

        <ImmersiveGrid
          :assets="assetStore.assets"
          :density="gridDensity"
          :layout="gridLayout"
          :has-more="assetStore.hasNextPage"
          :is-loading-more="assetStore.isLoadingMore"
          @asset-open="handleAssetOpen"
          @asset-preview="handleAssetPreview"
          @asset-download="handleAssetDownload"
          @asset-share="handleAssetShare"
          @asset-delete="handleAssetDelete"
          @asset-add-tags="handleAssetAddTags"
          @asset-move="handleAssetMove"
          @asset-more="handleAssetMore"
          @asset-contextmenu="handleAssetContextMenu"
          @load-more="assetStore.loadMore"
        />
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

    <!-- Asset context menu (right-click) -->
    <AssetContextMenu
      :open="contextMenuOpen"
      :x="contextMenuX"
      :y="contextMenuY"
      :asset="contextMenuAsset"
      @close="closeContextMenu"
      @open="handleAssetOpen"
      @download="handleAssetDownload"
      @share="handleAssetShare"
      @edit-metadata="handleAssetEditMetadata"
      @ai-tag="handleSingleAiTag"
      @favorite="handleAssetFavoriteFromContext"
      @delete="handleAssetDeleteFromContext"
    />
    <ShareModal
      :is-open="showBulkShareModal"
      :assets="selectedAssetsList"
      @close="showBulkShareModal = false"
      @success="handleShareSuccess"
    />

    <MetadataPanel
      :open="metadataPanelOpen"
      :asset="metadataPanelAsset"
      @close="metadataPanelOpen = false; metadataPanelAsset = null"
      @saved="onMetadataSaved"
      @error="(msg) => showToast(msg, 'error')"
    />

    <!-- Add to Collection Modal -->
    <AddToCollectionModal
      v-if="showAddToCollectionModal"
      :selected-ids="Array.from(assetStore.selectedAssets)"
      @close="showAddToCollectionModal = false"
      @done="onAddToCollectionDone"
    />

    <!-- Save Search Modal (Sprint 1 Discovery UX) -->
    <SaveSearchModal
      :is-open="showSaveSearchModal"
      :backend-error="saveSearchBackendError"
      @close="closeSaveSearchModal"
      @save="handleSaveSearch"
    />

    <!-- Rename Saved Search Modal -->
    <RenameSavedSearchModal
      :is-open="showRenameSavedSearchModal"
      :item="renameSavedSearchItem"
      @close="closeRenameSavedSearchModal"
      @save="handleRenameSavedSearch"
    />

    <!-- Confirm Delete Saved Search -->
    <ConfirmModal
      :is-open="showDeleteSavedSearchConfirm"
      title="Удалить сохранённый поиск?"
      message="Это действие нельзя отменить."
      confirm-text="Удалить"
      confirm-variant="danger"
      @close="showDeleteSavedSearchConfirm = false"
      @confirm="confirmDeleteSavedSearch"
    />

    <!-- Hotkeys cheat sheet (Sprint 2) -->
    <HotkeysCheatSheetModal
      :is-open="showHotkeysCheatSheetModal"
      @close="showHotkeysCheatSheetModal = false"
    />

    <!-- Quick preview modal (Space) -->
    <AssetPreviewModal
      :is-open="showPreviewModal"
      :assets="assetStore.assets"
      :start-index="previewStartIndex"
      @update:is-open="closePreviewModal"
      @close="closePreviewModal(false)"
    />

    <!-- Floating Bulk Actions Bar (New Glassmorphism Version) -->
    <BulkActionsBar
      @share="handleBulkShare"
      @download="handleBulkDownload"
      @ai-tag="handleBulkAiTag"
      @add-to-collection="showAddToCollectionModal = true"
      @delete="handleBulkDelete"
      @clear="handleClearSelection"
    />

    <!-- Toast (AI and other feedback) -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="toast.show"
        class="fixed bottom-24 left-1/2 -translate-x-1/2 z-[1100] px-4 py-3 rounded-xl shadow-lg flex items-center gap-3 min-w-[280px] max-w-[90vw]"
        :class="toast.type === 'error' ? 'bg-red-600 text-white' : toast.type === 'success' ? 'bg-emerald-600 text-white' : 'bg-neutral-800 text-white'"
        role="status"
        aria-live="polite"
      >
        <svg v-if="toast.type === 'success'" class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else-if="toast.type === 'error'" class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-sm font-medium">{{ toast.message }}</span>
      </div>
    </Transition>

    <!-- Filters Drawer -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isFiltersOpen"
        class="fixed inset-0 z-[900] bg-black/30"
        @click="closeFilters"
        aria-hidden="true"
      />
    </Transition>
    <Transition
      enter-active-class="transition ease-out duration-250"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <aside
        v-if="isFiltersOpen"
        ref="filtersPanelRef"
        class="fixed top-16 right-0 bottom-0 w-[360px] max-w-[90vw]
               bg-white border-l border-gray-200 shadow-2xl z-[950]
               overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-labelledby="gallery-filters-title"
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <h3 id="gallery-filters-title" class="text-sm font-semibold text-gray-900">Фильтры</h3>
          <button
            type="button"
            class="text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-lg p-2 transition-colors"
            @click="closeFilters"
            aria-label="Закрыть фильтры"
            data-autofocus
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-4">
          <FiltersPanel
            :facets="filtersFacets"
            v-model="filtersModel"
            @reset="handleFiltersReset"
          />
        </div>
      </aside>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch, ref, computed, reactive, defineAsyncComponent, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/apiService'
import { aiAnalysisService } from '@/services/aiAnalysisService'
import { useAssetStore } from '@/stores/assetStore'
import { useDistributionStore } from '@/stores/distributionStore'
import { useFavoritesStore } from '@/stores/favoritesStore'
import { useDamSearchFilters } from '@/composables/useDamSearchFilters'
import AssetCardSkeleton from './AssetCardSkeleton.vue'
import AssetGrid from './AssetGrid.vue'
import ImmersiveGrid from './ImmersiveGrid.vue'
const AssetContextMenu = defineAsyncComponent(() => import('./AssetContextMenu.vue'))
import BulkActionsBar from './BulkActionsBar.vue'
import AddToCollectionModal from './AddToCollectionModal.vue'
import BulkTagModal from './BulkTagModal.vue'
import BulkMoveModal from './BulkMoveModal.vue'
import BulkDeleteModal from './BulkDeleteModal.vue'
import BulkDownloadModal from './BulkDownloadModal.vue'
import ShareModal from './ShareModal.vue'
import SaveSearchModal from './SaveSearchModal.vue'
import RenameSavedSearchModal from './RenameSavedSearchModal.vue'
import ConfirmModal from '@/components/Common/ConfirmModal.vue'
import SavedSearchesDropdown from './SavedSearchesDropdown.vue'
const MetadataPanel = defineAsyncComponent(() => import('./MetadataPanel.vue'))
const AssetPreviewModal = defineAsyncComponent(() => import('@/components/modals/AssetPreviewModal.vue'))
import Pagination from '@/components/Common/Pagination.vue'
import GalleryHeaderActions from './GalleryHeaderActions.vue'
import RecentlyViewedBlock from './RecentlyViewedBlock.vue'
import FiltersPanel from './FiltersPanel.vue'
import HotkeysCheatSheetModal from './HotkeysCheatSheetModal.vue'
import { useGalleryHotkeys } from '@/composables/useGalleryHotkeys'
import { useFocusTrap } from '@/composables/useFocusTrap'
import { createSavedSearch, updateSavedSearch, deleteSavedSearch } from '@/services/savedSearchesService'
import { buildSavedSearchFilters } from '@/utils/savedSearchFilters'
import type { SavedSearch } from '@/services/savedSearchesService'
import type { Asset } from '@/types/api'
import type { Facets, SearchFilters } from '@/types/api'

// Emits
const emit = defineEmits<{
  'open-upload': []
  'delete': [asset: Asset]
}>()

const router = useRouter()
const assetStore = useAssetStore()
const distributionStore = useDistributionStore()
const damSearch = useDamSearchFilters()
const favoritesStore = useFavoritesStore()

const gridDensity = computed(() => damSearch.state.density)
const gridLayout = computed(() => damSearch.state.layout)
const gridSort = computed(() => damSearch.state.sort)

/** Use virtualized ImmersiveGrid for 80+ assets; standard AssetGrid otherwise. */
const isVirtual = computed(() => assetStore.assets.length >= 80)

// Filters drawer
const isFiltersOpen = ref(false)
const filtersPanelRef = ref<HTMLElement | null>(null)
const isFiltersTrapActive = ref(false)
const { activate: activateFiltersTrap, deactivate: deactivateFiltersTrap } = useFocusTrap(
  filtersPanelRef,
  isFiltersTrapActive
)

// Context menu (right-click on asset)
const contextMenuOpen = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuAsset = ref<Asset | null>(null)

// Metadata panel (slide-over)
const metadataPanelOpen = ref(false)
const metadataPanelAsset = ref<Asset | null>(null)

function handleAssetContextMenu(asset: Asset, event: MouseEvent) {
  contextMenuAsset.value = asset
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  contextMenuOpen.value = true
}

function closeContextMenu() {
  contextMenuOpen.value = false
  contextMenuAsset.value = null
}

// Toast for AI and other feedback
const toast = reactive<{ show: boolean; message: string; type: 'info' | 'success' | 'error' }>({
  show: false,
  message: '',
  type: 'info'
})
let toastTimer: ReturnType<typeof setTimeout> | null = null
function showToast(message: string, type: 'info' | 'success' | 'error' = 'info') {
  toast.message = message
  toast.type = type
  toast.show = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.show = false
    toastTimer = null
  }, 4000)
}

async function handleBulkAiTag() {
  const ids = selectedAssetIds.value
  if (ids.length === 0) return
  try {
    await aiAnalysisService.runBulkAIAnalysis(ids)
    showToast(
      `AI анализирует ${ids.length} активов. Результаты появятся через несколько минут.`,
      'info'
    )
  } catch (err: any) {
    const msg = err?.response?.data?.detail || err?.message || 'Ошибка запуска AI-анализа'
    showToast(String(msg), 'error')
  }
}

function handleSingleAiTag(asset: Asset) {
  aiAnalysisService.runAIAnalysis(asset.id).then(() => {
    showToast('Анализ запущен', 'success')
  }).catch((err: any) => {
    const msg = err?.response?.data?.detail || err?.message || 'Ошибка запуска анализа'
    showToast(String(msg), 'error')
  })
}

function handleAssetEditMetadata(asset: Asset) {
  closeContextMenu()
  metadataPanelAsset.value = asset
  metadataPanelOpen.value = true
}

function onMetadataSaved() {
  assetStore.fetchAssets()
  metadataPanelOpen.value = false
  metadataPanelAsset.value = null
}

function onAddToCollectionDone() {
  showToast('Активы добавлены в коллекцию', 'success')
  assetStore.clearSelection()
}

async function handleAssetFavoriteFromContext(asset: Asset) {
  closeContextMenu()
  try {
    const favorited = await favoritesStore.toggleFavorite(asset.id, asset)
    showToast(favorited ? 'Добавлено в избранное' : 'Убрано из избранного', favorited ? 'success' : 'info')
  } catch {
    showToast('Не удалось изменить избранное', 'error')
  }
}

function handleAssetDeleteFromContext(asset: Asset) {
  closeContextMenu()
  handleAssetDelete(asset)
}

const activeFiltersCount = computed(() => {
  return damSearch.activeFiltersCount.value
})

const filtersFacets = computed<Facets>(() => {
  const tagsRecord: Record<string, number> =
    Object.keys(assetStore.tagCounts).length > 0
      ? { ...assetStore.tagCounts }
      : Object.fromEntries(assetStore.availableTags.map((tag) => [tag, 1]))
  return {
    type: assetStore.typeCounts,
    tags: tagsRecord
  }
})

const filtersModel = computed<SearchFilters>({
  get: () => ({
    type: damSearch.state.filters.type,
    tags: damSearch.state.filters.tags,
    date_range:
      damSearch.state.filters.dateFrom && damSearch.state.filters.dateTo
        ? [damSearch.state.filters.dateFrom, damSearch.state.filters.dateTo]
        : null,
    size:
      typeof damSearch.state.filters.sizeMin === 'number' || typeof damSearch.state.filters.sizeMax === 'number'
        ? { min: damSearch.state.filters.sizeMin, max: damSearch.state.filters.sizeMax }
        : undefined,
    orientation: damSearch.state.filters.orientation,
    favoritesOnly: damSearch.state.filters.favoritesOnly
  }),
  set: (value) => {
    // Convert SearchFilters -> composable state
    damSearch.state.filters.type = value.type || []
    damSearch.state.filters.tags = value.tags || []
    damSearch.state.filters.dateFrom = value.date_range?.[0]
    damSearch.state.filters.dateTo = value.date_range?.[1]
    damSearch.state.filters.sizeMin = value.size?.min
    damSearch.state.filters.sizeMax = value.size?.max
    damSearch.state.filters.orientation = value.orientation
    damSearch.state.filters.favoritesOnly = value.favoritesOnly ?? false
    // Trigger debounced sync+fetch (without changing q)
    damSearch.scheduleFetch()
  }
})

onMounted(() => {
  // NOTE: Do not fetch share links on gallery mount.
  // This endpoint is unstable in some deployments and creates console noise.
  // We load share links lazily when the Share modal is opened.
})

// NOTE: Share links are loaded lazily inside handleBulkShare()

onUnmounted(() => {})

// NOTE: Do not watch currentPage here — assetStore pagination actions already fetch,
// and SSoT composable resets currentPage on filter/search changes. A watcher here
// causes duplicate requests.

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

function handleDensityChange(value: 'compact' | 'comfortable') {
  damSearch.setView({ density: value })
}

function handleLayoutChange(value: 'grid' | 'masonry') {
  // masonry + virtual list плохо дружат; пока ограничим только обычный режим
  damSearch.setView({ layout: value })
}

function handleSortChange(value: 'date' | 'name' | 'size') {
  damSearch.setSort(value)
}

function openFilters() {
  isFiltersOpen.value = true
}

function closeFilters() {
  isFiltersOpen.value = false
}

watch(isFiltersOpen, (isOpen, _previous, onCleanup) => {
  isFiltersTrapActive.value = isOpen

  if (isOpen) {
    void nextTick(() => activateFiltersTrap())

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeFilters()
      }
    }

    document.addEventListener('keydown', handleEscape)
    onCleanup(() => {
      document.removeEventListener('keydown', handleEscape)
      deactivateFiltersTrap()
    })
  } else {
    deactivateFiltersTrap()
  }
})

function handleFiltersReset() {
  damSearch.resetFilters()
  isFiltersOpen.value = false
}

function handleAssetOpen(asset: Asset) {
  router.push(`/dam/assets/${asset.id}`)
}

function handleAssetPreview(asset: Asset) {
  const idx = assetStore.assets.findIndex(a => a.id === asset.id)
  previewStartIndexOverride.value = idx >= 0 ? idx : 0
  showPreviewModal.value = true
}

/** Close preview modal and clear override (called from template to avoid ref unwrap). */
function closePreviewModal(v: boolean) {
  showPreviewModal.value = v
  if (!v) previewStartIndexOverride.value = null
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

function handleAssetDelete(asset: Asset) {
  emit('delete', asset)
}

function handleAssetAddTags(asset: Asset) {
  // Single-asset action -> reuse bulk modal UX
  assetStore.clearSelection()
  assetStore.toggleSelection(asset.id)
  showBulkTagModal.value = true
}

function handleAssetMove(asset: Asset) {
  // Single-asset action -> reuse bulk modal UX
  assetStore.clearSelection()
  assetStore.toggleSelection(asset.id)
  showBulkMoveModal.value = true
}

function handlePageChange(page: number) {
  assetStore.setPage(page)
}

function handleRetry() {
  assetStore.fetchAssets()
}

// Bulk Operations
const showAddToCollectionModal = ref(false)
const showBulkTagModal = ref(false)
const showBulkMoveModal = ref(false)
const showBulkDeleteModal = ref(false)
const showBulkDownloadModal = ref(false)
const showBulkShareModal = ref(false)

// Saved Searches (Sprint 1 Discovery UX)
const savedSearchesDropdownRef = ref<InstanceType<typeof SavedSearchesDropdown> | null>(null)
const showSaveSearchModal = ref(false)
const saveSearchBackendError = ref<string | null>(null)
const showRenameSavedSearchModal = ref(false)
const renameSavedSearchItem = ref<SavedSearch | null>(null)
const showDeleteSavedSearchConfirm = ref(false)
const deleteSavedSearchId = ref<number | null>(null)

// Sprint 2: Hotkeys cheat sheet and preview modals
const showHotkeysCheatSheetModal = ref(false)
const showPreviewModal = ref(false)
/** When set, preview modal uses this index instead of selection (e.g. opened from card click). */
const previewStartIndexOverride = ref<number | null>(null)

const selectedAssetIds = computed(() => Array.from(assetStore.selectedAssets))
const selectedAssetsList = computed(() => 
  assetStore.assets.filter(asset => assetStore.selectedAssets.has(asset.id))
)

/** Index of asset to show in preview modal (from selection or from card click). */
const previewStartIndex = computed(() => {
  if (previewStartIndexOverride.value != null) {
    const v = previewStartIndexOverride.value
    return Math.max(0, Math.min(v, assetStore.assets.length - 1))
  }
  const firstId = selectedAssetIds.value[0]
  if (firstId == null) return 0
  const idx = assetStore.assets.findIndex(a => a.id === firstId)
  return idx >= 0 ? idx : 0
})

// Sprint 2: Gallery hotkeys (F, Space, Delete, Esc, Ctrl+A, ?)
useGalleryHotkeys({
  getSelectedCount: () => assetStore.selectedAssets.size,
  onFavorite: async () => {
    const list = selectedAssetsList.value
    if (list.length === 0) return
    try {
      for (const asset of list) {
        await favoritesStore.toggleFavorite(asset.id, asset)
      }
      const count = list.length
      showToast(count === 1 ? 'Избранное обновлено' : `Обновлено избранное для ${count} активов`, 'success')
    } catch {
      showToast('Не удалось обновить избранное', 'error')
    }
  },
  onPreview: () => {
    if (selectedAssetsList.value.length > 0) {
      showPreviewModal.value = true
    }
  },
  onDelete: () => {
    if (assetStore.selectedAssets.size > 0) {
      showBulkDeleteModal.value = true
    }
  },
  onClearSelection: () => assetStore.clearSelection(),
  onSelectAll: () => assetStore.selectAll(),
  onOpenCheatSheet: () => { showHotkeysCheatSheetModal.value = true },
  isPreviewOpen: () => showPreviewModal.value,
  isCheatSheetOpen: () => showHotkeysCheatSheetModal.value,
  onClosePreview: () => {
    showPreviewModal.value = false
    previewStartIndexOverride.value = null
  },
  onCloseCheatSheet: () => { showHotkeysCheatSheetModal.value = false }
})

function handleBulkTag() {
  showBulkTagModal.value = true
}

function handleBulkDelete() {
  showBulkDeleteModal.value = true
}

function handleBulkDownload() {
  showBulkDownloadModal.value = true
}

function handleBulkShare() {
  // Lazy-load share links only when the Share modal is actually opened.
  if (!distributionStore.sharedLinksLoading && (distributionStore.sharedLinks?.length || 0) === 0) {
    distributionStore.fetchSharedLinks()
  }
  showBulkShareModal.value = true
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

// Saved Searches handlers (Sprint 1 Discovery UX)
function openSaveSearchModal() {
  saveSearchBackendError.value = null
  showSaveSearchModal.value = true
}

function closeSaveSearchModal() {
  showSaveSearchModal.value = false
  saveSearchBackendError.value = null
  savedSearchesDropdownRef.value?.refresh()
}

function handleSaveSearch(name: string) {
  const filters = buildSavedSearchFilters(damSearch.state.filters)
  createSavedSearch({
    name,
    query: damSearch.state.q,
    filters
  })
    .then(() => {
      closeSaveSearchModal()
      showToast('Поиск сохранён', 'success')
    })
    .catch((e: unknown) => {
      const data = e && typeof e === 'object' && e !== null && 'response' in e ? (e as { response?: { data?: unknown } }).response?.data : null
      const msg = data && typeof data === 'object' && data !== null && 'name' in data && Array.isArray((data as { name?: unknown }).name)
        ? (data as { name: string[] }).name[0]
        : data && typeof data === 'object' && 'detail' in data
          ? String((data as { detail: unknown }).detail)
          : 'Не удалось сохранить поиск'
      saveSearchBackendError.value = msg
    })
}

function handleSavedSearchRun(item: SavedSearch) {
  damSearch.applySavedSearch(item.query || '', item.filters || {})
}

function openRenameSavedSearchModal(item: SavedSearch) {
  renameSavedSearchItem.value = item
  showRenameSavedSearchModal.value = true
}

function closeRenameSavedSearchModal() {
  showRenameSavedSearchModal.value = false
  renameSavedSearchItem.value = null
  savedSearchesDropdownRef.value?.refresh()
}

function handleRenameSavedSearch(id: number, name: string) {
  updateSavedSearch(id, { name })
    .then(() => {
      closeRenameSavedSearchModal()
      showToast('Поиск переименован', 'success')
    })
    .catch(() => {
      showToast('Не удалось переименовать', 'error')
    })
}

function handleSavedSearchDelete(id: number) {
  deleteSavedSearchId.value = id
  showDeleteSavedSearchConfirm.value = true
}

function confirmDeleteSavedSearch() {
  const id = deleteSavedSearchId.value
  showDeleteSavedSearchConfirm.value = false
  deleteSavedSearchId.value = null
  if (id == null) return
  deleteSavedSearch(id)
    .then(() => {
      savedSearchesDropdownRef.value?.refresh()
      showToast('Сохранённый поиск удалён', 'success')
    })
    .catch(() => {
      showToast('Не удалось удалить', 'error')
    })
}

function handleBulkOperationSuccess() {
  // Refresh assets after bulk operation
  assetStore.fetchAssets()
  assetStore.clearSelection()

  // UX: ensure modals are not left open showing "0 выбрано"
  showBulkTagModal.value = false
  showBulkMoveModal.value = false
  showBulkDeleteModal.value = false
  showBulkDownloadModal.value = false
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

