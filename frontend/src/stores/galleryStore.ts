/**
 * Gallery Store
 *
 * Manages virtualized gallery data with infinite scroll, filtering, search, and grouping.
 * Optimized for handling 10,000+ assets with smooth scrolling performance.
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { assetService } from '@/services/assetService'
import { debounce } from 'lodash-es'
import type { Asset, GetAssetsParams, PaginatedResponse } from '@/types/api'

// Types
export interface GalleryItem extends Asset {
  // Additional gallery-specific properties
  isVisible: boolean
  groupId?: string
  sortOrder: number
}

export interface GalleryGroup {
  id: string
  name: string
  count: number
  collapsed: boolean
  items: GalleryItem[]
}

export interface GalleryFilters {
  search?: string
  type?: string[]
  tags?: string[]
  dateFrom?: string
  dateTo?: string
  sizeMin?: number
  sizeMax?: number
  collectionId?: string
  folderId?: string
  uploadedBy?: string[]
}

export interface GallerySort {
  field: 'name' | 'date_added' | 'date_modified' | 'size' | 'type'
  direction: 'asc' | 'desc'
}

export interface GalleryState {
  // Data
  items: GalleryItem[]
  totalCount: number
  loadedPages: Set<number>

  // Virtual scrolling
  pageSize: number
  currentPage: number
  isLoading: boolean
  hasMore: boolean

  // Filtering & Search
  filters: GalleryFilters
  searchQuery: string
  sort: GallerySort

  // Grouping
  groupBy: 'none' | 'type' | 'collection' | 'date' | 'tag'
  groups: GalleryGroup[]
  collapsedGroups: Set<string>

  // Selection
  selectedItems: Set<string>
  lastSelectedIndex: number

  // View options
  viewMode: 'grid' | 'list'
  gridColumns: number
  itemHeight: number

  // Error handling
  error: string | null
  retryCount: number
}

export const useGalleryStore = defineStore(
  'gallery',
  () => {
    // State
    const items = ref<GalleryItem[]>([])
    const totalCount = ref(0)
    const loadedPages = ref(new Set<number>())

    const pageSize = ref(100) // Larger pages for better virtual scrolling
    const currentPage = ref(0)
    const isLoading = ref(false)
    const hasMore = ref(true)

    const filters = ref<GalleryFilters>({})
    const searchQuery = ref('')
    const sort = ref<GallerySort>({ field: 'date_added', direction: 'desc' })

    const groupBy = ref<'none' | 'type' | 'collection' | 'date' | 'tag'>('none')
    const groups = ref<GalleryGroup[]>([])
    const collapsedGroups = ref(new Set<string>())

    const selectedItems = ref(new Set<string>())
    const lastSelectedIndex = ref(-1)

    const viewMode = ref<'grid' | 'list'>('grid')
    const gridColumns = ref(4)
    const itemHeight = ref(260)

    const error = ref<string | null>(null)
    const retryCount = ref(0)

    // Getters
    const visibleItems = computed(() => {
      if (groupBy.value === 'none') {
        return items.value
      }

      // Return flattened items from groups, respecting collapse state
      const result: GalleryItem[] = []
      groups.value.forEach(group => {
        if (!collapsedGroups.value.has(group.id)) {
          result.push(...group.items)
        }
      })
      return result
    })

    const selectedCount = computed(() => selectedItems.value.size)

    const isAllSelected = computed(() => {
      return visibleItems.value.length > 0 && selectedItems.value.size === visibleItems.value.length
    })

    const isIndeterminate = computed(() => {
      return selectedItems.value.size > 0 && selectedItems.value.size < visibleItems.value.length
    })

    const groupedItems = computed(() => {
      if (groupBy.value === 'none') return []

      const groupMap = new Map<string, GalleryItem[]>()

      items.value.forEach(item => {
        let groupKey = ''

        switch (groupBy.value) {
          case 'type':
            groupKey = item.type || 'unknown'
            break
          case 'collection':
            groupKey = item.collection?.name || 'No Collection'
            break
          case 'date':
            const date = new Date(item.date_added)
            groupKey = date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
            break
          case 'tag':
            groupKey = item.tags?.[0] || 'No Tags'
            break
        }

        if (!groupMap.has(groupKey)) {
          groupMap.set(groupKey, [])
        }
        groupMap.get(groupKey)!.push(item)
      })

      return Array.from(groupMap.entries()).map(([name, groupItems], index) => ({
        id: `${groupBy.value}-${index}`,
        name,
        count: groupItems.length,
        collapsed: collapsedGroups.value.has(`${groupBy.value}-${index}`),
        items: groupItems
      }))
    })

    const hasActiveFilters = computed(() => {
      return Object.values(filters.value).some(value => {
        if (Array.isArray(value)) return value.length > 0
        return value !== undefined && value !== null && value !== ''
      }) || searchQuery.value.trim() !== ''
    })

    // Actions
    const resetGallery = () => {
      items.value = []
      totalCount.value = 0
      loadedPages.value.clear()
      currentPage.value = 0
      hasMore.value = true
      selectedItems.value.clear()
      lastSelectedIndex.value = -1
      error.value = null
      retryCount.value = 0
    }

    const setFilters = (newFilters: Partial<GalleryFilters>) => {
      filters.value = { ...filters.value, ...newFilters }
      resetGallery()
      loadItems()
    }

    const setSearchQuery = (query: string) => {
      searchQuery.value = query
      debouncedSearch()
    }

    const setSort = (newSort: Partial<GallerySort>) => {
      sort.value = { ...sort.value, ...newSort }
      resetGallery()
      loadItems()
    }

    const setGroupBy = (group: typeof groupBy.value) => {
      groupBy.value = group
      updateGroups()
    }

    const toggleGroup = (groupId: string) => {
      if (collapsedGroups.value.has(groupId)) {
        collapsedGroups.value.delete(groupId)
      } else {
        collapsedGroups.value.add(groupId)
      }
      groups.value = groupedItems.value
    }

    const setViewMode = (mode: typeof viewMode.value) => {
      viewMode.value = mode
      updateItemHeight()
    }

    const setGridColumns = (columns: number) => {
      gridColumns.value = Math.max(1, Math.min(8, columns))
      updateItemHeight()
    }

    const updateItemHeight = () => {
      if (viewMode.value === 'list') {
        itemHeight.value = 60 // List item height
      } else {
        // Grid item height based on aspect ratio
        itemHeight.value = 260 // Fixed height for grid
      }
    }

    const updateGroups = () => {
      groups.value = groupedItems.value
    }

    const loadItems = async (page: number = 0) => {
      if (loadedPages.value.has(page) || isLoading.value) return

      isLoading.value = true
      error.value = null

      try {
        const params: GetAssetsParams = {
          page: page + 1, // API uses 1-based pagination
          page_size: pageSize.value,
          search: searchQuery.value || undefined,
          sort: `${sort.value.direction === 'desc' ? '-' : ''}${sort.value.field}`,
          ...filters.value
        }

        // Remove empty filter values
        Object.keys(params).forEach(key => {
          const value = (params as any)[key]
          if (value === undefined || value === null || value === '' ||
              (Array.isArray(value) && value.length === 0)) {
            delete (params as any)[key]
          }
        })

        const response: PaginatedResponse<Asset> = await assetService.getAssets(params)

        // Convert to GalleryItem format
        const newItems: GalleryItem[] = response.results.map((asset, index) => ({
          ...asset,
          isVisible: true,
          sortOrder: page * pageSize.value + index
        }))

        // Add to existing items (for virtual scrolling, we append)
        if (page === 0) {
          items.value = newItems
        } else {
          items.value.push(...newItems)
        }

        totalCount.value = response.count
        loadedPages.value.add(page)
        hasMore.value = !!response.next
        currentPage.value = page

        // Update groups if needed
        if (groupBy.value !== 'none') {
          updateGroups()
        }

      } catch (err: any) {
        error.value = err.message || 'Failed to load gallery items'
        console.error('Gallery load error:', err)
      } finally {
        isLoading.value = false
      }
    }

    const loadMoreItems = () => {
      if (hasMore.value && !isLoading.value) {
        loadItems(currentPage.value + 1)
      }
    }

    const retryLoad = () => {
      retryCount.value++
      error.value = null
      loadItems(currentPage.value)
    }

    // Selection management
    const selectItem = (itemId: string, index: number) => {
      selectedItems.value.add(itemId)
      lastSelectedIndex.value = index
    }

    const deselectItem = (itemId: string) => {
      selectedItems.value.delete(itemId)
    }

    const toggleItemSelection = (itemId: string, index: number) => {
      if (selectedItems.value.has(itemId)) {
        deselectItem(itemId)
      } else {
        selectItem(itemId, index)
      }
    }

    const selectRange = (startIndex: number, endIndex: number) => {
      const start = Math.min(startIndex, endIndex)
      const end = Math.max(startIndex, endIndex)

      for (let i = start; i <= end; i++) {
        const item = visibleItems.value[i]
        if (item) {
          selectedItems.value.add(item.id)
        }
      }
    }

    const selectAll = () => {
      visibleItems.value.forEach(item => {
        selectedItems.value.add(item.id)
      })
    }

    const deselectAll = () => {
      selectedItems.value.clear()
    }

    const toggleSelectAll = () => {
      if (isAllSelected.value) {
        deselectAll()
      } else {
        selectAll()
      }
    }

    // Keyboard selection handling
    const handleKeyboardSelection = (event: KeyboardEvent, currentIndex: number) => {
      const { ctrlKey, shiftKey, key } = event
      const item = visibleItems.value[currentIndex]

      if (!item) return

      switch (key) {
        case ' ':
        case 'Enter':
          event.preventDefault()
          if (shiftKey && lastSelectedIndex.value >= 0) {
            selectRange(lastSelectedIndex.value, currentIndex)
          } else if (ctrlKey) {
            toggleItemSelection(item.id, currentIndex)
          } else {
            deselectAll()
            selectItem(item.id, currentIndex)
          }
          break

        case 'a':
          if (ctrlKey) {
            event.preventDefault()
            selectAll()
          }
          break

        case 'Escape':
          deselectAll()
          break
      }
    }

    // Debounced search
    const debouncedSearch = debounce(() => {
      resetGallery()
      loadItems()
    }, 300)

    // Watch for groupBy changes
    watch(groupBy, updateGroups)

    // Watch for search query changes (debounced)
    watch(searchQuery, debouncedSearch)

    // Initialize
    const initialize = () => {
      updateItemHeight()
      loadItems()
    }

    return {
      // State
      items,
      totalCount,
      loadedPages,
      pageSize,
      currentPage,
      isLoading,
      hasMore,
      filters,
      searchQuery,
      sort,
      groupBy,
      groups,
      collapsedGroups,
      selectedItems,
      lastSelectedIndex,
      viewMode,
      gridColumns,
      itemHeight,
      error,
      retryCount,

      // Getters
      visibleItems,
      selectedCount,
      isAllSelected,
      isIndeterminate,
      hasActiveFilters,

      // Actions
      resetGallery,
      loadItems,
      loadMoreItems,
      retryLoad,
      setFilters,
      setSearchQuery,
      setSort,
      setGroupBy,
      toggleGroup,
      setViewMode,
      setGridColumns,
      selectItem,
      deselectItem,
      toggleItemSelection,
      selectRange,
      selectAll,
      deselectAll,
      toggleSelectAll,
      handleKeyboardSelection,
      initialize
    }
  },
  {
    persist: {
      paths: ['filters', 'searchQuery', 'sort', 'groupBy', 'collapsedGroups', 'viewMode', 'gridColumns']
    }
  }
)




