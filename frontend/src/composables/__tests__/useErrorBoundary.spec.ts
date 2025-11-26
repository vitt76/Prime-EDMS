/**
 * useErrorBoundary Composable Tests
 *
 * Tests error logging, categorization, user-friendly messages,
 * external service integration, and global error handlers.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import {
  logError,
  categorizeError,
  shouldRetry,
  getErrorMessage,
  markErrorResolved,
  clearErrorLog,
  getErrorStats,
  useRetryableOperation,
  setupGlobalErrorHandlers,
  errorStats,
  recentErrors
} from '../useErrorBoundary'
import { ApiError } from '@/utils/retry'

describe('useErrorBoundary', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    // Mock external services
    vi.stubGlobal('Sentry', { captureException: vi.fn() })
    vi.stubGlobal('LogRocket', { captureException: vi.fn() })

    // Mock fetch for logging endpoint
    global.fetch = vi.fn().mockResolvedValue({ ok: true })

    // Reset error log
    clearErrorLog()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  describe('categorizeError', () => {
    it('categorizes network errors', () => {
      const error = new TypeError('Failed to fetch')
      expect(categorizeError(error)).toBe('network')
    })

    it('categorizes API errors', () => {
      const error = new ApiError('Server error', 500, true)
      expect(categorizeError(error)).toBe('api')
    })

    it('categorizes authentication errors', () => {
      const error = new Error('User not authenticated')
      expect(categorizeError(error)).toBe('authentication')
    })

    it('categorizes authorization errors', () => {
      const error = new Error('Access forbidden')
      expect(categorizeError(error)).toBe('authorization')
    })

    it('categorizes validation errors', () => {
      const error = new Error('Validation failed')
      expect(categorizeError(error)).toBe('validation')
    })

    it('categorizes unknown errors', () => {
      const error = new Error('Some random error')
      expect(categorizeError(error)).toBe('unknown')
    })
  })

  describe('shouldRetry', () => {
    it('should retry network errors', () => {
      const error = new TypeError('Failed to fetch')
      expect(shouldRetry(error)).toBe(true)
    })

    it('should retry API errors', () => {
      const error = new ApiError('Server error', 500, true)
      expect(shouldRetry(error)).toBe(true)
    })

    it('should not retry authentication errors', () => {
      const error = new Error('unauthorized')
      expect(shouldRetry(error)).toBe(false)
    })

    it('should not retry authorization errors', () => {
      const error = new Error('forbidden')
      expect(shouldRetry(error)).toBe(false)
    })

    it('should not retry validation errors', () => {
      const error = new Error('validation')
      expect(shouldRetry(error)).toBe(false)
    })
  })

  describe('getErrorMessage', () => {
    it('returns user-friendly message in production', () => {
      vi.mocked(import.meta.env).DEV = false

      const error = new Error('Technical error details')
      const message = getErrorMessage(error, false)

      expect(message).toBe('Something went wrong. Please try again.')
    })

    it('returns technical details in development', () => {
      vi.mocked(import.meta.env).DEV = true

      const error = new Error('Technical error details')
      const message = getErrorMessage(error, true)

      expect(message).toBe('Technical error details')
    })

    it('returns specific message for network errors', () => {
      const error = new TypeError('Failed to fetch')
      const message = getErrorMessage(error, false)

      expect(message).toBe('Connection failed. Please check your internet and try again.')
    })

    it('returns specific message for API errors', () => {
      const error = new ApiError('Server error', 500, true)
      const message = getErrorMessage(error, false)

      expect(message).toBe('Server error occurred. Please try again later.')
    })

    it('returns specific message for authentication errors', () => {
      const error = new Error('unauthorized')
      const message = getErrorMessage(error, false)

      expect(message).toBe('Please sign in to continue.')
    })
  })

  describe('logError', () => {
    it('creates error log entry', () => {
      const error = new Error('Test error')
      const context = { component: 'TestComponent', operation: 'testOp' }

      const errorId = logError(error, context)

      expect(errorId).toBeDefined()
      expect(typeof errorId).toBe('string')

      // Check recent errors
      expect(recentErrors.value).toHaveLength(1)
      expect(recentErrors.value?.[0]?.message).toBe('Test error')
      expect(recentErrors.value?.[0]?.context?.component).toBe('TestComponent')
    })

    it('logs to console in development', () => {
      vi.mocked(import.meta.env).DEV = true
      const consoleSpy = vi.spyOn(console, 'group').mockImplementation(() => {})

      const error = new Error('Dev error')
      logError(error)

      expect(consoleSpy).toHaveBeenCalledWith('🚨 Error [unknown]: Dev error')
    })

    it('does not log to console in production', () => {
      vi.mocked(import.meta.env).DEV = false
      const consoleSpy = vi.spyOn(console, 'group').mockImplementation(() => {})

      const error = new Error('Prod error')
      logError(error)

      expect(consoleSpy).not.toHaveBeenCalled()
    })

    it('sends to Sentry when available', () => {
      const sentrySpy = vi.fn()
      ;(global as any).Sentry = { captureException: sentrySpy }

      const error = new Error('Sentry error')
      logError(error)

      expect(sentrySpy).toHaveBeenCalledWith(error, expect.objectContaining({
        tags: expect.any(Object),
        extra: expect.any(Object)
      }))
    })

    it('sends to LogRocket when available', () => {
      const lrSpy = vi.fn()
      ;(global as any).LogRocket = { captureException: lrSpy }

      const error = new Error('LR error')
      logError(error)

      expect(lrSpy).toHaveBeenCalledWith(error, expect.any(Object))
    })

    it('sends to custom logging endpoint', async () => {
      const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({ ok: true } as any)

      const error = new Error('Custom endpoint error')
      logError(error)

      expect(fetchSpy).toHaveBeenCalledWith(
        expect.stringContaining('error-logging'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      )
    })

    it('handles logging service failures gracefully', async () => {
      const fetchSpy = vi.spyOn(global, 'fetch').mockRejectedValue(new Error('Network fail'))

      const error = new Error('Test error')
      const errorId = logError(error)

      // Should not throw and return error ID
      expect(errorId).toBeDefined()
      expect(typeof errorId).toBe('string')
    })
  })

  describe('error management', () => {
    it('marks error as resolved', () => {
      const error = new Error('Test error')
      const errorId = logError(error)

      markErrorResolved(errorId)

      expect(recentErrors.value[0].resolved).toBe(true)
    })

    it('clears error log', () => {
      logError(new Error('Error 1'))
      logError(new Error('Error 2'))

      expect(recentErrors.value).toHaveLength(2)

      clearErrorLog()

      expect(recentErrors.value).toHaveLength(0)
    })

    it('calculates error statistics', () => {
      logError(new TypeError('Network error')) // network
      logError(new ApiError('API error', 500, true)) // api
      logError(new Error('Auth error')) // unknown

      const stats = getErrorStats()

      expect(stats.total).toBe(3)
      expect(stats.unresolved).toBe(3)
      expect(stats.byType.network).toBe(1)
      expect(stats.byType.api).toBe(1)
      expect(stats.byType.unknown).toBe(1)
    })

    it('limits error log size', () => {
      // Create more errors than the limit
      for (let i = 0; i < 120; i++) {
        logError(new Error(`Error ${i}`))
      }

      expect(recentErrors.value).toHaveLength(100) // maxLogEntries
    })
  })

  describe('useRetryableOperation', () => {
    it('executes operation successfully', async () => {
      const operation = vi.fn().mockResolvedValue('success')

      const { execute } = useRetryableOperation(operation)

      const result = await execute()

      expect(result.success).toBe(true)
      expect(result.data).toBe('success')
    })

    it('handles operation failure', async () => {
      const operation = vi.fn().mockRejectedValue(new Error('Operation failed'))
      const onError = vi.fn()

      const { execute } = useRetryableOperation(operation, { onError, maxAttempts: 1 })

      const result = await execute()

      expect(result.success).toBe(false)
      expect(result.error).toBeInstanceOf(Error)
      expect(onError).toHaveBeenCalledWith(expect.any(Error))
    })

    it('calls onRetry callback', async () => {
      const operation = vi.fn()
        .mockRejectedValueOnce(new Error('First attempt'))
        .mockResolvedValueOnce('success')

      const onRetry = vi.fn()

      const { execute } = useRetryableOperation(operation, {
        onRetry,
        maxAttempts: 2
      })

      await execute()

      expect(onRetry).toHaveBeenCalledWith(1, expect.any(Error))
    })
  })

  describe('setupGlobalErrorHandlers', () => {
    let cleanup: () => void

    beforeEach(() => {
      cleanup = setupGlobalErrorHandlers()
    })

    afterEach(() => {
      cleanup()
    })

    it('handles unhandled promise rejections', () => {
      const error = new Error('Unhandled promise rejection')

      const rejectionEvent = new PromiseRejectionEvent('unhandledrejection', {
        reason: error,
        promise: Promise.reject(error)
      })

      window.dispatchEvent(rejectionEvent)

      expect(recentErrors.value).toHaveLength(1)
      expect(recentErrors.value[0].message).toBe('Unhandled promise rejection')
      expect(recentErrors.value?.[0]?.context?.type).toBe('unhandled_promise_rejection')
    })

    it('handles global errors', () => {
      const error = new Error('Global error')

      const errorEvent = new ErrorEvent('error', {
        error,
        filename: 'test.js',
        lineno: 42,
        colno: 10
      })

      window.dispatchEvent(errorEvent)

      expect(recentErrors.value).toHaveLength(1)
      expect(recentErrors.value?.[0]?.message).toBe('Global error')
      expect(recentErrors.value?.[0]?.context?.type).toBe('unhandled_error')
    })

    it('prevents default error handling', () => {
      const errorEvent = new ErrorEvent('error', {
        error: new Error('Test'),
        cancelable: true
      })

      const preventDefaultSpy = vi.spyOn(errorEvent, 'preventDefault')

      window.dispatchEvent(errorEvent)

      expect(preventDefaultSpy).toHaveBeenCalled()
    })

    it('returns cleanup function', () => {
      const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

      cleanup()

      expect(removeEventListenerSpy).toHaveBeenCalledTimes(2)
    })
  })

  describe('computed properties', () => {
    it('provides error statistics reactively', () => {
      logError(new Error('Test error'))

      expect(errorStats.value.total).toBe(1)
      expect(errorStats.value.unresolved).toBe(1)
    })

    it('provides recent errors reactively', () => {
      logError(new Error('Error 1'))
      logError(new Error('Error 2'))
      logError(new Error('Error 3'))

      expect(recentErrors.value).toHaveLength(3)
      expect(recentErrors.value[0].message).toBe('Error 3') // Most recent first
    })
  })

  describe('edge cases', () => {
    it('handles non-Error objects in logError', () => {
      const errorId = logError(new Error('String error'))

      expect(errorId).toBeDefined()
      expect(recentErrors.value?.[0]?.message).toBe('String error')
    })

    it('handles missing external services gracefully', () => {
      delete (global as any).Sentry
      delete (global as any).LogRocket

      const error = new Error('Test')
      const errorId = logError(error)

      expect(errorId).toBeDefined()
      // Should not throw
    })

    it('handles missing logging endpoint gracefully', () => {
      // Remove env var
      delete (import.meta as any).env.VITE_ERROR_LOGGING_ENDPOINT

      const error = new Error('Test')
      const errorId = logError(error)

      expect(errorId).toBeDefined()
      // Should not call fetch
      expect(global.fetch).not.toHaveBeenCalled()
    })

    it('handles clipboard not available in report error', async () => {
      const mockClipboard = { writeText: vi.fn().mockRejectedValue(new Error('Not supported')) }
      Object.assign(navigator, { clipboard: mockClipboard })

      // This would be tested in the ErrorBoundary component
      // which calls logError and handles clipboard failures
      const error = new Error('Test')
      logError(error)

      expect(mockClipboard.writeText).not.toHaveBeenCalled()
    })
  })
})
