/**
 * Recently Viewed Service — Sprint 1 Discovery UX
 *
 * Fetches documents recently viewed or downloaded by the current user
 * in the current organization (AssetEvent-based).
 * API: GET /api/v4/headless/documents/recently-viewed/
 */

import { apiService } from './apiService'
import {
  adaptBackendAsset,
  type BackendOptimizedDocument
} from './adapters/mayanAdapter'
import type { Asset } from '@/types/api'

const RECENTLY_VIEWED_API = '/api/v4/headless/documents/recently-viewed/'

export interface RecentlyViewedParams {
  /** Max items to return (default 20, max 50 on backend) */
  limit?: number
  /** Look back period in days (default 30, max 365 on backend) */
  days?: number
}

export interface RecentlyViewedResponse {
  results: Asset[]
  count: number
}

/**
 * Get recently viewed documents for the current user in the current organization.
 * Requires X-Organization-Id header (set by apiService from localStorage).
 */
export async function getRecentlyViewed(
  params: RecentlyViewedParams = {}
): Promise<RecentlyViewedResponse> {
  const limit = Math.min(Math.max(1, params.limit ?? 20), 50)
  const days = Math.min(Math.max(1, params.days ?? 30), 365)

  const response = await apiService.get<{
    results: BackendOptimizedDocument[]
    count: number
  }>(RECENTLY_VIEWED_API, {
    params: { limit, days }
  })

  const results = (response.results || []).map((doc) => adaptBackendAsset(doc))
  return {
    results,
    count: response.count ?? results.length
  }
}
