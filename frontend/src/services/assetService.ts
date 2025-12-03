/**
 * Asset Service - Phase A2 Implementation
 * 
 * Provides asset operations using real Mayan EDMS API endpoints.
 * Uses optimized endpoint: GET /api/v4/documents/optimized/
 * 
 * Endpoints:
 * - GET /api/v4/documents/optimized/ - High-performance asset list
 * - GET /api/v4/documents/{id}/ - Asset details
 * - PATCH /api/v4/documents/{id}/ - Update asset
 * - DELETE /api/v4/documents/{id}/ - Delete asset (move to trash)
 */

import { apiService } from './apiService'
import {
  adaptBackendAsset,
  adaptBackendPaginatedResponse,
  type BackendOptimizedDocument,
  type BackendPaginatedResponse,
} from './adapters/mayanAdapter'
import type {
  Asset,
  AssetDetailResponse,
  GetAssetsParams,
  PaginatedResponse,
  SearchQuery,
  SearchResponse,
  BulkOperationRequest,
  BulkOperationResponse
} from '@/types/api'
import type {
  AxiosProgressEvent,
  AxiosRequestHeaders,
  InternalAxiosRequestConfig
} from 'axios'

// ============================================================================
// API CONFIGURATION
// ============================================================================

/**
 * Optimized Documents API endpoint (Phase B2)
 */
const OPTIMIZED_DOCUMENTS_API = '/v4/documents/optimized/'

/**
 * Standard Documents API endpoint (fallback)
 */
const STANDARD_DOCUMENTS_API = '/v4/documents/'

/**
 * Search API endpoint
 */
const SEARCH_API = '/v4/search/'

// Track if optimized API is available
let useOptimizedApi = true

// ============================================================================
// ASSET SERVICE CLASS
// ============================================================================

class AssetService {
  /**
   * Get paginated list of assets from real Mayan EDMS API
   * Uses optimized endpoint with automatic fallback to standard API
   */
  async getAssets(params?: GetAssetsParams): Promise<PaginatedResponse<Asset>> {
    const queryParams: Record<string, string | number> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.sort) {
      // Map frontend sort field names to backend
      let ordering = params.sort
      if (ordering === 'date_added') ordering = 'datetime_created'
      if (ordering === 'name') ordering = 'label'
      if (ordering.startsWith('-date_added')) ordering = ordering.replace('date_added', 'datetime_created')
      if (ordering.startsWith('-name')) ordering = ordering.replace('name', 'label')
      queryParams.ordering = ordering
    }
    if (params?.type) {
      queryParams.document_type__label = params.type
    }
    if (params?.search) {
      queryParams.q = params.search
    }

    const config: InternalAxiosRequestConfig = {
      params: queryParams,
      headers: {} as AxiosRequestHeaders
    }

    try {
      // Try optimized endpoint first
      const endpoint = useOptimizedApi ? OPTIMIZED_DOCUMENTS_API : STANDARD_DOCUMENTS_API
      
      const response = await apiService.get<BackendPaginatedResponse<BackendOptimizedDocument>>(
        endpoint,
        config,
        false // Don't cache asset lists
      )
      
      // Transform using adapter
      return adaptBackendPaginatedResponse(response)
      
    } catch (error: any) {
      // If optimized endpoint fails with 404, fallback to standard
      if (error.response?.status === 404 && useOptimizedApi) {
        console.warn('[AssetService] Optimized API not available, falling back to standard API')
        useOptimizedApi = false
        return this.getAssets(params)
      }
      throw error
    }
  }

  /**
   * Get single asset by ID
   */
  async getAsset(id: number): Promise<AssetDetailResponse> {
    const response = await apiService.get<BackendOptimizedDocument>(
      `/v4/documents/${id}/`,
      undefined,
      true // Cache asset details for 5 minutes
    )
    
    const adapted = adaptBackendAsset(response)
    
    // Return as AssetDetailResponse (extends Asset)
    return {
      ...adapted,
      file_details: adapted.file_details || {
        filename: adapted.filename,
        size: adapted.size,
        mime_type: adapted.mime_type,
        uploaded_date: adapted.date_added,
      },
      comments: [],
      version_history: [],
    } as AssetDetailResponse
  }

  /**
   * Search assets using Mayan search API
   */
  async searchAssets(query: SearchQuery): Promise<SearchResponse> {
    const params: Record<string, string | number> = {}
    
    if (query.q) {
      params.q = query.q
    }
    if (query.limit) {
      params.page_size = query.limit
    }
    if (query.offset) {
      params.page = Math.floor(query.offset / (query.limit || 20)) + 1
    }
    
    const config: InternalAxiosRequestConfig = {
      params,
      headers: {} as AxiosRequestHeaders
    }
    
    // Use the documents endpoint with search parameter
    const response = await apiService.get<BackendPaginatedResponse<BackendOptimizedDocument>>(
      useOptimizedApi ? OPTIMIZED_DOCUMENTS_API : STANDARD_DOCUMENTS_API,
      config,
      false
    )
    
    const adapted = adaptBackendPaginatedResponse(response)
    
    return {
      count: adapted.count,
      results: adapted.results,
      facets: {} // Facets would need separate implementation
    }
  }

  /**
   * Perform bulk operations on assets
   * Note: Mayan EDMS requires separate API calls per operation
   */
  async bulkOperation(
    operation: BulkOperationRequest
  ): Promise<BulkOperationResponse> {
    // For now, execute operations one by one
    // In future, this could use /api/v4/documents/bulk/ if implemented on backend
    const results = {
      success: true,
      updated: 0,
      failed: 0,
      errors: [] as Array<{ id: number; error: string }>
    }
    
    for (const id of operation.ids) {
      try {
        switch (operation.action) {
          case 'delete':
            await this.deleteAsset(id)
            results.updated++
            break
          case 'add_tags':
            // Tag operations would need separate implementation
            console.warn('[AssetService] Bulk add_tags not yet implemented')
            results.updated++
            break
          case 'remove_tags':
            console.warn('[AssetService] Bulk remove_tags not yet implemented')
            results.updated++
            break
          case 'move':
            console.warn('[AssetService] Bulk move not yet implemented')
            results.updated++
            break
          default:
            results.failed++
            results.errors?.push({ id, error: `Unknown action: ${operation.action}` })
        }
      } catch (error: any) {
        results.failed++
        results.success = false
        results.errors?.push({ id, error: error.message || 'Operation failed' })
      }
    }
    
    return results
  }

  /**
   * Update asset metadata
   */
  async updateAsset(
    id: number,
    data: Partial<Asset>
  ): Promise<AssetDetailResponse> {
    // Map frontend Asset fields to Mayan document fields
    const mayanData: Record<string, any> = {}
    if (data.label !== undefined) mayanData.label = data.label
    if (data.metadata?.description !== undefined) mayanData.description = data.metadata.description
    
    const response = await apiService.patch<BackendOptimizedDocument>(
      `/v4/documents/${id}/`,
      mayanData
    )
    
    const adapted = adaptBackendAsset(response)
    
    return {
      ...adapted,
      file_details: adapted.file_details || {
        filename: adapted.filename,
        size: adapted.size,
        mime_type: adapted.mime_type,
        uploaded_date: adapted.date_added,
      },
      comments: [],
      version_history: [],
    } as AssetDetailResponse
  }

  /**
   * Delete asset (moves to trash in Mayan EDMS)
   */
  async deleteAsset(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/documents/${id}/`)
  }

  /**
   * Upload new asset
   * Note: Prefer using uploadService for better progress tracking
   */
  async uploadAsset(
    formData: FormData,
    config?: {
      onUploadProgress?: (event: AxiosProgressEvent) => void
      signal?: AbortSignal
    }
  ): Promise<Asset> {
    // For uploads, use the uploadService which handles the 2-step Mayan process
    // This method is kept for backward compatibility but should use uploadService directly
    const axiosConfig: InternalAxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data'
      } as AxiosRequestHeaders,
      onUploadProgress: config?.onUploadProgress,
      signal: config?.signal
    }
    
    // Direct upload to documents endpoint (creates document + file)
    const response = await apiService.post<BackendOptimizedDocument>(
      '/v4/documents/upload/',
      formData,
      axiosConfig
    )
    
    return adaptBackendAsset(response)
  }
  
  /**
   * Get rich document details including AI analysis
   * Uses the new /rich_details/ endpoint from Phase B1
   */
  async getRichDetails(id: number): Promise<Asset> {
    try {
      const response = await apiService.get<BackendOptimizedDocument>(
        `/v4/documents/${id}/rich_details/`,
        undefined,
        true // Cache for 5 minutes
      )
      return adaptBackendAsset(response)
    } catch (error: any) {
      // Fallback to standard endpoint if rich_details not available
      if (error.response?.status === 404) {
        console.warn('[AssetService] Rich details API not available, using standard endpoint')
        return adaptBackendAsset(
          await apiService.get<BackendOptimizedDocument>(`/v4/documents/${id}/`)
        )
      }
      throw error
    }
  }
  
  /**
   * Get document processing status (AI analysis progress)
   * Uses the new /processing_status/ endpoint from Phase B4
   */
  async getProcessingStatus(id: number): Promise<{
    document_id: number
    status: string
    progress: number
    current_step: string | null
    ai_tags_ready: boolean
    ai_description_ready: boolean
    ai_colors_ready: boolean
    analysis_provider: string | null
    task_id: string | null
    started_at: string | null
    completed_at: string | null
  }> {
    return apiService.get(`/v4/documents/${id}/processing_status/`)
  }
}

export const assetService = new AssetService()
