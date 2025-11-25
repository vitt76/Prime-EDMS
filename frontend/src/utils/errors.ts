import type { ApiError } from '@/types'

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
    return apiError.code === 'NETWORK_ERROR' || apiError.code === 'TIMEOUT'
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


