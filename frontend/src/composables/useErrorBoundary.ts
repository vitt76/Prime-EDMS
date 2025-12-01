/**
 * Error Boundary Composable
 *
 * Provides centralized error handling logic for the application.
 * Integrates with retry utility and logging systems.
 */

import { ref, computed } from 'vue'
import { withRetry, RetryOptions, ApiError } from '@/utils/retry'

// Error types for categorization
export enum ErrorType {
  NETWORK = 'network',
  API = 'api',
  VALIDATION = 'validation',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  BUSINESS_LOGIC = 'business_logic',
  UNKNOWN = 'unknown'
}

export interface ErrorContext {
  component?: string
  operation?: string
  userId?: string
  url?: string
  timestamp?: string
  stack?: string
  info?: string
  [key: string]: any
}

export interface ErrorLogEntry {
  id: string
  type: ErrorType
  message: string
  context: ErrorContext
  timestamp: Date
  userAgent: string
  resolved: boolean
}

// Reactive state
const errorLog = ref<ErrorLogEntry[]>([])
const maxLogEntries = 100

/**
 * Categorize error type based on error properties
 */
export function categorizeError(error: Error): ErrorType {
  // Network errors
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return ErrorType.NETWORK
  }

  // API errors
  if (error instanceof ApiError) {
    if (error.status === 401) return ErrorType.AUTHENTICATION
    if (error.status === 403) return ErrorType.AUTHORIZATION
    if (error.status === 422) return ErrorType.VALIDATION
    return ErrorType.API
  }

  // Authentication errors
  if (error.message.includes('unauthorized') || error.message.includes('authentication')) {
    return ErrorType.AUTHENTICATION
  }

  // Authorization errors
  if (error.message.includes('forbidden') || error.message.includes('permission')) {
    return ErrorType.AUTHORIZATION
  }

  // Validation errors
  if (error.message.includes('validation') || error.message.includes('invalid')) {
    return ErrorType.VALIDATION
  }

  return ErrorType.UNKNOWN
}

/**
 * Check if error should trigger retry
 */
export function shouldRetry(error: Error): boolean {
  const errorType = categorizeError(error)

  switch (errorType) {
    case ErrorType.NETWORK:
    case ErrorType.API:
      return true
    case ErrorType.AUTHENTICATION:
    case ErrorType.AUTHORIZATION:
    case ErrorType.VALIDATION:
    case ErrorType.BUSINESS_LOGIC:
      return false
    default:
      return false
  }
}

/**
 * Get user-friendly error message
 */
export function getErrorMessage(error: Error, isDevelopment: boolean = false): string {
  const errorType = categorizeError(error)

  // Development mode: show technical details
  if (isDevelopment) {
    return error.message
  }

  // Production mode: show user-friendly messages
  switch (errorType) {
    case ErrorType.NETWORK:
      return 'Connection failed. Please check your internet and try again.'
    case ErrorType.API:
      return 'Server error occurred. Please try again later.'
    case ErrorType.AUTHENTICATION:
      return 'Please sign in to continue.'
    case ErrorType.AUTHORIZATION:
      return 'You don\'t have permission to perform this action.'
    case ErrorType.VALIDATION:
      return 'Please check your input and try again.'
    case ErrorType.BUSINESS_LOGIC:
      return 'Unable to complete the request. Please try again.'
    default:
      return 'Something went wrong. Please try again.'
  }
}

/**
 * Log error to storage and external services
 */
export function logError(error: Error, context: ErrorContext = {}): string {
  const isDevelopment = import.meta.env.DEV
  const errorId = crypto.randomUUID()
  const errorType = categorizeError(error)

  const logEntry: ErrorLogEntry = {
    id: errorId,
    type: errorType,
    message: error.message,
    context: {
      ...context,
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString()
    },
    timestamp: new Date(),
    userAgent: navigator.userAgent,
    resolved: false
  }

  // Add to local log
  errorLog.value.unshift(logEntry)

  // Keep only max entries
  if (errorLog.value.length > maxLogEntries) {
    errorLog.value = errorLog.value.slice(0, maxLogEntries)
  }

  // Log to console in development
  if (isDevelopment) {
    console.group(`🚨 Error [${errorType}]: ${error.message}`)
    console.error(error)
    console.log('Context:', context)
    console.log('Error ID:', errorId)
    console.groupEnd()
  }

  // Send to external logging service (Sentry, etc.)
  sendToExternalLogger(logEntry)

  return errorId
}

/**
 * Send error to external logging service
 */
async function sendToExternalLogger(logEntry: ErrorLogEntry): Promise<void> {
  // Check if external logging is enabled
  const sentryDsn = import.meta.env.VITE_SENTRY_DSN
  const logRocketId = import.meta.env.VITE_LOGROCKET_ID

  try {
    // Sentry integration
    if (sentryDsn && window.Sentry) {
      window.Sentry.captureException(new Error(logEntry.message), {
        tags: {
          errorType: logEntry.type,
          errorId: logEntry.id
        },
        extra: logEntry.context
      })
    }

    // LogRocket integration
    if (logRocketId && window.LogRocket) {
      window.LogRocket.captureException(new Error(logEntry.message), {
        tags: {
          errorType: logEntry.type,
          errorId: logEntry.id
        },
        extra: logEntry.context
      })
    }

    // Custom logging endpoint
    const loggingEndpoint = import.meta.env.VITE_ERROR_LOGGING_ENDPOINT
    if (loggingEndpoint) {
      await fetch(loggingEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(logEntry)
      })
    }
  } catch (loggingError) {
    // Don't throw if logging fails
    console.warn('Failed to send error to external logger:', loggingError)
  }
}

/**
 * Mark error as resolved
 */
export function markErrorResolved(errorId: string): void {
  const entry = errorLog.value.find(e => e.id === errorId)
  if (entry) {
    entry.resolved = true
  }
}

/**
 * Clear error log
 */
export function clearErrorLog(): void {
  errorLog.value = []
}

/**
 * Get error statistics
 */
export function getErrorStats() {
  const total = errorLog.value.length
  const resolved = errorLog.value.filter(e => e.resolved).length
  const unresolved = total - resolved

  const byType = errorLog.value.reduce((acc, entry) => {
    acc[entry.type] = (acc[entry.type] || 0) + 1
    return acc
  }, {} as Record<ErrorType, number>)

  return {
    total,
    resolved,
    unresolved,
    byType
  }
}

/**
 * Retryable operation wrapper
 */
export function useRetryableOperation<T>(
  operation: () => Promise<T>,
  options: RetryOptions & {
    onError?: (error: Error) => void
    onRetry?: (attempt: number, error: Error) => void
  } = {}
) {
  const { onError, onRetry, ...retryOptions } = options

  const execute = async (): Promise<{ success: boolean; data?: T; error?: Error }> => {
    try {
      const result = await withRetry(operation, {
        ...retryOptions,
        onRetry: (attempt, error, delay) => {
          logError(error, { operation: operation.name, attempt, delay })
          onRetry?.(attempt, error)
        }
      })

      if (result.success) {
        return { success: true, data: result.data }
      } else {
        const error = result.error!
        logError(error, { operation: operation.name, attempts: result.attempts })
        onError?.(error)
        return { success: false, error }
      }
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error))
      logError(err, { operation: operation.name })
      onError?.(err)
      return { success: false, error: err }
    }
  }

  return { execute }
}

/**
 * Global error handler for unhandled promise rejections
 */
export function setupGlobalErrorHandlers(): () => void {
  const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
    const error = event.reason instanceof Error
      ? event.reason
      : new Error(String(event.reason))

    logError(error, {
      type: 'unhandled_promise_rejection',
      originalReason: event.reason
    })

    // Prevent default browser error handling
    event.preventDefault()
  }

  const handleError = (event: ErrorEvent) => {
    logError(event.error || new Error(event.message), {
      type: 'unhandled_error',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    })

    // Prevent default browser error handling
    event.preventDefault()
  }

  // Add global handlers
  window.addEventListener('unhandledrejection', handleUnhandledRejection)
  window.addEventListener('error', handleError)

  // Return cleanup function
  return () => {
    window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    window.removeEventListener('error', handleError)
  }
}

// Computed properties for templates
export const errorStats = computed(() => getErrorStats())
export const recentErrors = computed(() =>
  errorLog.value.slice(0, 10)
)

// Global type declarations for external services
declare global {
  interface Window {
    Sentry?: any
    LogRocket?: any
  }
}





