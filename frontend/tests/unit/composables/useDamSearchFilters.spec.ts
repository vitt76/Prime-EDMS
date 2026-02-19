import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import {
  getDamSearchHistory,
  pushDamSearchHistory,
  DAM_SEARCH_HISTORY_KEY,
  DAM_SEARCH_HISTORY_MAX
} from '@/composables/useDamSearchFilters'

describe('useDamSearchFilters — search history', () => {
  let localStorageMock: Record<string, string>

  beforeEach(() => {
    localStorageMock = {}
    vi.stubGlobal('localStorage', {
      getItem: (key: string) => localStorageMock[key] ?? null,
      setItem: (key: string, value: string) => {
        localStorageMock[key] = value
      },
      removeItem: (key: string) => {
        delete localStorageMock[key]
      },
      clear: () => {
        Object.keys(localStorageMock).forEach((k) => delete localStorageMock[k])
      },
      length: 0,
      key: () => null
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns empty array when no history', () => {
    expect(getDamSearchHistory()).toEqual([])
  })

  it('returns parsed history from localStorage', () => {
    localStorageMock[DAM_SEARCH_HISTORY_KEY] = JSON.stringify(['q1', 'q2'])
    expect(getDamSearchHistory()).toEqual(['q1', 'q2'])
  })

  it('filters non-string entries and invalid JSON', () => {
    localStorageMock[DAM_SEARCH_HISTORY_KEY] = JSON.stringify(['a', 1, null, 'b'])
    expect(getDamSearchHistory()).toEqual(['a', 'b'])
  })

  it('limits history to DAM_SEARCH_HISTORY_MAX (10) items', () => {
    for (let i = 0; i < 15; i++) {
      pushDamSearchHistory(`query-${i}`)
    }
    const list = getDamSearchHistory()
    expect(list).toHaveLength(DAM_SEARCH_HISTORY_MAX)
    expect(list[0]).toBe('query-14')
    expect(list[9]).toBe('query-5')
  })

  it('deduplicates: repeated query moves to top and is not duplicated', () => {
    pushDamSearchHistory('first')
    pushDamSearchHistory('second')
    pushDamSearchHistory('third')
    expect(getDamSearchHistory()).toEqual(['third', 'second', 'first'])

    pushDamSearchHistory('second')
    expect(getDamSearchHistory()).toEqual(['second', 'third', 'first'])
  })

  it('ignores empty or whitespace-only query', () => {
    pushDamSearchHistory('valid')
    pushDamSearchHistory('')
    pushDamSearchHistory('   ')
    expect(getDamSearchHistory()).toEqual(['valid'])
  })

  it('trims query before storing', () => {
    pushDamSearchHistory('  trimmed  ')
    expect(getDamSearchHistory()).toEqual(['trimmed'])
  })
})
