/**
 * Build backend-compatible filters object from DAM search state (Sprint 1 Discovery UX).
 * Used when saving a search so run/ endpoint applies the same filters.
 */

import type { DamFiltersState } from '@/composables/useDamSearchFilters'
import type { OrientationFilter } from '@/types/api'

export function buildSavedSearchFilters(filters: DamFiltersState): Record<string, unknown> {
  const out: Record<string, unknown> = {}
  const categories = new Set(['image', 'video', 'audio', 'document'])

  if (filters.type?.length) {
    const hasCategory = filters.type.some((t) => categories.has(String(t)))
    if (hasCategory) {
      const list: string[] = []
      filters.type.forEach((t) => {
        const v = String(t)
        if (v === 'image') list.push('image/')
        else if (v === 'video') list.push('video/')
        else if (v === 'audio') list.push('audio/')
        else if (v === 'document') list.push('application/')
      })
      if (list.length) out['file_latest__mimetype__startswith'] = list
    } else {
      out['document_type__label'] = filters.type
    }
  }
  if (filters.tags?.length) {
    out['tags__label__in'] = filters.tags.join(',')
  }
  if (filters.status?.length) {
    out['status__in'] = filters.status.join(',')
  }
  if (filters.dateFrom) out['datetime_created__gte'] = filters.dateFrom
  if (filters.dateTo) out['datetime_created__lte'] = filters.dateTo
  if (typeof filters.sizeMin === 'number') out['file_latest__size__gte'] = filters.sizeMin
  if (typeof filters.sizeMax === 'number') out['file_latest__size__lte'] = filters.sizeMax
  if (filters.orientation) out['orientation'] = filters.orientation
  if (filters.favoritesOnly) out['favorites_only'] = 'true'
  if (typeof filters.owner === 'number') out['files__user_id'] = filters.owner
  return out
}

/**
 * Parse backend filters (from SavedSearch.filters) back into DamFiltersState shape.
 * Used when applying a saved search to the gallery (Run).
 */
export function parseSavedSearchFilters(
  backend: Record<string, unknown> | null | undefined
): Partial<DamFiltersState> {
  if (!backend || typeof backend !== 'object') return {}
  const f: Partial<DamFiltersState> = {}
  if (typeof backend.orientation === 'string' && ['portrait', 'landscape', 'square'].includes(backend.orientation)) {
    f.orientation = backend.orientation as OrientationFilter
  }
  if (typeof backend['tags__label__in'] === 'string') {
    f.tags = backend['tags__label__in'].split(',').map((s) => s.trim()).filter(Boolean)
  }
  if (typeof backend['status__in'] === 'string') {
    f.status = backend['status__in'].split(',').map((s) => s.trim()).filter(Boolean)
  }
  if (Array.isArray(backend.document_type__label)) {
    f.type = backend.document_type__label.map(String)
  }
  if (typeof backend['datetime_created__gte'] === 'string') f.dateFrom = backend['datetime_created__gte'] as string
  if (typeof backend['datetime_created__lte'] === 'string') f.dateTo = backend['datetime_created__lte'] as string
  if (typeof backend['file_latest__size__gte'] === 'number') f.sizeMin = backend['file_latest__size__gte'] as number
  if (typeof backend['file_latest__size__lte'] === 'number') f.sizeMax = backend['file_latest__size__lte'] as number
  if (typeof backend['files__user_id'] === 'number') f.owner = backend['files__user_id'] as number
  if (typeof backend['file_latest__mimetype__startswith'] === 'object' && Array.isArray(backend['file_latest__mimetype__startswith'])) {
    const arr = backend['file_latest__mimetype__startswith'] as string[]
    f.type = arr.map((m) => {
      if (m.startsWith('image/')) return 'image'
      if (m.startsWith('video/')) return 'video'
      if (m.startsWith('audio/')) return 'audio'
      if (m.startsWith('application/')) return 'document'
      return m
    })
  }
  if (typeof backend['favorites_only'] === 'string') {
    f.favoritesOnly = ['true', '1'].includes(backend['favorites_only'])
  } else if (typeof backend['favorites_only'] === 'boolean') {
    f.favoritesOnly = backend['favorites_only']
  }
  return f
}
