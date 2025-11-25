import { describe, it, expect } from 'vitest'
import {
  formatApiError,
  isNetworkError,
  isAuthError,
  isServerError,
  getErrorCode,
  getErrorDetails
} from '@/utils/errors'
import type { ApiError } from '@/types/api'

describe('Error utilities', () => {
  describe('formatApiError', () => {
    it('should format string error', () => {
      expect(formatApiError('Simple error')).toBe('Simple error')
    })

    it('should format ApiError object', () => {
      const error: ApiError = {
        code: 'TEST_ERROR',
        message: 'Test error message'
      }
      expect(formatApiError(error)).toBe('Test error message')
    })

    it('should return default message for error without message', () => {
      const error: ApiError = {
        code: 'TEST_ERROR',
        message: ''
      }
      expect(formatApiError(error)).toBe('Произошла ошибка')
    })

    it('should handle unknown error format', () => {
      expect(formatApiError({})).toBe('Произошла неизвестная ошибка')
      expect(formatApiError(null)).toBe('Произошла неизвестная ошибка')
    })
  })

  describe('isNetworkError', () => {
    it('should return true for NETWORK_ERROR', () => {
      const error: ApiError = {
        code: 'NETWORK_ERROR',
        message: 'Network error'
      }
      expect(isNetworkError(error)).toBe(true)
    })

    it('should return true for TIMEOUT', () => {
      const error: ApiError = {
        code: 'TIMEOUT',
        message: 'Request timeout'
      }
      expect(isNetworkError(error)).toBe(true)
    })

    it('should return true for ECONNABORTED', () => {
      const error: ApiError = {
        code: 'ECONNABORTED',
        message: 'Connection aborted'
      }
      expect(isNetworkError(error)).toBe(true)
    })

    it('should return false for other errors', () => {
      const error: ApiError = {
        code: 'SERVER_ERROR',
        message: 'Server error'
      }
      expect(isNetworkError(error)).toBe(false)
    })

    it('should return false for non-error objects', () => {
      expect(isNetworkError({})).toBe(false)
      expect(isNetworkError(null)).toBe(false)
    })
  })

  describe('isAuthError', () => {
    it('should return true for UNAUTHORIZED', () => {
      const error: ApiError = {
        code: 'UNAUTHORIZED',
        message: 'Unauthorized'
      }
      expect(isAuthError(error)).toBe(true)
    })

    it('should return true for FORBIDDEN', () => {
      const error: ApiError = {
        code: 'FORBIDDEN',
        message: 'Forbidden'
      }
      expect(isAuthError(error)).toBe(true)
    })

    it('should return false for other errors', () => {
      const error: ApiError = {
        code: 'SERVER_ERROR',
        message: 'Server error'
      }
      expect(isAuthError(error)).toBe(false)
    })
  })

  describe('isServerError', () => {
    it('should return true for SERVER_ERROR', () => {
      const error: ApiError = {
        code: 'SERVER_ERROR',
        message: 'Server error'
      }
      expect(isServerError(error)).toBe(true)
    })

    it('should return false for other errors', () => {
      const error: ApiError = {
        code: 'CLIENT_ERROR',
        message: 'Client error'
      }
      expect(isServerError(error)).toBe(false)
    })
  })

  describe('getErrorCode', () => {
    it('should extract error code', () => {
      const error: ApiError = {
        code: 'TEST_ERROR',
        message: 'Test'
      }
      expect(getErrorCode(error)).toBe('TEST_ERROR')
    })

    it('should return null for non-error objects', () => {
      expect(getErrorCode({})).toBeNull()
      expect(getErrorCode(null)).toBeNull()
    })
  })

  describe('getErrorDetails', () => {
    it('should extract error details', () => {
      const error: ApiError = {
        code: 'TEST_ERROR',
        message: 'Test',
        details: { field: 'value' }
      }
      expect(getErrorDetails(error)).toEqual({ field: 'value' })
    })

    it('should return null for error without details', () => {
      const error: ApiError = {
        code: 'TEST_ERROR',
        message: 'Test'
      }
      expect(getErrorDetails(error)).toBeNull()
    })

    it('should return null for non-error objects', () => {
      expect(getErrorDetails({})).toBeNull()
      expect(getErrorDetails(null)).toBeNull()
    })
  })
})

