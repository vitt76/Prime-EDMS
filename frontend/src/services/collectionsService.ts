/**
 * Collections Service
 *
 * Backed by Mayan Cabinets API (/api/v4/cabinets/). Maps Cabinet DTOs to
 * Collection shape for the Collections UI (Sprint 4.1).
 */

import { apiService } from './apiService'
import { withRetry } from '@/utils/retry'
import type { Asset } from '@/types/api'
import type { Collection } from '@/types/collections'

const CABINET_BASE = '/api/v4/cabinets'

/** Cabinet API response shape (tree node). */
interface CabinetDTO {
  id: number
  label: string
  parent_id: number | null
  children?: CabinetDTO[]
  document_count?: number
  can_add_children?: boolean
  can_delete?: boolean
  can_edit?: boolean
  created_at?: string | null
  updated_at?: string | null
}

interface CabinetDocumentDTO {
  id: number
  label: string
  description?: string
  datetime_created?: string
  file_latest?: {
    id?: number
    filename?: string
    size?: number
    mimetype?: string
    download_url?: string
    pages_first?: {
      image_url?: string
    } | null
  } | null
}

function cabinetToCollection(c: CabinetDTO): Collection {
  return {
    id: c.id,
    name: c.label,
    parent_id: c.parent_id ?? null,
    visibility: 'private',
    asset_count: c.document_count ?? 0,
    created_at: c.created_at ?? '',
    updated_at: c.updated_at ?? ''
  }
}

function flattenTree(nodes: CabinetDTO[]): CabinetDTO[] {
  return nodes.flatMap((n) => [n, ...flattenTree(n.children ?? [])])
}

function cabinetDocumentToAsset(document: CabinetDocumentDTO): Asset {
  const latestFile = document.file_latest

  return {
    id: document.id,
    label: document.label,
    description: document.description ?? '',
    filename: latestFile?.filename ?? document.label,
    size: latestFile?.size ?? 0,
    mime_type: latestFile?.mimetype ?? 'application/octet-stream',
    date_added: document.datetime_created ?? '',
    thumbnail_url: latestFile?.pages_first?.image_url ?? undefined,
    preview_url: latestFile?.download_url ?? undefined,
    download_url: latestFile?.download_url ?? undefined,
    file_latest_id: latestFile?.id ?? undefined,
    metadata: {}
  }
}

export interface CreateCollectionRequest {
  name: string
  description?: string
  type?: 'folder' | 'collection'
  parent_id?: number | null
}

export interface UpdateCollectionRequest {
  name?: string
  description?: string
  parent_id?: number | null
  visibility?: 'private' | 'shared' | 'public'
  is_favorite?: boolean
}

export interface CollectionsQuery {
  parent_id?: number | null
  type?: string
  search?: string
  include_tree?: boolean
  include_permissions?: boolean
  limit?: number
  offset?: number
}

export interface CollectionAssetsQuery {
  collection_id: string
  limit?: number
  offset?: number
  sort_by?: string
  sort_order?: string
}

export interface PaginatedCollections {
  results: Collection[]
  count: number
}

export interface SpecialCollectionsResponse {
  favorites: Collection[]
  recent: Collection[]
  shared_with_me: Collection[]
  my_uploads: Collection[]
  public_collections: Collection[]
}

export interface BulkCollectionOperation {
  ids: number[]
  action: 'delete' | 'move' | 'share' | 'export'
  data?: { new_parent_id?: number | null }
}

export interface BulkOperationResponse {
  success: boolean
  updated: number
  failed: number
  errors?: Array<{ id: number; error: string }>
}

/** Cabinet share link (from GET cabinets/:id/shares/). */
export interface CabinetShareDTO {
  id?: number
  uuid: string
  share_url: string
  expires_at?: string | null
  created_at?: string
}

/** Public share response (GET public/shares/:uuid/). */
export interface PublicShareResponse {
  label: string
  uuid: string
  documents: Array<{ id: number; label: string; thumbnail_url: string | null }>
}

class CollectionsService {
  async getCollections(query?: CollectionsQuery): Promise<PaginatedCollections> {
    const operation = () =>
      apiService.get<CabinetDTO[]>(`${CABINET_BASE}/tree/`)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    const tree = result.data ?? []
    const flat = flattenTree(tree)
    const results = flat.map(cabinetToCollection)
    return { results, count: results.length }
  }

  async getCollection(id: number | string, _includeTree = false): Promise<Collection> {
    const idNum = typeof id === 'string' ? parseInt(id, 10) : id
    const operation = () => apiService.get<CabinetDTO>(`${CABINET_BASE}/${idNum}/`)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    return cabinetToCollection(result.data!)
  }

  async createCollection(data: CreateCollectionRequest): Promise<Collection> {
    const payload = {
      label: data.name,
      parent: data.parent_id ?? null
    }
    const operation = () => apiService.post<CabinetDTO>(`${CABINET_BASE}/`, payload)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    return cabinetToCollection(result.data!)
  }

  async updateCollection(
    id: number | string,
    data: UpdateCollectionRequest
  ): Promise<Collection> {
    const idNum = typeof id === 'string' ? parseInt(id, 10) : id
    const payload: Record<string, unknown> = {}
    if (data.name !== undefined) payload.label = data.name
    if (data.parent_id !== undefined) payload.parent = data.parent_id
    const operation = () =>
      apiService.patch<CabinetDTO>(`${CABINET_BASE}/${idNum}/`, payload)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    return cabinetToCollection(result.data!)
  }

  async deleteCollection(id: number | string): Promise<void> {
    const idNum = typeof id === 'string' ? parseInt(id, 10) : id
    const operation = () => apiService.delete(`${CABINET_BASE}/${idNum}/`)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
  }

  async moveCollection(
    id: number | string,
    body: { collection_id?: number; new_parent_id?: number | null }
  ): Promise<Collection> {
    const idNum = typeof id === 'string' ? parseInt(id, 10) : id
    const newParentId = body.new_parent_id ?? null
    const operation = () =>
      apiService.patch<CabinetDTO>(`${CABINET_BASE}/${idNum}/`, {
        parent: newParentId
      })
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    return cabinetToCollection(result.data!)
  }

  async getCollectionAssets(query: CollectionAssetsQuery): Promise<{
    results: Asset[]
    count: number
  }> {
    const cid = parseInt(query.collection_id, 10)
    const operation = () =>
      apiService.get<{ results: CabinetDocumentDTO[]; count?: number }>(
        `${CABINET_BASE}/${cid}/documents/`,
        { params: { page_size: query.limit ?? 50, page: query.offset ? Math.floor(query.offset / (query.limit ?? 50)) + 1 : 1 } }
      )
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    const data = result.data!
    const rawResults = Array.isArray(data) ? data : (data.results ?? [])
    const results = rawResults.map(cabinetDocumentToAsset)
    const count = (data as { count?: number }).count ?? results.length
    return { results, count }
  }

  async addAssetsToCollection(
    collectionId: string,
    assetIds: string[],
    _position?: number
  ): Promise<void> {
    const cid = parseInt(collectionId, 10)
    const docIds = assetIds.map((a) => parseInt(a, 10)).filter((n) => !Number.isNaN(n))
    const operation = () =>
      apiService.post(`${CABINET_BASE}/${cid}/documents/bulk-add/`, {
        documents: docIds
      })
    const result = await withRetry(operation)
    if (!result.success) throw result.error
  }

  async removeAssetsFromCollection(
    collectionId: string,
    assetIds: string[]
  ): Promise<void> {
    const cid = parseInt(collectionId, 10)
    const docIds = assetIds.map((a) => parseInt(a, 10)).filter((n) => !Number.isNaN(n))
    const operation = () =>
      apiService.post(`${CABINET_BASE}/${cid}/documents/bulk-remove/`, {
        documents: docIds
      })
    const result = await withRetry(operation)
    if (!result.success) throw result.error
  }

  async getCollectionTree(_rootParentId?: string): Promise<Collection[]> {
    const operation = () => apiService.get<CabinetDTO[]>(`${CABINET_BASE}/tree/`)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    const tree = result.data ?? []
    return flattenTree(tree).map(cabinetToCollection)
  }

  async getSpecialCollections(): Promise<SpecialCollectionsResponse> {
    let sharedWithMe: Collection[] = []
    try {
      const shared = await apiService.get<CabinetDTO[]>(
        '/api/v4/headless/cabinets/shared-with-me/'
      )
      sharedWithMe = Array.isArray(shared)
        ? shared.map((c) => cabinetToCollection(c))
        : []
    } catch {
      sharedWithMe = []
    }
    return {
      favorites: [],
      recent: [],
      shared_with_me: sharedWithMe,
      my_uploads: [],
      public_collections: []
    }
  }

  async toggleFavorite(id: number): Promise<Collection> {
    const c = await this.getCollection(id)
    return { ...c, is_favorite: !c.is_favorite }
  }

  async bulkOperation(op: BulkCollectionOperation): Promise<BulkOperationResponse> {
    let updated = 0
    const errors: Array<{ id: number; error: string }> = []
    if (op.action === 'delete') {
      for (const id of op.ids) {
        try {
          await this.deleteCollection(id)
          updated++
        } catch (e: unknown) {
          errors.push({
            id,
            error: e instanceof Error ? e.message : String(e)
          })
        }
      }
    } else if (op.action === 'move' && op.data?.new_parent_id !== undefined) {
      const newParentId = op.data.new_parent_id
      for (const id of op.ids) {
        try {
          await this.moveCollection(id, { new_parent_id: newParentId })
          updated++
        } catch (e: unknown) {
          errors.push({
            id,
            error: e instanceof Error ? e.message : String(e)
          })
        }
      }
    } else {
      return { success: false, updated: 0, failed: op.ids.length, errors: [] }
    }
    return {
      success: errors.length === 0,
      updated,
      failed: errors.length,
      errors: errors.length ? errors : undefined
    }
  }

  async reorderCollectionAssets(
    _collectionId: string,
    _assetIds: string[]
  ): Promise<void> {
    return
  }

  async searchCollections(
    _query: string,
    _options?: { type?: string; parent_id?: string; limit?: number }
  ): Promise<Collection[]> {
    const { results } = await this.getCollections({})
    return results
  }

  async getCollectionStats(_id: string): Promise<{
    total_assets: number
    total_size: number
    asset_types: Record<string, number>
    recent_activity: unknown[]
    permissions: unknown[]
  }> {
    return {
      total_assets: 0,
      total_size: 0,
      asset_types: {},
      recent_activity: [],
      permissions: []
    }
  }

  async exportCollection(
    _id: string,
    _format: 'zip' | 'csv' | 'json' = 'zip'
  ): Promise<string> {
    throw new Error('Export not implemented')
  }

  /** Create a public share link for a collection (cabinet). */
  async shareCollection(
    id: string,
    shareOptions: { expires_at?: string | null; password?: string } = {}
  ): Promise<{ share_url: string; share_id: string; expires_at?: string }> {
    const cid = parseInt(id, 10)
    const payload: Record<string, unknown> = {}
    if (shareOptions.expires_at != null) payload.expires_at = shareOptions.expires_at
    if (shareOptions.password != null) payload.password = shareOptions.password
    const operation = () =>
      apiService.post<{ uuid: string; share_url: string; expires_at?: string }>(
        `${CABINET_BASE}/${cid}/shares/`,
        payload
      )
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    const data = result.data!
    return {
      share_url: data.share_url ?? '',
      share_id: data.uuid ?? '',
      expires_at: data.expires_at
    }
  }

  /** List active share links for a collection. */
  async getCollectionShares(id: string): Promise<CabinetShareDTO[]> {
    const cid = parseInt(id, 10)
    const operation = () =>
      apiService.get<CabinetShareDTO[] | { results: CabinetShareDTO[] }>(
        `${CABINET_BASE}/${cid}/shares/`
      )
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    const data = result.data
    if (Array.isArray(data)) return data
    if (data && typeof data === 'object' && 'results' in data) {
      return Array.isArray((data as { results: CabinetShareDTO[] }).results)
        ? (data as { results: CabinetShareDTO[] }).results
        : []
    }
    return []
  }

  /** Revoke a share link. */
  async revokeCollectionShare(collectionId: string, shareId: string): Promise<void> {
    const cid = parseInt(collectionId, 10)
    const operation = () =>
      apiService.delete(`${CABINET_BASE}/${cid}/shares/${encodeURIComponent(shareId)}/`)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
  }

  /** Public (unauthenticated) fetch of a shared collection. */
  async getPublicShare(
    uuid: string,
    password?: string
  ): Promise<PublicShareResponse> {
    const params = password != null && password !== '' ? { password } : {}
    const operation = () =>
      apiService.get<PublicShareResponse>(
        `/api/v4/public/shares/${encodeURIComponent(uuid)}/`,
        { params }
      )
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    return result.data!
  }

  async bulkDelete(collectionIds: string[]): Promise<void> {
    await this.bulkOperation({
      ids: collectionIds.map((s) => parseInt(s, 10)).filter((n) => !Number.isNaN(n)),
      action: 'delete'
    })
  }

  async bulkMove(
    collectionIds: string[],
    newParentId: number | null
  ): Promise<void> {
    await this.bulkOperation({
      ids: collectionIds.map((s) => parseInt(s, 10)).filter((n) => !Number.isNaN(n)),
      action: 'move',
      data: { new_parent_id: newParentId }
    })
  }

  async duplicateCollection(
    _id: string,
    _newName?: string,
    _newParentId?: string
  ): Promise<Collection> {
    throw new Error('Duplicate not implemented')
  }
}

export const collectionsService = new CollectionsService()
