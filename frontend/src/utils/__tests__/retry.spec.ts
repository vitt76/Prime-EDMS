/**
 * Retry Utility Tests
 *
 * Tests retry logic, exponential backoff, custom conditions,
 * abort signals, and edge cases.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import {
  withRetry,
  fetchWithRetry,
  ApiError,
  createRetryableFunction,
  useRetryableOperation
} from '../retry'

describe('Retry Utility', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  describe('withRetry', () => {
    it('returns success on first attempt', async () => {
      const operation = vi.fn().mockResolvedValue('success')

      const result = await withRetry(operation)

      expect(result.success).toBe(true)
      expect(result.data).toBe('success')
      expect(result.attempts).toBe(1)
      expect(operation).toHaveBeenCalledTimes(1)
    })

    it('retries on failure and succeeds', async () => {
      const operation = vi.fn()
        .mockRejectedValueOnce(new Error('First failure'))
        .mockRejectedValueOnce(new Error('Second failure'))
        .mockResolvedValueOnce('success')

      const result = await withRetry(operation, { maxAttempts: 3 })

      expect(result.success).toBe(true)
      expect(result.data).toBe('success')
      expect(result.attempts).toBe(3)
      expect(operation).toHaveBeenCalledTimes(3)
    })

    it('gives up after max attempts', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Always fails'))

      const result = await withRetry(operation, { maxAttempts: 3 })

      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(Error)
      expect(result.error!.message).toBe('Always fails')
      expect(result.attempts).toBe(3)
      expect(operation).toHaveBeenCalledTimes(3)
    })

    it('respects retry condition', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Not retryable'))

      const result = await withRetry(operation, {
        maxAttempts: 3,
        retryCondition: () => false // Never retry
      })

      expect(result.success).toBe(false)
      expect(result.attempts).toBe(1) // Only first attempt
    })

    it('uses exponential backoff with jitter', async () => {
      const operation = vi.fn()
        .mockRejectedValueOnce(new Error('Fail 1'))
        .mockRejectedValueOnce(new Error('Fail 2'))
        .mockResolvedValueOnce('success')

      const onRetry = vi.fn()

      await withRetry(operation, {
        maxAttempts: 3,
        initialDelay: 1000,
        backoffFactor: 2,
        jitter: true,
        onRetry
      })

      expect(onRetry).toHaveBeenCalledTimes(2)
      // Check that delays are increasing exponentially
      expect(onRetry.mock.calls[0][2]).toBeGreaterThanOrEqual(1000)
      expect(onRetry.mock.calls[1][2]).toBeGreaterThanOrEqual(2000)
    })

    it('respects max delay', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Always fails'))

      const onRetry = vi.fn()

      await withRetry(operation, {
        maxAttempts: 5,
        initialDelay: 1000,
        maxDelay: 2000,
        backoffFactor: 10, // Would normally be huge
        onRetry
      })

      // All retry delays should be <= maxDelay
      onRetry.mock.calls.forEach(call => {
        expect(call[2]).toBeLessThanOrEqual(2000)
      })
    })

    it('handles abort signal', async () => {
      const abortController = new AbortController()
      const operation = vi.fn().mockImplementation(() => {
        return new Promise((resolve, reject) => {
          setTimeout(() => reject(new Error('Timeout')), 100)
        })
      })

      // Abort after first failure
      setTimeout(() => abortController.abort(), 50)

      const result = await withRetry(operation, {
        maxAttempts: 3,
        signal: abortController.signal
      })

      expect(result.success).toBe(false)
      expect(result.error!.message).toBe('Operation cancelled')
    })

    it('calls onRetry callback with correct parameters', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Test error'))
      const onRetry = vi.fn()

      await withRetry(operation, {
        maxAttempts: 2,
        onRetry
      })

      expect(onRetry).toHaveBeenCalledWith(1, expect.any(Error), expect.any(Number))
      expect(onRetry.mock.calls[0][0]).toBe(1) // attempt
      expect(onRetry.mock.calls[0][1].message).toBe('Test error') // error
    })

    it('tracks total duration', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Always fails'))

      const startTime = Date.now()
      const result = await withRetry(operation, { maxAttempts: 2 })

      expect(result.totalDuration).toBeGreaterThanOrEqual(0)
      expect(result.totalDuration).toBeLessThanOrEqual(Date.now() - startTime + 100)
    })
  })

  describe('ApiError', () => {
    it('creates retryable API error', () => {
      const error = new ApiError('Server error', 500, true, 'SERVER_ERROR')

      expect(error.message).toBe('Server error')
      expect(error.status).toBe(500)
      expect(error.retryable).toBe(true)
      expect(error.code).toBe('SERVER_ERROR')
    })

    it('creates non-retryable API error', () => {
      const error = new ApiError('Bad request', 400, false)

      expect(error.status).toBe(400)
      expect(error.retryable).toBe(false)
    })
  })

  describe('fetchWithRetry', () => {
    let fetchSpy: any

    beforeEach(() => {
      fetchSpy = vi.spyOn(global, 'fetch')
    })

    afterEach(() => {
      fetchSpy.mockRestore()
    })

    it('returns response on successful fetch', async () => {
      const mockResponse = { ok: true, status: 200, json: () => Promise.resolve({ data: 'test' }) }
      fetchSpy.mockResolvedValue(mockResponse)

      const result = await fetchWithRetry('https://api.example.com/data')

      expect(result).toBe(mockResponse)
      expect(fetchSpy).toHaveBeenCalledTimes(1)
    })

    it('retries on 5xx errors', async () => {
      fetchSpy
        .mockResolvedValueOnce({ ok: false, status: 500, statusText: 'Internal Server Error' })
        .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ data: 'success' }) })

      const result = await fetchWithRetry('https://api.example.com/data')

      expect(fetchSpy).toHaveBeenCalledTimes(2)
      expect(result.ok).toBe(true)
    })

    it('retries on network errors', async () => {
      fetchSpy
        .mockRejectedValueOnce(new TypeError('Failed to fetch'))
        .mockResolvedValueOnce({ ok: true, status: 200, json: () => Promise.resolve({ data: 'success' }) })

      const result = await fetchWithRetry('https://api.example.com/data')

      expect(fetchSpy).toHaveBeenCalledTimes(2)
      expect(result.ok).toBe(true)
    })

    it('does not retry on 4xx errors', async () => {
      const mockResponse = { ok: false, status: 400, statusText: 'Bad Request' }
      fetchSpy.mockResolvedValue(mockResponse)

      await expect(fetchWithRetry('https://api.example.com/data')).rejects.toThrow()

      expect(fetchSpy).toHaveBeenCalledTimes(1)
    })

    it('throws ApiError on HTTP errors', async () => {
      fetchSpy.mockResolvedValue({ ok: false, status: 500, statusText: 'Server Error' })

      await expect(fetchWithRetry('https://api.example.com/data')).rejects.toThrow(ApiError)
    })
  })

  describe('createRetryableFunction', () => {
    it('wraps function with retry logic', async () => {
      const originalFn = vi.fn()
        .mockRejectedValueOnce(new Error('First call'))
        .mockResolvedValueOnce('success')

      const retryableFn = createRetryableFunction(originalFn, { maxAttempts: 3 })

      const result = await retryableFn('arg1', 'arg2')

      expect(result.success).toBe(true)
      expect(result.data).toBe('success')
      expect(originalFn).toHaveBeenCalledWith('arg1', 'arg2')
      expect(originalFn).toHaveBeenCalledTimes(2)
    })

    it('preserves function signature', () => {
      const originalFn = (a: string, b: number) => Promise.resolve(`${a}-${b}`)
      const retryableFn = createRetryableFunction(originalFn)

      expect(typeof retryableFn).toBe('function')
      // TypeScript should preserve parameter types
    })
  })

  describe('useRetryableOperation', () => {
    it('executes operation with retry', async () => {
      const operation = vi.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce('success')

      const { execute } = useRetryableOperation(operation, { maxAttempts: 2 })

      const result = await execute()

      expect(result.success).toBe(true)
      expect(result.data).toBe('success')
      expect(operation).toHaveBeenCalledTimes(2)
    })

    it('handles auto-retry', () => {
      const operation = vi.fn().mockRejectedValue(new Error('Network error'))
      const { execute } = useRetryableOperation(operation, {
        autoRetry: true,
        autoRetryDelay: 1000
      })

      execute()

      // Should set up auto-retry timer
      vi.advanceTimersByTime(1000)

      expect(operation).toHaveBeenCalledTimes(2) // Initial + auto-retry
    })

    it('cancels auto-retry', () => {
      const operation = vi.fn().mockRejectedValue(new Error('Network error'))
      const { execute, cancel } = useRetryableOperation(operation, {
        autoRetry: true,
        autoRetryDelay: 1000
      })

      execute()
      cancel()

      vi.advanceTimersByTime(1000)

      expect(operation).toHaveBeenCalledTimes(1) // Only initial call
    })

    it('calls error callback on failure', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Test error'))
      const onError = vi.fn()

      const { execute } = useRetryableOperation(operation, {
        onError,
        maxAttempts: 1
      })

      const result = await execute()

      expect(result.success).toBe(false)
      expect(onError).toHaveBeenCalledWith(expect.any(Error))
    })
  })

  describe('Default retry condition', () => {
    it('retries network errors', () => {
      const networkError = new TypeError('Failed to fetch')
      expect(defaultRetryCondition(networkError)).toBe(true)
    })

    it('does not retry abort errors', () => {
      const abortError = new Error('Aborted')
      abortError.name = 'AbortError'
      expect(defaultRetryCondition(abortError)).toBe(false)
    })

    it('retries retryable API errors', () => {
      const apiError = new ApiError('Server error', 500, true)
      expect(defaultRetryCondition(apiError)).toBe(true)
    })

    it('does not retry non-retryable API errors', () => {
      const apiError = new ApiError('Bad request', 400, false)
      expect(defaultRetryCondition(apiError)).toBe(false)
    })

    it('retries 5xx HTTP status codes', () => {
      const error = { status: 500 } as any
      expect(defaultRetryCondition(error)).toBe(true)
    })

    it('retries timeout errors', () => {
      const error = { status: 408 } as any
      expect(defaultRetryCondition(error)).toBe(true)
    })

    it('retries rate limit errors', () => {
      const error = { status: 429 } as any
      expect(defaultRetryCondition(error)).toBe(true)
    })

    it('does not retry 4xx client errors', () => {
      const error = { status: 400 } as any
      expect(defaultRetryCondition(error)).toBe(false)
    })
  })

  describe('Edge cases', () => {
    it('handles undefined operation', async () => {
      const operation = vi.fn().mockResolvedValue(undefined)

      const result = await withRetry(operation)

      expect(result.success).toBe(true)
      expect(result.data).toBeUndefined()
    })

    it('handles operation throwing non-Error objects', async () => {
      const operation = vi.fn().mockRejectedValue('String error')

      const result = await withRetry(operation)

      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(Error)
      expect(result.error!.message).toBe('String error')
    })

    it('respects zero maxAttempts (no retries)', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Fail'))

      const result = await withRetry(operation, { maxAttempts: 1 })

      expect(result.attempts).toBe(1)
      expect(operation).toHaveBeenCalledTimes(1)
    })

    it('handles very short delays', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Fail'))

      const onRetry = vi.fn()

      await withRetry(operation, {
        maxAttempts: 2,
        initialDelay: 1,
        onRetry
      })

      expect(onRetry).toHaveBeenCalledWith(1, expect.any(Error), 1)
    })

    it('handles very long operations', async () => {
      const operation = vi.fn().mockImplementation(() => {
        return new Promise(resolve => setTimeout(() => resolve('success'), 100))
      })

      const startTime = Date.now()
      const result = await withRetry(operation)

      expect(result.totalDuration).toBeGreaterThanOrEqual(100)
      expect(result.totalDuration).toBeLessThan(200)
    })
  })
})




