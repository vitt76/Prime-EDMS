import { describe, it, expect } from 'vitest'
import {
  buildSavedSearchFilters,
  parseSavedSearchFilters
} from '@/utils/savedSearchFilters'
import type { DamFiltersState } from '@/composables/useDamSearchFilters'

describe('savedSearchFilters', () => {
  describe('buildSavedSearchFilters', () => {
    it('builds empty object for empty filters', () => {
      const f: DamFiltersState = {
        type: [],
        tags: [],
        status: [],
        dateFrom: undefined,
        dateTo: undefined,
        sizeMin: undefined,
        sizeMax: undefined,
        owner: undefined,
        orientation: undefined
      }
      expect(buildSavedSearchFilters(f)).toEqual({})
    })

    it('includes orientation', () => {
      const f: DamFiltersState = {
        type: [],
        tags: [],
        status: [],
        orientation: 'landscape'
      }
      expect(buildSavedSearchFilters(f)).toMatchObject({ orientation: 'landscape' })
    })

    it('includes tags and date range', () => {
      const f: DamFiltersState = {
        type: [],
        tags: ['a', 'b'],
        status: [],
        dateFrom: '2024-01-01',
        dateTo: '2024-12-31'
      }
      expect(buildSavedSearchFilters(f)).toMatchObject({
        'tags__label__in': 'a,b',
        'datetime_created__gte': '2024-01-01',
        'datetime_created__lte': '2024-12-31'
      })
    })
  })

  describe('parseSavedSearchFilters', () => {
    it('returns empty for null/undefined', () => {
      expect(parseSavedSearchFilters(null)).toEqual({})
      expect(parseSavedSearchFilters(undefined)).toEqual({})
    })

    it('parses orientation and tags', () => {
      const out = parseSavedSearchFilters({
        orientation: 'portrait',
        'tags__label__in': 'x,y'
      })
      expect(out.orientation).toBe('portrait')
      expect(out.tags).toEqual(['x', 'y'])
    })
  })
})
