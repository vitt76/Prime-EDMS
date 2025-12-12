/**
 * Asset Store - Phase A2 Implementation
 * 
 * Manages DAM assets state connected to real Mayan EDMS backend.
 * Uses optimized API endpoint: GET /api/v4/documents/optimized/
 * 
 * Features:
 * - Real API integration (no more mock mode)
 * - Pagination, filtering, sorting
 * - Selection management
 * - CRUD operations
 * - Upload support via 2-step Mayan API
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import type { Asset, GetAssetsParams, PaginatedResponse } from '@/types/api'
import { formatApiError } from '@/utils/errors'
import type { AxiosProgressEvent } from 'axios'
import type { FolderSource } from '@/mocks/folders'

// Import optimized adapter for Mayan API transformation
import {
  adaptBackendPaginatedResponse,
  adaptBackendAsset,
  type BackendOptimizedDocument,
  type BackendPaginatedResponse,
} from '@/services/adapters/mayanAdapter'

import { getToken, clearToken } from '@/services/authService'
import {
  uploadService,
  updateDocumentMetadata,
  deleteDocument as deleteDocumentApi,
  type UploadProgress
} from '@/services/uploadService'
const LOG_ENDPOINT = 'http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac'

// Import auth store for logout on 401
import { useAuthStore } from '@/stores/authStore'

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
// API CONFIGURATION
// ============================================================================

/** 
 * Optimized Documents API endpoint
 * Phase B2: Returns high-performance JSON with N+1 query fixes
 */
const OPTIMIZED_DOCUMENTS_API = '/api/v4/documents/optimized/'

/**
 * Fallback to standard Documents API if optimized not available
 */
const STANDARD_DOCUMENTS_API = '/api/v4/documents/'

// ============================================================================
// STORE DEFINITION
// ============================================================================

export const useAssetStore = defineStore(
  'asset',
  () => {
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
    const folderFilterId = ref<string | null>(null)
    const folderFilterType = ref<FolderSource | null>(null)
    
    // Facets for filtering UI
    const availableTags = ref<string[]>([])
    const typeCounts = ref<Record<string, number>>({})
    const statusCounts = ref<Record<string, number>>({})
    
    // Debug mode
    const debugMode = ref(import.meta.env.DEV)
    const lastRawResponse = ref<any>(null)
    
    // API endpoint preference
    const useOptimizedApi = ref(true)
    
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

    const activeFolderId = computed(() => folderFilterId.value)
    
    // ========================================================================
    // HELPER FUNCTIONS
    // ========================================================================
    
    /**
     * Build query parameters for API request
     */
    function buildQueryParams(params?: GetAssetsParams): URLSearchParams {
      const queryParams = new URLSearchParams()
      
      // Pagination
      queryParams.set('page', String(params?.page || currentPage.value))
      queryParams.set('page_size', String(params?.page_size || pageSize.value))
      
      // Sorting - map frontend field names to backend
      const sortField = sort.value.field === 'date_added' ? 'datetime_created' 
                      : sort.value.field === 'name' ? 'label' 
                      : sort.value.field
      const sortDirection = sort.value.direction === 'desc' ? '-' : ''
      queryParams.set('ordering', `${sortDirection}${sortField}`)
      
      // Search
      if (searchQuery.value.trim()) {
        queryParams.set('q', searchQuery.value.trim())
      }

      // Folder (cabinet) filter - only for local system folders
      if (folderFilterId.value && folderFilterType.value === 'local') {
        queryParams.set('cabinets__id', folderFilterId.value)
      }
      
      // Type filter
      if (filters.value.type?.length) {
        // Mayan uses document_type__label for filtering
        filters.value.type.forEach(type => {
          queryParams.append('document_type__label', type)
        })
      }
      
      // Date range
      if (filters.value.dateFrom) {
        queryParams.set('datetime_created__gte', filters.value.dateFrom)
      }
      if (filters.value.dateTo) {
        queryParams.set('datetime_created__lte', filters.value.dateTo)
      }
      
      return queryParams
    }
    
    /**
     * Get authorization headers
     */
    function getAuthHeaders(): Record<string, string> {
      const token = getToken()
      if (!token) {
        throw new Error('Not authenticated')
      }
      return {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    }
    
    /**
     * Handle API errors with proper logout on 401
     */
    async function handleApiError(err: any): Promise<void> {
      console.error('[AssetStore] API error:', err)
      
      if (err.response?.status === 401) {
        // Token expired or invalid - logout user
        console.warn('[AssetStore] 401 Unauthorized - logging out')
        const authStore = useAuthStore()
        await authStore.logout()
        error.value = 'Сессия истекла. Войдите снова.'
        return
      }
      
      if (err.response?.status === 403) {
        error.value = 'Нет доступа к документам.'
        return
      }
      
      if (err.code === 'ERR_NETWORK' || err.message?.includes('Network')) {
        error.value = 'Ошибка сети. Проверьте подключение.'
        return
      }
      
      error.value = formatApiError(err)
    }
    
    // ========================================================================
    // ACTIONS - FETCH
    // ========================================================================
    
    /**
     * Fetch assets from real Mayan EDMS API
     * Uses optimized endpoint: GET /api/v4/documents/optimized/
     */
    async function fetchAssets(params?: GetAssetsParams): Promise<void> {
      isLoading.value = true
      error.value = null
      lastRawResponse.value = null

      try {
        const token = getToken()
        
        if (!token) {
          console.warn('[AssetStore] No auth token - redirecting to login')
          const authStore = useAuthStore()
          await authStore.logout()
          error.value = 'Необходимо войти в систему'
          return
        }
        
        const queryParams = buildQueryParams(params)
        
        // Try optimized endpoint first, fallback to standard if needed
        const apiEndpoint = useOptimizedApi.value 
          ? OPTIMIZED_DOCUMENTS_API 
          : STANDARD_DOCUMENTS_API

        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: `log_fetchAssets_req_${Date.now()}`,
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'post-fix',
            hypothesisId: 'H4',
            location: 'assetStore:fetchAssets',
            message: 'Requesting assets',
            data: {
              apiEndpoint,
              query: queryParams.toString(),
              folderFilterId: folderFilterId.value,
              folderFilterType: folderFilterType.value
            }
          })
        }).catch(() => {})
        // #endregion agent log
        
        console.log(`[AssetStore] Fetching from ${apiEndpoint}?${queryParams.toString()}`)

        const response = await axios.get<BackendPaginatedResponse<BackendOptimizedDocument>>(
          `${apiEndpoint}?${queryParams.toString()}`,
          { headers: getAuthHeaders() }
        )

        // Store raw response for debugging
        if (debugMode.value) {
          lastRawResponse.value = response.data
          console.log('[AssetStore] Raw API response:', response.data)
        }

        // Transform using optimized adapter
        const adapted = adaptBackendPaginatedResponse(response.data)
        
        assets.value = adapted.results
        totalCount.value = adapted.count
        totalPages.value = adapted.total_pages || Math.ceil(adapted.count / pageSize.value)

        if (params?.page) {
          currentPage.value = params.page
        }

        // Extract unique tags for filter UI
        const allTags = new Set<string>()
        adapted.results.forEach(asset => {
          asset.tags?.forEach(tag => allTags.add(tag))
        })
        availableTags.value = Array.from(allTags).sort()

        console.log(`[AssetStore] Loaded ${adapted.results.length} assets from API`)

        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: `log_fetchAssets_ok_${Date.now()}`,
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'post-fix',
            hypothesisId: 'H4',
            location: 'assetStore:fetchAssets',
            message: 'Assets loaded',
            data: {
              count: adapted.results.length,
              total: adapted.count,
              folderFilterId: folderFilterId.value,
              folderFilterType: folderFilterType.value
            }
          })
        }).catch(() => {})
        // #endregion agent log
        
      } catch (err: any) {
        // If optimized endpoint fails with 404, try standard endpoint
        if (err.response?.status === 404 && useOptimizedApi.value) {
          console.warn('[AssetStore] Optimized API not available, falling back to standard API')
          useOptimizedApi.value = false
          return fetchAssets(params)
        }
        
        await handleApiError(err)
        assets.value = []
        totalCount.value = 0
        totalPages.value = 0
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
        const queryParams = buildQueryParams({ page: nextPage })
        
        const apiEndpoint = useOptimizedApi.value 
          ? OPTIMIZED_DOCUMENTS_API 
          : STANDARD_DOCUMENTS_API

        const response = await axios.get<BackendPaginatedResponse<BackendOptimizedDocument>>(
          `${apiEndpoint}?${queryParams.toString()}`,
          { headers: getAuthHeaders() }
        )

        const adapted = adaptBackendPaginatedResponse(response.data)
        assets.value = [...assets.value, ...adapted.results]
        currentPage.value = nextPage
        
        console.log(`[AssetStore] Loaded more: ${adapted.results.length} assets`)
        
      } catch (err: any) {
        await handleApiError(err)
      } finally {
        isLoadingMore.value = false
      }
    }
    
    /**
     * Get single asset details
     * First tries enriched endpoint (/api/v4/document-detail/) for full document details
     * Falls back to standard endpoint if DAM endpoint unavailable
     */
    async function getAssetDetail(id: number, forceReload = false): Promise<Asset | null> {
      // Try existing cached asset first (already has URLs)
      if (!forceReload) {
        const cached = assets.value.find(a => a.id === id)
        if (cached) {
          currentAsset.value = cached
          return cached
        }
      }
      
      isLoading.value = true
      error.value = null

      try {
        // Try DAM-enriched endpoint first (includes AI analysis, metadata)
        let response: any
        
        try {
          response = await axios.get<BackendOptimizedDocument>(
            `/api/v4/document-detail/${id}/`,
            { headers: getAuthHeaders() }
          )
          if (debugMode.value) {
            console.log('[AssetStore] Loaded via DAM endpoint:', response.data)
          }
        } catch (damError: any) {
          // Fallback to standard documents API if DAM endpoint not available
          if (damError.response?.status === 404) {
            console.warn('[AssetStore] DAM endpoint not found, using standard API')
            response = await axios.get<BackendOptimizedDocument>(
              `/api/v4/documents/${id}/`,
              { headers: getAuthHeaders() }
            )
          } else {
            throw damError
          }
        }

        const asset = adaptBackendAsset(response.data)

        // If no file information, try to fetch file details separately
        console.log('[AssetStore] Checking file details:', { hasFileDetails: !!asset.file_details, size: asset.size, fileLatestId: asset.file_latest_id })
        if (!asset.file_details || asset.size === 0) {
          console.log('[AssetStore] Fetching file details for asset', id)
          try {
            // Try to get file list and take the latest file
            const filesResponse = await axios.get(
              `/api/v4/documents/${id}/files/`,
              { headers: getAuthHeaders() }
            )

            // #region agent log
            try {
              fetch(LOG_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  sessionId: 'debug-session',
                  runId: 'info-card-debug',
                  hypothesisId: 'H-info-fields',
                  location: 'assetStore:getAssetDetail',
                  message: 'Files list API response',
                  data: {
                    documentId: id,
                    filesCount: filesResponse.data?.results?.length || 0,
                    filesData: filesResponse.data?.results,
                    hasResults: !!filesResponse.data?.results
                  },
                  timestamp: Date.now()
                })
              }).catch(() => {})
            } catch (e) {
              // ignore logging errors
            }
            // #endregion agent log

            if (filesResponse.data?.results && filesResponse.data.results.length > 0) {
              // Sort by timestamp descending and take the latest file
              const latestFile = filesResponse.data.results
                .sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())[0]

              // #region agent log
              try {
                fetch(LOG_ENDPOINT, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    sessionId: 'debug-session',
                    runId: 'info-card-debug',
                    hypothesisId: 'H-info-fields',
                    location: 'assetStore:getAssetDetail',
                    message: 'Latest file selected',
                    data: {
                      documentId: id,
                      latestFileId: latestFile.id,
                      latestFilename: latestFile.filename,
                      latestSize: latestFile.size,
                      latestMimetype: latestFile.mimetype,
                      latestTimestamp: latestFile.timestamp
                    },
                    timestamp: Date.now()
                  })
                }).catch(() => {})
              } catch (e) {
                // ignore logging errors
              }
              // #endregion agent log

              asset.filename = latestFile.filename || asset.filename
              asset.size = latestFile.size || asset.size
              asset.mime_type = latestFile.mimetype || asset.mime_type
              asset.file_details = {
                filename: latestFile.filename,
                size: latestFile.size,
                mime_type: latestFile.mimetype,
                uploaded_date: latestFile.timestamp,
                checksum: latestFile.checksum,
              }
              console.log('[AssetStore] Updated asset with file details:', {
                filename: asset.filename,
                size: asset.size,
                mime_type: asset.mime_type,
                date_added: asset.date_added
              })
              // Use file upload date as the asset date_added if available
              if (latestFile.timestamp) {
                asset.date_added = latestFile.timestamp
                // #region agent log
                try {
                  fetch(LOG_ENDPOINT, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      sessionId: 'debug-session',
                      runId: 'info-card-debug',
                      hypothesisId: 'H-info-fields',
                      location: 'assetStore:getAssetDetail',
                      message: 'Updated asset date_added from file',
                      data: {
                        documentId: id,
                        originalDate: asset.date_added,
                        fileTimestamp: latestFile.timestamp,
                        finalDate: asset.date_added
                      },
                      timestamp: Date.now()
                    })
                  }).catch(() => {})
                } catch (e) {
                  // ignore logging errors
                }
                // #endregion agent log
              }
            }
          } catch (fileError: any) {
            console.warn('[AssetStore] Could not fetch file details:', fileError)
            console.log('[AssetStore] File details fetch failed, asset remains:', { size: asset.size, hasFileDetails: !!asset.file_details })
            // #region agent log
            try {
              fetch(LOG_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  sessionId: 'debug-session',
                  runId: 'info-card-debug',
                  hypothesisId: 'H-info-fields',
                  location: 'assetStore:getAssetDetail',
                  message: 'File details API error',
                  data: {
                    documentId: id,
                    error: fileError.message,
                    status: fileError.response?.status
                  },
                  timestamp: Date.now()
                })
              }).catch(() => {})
            } catch (e) {
              // ignore logging errors
            }
            // #endregion agent log
          }
        }

        // Fetch metadata separately (optimized endpoint may omit it)
        const meta = await fetchDocumentMetadata(id)
        if (meta) {
          const metaMap: Record<string, string> = {}
          meta.forEach((m: any) => {
            const key = m.metadata_type?.name || m.metadata_type?.label || `meta_${m.id}`
            if (key) {
              metaMap[key] = m.value
            }
          })
          if (metaMap.description && !asset.description) {
            asset.description = metaMap.description
          }
          if (metaMap.tags) {
            const metaTags = metaMap.tags.split(',').map((t: string) => t.trim()).filter(Boolean)
            asset.tags = Array.from(new Set([...(asset.tags || []), ...metaTags]))
          }
          asset.metadata = { ...(asset.metadata || {}), ...metaMap }
        }
        // Fetch tags separately (Mayan tags API)
        const tagList = await fetchDocumentTags(id)
        if (tagList && Array.isArray(tagList)) {
          const tagNames = tagList
            .map((t: any) => t.label || t.name || t.tag || '')
            .filter((t: string) => !!t)
          asset.tags = Array.from(new Set([...(asset.tags || []), ...tagNames]))
        }
        // #region agent log
        try {
          fetch(LOG_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              sessionId: 'debug-session',
              runId: 'upload-meta',
              hypothesisId: 'H-detail',
              location: 'assetStore:getAssetDetail',
              message: 'Detail snapshot',
              data: {
                id,
                description: asset.description || '',
                tags: asset.tags ? asset.tags.length : 0,
                metadataKeys: asset.metadata ? Object.keys(asset.metadata).length : 0,
                metaFetched: meta ? meta.length : 0,
                tagsFetched: tagList ? tagList.length : 0
              },
              timestamp: Date.now()
            })
          }).catch(() => {})
        } catch (e) {
          // ignore logging errors
        }
        // #endregion agent log

        currentAsset.value = asset
        return asset
        
      } catch (err: any) {
        await handleApiError(err)
        currentAsset.value = null
        return null
      } finally {
        isLoading.value = false
      }
    }

    async function fetchDocumentMetadata(id: number): Promise<any[] | null> {
      try {
        const resp = await axios.get(`/api/v4/documents/${id}/metadata/`, {
          headers: getAuthHeaders()
        })
        const data = Array.isArray(resp.data) ? resp.data : resp.data?.results || null
        // #region agent log
        try {
          fetch(LOG_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              sessionId: 'debug-session',
              runId: 'upload-meta',
              hypothesisId: 'H-meta-fetch',
              location: 'assetStore:fetchDocumentMetadata',
              message: 'Metadata fetched',
              data: { id, count: data ? data.length : 0 },
              timestamp: Date.now()
            })
          }).catch(() => {})
        } catch (e) {
          // ignore logging errors
        }
        // #endregion agent log
        return data
      } catch (err: any) {
        if (err.response?.status === 404) {
          return null
        }
        console.error('[AssetStore] Error fetching document metadata:', err)
        return null
      }
    }

    async function fetchDocumentTags(id: number): Promise<any[] | null> {
      try {
        const resp = await axios.get(`/api/v4/documents/${id}/tags/`, {
          headers: getAuthHeaders()
        })
        const data = Array.isArray(resp.data) ? resp.data : resp.data?.results || null
        // #region agent log
        try {
          fetch(LOG_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              sessionId: 'debug-session',
              runId: 'upload-meta',
              hypothesisId: 'H-tags-fetch',
              location: 'assetStore:fetchDocumentTags',
              message: 'Tags fetched',
              data: { id, count: data ? data.length : 0 },
              timestamp: Date.now()
            })
          }).catch(() => {})
        } catch (e) {
          // ignore logging errors
        }
        // #endregion agent log
        return data
      } catch (err: any) {
        if (err.response?.status === 404) {
          return null
        }
        console.error('[AssetStore] Error fetching document tags:', err)
        return null
      }
    }

    /**
     * Get asset processing status (AI analysis progress)
     * Uses /api/v4/documents/{id}/processing_status/
     */
    async function getProcessingStatus(id: number): Promise<{
      status: string
      progress: number
      current_step: string | null
      ai_tags_ready: boolean
      ai_description_ready: boolean
      ai_colors_ready: boolean
    } | null> {
      try {
        const response = await axios.get(
          `/api/v4/documents/${id}/processing_status/`,
          { headers: getAuthHeaders() }
        )
        return response.data
      } catch (err: any) {
        if (err.response?.status === 404) {
          // Processing status endpoint not available
          return null
        }
        console.error('[AssetStore] Error fetching processing status:', err)
        return null
      }
    }
    
    // ========================================================================
    // ACTIONS - CRUD
    // ========================================================================
    
    /**
     * Delete an asset
     * Uses DELETE /api/v4/documents/{id}/
     */
    async function deleteAsset(id: number): Promise<boolean> {
      try {
        console.log('[AssetStore] Deleting document:', id)
        await deleteDocumentApi(id)
        
        // Remove from local state
        assets.value = assets.value.filter(a => a.id !== id)
        totalCount.value = Math.max(0, totalCount.value - 1)
        selectedAssets.value.delete(id)
        
        if (currentAsset.value?.id === id) {
          currentAsset.value = null
        }
        
        console.log('[AssetStore] Document deleted successfully')
        return true
        
      } catch (err: any) {
        await handleApiError(err)
        return false
      }
    }
    
    /**
     * Update an asset's metadata
     * Uses PATCH /api/v4/documents/{id}/
     */
    async function updateAssetData(id: number, data: Partial<Asset>): Promise<Asset | null> {
      try {
        console.log('[AssetStore] Updating document metadata:', id, data)
        
        // Map Asset fields to Mayan document fields
        const mayanData: Record<string, any> = {}
        if (data.label !== undefined) mayanData.label = data.label
        
        const response = await updateDocumentMetadata(id, mayanData)
        const updated = adaptBackendAsset(response as BackendOptimizedDocument)
        
        // Update local state
        const index = assets.value.findIndex(a => a.id === id)
        if (index !== -1) {
          assets.value[index] = updated
        }
        if (currentAsset.value?.id === id) {
          currentAsset.value = updated
        }
        
        console.log('[AssetStore] Document updated successfully')
        return updated
        
      } catch (err: any) {
        await handleApiError(err)
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
    
    function selectAsset(asset: Asset, multiSelect = false): void {
      if (multiSelect) {
        if (selectedAssets.value.has(asset.id)) {
          selectedAssets.value.delete(asset.id)
        } else {
          selectedAssets.value.add(asset.id)
        }
      } else {
        selectedAssets.value.clear()
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

    /**
     * Set folder (cabinet) filter for assets
     */
    function setFolderFilter(
      folderId: string | null,
      folderType: FolderSource | null = null
    ): void {
      folderFilterId.value = folderId
      folderFilterType.value = folderType
      currentPage.value = 1

      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: `log_setFolderFilter_${Date.now()}`,
          timestamp: Date.now(),
          sessionId: 'debug-session',
          runId: 'post-fix',
          hypothesisId: 'H4',
          location: 'assetStore:setFolderFilter',
          message: 'Set folder filter',
          data: { folderId, folderType }
        })
      }).catch(() => {})
      // #endregion agent log
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
    
    /**
     * Upload a file using the real Mayan EDMS API
     * Two-step process: Create document → Upload file
     */
    async function uploadFile(
      file: File,
      options?: {
        onProgress?: (progress: UploadProgress) => void
        signal?: AbortSignal
        documentTypeId?: number
        description?: string
        cabinetId?: number
      }
    ): Promise<{ documentId: number; fileId: number }> {
      const token = getToken()
      
      if (!token) {
        throw new Error('Not authenticated. Please login first.')
      }
      
      console.log('[AssetStore] Uploading file:', file.name)
      
      const result = await uploadService.uploadAsset(file, {
        onProgress: options?.onProgress,
        signal: options?.signal,
        documentTypeId: options?.documentTypeId,
        description: options?.description,
        cabinetId: options?.cabinetId
      })
      
      console.log('[AssetStore] Upload complete:', result)
      
      // Refresh assets to include the new upload
      await fetchAssets()
      
      return {
        documentId: result.documentId,
        fileId: result.fileId
      }
    }
    
    // ========================================================================
    // RETURN
    // ========================================================================

    return {
      // Configuration
      debugMode,
      lastRawResponse,
      useOptimizedApi,
      
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
      folderFilterId,
      folderFilterType,

      // Getters
      hasNextPage,
      hasPreviousPage,
      selectedCount,
      hasSelection,
      allSelected,
      currentPageAssets,
      hasActiveFilters,
      selectedAssetsList,
      activeFolderId,

      // Actions - Fetch
      fetchAssets,
      loadMore,
      getAssetDetail,
      getProcessingStatus,
      
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
      setFolderFilter,
      refresh,
      
      // Actions - Upload
      uploadFile,
    }
  },
  {
    persist: {
      paths: ['pageSize', 'sort']
    }
  }
)
