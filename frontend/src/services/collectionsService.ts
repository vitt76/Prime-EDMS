/**
 * Collections Service
 *
 * Handles collection/folder operations including CRUD, asset assignment,
 * tree structure management, and search functionality.
 */

import { apiService } from './apiService'
import { withRetry } from '@/utils/retry'

export interface Collection {
  id: string
  name: string
  description?: string
  type: 'folder' | 'collection' | 'smart_collection'
  parent_id?: string
  path: string[]
  created_at: string
  updated_at: string
  created_by: string
  permissions: {
    can_read: boolean
    can_write: boolean
    can_delete: boolean
    can_share: boolean
  }
  asset_count?: number
  children?: Collection[]
}

export interface CreateCollectionRequest {
  name: string
  description?: string
  type?: 'folder' | 'collection'
  parent_id?: string
}

export interface UpdateCollectionRequest {
  name?: string
  description?: string
  parent_id?: string
}

export interface CollectionsQuery {
  parent_id?: string
  type?: string
  search?: string
  include_tree?: boolean
  include_permissions?: boolean
  limit?: number
  offset?: number
}

export interface AddAssetsToCollectionRequest {
  collection_id: string
  asset_ids: string[]
  position?: number
}

export interface CollectionAssetsQuery {
  collection_id: string
  limit?: number
  offset?: number
  sort_by?: 'name' | 'created_at' | 'updated_at' | 'size'
  sort_order?: 'asc' | 'desc'
}

class CollectionsService {
  /**
   * Get collections with optional filtering and tree structure
   */
  async getCollections(query: CollectionsQuery = {}): Promise<Collection[]> {
    const operation = () => apiService.get<Collection[]>('/v4/collections/', {
      params: query as Record<string, any>
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get single collection by ID
   */
  async getCollection(id: string, includeTree: boolean = false): Promise<Collection> {
    const operation = () => apiService.get<Collection>(`/v4/collections/${id}/`, {
      params: includeTree ? { include_tree: true } : {}
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Create new collection/folder
   */
  async createCollection(data: CreateCollectionRequest): Promise<Collection> {
    const operation = () => apiService.post<Collection>('/v4/collections/', data)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Update existing collection
   */
  async updateCollection(id: string, data: UpdateCollectionRequest): Promise<Collection> {
    const operation = () => apiService.patch<Collection>(`/v4/collections/${id}/`, data)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Delete collection
   */
  async deleteCollection(id: string): Promise<void> {
    const operation = () => apiService.delete(`/v4/collections/${id}/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Move collection to new parent
   */
  async moveCollection(id: string, newParentId: string | null): Promise<Collection> {
    const operation = () => apiService.post<Collection>(`/v4/collections/${id}/move/`, {
      parent_id: newParentId
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get assets in a collection
   */
  async getCollectionAssets(query: CollectionAssetsQuery) {
    const { collection_id, ...params } = query
    const operation = () => apiService.get(`/v4/collections/${collection_id}/assets/`, { params })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Add assets to collection
   */
  async addAssetsToCollection(collectionId: string, assetIds: string[], position?: number): Promise<void> {
    const operation = () => apiService.post(`/v4/collections/${collectionId}/assets/`, {
      asset_ids: assetIds,
      position
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Remove assets from collection
   */
  async removeAssetsFromCollection(collectionId: string, assetIds: string[]): Promise<void> {
    const operation = () => apiService.delete(`/v4/collections/${collectionId}/assets/`, {
      data: { asset_ids: assetIds }
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Reorder assets in collection
   */
  async reorderCollectionAssets(collectionId: string, assetIds: string[]): Promise<void> {
    const operation = () => apiService.post(`/v4/collections/${collectionId}/assets/reorder/`, {
      asset_ids: assetIds
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Search collections
   */
  async searchCollections(query: string, options: {
    type?: string
    parent_id?: string
    limit?: number
  } = {}): Promise<Collection[]> {
    const operation = () => apiService.get<Collection[]>('/v4/collections/search/', {
      params: { q: query, ...options }
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get collection tree structure (nested)
   */
  async getCollectionTree(rootParentId?: string): Promise<Collection[]> {
    const operation = () => apiService.get<Collection[]>('/v4/collections/tree/', {
      params: rootParentId ? { parent_id: rootParentId } : {}
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Duplicate collection
   */
  async duplicateCollection(id: string, newName?: string, newParentId?: string): Promise<Collection> {
    const operation = () => apiService.post<Collection>(`/v4/collections/${id}/duplicate/`, {
      name: newName,
      parent_id: newParentId
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get collection statistics
   */
  async getCollectionStats(id: string): Promise<{
    total_assets: number
    total_size: number
    asset_types: Record<string, number>
    recent_activity: any[]
    permissions: any[]
  }> {
    const operation = () => apiService.get(`/v4/collections/${id}/stats/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Export collection
   */
  async exportCollection(id: string, format: 'zip' | 'csv' | 'json' = 'zip'): Promise<string> {
    const operation = () => apiService.post<{ download_url: string }>(`/v4/collections/${id}/export/`, {
      format
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!.download_url
  }

  /**
   * Share collection (create share link)
   */
  async shareCollection(id: string, shareOptions: {
    permissions: {
      view: boolean
      download: boolean
      edit: boolean
    }
    expiration?: Date
    password?: string
    recipients?: string[]
    isPublic?: boolean
  }): Promise<{
    share_url: string
    share_id: string
    expires_at?: string
  }> {
    const operation = () => apiService.post(`/v4/collections/${id}/share/`, shareOptions)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get collection share links
   */
  async getCollectionShares(id: string): Promise<Array<{
    id: string
    share_url: string
    created_at: string
    expires_at?: string
    permissions: any
    is_active: boolean
  }>> {
    const operation = () => apiService.get(`/v4/collections/${id}/shares/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Revoke collection share
   */
  async revokeCollectionShare(collectionId: string, shareId: string): Promise<void> {
    const operation = () => apiService.delete(`/v4/collections/${collectionId}/shares/${shareId}/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Bulk operations on collections
   */
  async bulkDelete(collectionIds: string[]): Promise<void> {
    const operation = () => apiService.post('/v4/collections/bulk/delete/', {
      collection_ids: collectionIds
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  async bulkMove(collectionIds: string[], newParentId: string | null): Promise<void> {
    const operation = () => apiService.post('/v4/collections/bulk/move/', {
      collection_ids: collectionIds,
      parent_id: newParentId
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }
}

export const collectionsService = new CollectionsService()