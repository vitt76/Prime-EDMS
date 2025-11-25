import { apiService } from './apiService'
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

class AssetService {
  /**
   * Get paginated list of assets
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
      queryParams.ordering = params.sort
    }
    if (params?.type) {
      queryParams.type = params.type
    }
    if (params?.tags) {
      queryParams.tags = params.tags
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<PaginatedResponse<Asset>>(
      '/v4/dam/assets/',
      { params: queryParams },
      false // Don't cache asset lists
    )
  }

  /**
   * Get single asset by ID
   */
  async getAsset(id: number): Promise<AssetDetailResponse> {
    return apiService.get<AssetDetailResponse>(
      `/v4/dam/assets/${id}/`,
      undefined,
      true // Cache asset details for 5 minutes
    )
  }

  /**
   * Search assets with advanced query
   */
  async searchAssets(query: SearchQuery): Promise<SearchResponse> {
    return apiService.post<SearchResponse>('/v4/dam/assets/search/', query)
  }

  /**
   * Perform bulk operations on assets
   */
  async bulkOperation(
    operation: BulkOperationRequest
  ): Promise<BulkOperationResponse> {
    return apiService.post<BulkOperationResponse>(
      '/v4/dam/assets/bulk/',
      operation
    )
  }

  /**
   * Update asset metadata
   */
  async updateAsset(
    id: number,
    data: Partial<Asset>
  ): Promise<AssetDetailResponse> {
    return apiService.put<AssetDetailResponse>(`/v4/dam/assets/${id}/`, data)
  }

  /**
   * Delete asset
   */
  async deleteAsset(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/dam/assets/${id}/`)
  }

  /**
   * Upload new asset
   */
  async uploadAsset(file: File, metadata?: Record<string, unknown>): Promise<Asset> {
    const formData = new FormData()
    formData.append('file', file)
    
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata))
    }

    return apiService.post<Asset>('/v4/dam/assets/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

export const assetService = new AssetService()
