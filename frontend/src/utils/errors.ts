import type { ApiError } from '@/types/api'

/**
 * Format API error to user-friendly message
 */
export function formatApiError(error: unknown): string {
  if (typeof error === 'string') return error

  if (error && typeof error === 'object' && 'message' in error) {
    const apiError = error as ApiError
    return apiError.message || 'Произошла ошибка'
  }

  return 'Произошла неизвестная ошибка'
}

/**
 * Check if error is network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error && typeof error === 'object' && 'code' in error) {
    const apiError = error as ApiError
    return (
      apiError.code === 'NETWORK_ERROR' ||
      apiError.code === 'TIMEOUT' ||
      apiError.code === 'ECONNABORTED'
    )
  }
  return false
}

/**
 * Check if error is authentication error
 */
export function isAuthError(error: unknown): boolean {
  if (error && typeof error === 'object' && 'code' in error) {
    const apiError = error as ApiError
    return apiError.code === 'UNAUTHORIZED' || apiError.code === 'FORBIDDEN'
  }
  return false
}

/**
 * Check if error is server error (5xx)
 */
export function isServerError(error: unknown): boolean {
  if (error && typeof error === 'object' && 'code' in error) {
    const apiError = error as ApiError
    return apiError.code === 'SERVER_ERROR'
  }
  return false
}

/**
 * Get error code from error
 */
export function getErrorCode(error: unknown): string | null {
  if (error && typeof error === 'object' && 'code' in error) {
    const apiError = error as ApiError
    return apiError.code
  }
  return null
}

/**
 * Get error details from error
 */
export function getErrorDetails(error: unknown): Record<string, unknown> | null {
  if (error && typeof error === 'object' && 'details' in error) {
    const apiError = error as ApiError
    return apiError.details || null
  }
  return null
}


