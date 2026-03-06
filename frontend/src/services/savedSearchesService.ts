/**
 * Saved Searches Service — Sprint 1 Discovery UX
 *
 * CRUD and run for saved searches (tenant-scoped).
 * API: /api/v4/headless/saved-searches/
 */

import { apiService } from './apiService'
import {
  adaptBackendAsset,
  type BackendOptimizedDocument
} from './adapters/mayanAdapter'
import type { Asset } from '@/types/api'

const SAVED_SEARCHES_API = '/api/v4/headless/saved-searches/'

export interface SavedSearch {
  id: number
  name: string
  query: string
  filters: Record<string, unknown>
  created_at: string
  notification_enabled?: boolean
  last_notified_at?: string | null
}

export interface SavedSearchCreateInput {
  name: string
  query?: string
  filters?: Record<string, unknown>
}

export interface SavedSearchRunResponse {
  results: Asset[]
  count: number
}

/**
 * List saved searches for the current user and organization.
 * Requires X-Organization-Id (set by apiService).
 */
export async function listSavedSearches(): Promise<SavedSearch[]> {
  const data = await apiService.get<SavedSearch[]>(SAVED_SEARCHES_API)
  return Array.isArray(data) ? data : []
}

/**
 * Create a saved search.
 */
export async function createSavedSearch(
  input: SavedSearchCreateInput
): Promise<SavedSearch> {
  return apiService.post<SavedSearch>(SAVED_SEARCHES_API, {
    name: input.name.trim(),
    query: input.query ?? '',
    filters: input.filters ?? {}
  })
}

/**
 * Update a saved search (e.g. rename).
 */
export async function updateSavedSearch(
  id: number,
  patch: { name?: string }
): Promise<SavedSearch> {
  return apiService.patch<SavedSearch>(
    `${SAVED_SEARCHES_API}${id}/`,
    patch
  )
}

/**
 * Delete a saved search.
 */
export async function deleteSavedSearch(id: number): Promise<void> {
  await apiService.delete(`${SAVED_SEARCHES_API}${id}/`)
}

/**
 * Run a saved search and return document list (same format as optimized list).
 * Optional page_size (max 100).
 */
export async function runSavedSearch(
  id: number,
  pageSize: number = 50
): Promise<SavedSearchRunResponse> {
  const size = Math.min(Math.max(1, pageSize), 100)
  const data = await apiService.get<{
    results: BackendOptimizedDocument[]
    count: number
  }>(`${SAVED_SEARCHES_API}${id}/run/`, {
    params: { page_size: size }
  })
  const results = (data.results || []).map((doc) => adaptBackendAsset(doc))
  return {
    results,
    count: data.count ?? results.length
  }
}
