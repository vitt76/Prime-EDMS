import { apiService } from './apiService'
import type {
  Collection,
  CollectionWithAssets,
  CreateCollectionRequest,
  UpdateCollectionRequest,
  MoveCollectionRequest,
  BulkCollectionOperation,
  BulkOperationResponse,
  GetCollectionsParams,
  PaginatedCollections,
  SpecialCollectionsResponse
} from '@/types/collections'

// TODO: Confirm COLLECTIONS_BASE_PATH with backend team before production deploy.
const COLLECTIONS_BASE_PATH = '/api/v4/dam/collections/'

/**
 * Collections Service
 * 
 * Service class for collections-related API operations.
 * Handles CRUD operations, tree management, and special collections.
 */
class CollectionsService {
  /**
   * Get paginated list of collections
   */
  async getCollections(
    params?: GetCollectionsParams
  ): Promise<PaginatedCollections> {
    const queryParams: Record<string, string | number | boolean | null> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.parent_id !== undefined) {
      queryParams.parent_id = params.parent_id
    }
    if (params?.search) {
      queryParams.search = params.search
    }
    if (params?.sort_by) {
      queryParams.sort_by = params.sort_by
    }
    if (params?.include_shared !== undefined) {
      queryParams.include_shared = params.include_shared
    }
    if (params?.visibility) {
      queryParams.visibility = params.visibility
    }

    return apiService.get<PaginatedCollections>(
        COLLECTIONS_BASE_PATH,
      { params: queryParams },
      true // Cache collections for 5 minutes
    )
  }

  /**
   * Get single collection by ID with assets
   */
  async getCollection(id: number): Promise<CollectionWithAssets> {
    return apiService.get<CollectionWithAssets>(
      `${COLLECTIONS_BASE_PATH}${id}/`,
      undefined,
      true
    )
  }

  /**
   * Create new collection
   */
  async createCollection(
    data: CreateCollectionRequest
  ): Promise<Collection> {
    // Validate name
    if (!data.name || data.name.trim().length === 0) {
      throw new Error('Collection name is required')
    }
    if (data.name.length > 255) {
      throw new Error('Collection name must be 255 characters or less')
    }

    return apiService.post<Collection>(COLLECTIONS_BASE_PATH, data)
  }

  /**
   * Update collection
   */
  async updateCollection(
    id: number,
    data: UpdateCollectionRequest
  ): Promise<Collection> {
    // Validate name if provided
    if (data.name !== undefined) {
      if (data.name.trim().length === 0) {
        throw new Error('Collection name cannot be empty')
      }
      if (data.name.length > 255) {
        throw new Error('Collection name must be 255 characters or less')
      }
    }

    return apiService.put<Collection>(`${COLLECTIONS_BASE_PATH}${id}/`, data)
  }

  /**
   * Delete collection
   */
  async deleteCollection(id: number): Promise<void> {
    return apiService.delete<void>(`${COLLECTIONS_BASE_PATH}${id}/`)
  }

  /**
   * Move collection to new parent
   */
  async moveCollection(
    id: number,
    data: MoveCollectionRequest
  ): Promise<Collection> {
    return apiService.post<Collection>(`${COLLECTIONS_BASE_PATH}${id}/move/`, {
      new_parent_id: data.new_parent_id
    })
  }

  /**
   * Bulk collection operation
   */
  async bulkOperation(
    operation: BulkCollectionOperation
  ): Promise<BulkOperationResponse> {
    // Validate max size
    if (operation.ids.length > 50) {
      throw new Error('Maximum 50 collections allowed per bulk operation')
    }

    return apiService.post<BulkOperationResponse>(
      `${COLLECTIONS_BASE_PATH}bulk/`,
      operation
    )
  }

  /**
   * Toggle favorite status for collection
   */
  async toggleFavorite(id: number): Promise<Collection> {
    return apiService.post<Collection>(
      `${COLLECTIONS_BASE_PATH}${id}/toggle-favorite/`
    )
  }

  /**
   * Get special collections (favorites, recent, shared, etc.)
   */
  async getSpecialCollections(): Promise<SpecialCollectionsResponse> {
    return apiService.get<SpecialCollectionsResponse>(
      `${COLLECTIONS_BASE_PATH}special/`,
      undefined,
      true // Cache special collections for 5 minutes
    )
  }
}

export const collectionsService = new CollectionsService()



