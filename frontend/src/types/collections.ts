/**
 * Collections Module TypeScript Types
 * 
 * Enterprise-grade type definitions for DAM Collections functionality.
 * Collections support hierarchical structure (nested folders) with drag-drop,
 * visibility controls, and special collections (favorites, recent, etc.).
 */

import type { PaginatedResponse } from './api'
import type { Asset } from './api'

/**
 * Collection Visibility Type
 * 
 * Controls who can access the collection:
 * - private: Only creator
 * - shared: Creator + explicitly shared users
 * - public: All authenticated users
 */
export type CollectionVisibility = 'private' | 'shared' | 'public'

/**
 * Special Collection Type
 * 
 * System-generated collections that cannot be manually created:
 * - favorites: User's favorite collections
 * - recent: Recently accessed collections
 * - my_uploads: Collections created by current user
 * - shared_with_me: Collections shared with current user
 * - public_collections: All public collections
 */
export type SpecialCollectionType =
  | 'favorites'
  | 'recent'
  | 'my_uploads'
  | 'shared_with_me'
  | 'public_collections'

/**
 * Collection Sort Options
 */
export type CollectionSortBy =
  | 'name'
  | 'created_at'
  | 'updated_at'
  | 'asset_count'
  | 'created_by'

/**
 * Base Collection Interface
 * 
 * Represents a collection in the DAM system with hierarchical support.
 * Collections can be nested (parent_id) and have visibility controls.
 */
export interface Collection {
  id: number
  name: string
  description?: string
  parent_id: number | null
  is_favorite?: boolean
  is_shared?: boolean
  visibility: CollectionVisibility
  asset_count?: number
  created_by?: number
  created_by_username?: string
  created_at?: string
  updated_at?: string
  cover_image_id?: number | null
  cover_image_url?: string | null
}

/**
 * Collection with Assets
 * 
 * Extended collection interface that includes the assets within the collection.
 * Used for detail views and collection browsing.
 */
export interface CollectionWithAssets extends Collection {
  assets: Asset[]
}

/**
 * Special Collection Interface
 * 
 * System-generated collections that have a specific type and cannot be
 * manually created or modified in the same way as regular collections.
 */
export interface SpecialCollection extends Collection {
  type: SpecialCollectionType
}

/**
 * Collection Tree Node
 * 
 * Hierarchical representation of collections for tree views.
 * Each node contains a collection and its children, with level tracking
 * for indentation and navigation.
 */
export interface CollectionTree {
  collection: Collection
  children: CollectionTree[]
  level: number
}

/**
 * Create Collection Request
 * 
 * Payload for creating a new collection via API.
 * All required fields must be provided.
 * 
 * @property name - Collection name (min 1, max 255 characters)
 * @property description - Optional description
 * @property parent_id - Parent collection ID (null for root)
 * @property visibility - Collection visibility level
 */
export interface CreateCollectionRequest {
  name: string // min 1, max 255
  description?: string
  parent_id?: number | null
  visibility?: CollectionVisibility
}

/**
 * Update Collection Request
 * 
 * Partial update payload for collection modification.
 * Only provided fields will be updated.
 */
export interface UpdateCollectionRequest {
  name?: string // min 1, max 255
  description?: string
  visibility?: CollectionVisibility
  is_favorite?: boolean
  cover_image_id?: number | null
}

/**
 * Move Collection Request
 * 
 * Payload for moving a collection to a new parent.
 * 
 * @property collection_id - ID of collection to move
 * @property new_parent_id - New parent ID (null for root)
 */
export interface MoveCollectionRequest {
  collection_id: number
  new_parent_id: number | null
}

/**
 * Bulk Collection Operation
 * 
 * Payload for bulk operations on multiple collections.
 * 
 * @property ids - Array of collection IDs (max 50)
 * @property action - Operation type
 * @property data - Additional data for the operation
 */
export interface BulkCollectionOperation {
  ids: number[] // max 50
  action: 'delete' | 'move' | 'share' | 'export'
  data?: {
    new_parent_id?: number | null // For 'move'
    visibility?: CollectionVisibility // For 'share'
    format?: 'zip' | 'tar' // For 'export'
  }
}

/**
 * Bulk Operation Response
 * 
 * Response from bulk collection operations.
 */
export interface BulkOperationResponse {
  success: boolean
  updated: number
  failed: number
  errors?: Array<{
    id: number
    error: string
  }>
}

/**
 * Get Collections Parameters
 * 
 * Query parameters for fetching collections.
 * All fields are optional for flexible filtering.
 */
export interface GetCollectionsParams {
  page?: number
  page_size?: number
  parent_id?: number | null
  search?: string
  sort_by?: CollectionSortBy
  include_shared?: boolean
  visibility?: CollectionVisibility
}

/**
 * Paginated Collections Response
 * 
 * Paginated response for collections list.
 */
export interface PaginatedCollections extends PaginatedResponse<Collection> {
  results: Collection[]
}

/**
 * Special Collections Response
 * 
 * Response containing all special collections.
 */
export interface SpecialCollectionsResponse {
  favorites: Collection[]
  recent: Collection[]
  my_uploads: Collection[]
  shared_with_me: Collection[]
  public_collections: Collection[]
}

/**
 * Collection Breadcrumb Item
 * 
 * Single item in the breadcrumb trail from root to current collection.
 */
export interface CollectionBreadcrumb {
  id: number
  name: string
  level: number
}

/**
 * Type guard to check if collection is special
 */
export function isSpecialCollection(
  collection: Collection
): collection is SpecialCollection {
  return 'type' in collection && typeof (collection as SpecialCollection).type === 'string'
}

/**
 * Type guard to check if collection has assets
 */
export function isCollectionWithAssets(
  collection: Collection
): collection is CollectionWithAssets {
  return 'assets' in collection && Array.isArray((collection as CollectionWithAssets).assets)
}



