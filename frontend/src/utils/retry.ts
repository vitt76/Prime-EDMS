/**
 * Retry utility with exponential backoff for async operations
 *
 * Provides configurable retry logic for network requests, API calls,
 * and other async operations with intelligent backoff strategies.
 */

export interface RetryOptions {
  /** Maximum number of retry attempts */
  maxAttempts?: number
  /** Initial delay in milliseconds */
  initialDelay?: number
  /** Maximum delay between retries */
  maxDelay?: number
  /** Backoff multiplier */
  backoffFactor?: number
  /** Jitter to randomize delays */
  jitter?: boolean
  /** Should retry on specific error types */
  retryCondition?: (error: Error) => boolean
  /** Callback before each retry attempt */
  onRetry?: (attempt: number, error: Error, delay: number) => void
  /** Abort signal for cancellation */
  signal?: AbortSignal
}

export interface RetryResult<T> {
  success: boolean
  data?: T
  error?: Error
  attempts: number
  totalDuration: number
}

/**
 * Default retry condition - retries on network errors and 5xx status codes
 */
const defaultRetryCondition = (error: Error): boolean => {
  // Network errors (fetch failures, timeouts)
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return true
  }

  // Abort errors (user cancelled)
  if (error.name === 'AbortError') {
    return false
  }

  // Custom API errors with retry flag
  if (error instanceof ApiError && error.retryable) {
    return true
  }

  // HTTP status codes
  if ('status' in error && typeof error.status === 'number') {
    const status = error.status as number
    // Retry on 5xx server errors, timeouts, rate limits
    return status >= 500 || status === 408 || status === 429
  }

  return false
}

/**
 * Custom API error class with retryability flag
 */
export class ApiError extends Error {
  public readonly status?: number
  public readonly retryable: boolean
  public readonly code?: string

  constructor(
    message: string,
    status?: number,
    retryable: boolean = false,
    code?: string
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.retryable = retryable
    this.code = code
  }
}

/**
 * Calculate delay with exponential backoff and optional jitter
 */
const calculateDelay = (
  attempt: number,
  initialDelay: number,
  maxDelay: number,
  backoffFactor: number,
  jitter: boolean
): number => {
  const exponentialDelay = initialDelay * Math.pow(backoffFactor, attempt - 1)
  const clampedDelay = Math.min(exponentialDelay, maxDelay)

  if (jitter) {
    // Add random jitter (±25% of delay)
    const jitterRange = clampedDelay * 0.25
    return clampedDelay + (Math.random() * 2 - 1) * jitterRange
  }

  return clampedDelay
}

/**
 * Sleep for specified milliseconds
 */
const sleep = (ms: number, signal?: AbortSignal): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new Error('Operation cancelled'))
      return
    }

    const timeout = setTimeout(resolve, ms)

    if (signal) {
      signal.addEventListener('abort', () => {
        clearTimeout(timeout)
        reject(new Error('Operation cancelled'))
      })
    }
  })
}

/**
 * Retry an async operation with exponential backoff
 */
export async function withRetry<T>(
  operation: () => Promise<T>,
  options: RetryOptions = {}
): Promise<RetryResult<T>> {
  const {
    maxAttempts = 3,
    initialDelay = 1000,
    maxDelay = 30000,
    backoffFactor = 2,
    jitter = true,
    retryCondition = defaultRetryCondition,
    onRetry,
    signal
  } = options

  const startTime = Date.now()
  let lastError: Error

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      if (signal?.aborted) {
        throw new Error('Operation cancelled')
      }

      const result = await operation()
      return {
        success: true,
        data: result,
        attempts: attempt,
        totalDuration: Date.now() - startTime
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))

      // Don't retry if this is the last attempt
      if (attempt === maxAttempts) {
        break
      }

      // Check if we should retry this error
      if (!retryCondition(lastError)) {
        break
      }

      // Calculate delay for next attempt
      const delay = calculateDelay(attempt, initialDelay, maxDelay, backoffFactor, jitter)

      // Notify about retry
      onRetry?.(attempt, lastError, delay)

      // Wait before retrying
      try {
        await sleep(delay, signal)
      } catch (sleepError) {
        // Sleep was interrupted (cancelled)
        return {
          success: false,
          error: sleepError instanceof Error ? sleepError : new Error('Operation cancelled'),
          attempts: attempt,
          totalDuration: Date.now() - startTime
        }
      }
    }
  }

  return {
    success: false,
    error: lastError,
    attempts: maxAttempts,
    totalDuration: Date.now() - startTime
  }
}

/**
 * Retry wrapper for fetch requests with automatic retry headers
 */
export async function fetchWithRetry(
  url: string,
  options: RequestInit & { retryOptions?: RetryOptions } = {}
): Promise<Response> {
  const { retryOptions, ...fetchOptions } = options

  const operation = async (): Promise<Response> => {
    const response = await fetch(url, fetchOptions)

    // Throw error for non-2xx responses
    if (!response.ok) {
      const error = new ApiError(
        `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        response.status >= 500 || response.status === 429 // Retryable server errors
      )
      throw error
    }

    return response
  }

  const result = await withRetry(operation, retryOptions)

  if (!result.success) {
    throw result.error
  }

  return result.data!
}

/**
 * Retry wrapper for any async function
 */
export function createRetryableFunction<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  retryOptions: RetryOptions = {}
): T {
  return ((...args: Parameters<T>) => {
    const operation = () => fn(...args)
    return withRetry(operation, retryOptions)
  }) as T
}

/**
 * Hook for React-style error boundaries (Vue composable)
 */
export function useRetryableOperation<T>(
  operation: () => Promise<T>,
  options: RetryOptions & {
    autoRetry?: boolean
    autoRetryDelay?: number
  } = {}
) {
  const { autoRetry = false, autoRetryDelay = 5000, ...retryOptions } = options

  let retryTimeout: number | null = null

  const execute = async (): Promise<RetryResult<T>> => {
    const result = await withRetry(operation, retryOptions)

    // Auto-retry on network errors after delay
    if (!result.success && autoRetry && retryCondition(result.error!)) {
      if (retryTimeout) clearTimeout(retryTimeout)
      retryTimeout = window.setTimeout(() => {
        execute() // Recursive retry
      }, autoRetryDelay)
    }

    return result
  }

  const cancel = () => {
    if (retryTimeout) {
      clearTimeout(retryTimeout)
      retryTimeout = null
    }
  }

  return { execute, cancel }
}
