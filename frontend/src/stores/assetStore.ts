/**
 * Asset Store
 * 
 * Manages DAM assets state with support for:
 * - Real API (Mayan EDMS /api/v4/documents/)
 * - Mock data (for frontend-first development)
 * 
 * Handles pagination, filtering, sorting, selection, and CRUD operations.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { assetService } from '@/services/assetService'
import type { Asset, GetAssetsParams, PaginatedResponse } from '@/types/api'
import { formatApiError } from '@/utils/errors'
import type { AxiosProgressEvent } from 'axios'

// Import document adapter for Mayan API transformation
import {
  adaptPaginatedResponse,
  adaptDocument,
  type MayanDocument,
  type MayanPaginatedResponse
} from '@/services/adapters/documentAdapter'
import { getToken } from '@/services/authService'

// Import mock data functions
import {
  getMockAssets,
  getMockAssetById,
  deleteMockAsset,
  updateMockAsset,
  addMockAsset,
  getMockTags,
  getMockTypeCounts,
  getMockStatusCounts,
  type MockAssetFilters,
  type MockAssetSort,
} from '@/mocks/assets'

// ============================================================================
// TYPES
// ============================================================================

interface UploadOptions {
  onUploadProgress?: (event: AxiosProgressEvent) => void
  signal?: AbortSignal
}

interface AssetFilters {
  type?: string[]
  tags?: string[]
  status?: string[]
  dateFrom?: string
  dateTo?: string
  sizeMin?: number
  sizeMax?: number
  search?: string
}

interface AssetSort {
  field: 'date_added' | 'name' | 'size' | 'type'
  direction: 'asc' | 'desc'
}

// ============================================================================
// STORE DEFINITION
// ============================================================================

export const useAssetStore = defineStore(
  'asset',
  () => {
    // ========================================================================
    // CONFIGURATION
    // ========================================================================
    
    /**
     * Enable mock data mode.
     * When true, uses local mock data instead of API calls.
     * Set to false to connect to real Mayan EDMS backend.
     */
    const useMock = ref(import.meta.env.VITE_USE_MOCK_DATA === 'true')
    
    /**
     * Simulated network delay in milliseconds.
     * Only applies when useMock is true.
     */
    const mockDelay = ref(300)
    
    /**
     * Debug mode - stores raw API response for debugging
     */
    const debugMode = ref(import.meta.env.DEV)
    const lastRawResponse = ref<any>(null)
    
    // ========================================================================
    // STATE
    // ========================================================================
    
    const assets = ref<Asset[]>([])
    const totalCount = ref(0)
    const currentPage = ref(1)
    const pageSize = ref(24) // Good for 6-column grid
    const totalPages = ref(0)
    const isLoading = ref(false)
    const isLoadingMore = ref(false)
    const error = ref<string | null>(null)
    const selectedAssets = ref<Set<number>>(new Set())
    const currentAsset = ref<Asset | null>(null)
    
    // Filters and sorting
    const filters = ref<AssetFilters>({})
    const sort = ref<AssetSort>({ field: 'date_added', direction: 'desc' })
    const searchQuery = ref('')
    
    // Facets for filtering UI
    const availableTags = ref<string[]>([])
    const typeCounts = ref<Record<string, number>>({})
    const statusCounts = ref<Record<string, number>>({})
    
    // ========================================================================
    // GETTERS
    // ========================================================================
    
    const hasNextPage = computed(() => currentPage.value < totalPages.value)
    const hasPreviousPage = computed(() => currentPage.value > 1)
    const selectedCount = computed(() => selectedAssets.value.size)
    const hasSelection = computed(() => selectedAssets.value.size > 0)
    const allSelected = computed(() => 
      assets.value.length > 0 && selectedAssets.value.size === assets.value.length
    )
    const currentPageAssets = computed(() => assets.value)
    
    const hasActiveFilters = computed(() => {
      return !!(
        filters.value.type?.length ||
        filters.value.tags?.length ||
        filters.value.status?.length ||
        filters.value.dateFrom ||
        filters.value.dateTo ||
        filters.value.sizeMin !== undefined ||
        filters.value.sizeMax !== undefined ||
        searchQuery.value.trim()
      )
    })
    
    const selectedAssetsList = computed(() => 
      assets.value.filter(asset => selectedAssets.value.has(asset.id))
    )
    
    // ========================================================================
    // HELPER FUNCTIONS
    // ========================================================================
    
    /**
     * Simulate network delay for mock mode
     */
    async function simulateDelay(): Promise<void> {
      if (useMock.value && mockDelay.value > 0) {
        await new Promise(resolve => setTimeout(resolve, mockDelay.value))
      }
    }
    
    /**
     * Convert store filters to mock filter format
     */
    function toMockFilters(): MockAssetFilters {
      return {
        type: filters.value.type,
        tags: filters.value.tags,
        status: filters.value.status,
        dateFrom: filters.value.dateFrom,
        dateTo: filters.value.dateTo,
        sizeMin: filters.value.sizeMin,
        sizeMax: filters.value.sizeMax,
        search: searchQuery.value,
      }
    }
    
    /**
     * Convert store sort to mock sort format
     */
    function toMockSort(): MockAssetSort {
      return {
        field: sort.value.field,
        direction: sort.value.direction,
      }
    }
    
    // ========================================================================
    // ACTIONS - FETCH
    // ========================================================================
    
    /**
     * Fetch assets with current filters and pagination
     * Uses Mayan EDMS /api/v4/documents/ endpoint with documentAdapter
     */
    async function fetchAssets(params?: GetAssetsParams): Promise<void> {
      isLoading.value = true
      error.value = null
      lastRawResponse.value = null

      try {
        if (useMock.value) {
          // Use mock data
          await simulateDelay()
          
          const response = getMockAssets(
            params?.page || currentPage.value,
            params?.page_size || pageSize.value,
            toMockFilters(),
            toMockSort()
          )
          
          assets.value = response.results
          totalCount.value = response.count
          totalPages.value = response.total_pages || Math.ceil(response.count / pageSize.value)
          
          // Update facets
          availableTags.value = getMockTags()
          typeCounts.value = getMockTypeCounts()
          statusCounts.value = getMockStatusCounts()
          
          if (params?.page) {
            currentPage.value = params.page
          }
          
          console.log('[AssetStore] Loaded mock assets:', response.results.length)
        } else {
          // Use real Mayan EDMS API
          const token = getToken()
          
          // If no token available, fall back to mock data
          if (!token) {
            console.warn('[AssetStore] No auth token found, falling back to mock data')
            await simulateDelay()
            
            const response = getMockAssets(
              params?.page || currentPage.value,
              params?.page_size || pageSize.value,
              toMockFilters(),
              toMockSort()
            )
            
            assets.value = response.results
            totalCount.value = response.count
            totalPages.value = response.total_pages || Math.ceil(response.count / pageSize.value)
            
            if (params?.page) {
              currentPage.value = params.page
            }
            
            console.log('[AssetStore] Loaded mock assets (no token):', response.results.length)
            return
          }
          
          console.log('[AssetStore] Fetching from real API...')

          // Build query params
          const queryParams = new URLSearchParams()
          queryParams.set('page', String(params?.page || currentPage.value))
          queryParams.set('page_size', String(params?.page_size || pageSize.value))
          
          // Add search query if present
          if (searchQuery.value) {
            queryParams.set('q', searchQuery.value)
          }

          // Fetch from Mayan API
          const response = await axios.get<MayanPaginatedResponse<MayanDocument>>(
            `/api/v4/documents/?${queryParams.toString()}`,
            {
              headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
              }
            }
          )

          // Store raw response for debugging
          if (debugMode.value) {
            lastRawResponse.value = response.data
            console.log('[AssetStore] Raw API response:', response.data)
          }

          // Transform using adapter
          const adapted = adaptPaginatedResponse(response.data)
          
          assets.value = adapted.results
          totalCount.value = adapted.count
          totalPages.value = adapted.total_pages || Math.ceil(adapted.count / pageSize.value)

          if (params?.page) {
            currentPage.value = params.page
          }

          console.log('[AssetStore] Loaded real assets:', adapted.results.length)
        }
      } catch (err: any) {
        console.error('[AssetStore] Fetch error:', err)
        
        // Handle specific error cases
        if (err.response?.status === 401) {
          error.value = 'Сессия истекла. Войдите снова.'
        } else if (err.response?.status === 403) {
          error.value = 'Нет доступа к документам.'
        } else {
          error.value = formatApiError(err)
        }
        
        assets.value = []
        totalCount.value = 0
        totalPages.value = 0
        throw err
      } finally {
        isLoading.value = false
      }
    }
    
    /**
     * Load more assets (infinite scroll)
     */
    async function loadMore(): Promise<void> {
      if (!hasNextPage.value || isLoadingMore.value) return
      
      isLoadingMore.value = true
      error.value = null
      
      try {
        const nextPage = currentPage.value + 1
        
        if (useMock.value) {
          await simulateDelay()
          
          const response = getMockAssets(
            nextPage,
            pageSize.value,
            toMockFilters(),
            toMockSort()
          )
          
          assets.value = [...assets.value, ...response.results]
          currentPage.value = nextPage
        } else {
          // Use real Mayan API
          const token = getToken()
          
          // Fallback to mock if no token
          if (!token) {
            await simulateDelay()
            const response = getMockAssets(nextPage, pageSize.value, toMockFilters(), toMockSort())
            assets.value = [...assets.value, ...response.results]
            currentPage.value = nextPage
            return
          }

          const queryParams = new URLSearchParams()
          queryParams.set('page', String(nextPage))
          queryParams.set('page_size', String(pageSize.value))
          
          if (searchQuery.value) {
            queryParams.set('q', searchQuery.value)
          }

          const response = await axios.get<MayanPaginatedResponse<MayanDocument>>(
            `/api/v4/documents/?${queryParams.toString()}`,
            {
              headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
              }
            }
          )

          const adapted = adaptPaginatedResponse(response.data)
          assets.value = [...assets.value, ...adapted.results]
          currentPage.value = nextPage
        }
      } catch (err) {
        error.value = formatApiError(err)
      } finally {
        isLoadingMore.value = false
      }
    }
    
    /**
     * Get single asset details
     */
    async function getAssetDetail(id: number): Promise<Asset | null> {
      isLoading.value = true
      error.value = null

      try {
        if (useMock.value) {
          await simulateDelay()
          
          const asset = getMockAssetById(id)
          if (asset) {
            currentAsset.value = asset
            return asset
          }
          throw new Error(`Asset with ID ${id} not found`)
        } else {
          // Use real Mayan API
          const token = getToken()
          
          // Fallback to mock if no token
          if (!token) {
            await simulateDelay()
            const asset = getMockAssetById(id)
            if (asset) {
              currentAsset.value = asset
              return asset
            }
            throw new Error(`Asset with ID ${id} not found`)
          }

          const response = await axios.get<MayanDocument>(
            `/api/v4/documents/${id}/`,
            {
              headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
              }
            }
          )

          const asset = adaptDocument(response.data)
          currentAsset.value = asset
          return asset
        }
      } catch (err) {
        error.value = formatApiError(err)
        currentAsset.value = null
        return null
      } finally {
        isLoading.value = false
      }
    }
    
    // ========================================================================
    // ACTIONS - CRUD
    // ========================================================================
    
    /**
     * Delete an asset
     */
    async function deleteAsset(id: number): Promise<boolean> {
      try {
        await simulateDelay()
        
        if (useMock.value) {
          const success = deleteMockAsset(id)
          if (success) {
            // Remove from local state
            assets.value = assets.value.filter(a => a.id !== id)
            totalCount.value = Math.max(0, totalCount.value - 1)
            selectedAssets.value.delete(id)
            
            if (currentAsset.value?.id === id) {
              currentAsset.value = null
            }
          }
          return success
        } else {
          await assetService.deleteAsset(id)
          assets.value = assets.value.filter(a => a.id !== id)
          totalCount.value = Math.max(0, totalCount.value - 1)
          selectedAssets.value.delete(id)
          
          if (currentAsset.value?.id === id) {
            currentAsset.value = null
          }
          return true
        }
      } catch (err) {
        error.value = formatApiError(err)
        return false
      }
    }
    
    /**
     * Update an asset
     */
    async function updateAssetData(id: number, data: Partial<Asset>): Promise<Asset | null> {
      try {
        await simulateDelay()
        
        if (useMock.value) {
          const updated = updateMockAsset(id, data)
          if (updated) {
            // Update in local state
            const index = assets.value.findIndex(a => a.id === id)
            if (index !== -1) {
              assets.value[index] = updated
            }
            if (currentAsset.value?.id === id) {
              currentAsset.value = updated
            }
          }
          return updated || null
        } else {
          const updated = await assetService.updateAsset(id, data)
          const index = assets.value.findIndex(a => a.id === id)
          if (index !== -1) {
            assets.value[index] = updated
          }
          if (currentAsset.value?.id === id) {
            currentAsset.value = updated
          }
          return updated
        }
      } catch (err) {
        error.value = formatApiError(err)
        return null
      }
    }
    
    /**
     * Bulk delete assets
     */
    async function bulkDelete(ids: number[]): Promise<number> {
      let deletedCount = 0
      
      for (const id of ids) {
        const success = await deleteAsset(id)
        if (success) deletedCount++
      }
      
      return deletedCount
    }
    
    // ========================================================================
    // ACTIONS - PAGINATION
    // ========================================================================
    
    function nextPage(): void {
      if (hasNextPage.value) {
        currentPage.value++
        fetchAssets()
      }
    }

    function previousPage(): void {
      if (hasPreviousPage.value) {
        currentPage.value--
        fetchAssets()
      }
    }

    function setPage(page: number): void {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        fetchAssets()
      }
    }

    function setPageSize(size: number): void {
      pageSize.value = Math.min(Math.max(size, 1), 100)
      currentPage.value = 1
      fetchAssets()
    }
    
    // ========================================================================
    // ACTIONS - SELECTION
    // ========================================================================
    
    function selectAsset(asset: Asset): void {
      if (selectedAssets.value.has(asset.id)) {
        selectedAssets.value.delete(asset.id)
      } else {
        selectedAssets.value.add(asset.id)
      }
      // Trigger reactivity
      selectedAssets.value = new Set(selectedAssets.value)
    }
    
    function toggleSelection(id: number): void {
      if (selectedAssets.value.has(id)) {
        selectedAssets.value.delete(id)
      } else {
        selectedAssets.value.add(id)
      }
      selectedAssets.value = new Set(selectedAssets.value)
    }

    function selectAll(): void {
      assets.value.forEach(asset => selectedAssets.value.add(asset.id))
      selectedAssets.value = new Set(selectedAssets.value)
    }

    function clearSelection(): void {
      selectedAssets.value.clear()
      selectedAssets.value = new Set(selectedAssets.value)
    }
    
    function isSelected(id: number): boolean {
      return selectedAssets.value.has(id)
    }
    
    // ========================================================================
    // ACTIONS - FILTERS & SORT
    // ========================================================================
    
    function setSort(newSort: AssetSort): void {
      sort.value = newSort
      currentPage.value = 1
      fetchAssets()
    }
    
    function setSortBy(field: AssetSort['field'], direction: AssetSort['direction'] = 'desc'): void {
      setSort({ field, direction })
    }

    function applyFilters(newFilters: Partial<AssetFilters>): void {
      filters.value = { ...filters.value, ...newFilters }
      currentPage.value = 1
      fetchAssets()
    }
    
    function setFilters(newFilters: AssetFilters): void {
      filters.value = newFilters
      currentPage.value = 1
      fetchAssets()
    }

    function clearFilters(): void {
      filters.value = {}
      searchQuery.value = ''
      currentPage.value = 1
      fetchAssets()
    }
    
    function setSearchQuery(query: string): void {
      searchQuery.value = query
      currentPage.value = 1
      fetchAssets()
    }

    function refresh(): void {
      fetchAssets()
    }
    
    // ========================================================================
    // ACTIONS - UPLOAD
    // ========================================================================

    async function uploadAsset(
      formData: FormData,
      options?: UploadOptions
    ): Promise<Asset> {
      return assetService.uploadAsset(formData, {
        onUploadProgress: options?.onUploadProgress,
        signal: options?.signal
      })
    }
    
    /**
     * Add a new asset (for mock/local development)
     * Creates asset from provided data and adds to the store
     */
    async function addAsset(assetData: Omit<Asset, 'id'>): Promise<Asset> {
      await simulateDelay()
      
      if (useMock.value) {
        // Add to mock data store
        const newAsset = addMockAsset(assetData)
        
        // Add to local state at the beginning
        assets.value = [newAsset, ...assets.value]
        totalCount.value += 1
        
        // Update facets
        availableTags.value = getMockTags()
        typeCounts.value = getMockTypeCounts()
        statusCounts.value = getMockStatusCounts()
        
        return newAsset
      } else {
        // For real API, use uploadAsset instead
        throw new Error('addAsset is only available in mock mode. Use uploadAsset for real API.')
      }
    }
    
    /**
     * Add multiple assets at once (batch upload)
     */
    async function addAssets(assetsData: Omit<Asset, 'id'>[]): Promise<Asset[]> {
      const addedAssets: Asset[] = []
      
      for (const assetData of assetsData) {
        const newAsset = await addAsset(assetData)
        addedAssets.push(newAsset)
      }
      
      return addedAssets
    }
    
    // ========================================================================
    // RETURN
    // ========================================================================

    return {
      // Configuration
      useMock,
      mockDelay,
      debugMode,
      lastRawResponse,
      
      // State
      assets,
      totalCount,
      currentPage,
      pageSize,
      totalPages,
      isLoading,
      isLoadingMore,
      error,
      selectedAssets,
      currentAsset,
      filters,
      sort,
      searchQuery,
      availableTags,
      typeCounts,
      statusCounts,

      // Getters
      hasNextPage,
      hasPreviousPage,
      selectedCount,
      hasSelection,
      allSelected,
      currentPageAssets,
      hasActiveFilters,
      selectedAssetsList,

      // Actions - Fetch
      fetchAssets,
      loadMore,
      getAssetDetail,
      
      // Actions - CRUD
      deleteAsset,
      updateAssetData,
      bulkDelete,
      
      // Actions - Pagination
      nextPage,
      previousPage,
      setPage,
      setPageSize,
      
      // Actions - Selection
      selectAsset,
      toggleSelection,
      selectAll,
      clearSelection,
      isSelected,
      
      // Actions - Filters & Sort
      setSort,
      setSortBy,
      applyFilters,
      setFilters,
      clearFilters,
      setSearchQuery,
      refresh,
      
      // Actions - Upload
      uploadAsset,
      addAsset,
      addAssets,
    }
  },
  {
    persist: {
      paths: ['pageSize', 'sort', 'useMock']
    }
  }
)
