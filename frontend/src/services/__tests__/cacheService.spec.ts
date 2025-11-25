import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { cacheService } from '../cacheService'

describe('CacheService', () => {
  beforeEach(() => {
    cacheService.clear()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    cacheService.clear()
  })

  describe('get and set', () => {
    it('should store and retrieve cached value', () => {
      const testData = { id: 1, name: 'Test' }
      cacheService.set('test-key', testData)

      const result = cacheService.get('test-key')
      expect(result).toEqual(testData)
    })

    it('should return null for non-existent key', () => {
      const result = cacheService.get('non-existent')
      expect(result).toBeNull()
    })

    it('should return null for expired entry', () => {
      const testData = { id: 1, name: 'Test' }
      cacheService.set('test-key', testData, 1000) // 1 second TTL

      // Fast-forward time
      vi.advanceTimersByTime(2000)

      const result = cacheService.get('test-key')
      expect(result).toBeNull()
    })

    it('should use custom TTL', () => {
      const testData = { id: 1, name: 'Test' }
      cacheService.set('test-key', testData, 5000) // 5 seconds

      vi.advanceTimersByTime(3000)

      const result = cacheService.get('test-key')
      expect(result).toEqual(testData) // Still valid

      vi.advanceTimersByTime(3000)

      const expired = cacheService.get('test-key')
      expect(expired).toBeNull() // Now expired
    })
  })

  describe('delete', () => {
    it('should delete cached value', () => {
      cacheService.set('test-key', { data: 'test' })
      expect(cacheService.get('test-key')).not.toBeNull()

      cacheService.delete('test-key')
      expect(cacheService.get('test-key')).toBeNull()
    })
  })

  describe('clear', () => {
    it('should clear all cache', () => {
      cacheService.set('key1', { data: 'test1' })
      cacheService.set('key2', { data: 'test2' })

      expect(cacheService.size()).toBe(2)

      cacheService.clear()

      expect(cacheService.size()).toBe(0)
      expect(cacheService.get('key1')).toBeNull()
      expect(cacheService.get('key2')).toBeNull()
    })
  })

  describe('clearExpired', () => {
    it('should remove expired entries', () => {
      cacheService.set('key1', { data: 'test1' }, 1000)
      cacheService.set('key2', { data: 'test2' }, 5000)

      vi.advanceTimersByTime(2000)

      cacheService.clearExpired()

      expect(cacheService.get('key1')).toBeNull()
      expect(cacheService.get('key2')).not.toBeNull()
    })
  })

  describe('size', () => {
    it('should return correct cache size', () => {
      expect(cacheService.size()).toBe(0)

      cacheService.set('key1', { data: 'test1' })
      expect(cacheService.size()).toBe(1)

      cacheService.set('key2', { data: 'test2' })
      expect(cacheService.size()).toBe(2)
    })
  })

  describe('has', () => {
    it('should return true for existing valid key', () => {
      cacheService.set('test-key', { data: 'test' })
      expect(cacheService.has('test-key')).toBe(true)
    })

    it('should return false for non-existent key', () => {
      expect(cacheService.has('non-existent')).toBe(false)
    })

    it('should return false for expired key', () => {
      cacheService.set('test-key', { data: 'test' }, 1000)

      vi.advanceTimersByTime(2000)

      expect(cacheService.has('test-key')).toBe(false)
    })
  })
})

