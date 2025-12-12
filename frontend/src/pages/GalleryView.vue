// @ts-nocheck
<template>
  <div class="gallery-view-page">
    <!-- Header with search and filters -->
    <div class="gallery-view-page__header">
      <div class="gallery-view-page__search">
        <div class="gallery-view-page__search-input-wrapper">
          <svg class="gallery-view-page__search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search assets..."
            class="gallery-view-page__search-input"
            v-model="galleryStore.searchQuery"
            @keydown="handleSearchKeydown"
            aria-label="Search assets"
          />
          <button
            v-if="galleryStore.searchQuery"
            @click="clearSearch"
            class="gallery-view-page__search-clear"
            aria-label="Clear search"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="gallery-view-page__actions">
        <!-- View mode toggle -->
        <div class="gallery-view-page__view-toggle">
          <button
            @click="setViewMode('grid')"
            :class="{ 'gallery-view-page__view-btn--active': galleryStore.viewMode === 'grid' }"
            class="gallery-view-page__view-btn"
            aria-label="Grid view"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </button>
          <button
            @click="setViewMode('list')"
            :class="{ 'gallery-view-page__view-btn--active': galleryStore.viewMode === 'list' }"
            class="gallery-view-page__view-btn"
            aria-label="List view"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </button>
        </div>

        <!-- Group by dropdown -->
        <div class="gallery-view-page__group-by">
          <select
            v-model="galleryStore.groupBy"
            class="gallery-view-page__group-select"
            aria-label="Group by"
          >
            <option value="none">No grouping</option>
            <option value="type">Group by type</option>
            <option value="collection">Group by collection</option>
            <option value="date">Group by date</option>
            <option value="tag">Group by tag</option>
          </select>
        </div>

        <!-- Sort dropdown -->
        <div class="gallery-view-page__sort">
          <select
            :value="`${galleryStore.sort.field}-${galleryStore.sort.direction}`"
            @change="handleSortChange"
            class="gallery-view-page__sort-select"
            aria-label="Sort by"
          >
            <option value="date_added-desc">Newest first</option>
            <option value="date_added-asc">Oldest first</option>
            <option value="name-asc">Name A-Z</option>
            <option value="name-desc">Name Z-A</option>
            <option value="size-desc">Largest first</option>
            <option value="size-asc">Smallest first</option>
          </select>
        </div>

        <!-- Filters toggle -->
        <button
          @click="showFilters = !showFilters"
          :class="{ 'gallery-view-page__filters-btn--active': showFilters }"
          class="gallery-view-page__filters-btn"
          aria-label="Toggle filters"
          :aria-expanded="showFilters"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span v-if="galleryStore.hasActiveFilters" class="gallery-view-page__filter-indicator"></span>
        </button>
      </div>
    </div>

    <!-- Filters panel -->
    <div
      v-if="showFilters"
      class="gallery-view-page__filters"
      role="region"
      aria-label="Filters"
    >
      <div class="gallery-view-page__filter-grid">
        <!-- File type filter -->
        <div class="gallery-view-page__filter-group">
          <label class="gallery-view-page__filter-label">File Type</label>
          <div class="gallery-view-page__filter-options">
            <label
              v-for="type in fileTypes"
              :key="type.value"
              class="gallery-view-page__filter-option"
            >
              <input
                type="checkbox"
                :value="type.value"
                v-model="galleryStore.filters.type"
                class="gallery-view-page__filter-checkbox"
              />
              <span class="gallery-view-page__filter-text">{{ type.label }}</span>
            </label>
          </div>
        </div>

        <!-- Date range filter -->
        <div class="gallery-view-page__filter-group">
          <label class="gallery-view-page__filter-label">Date Range</label>
          <div class="gallery-view-page__filter-date-range">
            <input
              type="date"
              v-model="galleryStore.filters.dateFrom"
              class="gallery-view-page__filter-date"
              placeholder="From"
            />
            <span class="gallery-view-page__filter-date-separator">to</span>
            <input
              type="date"
              v-model="galleryStore.filters.dateTo"
              class="gallery-view-page__filter-date"
              placeholder="To"
            />
          </div>
        </div>

        <!-- Size filter -->
        <div class="gallery-view-page__filter-group">
          <label class="gallery-view-page__filter-label">File Size</label>
          <div class="gallery-view-page__filter-size-range">
            <select
              v-model="sizeFilterPreset"
              class="gallery-view-page__filter-select"
              @change="handleSizePresetChange"
            >
              <option value="">Any size</option>
              <option value="small">Small (&lt; 1MB)</option>
              <option value="medium">Medium (1MB - 10MB)</option>
              <option value="large">Large (10MB - 100MB)</option>
              <option value="xlarge">Extra Large (&gt; 100MB)</option>
            </select>
          </div>
        </div>

        <!-- Tags filter -->
        <div class="gallery-view-page__filter-group">
          <label class="gallery-view-page__filter-label">Tags</label>
          <input
            type="text"
            placeholder="Enter tags..."
            class="gallery-view-page__filter-input"
            @keydown="handleTagInput"
          />
          <div v-if="galleryStore.filters.tags?.length" class="gallery-view-page__filter-tags">
            <span
              v-for="tag in galleryStore.filters.tags"
              :key="tag"
              class="gallery-view-page__filter-tag"
            >
              {{ tag }}
              <button
                @click="removeTag(tag)"
                class="gallery-view-page__filter-tag-remove"
                :aria-label="`Remove ${tag} tag`"
              >
                ×
              </button>
            </span>
          </div>
        </div>
      </div>

      <!-- Filter actions -->
      <div class="gallery-view-page__filter-actions">
        <button
          @click="clearFilters"
          class="gallery-view-page__filter-clear"
        >
          Clear All
        </button>
        <button
          @click="applyFilters"
          class="gallery-view-page__filter-apply"
        >
          Apply Filters
        </button>
      </div>
    </div>

    <!-- Bulk actions toolbar -->
    <div
      v-if="galleryStore.selectedCount > 0"
      class="gallery-view-page__bulk-actions"
      role="toolbar"
      aria-label="Bulk actions"
    >
      <div class="gallery-view-page__bulk-info">
        <span class="gallery-view-page__bulk-count">
          {{ galleryStore.selectedCount }} item{{ galleryStore.selectedCount === 1 ? '' : 's' }} selected
        </span>
        <button
          @click="galleryStore.deselectAll()"
          class="gallery-view-page__bulk-clear"
        >
          Clear selection
        </button>
      </div>

      <div class="gallery-view-page__bulk-buttons">
        <button
          @click="handleBulkDownload"
          class="gallery-view-page__bulk-btn gallery-view-page__bulk-btn--primary"
          :disabled="bulkActionLoading"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Download
        </button>
        <button
          @click="handleBulkShare"
          class="gallery-view-page__bulk-btn"
          :disabled="bulkActionLoading"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
          Share
        </button>
        <button
          @click="handleBulkDelete"
          class="gallery-view-page__bulk-btn gallery-view-page__bulk-btn--danger"
          :disabled="bulkActionLoading"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Delete
        </button>
      </div>
    </div>

    <!-- Main gallery area -->
    <div class="gallery-view-page__content">
      <VirtualScroller
        ref="virtualScroller"
        :items="galleryStore.visibleItems"
        :total-items="galleryStore.totalCount"
        :item-height="galleryStore.itemHeight"
        :container-height="containerHeight"
        :buffer-size="bufferSize"
        :infinite-scroll="true"
        :load-more-threshold="loadMoreThreshold"
        :is-loading="galleryStore.isLoading"
        :error="galleryStore.error"
        aria-label="Asset gallery"
        @load-more="galleryStore.loadMoreItems()"
        @retry="galleryStore.retryLoad()"
        class="gallery-view-page__scroller"
      >
        <!-- Gallery item template -->
        <template #default="{ item, index }">
          <GalleryItem
            :item="{ ...item, is_favorite: favoritesStore.isFavorite(item.id), isFavorite: favoritesStore.isFavorite(item.id) }"
            :index="index"
            :view-mode="galleryStore.viewMode"
            :is-selected="galleryStore.selectedItems.has(item.id)"
            @select="handleItemSelect(item, index)"
            @open="handleItemOpen(item)"
            @favorite="handleItemFavorite(item)"
            @share="handleItemShare(item)"
            @delete="handleItemDelete(item)"
          />
        </template>

        <!-- Loading skeleton -->
        <template #skeleton="{ index }">
          <GalleryItemSkeleton
            :view-mode="galleryStore.viewMode"
            :index="index"
          />
        </template>

        <!-- Custom loading -->
        <template #loading>
          <div class="flex items-center justify-center py-6">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mr-3"></div>
            <span class="text-sm text-neutral-600 dark:text-neutral-400">Loading more assets...</span>
          </div>
        </template>
      </VirtualScroller>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
/**
 * Gallery View Page
 *
 * High-performance virtualized gallery supporting 10,000+ assets with
 * infinite scroll, filtering, search, grouping, and bulk operations.
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGalleryStore } from '@/stores/galleryStore'
import VirtualScroller from '@/components/VirtualScroller.vue'
import GalleryItem from '@/components/gallery/GalleryItem.vue'
import GalleryItemSkeleton from '@/components/gallery/GalleryItemSkeleton.vue'
import { useUIStore } from '@/stores/uiStore'
import { useFavoritesStore } from '@/stores/favoritesStore'

// Types
interface FileType {
  value: string
  label: string
}

// Composables
const galleryStore = useGalleryStore()
const uiStore = useUIStore()
const favoritesStore = useFavoritesStore()

// Reactive state
const virtualScroller = ref()
const showFilters = ref(false)
const bulkActionLoading = ref(false)
const sizeFilterPreset = ref('')
const containerHeight = ref(600)
const bufferSize = ref(5)
const loadMoreThreshold = ref(200)

// File types for filtering
const fileTypes: FileType[] = [
  { value: 'image', label: 'Images' },
  { value: 'video', label: 'Videos' },
  { value: 'audio', label: 'Audio' },
  { value: 'document', label: 'Documents' },
  { value: 'archive', label: 'Archives' },
  { value: 'other', label: 'Other' }
]

// Computed properties
const selectedCount = computed(() => galleryStore.selectedCount)

// Methods
const setViewMode = (mode: 'grid' | 'list') => {
  galleryStore.setViewMode(mode)
}

const handleSearchKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    clearSearch()
  }
}

const clearSearch = () => {
  galleryStore.setSearchQuery('')
}

const handleSortChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  const [field, direction] = target.value.split('-')
  galleryStore.setSort({ field: field as any, direction: direction as 'asc' | 'desc' })
}

const handleSizePresetChange = () => {
  const preset = sizeFilterPreset.value
  let sizeMin: number | undefined
  let sizeMax: number | undefined

  switch (preset) {
    case 'small':
      sizeMax = 1024 * 1024 // 1MB
      break
    case 'medium':
      sizeMin = 1024 * 1024 // 1MB
      sizeMax = 10 * 1024 * 1024 // 10MB
      break
    case 'large':
      sizeMin = 10 * 1024 * 1024 // 10MB
      sizeMax = 100 * 1024 * 1024 // 100MB
      break
    case 'xlarge':
      sizeMin = 100 * 1024 * 1024 // 100MB
      break
  }

  galleryStore.setFilters({ sizeMin, sizeMax })
}

const handleTagInput = (event: KeyboardEvent) => {
  const input = event.target as HTMLInputElement
  const value = input.value.trim()

  if (event.key === 'Enter' && value) {
    event.preventDefault()
    addTag(value)
    input.value = ''
  } else if (event.key === ',' && value) {
    event.preventDefault()
    const tagValue = value.replace(/,$/, '')
    addTag(tagValue)
    input.value = ''
  }
}

const addTag = (tag: string) => {
  const currentTags = galleryStore.filters.tags || []
  if (!currentTags.includes(tag)) {
    galleryStore.setFilters({ tags: [...currentTags, tag] })
  }
}

const removeTag = (tag: string) => {
  const currentTags = galleryStore.filters.tags || []
  galleryStore.setFilters({
    tags: currentTags.filter(t => t !== tag)
  })
}

const applyFilters = () => {
  // Filters are applied automatically via reactivity
  showFilters.value = false
}

const clearFilters = () => {
  galleryStore.setFilters({})
  sizeFilterPreset.value = ''
  showFilters.value = false
}

const handleItemSelect = (item: any, index: number) => {
  galleryStore.toggleItemSelection(item.id, index)
}

const handleItemOpen = (item: any) => {
  // Navigate to asset detail page
  console.log('Open item:', item)
}

const handleItemFavorite = async (item: any) => {
  try {
    const favorited = await favoritesStore.toggleFavorite(item.id)

    const target = galleryStore.items.find(i => i.id === item.id)
    if (target) {
      target.is_favorite = favorited
    }

    uiStore.addNotification({
      type: favorited ? 'success' : 'info',
      title: favorited ? 'Добавлено в избранное' : 'Убрано из избранного',
      message: favorited
        ? `"${item.name || item.label || 'Актив'}" добавлен в избранное`
        : `"${item.name || item.label || 'Актив'}" удалён из избранного`
    })
  } catch (error: any) {
    uiStore.addNotification({
      type: 'error',
      title: 'Ошибка избранного',
      message: error?.message || 'Не удалось обновить избранное'
    })
  }
}

const handleItemShare = (item: any) => {
  // Open share modal for single item
  console.log('Share item:', item)
}

const handleItemDelete = (item: any) => {
  // Open delete confirmation for single item
  console.log('Delete item:', item)
}

const handleBulkDownload = async () => {
  if (galleryStore.selectedCount === 0) return

  bulkActionLoading.value = true
  try {
    const selectedIds = Array.from(galleryStore.selectedItems)
    // Implement bulk download logic
    console.log('Bulk download:', selectedIds)

    uiStore.addNotification({
      type: 'success',
      title: 'Download Started',
      message: `Downloading ${selectedIds.length} assets...`
    })

    galleryStore.deselectAll()
  } catch (error: any) {
    uiStore.addNotification({
      type: 'error',
      title: 'Download Failed',
      message: error.message || 'Failed to start download'
    })
  } finally {
    bulkActionLoading.value = false
  }
}

const handleBulkShare = async () => {
  if (galleryStore.selectedCount === 0) return

  bulkActionLoading.value = true
  try {
    const selectedIds = Array.from(galleryStore.selectedItems)
    // Implement bulk share logic
    console.log('Bulk share:', selectedIds)

    uiStore.addNotification({
      type: 'success',
      title: 'Share Created',
      message: `Created share link for ${selectedIds.length} assets`
    })

    galleryStore.deselectAll()
  } catch (error: any) {
    uiStore.addNotification({
      type: 'error',
      title: 'Share Failed',
      message: error.message || 'Failed to create share link'
    })
  } finally {
    bulkActionLoading.value = false
  }
}

const handleBulkDelete = async () => {
  if (galleryStore.selectedCount === 0) return

  const confirmed = confirm(`Are you sure you want to delete ${galleryStore.selectedCount} assets? This action cannot be undone.`)

  if (!confirmed) return

  bulkActionLoading.value = true
  try {
    const selectedIds = Array.from(galleryStore.selectedItems)
    // Implement bulk delete logic
    console.log('Bulk delete:', selectedIds)

    uiStore.addNotification({
      type: 'success',
      title: 'Assets Deleted',
      message: `Successfully deleted ${selectedIds.length} assets`
    })

    galleryStore.deselectAll()
  } catch (error: any) {
    uiStore.addNotification({
      type: 'error',
      title: 'Delete Failed',
      message: error.message || 'Failed to delete assets'
    })
  } finally {
    bulkActionLoading.value = false
  }
}

// Resize handling for container height
const updateContainerHeight = () => {
  const windowHeight = window.innerHeight
  const headerHeight = 200 // Approximate header height
  containerHeight.value = Math.max(400, windowHeight - headerHeight)
}

const handleResize = () => {
  updateContainerHeight()
}

// Keyboard shortcuts
const handleKeydown = (event: KeyboardEvent) => {
  // Global keyboard shortcuts for gallery
  if (event.ctrlKey || event.metaKey) {
    switch (event.key) {
      case 'a':
        event.preventDefault()
        galleryStore.selectAll()
        break
      case 'f':
        event.preventDefault()
        showFilters.value = !showFilters.value
        break
    }
  }

  // Escape to clear selection
  if (event.key === 'Escape') {
    galleryStore.deselectAll()
  }
}

// Lifecycle
onMounted(() => {
  galleryStore.initialize()
  favoritesStore.fetchFavorites()
  updateContainerHeight()

  window.addEventListener('resize', handleResize)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.gallery-view-page {
  @apply flex flex-col h-full bg-neutral-50 dark:bg-neutral-900;
}

.gallery-view-page__header {
  @apply flex items-center justify-between px-6 py-4 bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700;
}

.gallery-view-page__search {
  @apply flex-1 max-w-md;
}

.gallery-view-page__search-input-wrapper {
  @apply relative;
}

.gallery-view-page__search-input {
  @apply w-full pl-10 pr-10 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:placeholder-neutral-400 dark:focus:ring-primary-600 dark:focus:border-primary-600;
}

.gallery-view-page__search-icon {
  @apply absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-neutral-400;
}

.gallery-view-page__search-clear {
  @apply absolute right-3 top-1/2 transform -translate-y-1/2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200 focus:outline-none;
}

.gallery-view-page__actions {
  @apply flex items-center space-x-4;
}

.gallery-view-page__view-toggle {
  @apply flex rounded-lg border border-neutral-300 dark:border-neutral-600;
}

.gallery-view-page__view-btn {
  @apply p-2 rounded-md transition-colors;
}

.gallery-view-page__view-btn:hover {
  @apply bg-neutral-100 dark:bg-neutral-700;
}

.gallery-view-page__view-btn--active {
  @apply bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400;
}

.gallery-view-page__group-by,
.gallery-view-page__sort {
  @apply min-w-0;
}

.gallery-view-page__group-select,
.gallery-view-page__sort-select {
  @apply px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:focus:ring-primary-600 dark:focus:border-primary-600 text-sm;
}

.gallery-view-page__filters-btn {
  @apply relative p-2 rounded-md border border-neutral-300 hover:bg-neutral-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:border-neutral-600 dark:hover:bg-neutral-700;
}

.gallery-view-page__filters-btn--active {
  @apply bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400;
}

.gallery-view-page__filter-indicator {
  @apply absolute -top-1 -right-1 w-3 h-3 bg-primary-600 rounded-full;
}

.gallery-view-page__filters {
  @apply bg-neutral-100 dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 px-6 py-4;
}

.gallery-view-page__filter-grid {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-4;
}

.gallery-view-page__filter-group {
  @apply space-y-2;
}

.gallery-view-page__filter-label {
  @apply block text-sm font-medium text-neutral-700 dark:text-neutral-300;
}

.gallery-view-page__filter-options {
  @apply space-y-2;
}

.gallery-view-page__filter-option {
  @apply flex items-center space-x-2 cursor-pointer;
}

.gallery-view-page__filter-checkbox {
  @apply w-4 h-4 text-primary-600 bg-neutral-100 border-neutral-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-neutral-800 focus:ring-2 dark:bg-neutral-700 dark:border-neutral-600;
}

.gallery-view-page__filter-text {
  @apply text-sm text-neutral-700 dark:text-neutral-300;
}

.gallery-view-page__filter-date-range {
  @apply flex items-center space-x-2;
}

.gallery-view-page__filter-date {
  @apply flex-1 px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:focus:ring-primary-600 dark:focus:border-primary-600 text-sm;
}

.gallery-view-page__filter-date-separator {
  @apply text-neutral-500 dark:text-neutral-400;
}

.gallery-view-page__filter-select {
  @apply w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:focus:ring-primary-600 dark:focus:border-primary-600 text-sm;
}

.gallery-view-page__filter-input {
  @apply w-full px-3 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:focus:ring-primary-600 dark:focus:border-primary-600 text-sm;
}

.gallery-view-page__filter-tags {
  @apply flex flex-wrap gap-2 mt-2;
}

.gallery-view-page__filter-tag {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900/20 dark:text-primary-400;
}

.gallery-view-page__filter-tag-remove {
  @apply ml-1 text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300 focus:outline-none;
}

.gallery-view-page__filter-actions {
  @apply flex justify-end space-x-3;
}

.gallery-view-page__filter-clear {
  @apply px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-neutral-100 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md;
}

.gallery-view-page__filter-apply {
  @apply px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md;
}

.gallery-view-page__bulk-actions {
  @apply bg-primary-50 dark:bg-primary-900/10 border-b border-primary-200 dark:border-primary-800 px-6 py-3;
}

.gallery-view-page__bulk-info {
  @apply flex items-center justify-between;
}

.gallery-view-page__bulk-count {
  @apply text-sm font-medium text-primary-900 dark:text-primary-100;
}

.gallery-view-page__bulk-clear {
  @apply text-sm text-primary-700 dark:text-primary-300 hover:text-primary-900 dark:hover:text-primary-100 underline focus:outline-none;
}

.gallery-view-page__bulk-buttons {
  @apply flex items-center space-x-3 mt-3;
}

.gallery-view-page__bulk-btn {
  @apply inline-flex items-center px-3 py-2 text-sm font-medium rounded-md border border-transparent focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed;
}

.gallery-view-page__bulk-btn--primary {
  @apply text-white bg-primary-600 hover:bg-primary-700;
}

.gallery-view-page__bulk-btn--danger {
  @apply text-white bg-red-600 hover:bg-red-700;
}

.gallery-view-page__content {
  @apply flex-1 overflow-hidden;
}

.gallery-view-page__scroller {
  @apply h-full;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .gallery-view-page__header {
    @apply flex-col space-y-4 items-stretch px-4 py-3;
  }

  .gallery-view-page__search {
    @apply max-w-none;
  }

  .gallery-view-page__actions {
    @apply flex-wrap justify-center gap-2;
  }

  .gallery-view-page__filter-grid {
    @apply grid-cols-1 gap-4;
  }

  .gallery-view-page__filter-date-range {
    @apply flex-col space-x-0 space-y-2;
  }

  .gallery-view-page__bulk-buttons {
    @apply flex-col space-x-0 space-y-2;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .gallery-view-page__view-btn,
  .gallery-view-page__filters-btn {
    @apply border-2;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .gallery-view-page__view-btn,
  .gallery-view-page__filters-btn,
  .gallery-view-page__filter-clear,
  .gallery-view-page__filter-apply {
    @apply transition-none;
  }
}
</style>












