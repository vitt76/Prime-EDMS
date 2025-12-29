import axios, {
  type AxiosInstance,
  type AxiosError,
  type InternalAxiosRequestConfig
} from 'axios'
import type { ApiResponse, ApiError } from '@/types/api'
import { cacheService } from './cacheService'
import { getToken, clearToken } from './authService'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''
const MAX_RETRIES = 3
const MAX_RETRIES_RATE_LIMIT = 5 // More retries for rate limit errors
const RETRY_DELAY = 1000 // 1 second

const shouldDebugLog = (): boolean => {
  try {
    // Auto-enable debug logging in dev mode if not explicitly disabled
    if (import.meta.env.DEV) {
      const debugFlag = localStorage.getItem('maddam_debug')
      if (debugFlag === null) {
        // Auto-enable if not set
        localStorage.setItem('maddam_debug', '1')
        return true
      }
      return debugFlag === '1'
    }
    return false
  } catch {
    return false
  }
}

// Request logging
const logRequest = (config: InternalAxiosRequestConfig): void => {
  if (shouldDebugLog()) {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
      params: config.params,
      data: config.data
    })
  }
}

const logResponse = (response: unknown): void => {
  if (shouldDebugLog()) {
    console.log('[API Response]', response)
  }
}

const logError = (error: unknown): void => {
  if (shouldDebugLog()) {
    console.error('[API Error]', error)
  }
}

// Retry logic
const shouldRetry = (error: AxiosError): boolean => {
  // Retry on network errors or 5xx errors
  if (!error.response) {
    return true // Network error
  }
  
  const status = error.response.status
  // Retry on 5xx errors or 429 (rate limit)
  return (status >= 500 && status < 600) || status === 429
}

const delay = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      withCredentials: true,  // Important for session cookies
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'  // Additional header to ensure JSON response
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Request logging
        logRequest(config)

        // Add Authorization Token header (DRF Token authentication)
        const token = getToken()
        if (token) {
          // Ensure headers object exists (blob requests may pass config without headers).
          if (!config.headers) {
            // eslint-disable-next-line no-param-reassign
            config.headers = {} as any
          }
          config.headers['Authorization'] = `Token ${token}`
        }

        // Add CSRF token from cookie or meta tag
        const csrfToken = this.getCSRFToken()
        if (csrfToken && config.headers) {
          config.headers['X-CSRFToken'] = csrfToken
        }

        return config
      },
      (error) => {
        logError(error)
        return Promise.reject(error)
      }
    )

    // Response interceptor with retry logic
    this.client.interceptors.response.use(
      (response) => {
        logResponse(response.data)
        return response
      },
      async (error: AxiosError<any>) => {
        logError(error)

        const config = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean
          _retryCount?: number
        }

        // Handle 401 Unauthorized
        if (error.response?.status === 401) {
          // Don't immediately logout - let the calling code handle it
          // This prevents premature logout during initial page load
          // Only clear token if we're sure the request was intentional (not during init)
          const isMenuRequest = error.config?.url?.includes('/templates/menu') || 
                                error.config?.url?.includes('menu_topbar') || 
                                error.config?.url?.includes('menu_main')
          
          if (!isMenuRequest) {
            // For non-menu requests, clear token but don't redirect immediately
            // Let the component/router handle the redirect
            console.warn('[API] 401 Unauthorized on non-menu request:', error.config?.url)
            clearToken()
          } else {
            // For menu requests, just log - Vue app will handle auth check
            console.warn('[API] 401 Unauthorized on menu request (will be handled by Vue app):', error.config?.url)
          }
          return Promise.reject(error)
        }

        // Handle 403 Forbidden
        if (error.response?.status === 403) {
          const apiError: ApiError = {
            code: 'FORBIDDEN',
            message: 'Доступ запрещен',
            details: (error.response.data as unknown as Record<string, unknown>)
          }
          return Promise.reject(apiError)
        }

        // Handle missing headless endpoints gracefully
        if (error.response?.status === 404 && error.config?.url?.includes('/headless/')) {
          const apiError: ApiError = {
            code: 'HEADLESS_NOT_AVAILABLE',
            message: 'Headless API недоступен. Проверьте VITE_BFF_ENABLED и развертывание BFF.',
            details: { url: error.config?.url }
          }
          return Promise.reject(apiError)
        }

        // Retry logic for network errors, 5xx, and 429 (rate limit)
        if (shouldRetry(error) && config && !config._retry) {
          config._retry = true
          config._retryCount = (config._retryCount || 0) + 1

          // Use different max retries for rate limit errors
          const maxRetries = error.response?.status === 429 ? MAX_RETRIES_RATE_LIMIT : MAX_RETRIES

          if (config._retryCount <= maxRetries) {
            // For 429 errors, use retry_after from response if available
            let delayMs = RETRY_DELAY * Math.pow(2, config._retryCount - 1)
            
            if (error.response?.status === 429) {
              // Try to get retry_after from response header or body
              const retryAfterHeader = error.response.headers['retry-after']
              const retryAfterBody = (error.response.data as any)?.retry_after
              
              if (retryAfterHeader) {
                // retry-after can be in seconds (string or number)
                const retryAfterSeconds = typeof retryAfterHeader === 'string' 
                  ? parseInt(retryAfterHeader, 10) 
                  : retryAfterHeader
                delayMs = Math.max(retryAfterSeconds * 1000, 1000) // Minimum 1 second
              } else if (retryAfterBody !== undefined && retryAfterBody !== null) {
                // retry_after from body can be number or string
                const retryAfterSeconds = typeof retryAfterBody === 'string'
                  ? parseInt(retryAfterBody, 10)
                  : retryAfterBody
                delayMs = Math.max(retryAfterSeconds * 1000, 1000) // Minimum 1 second
              } else {
                // Default to longer delay for rate limits with exponential backoff
                delayMs = 2000 * Math.pow(2, config._retryCount - 1)
              }
              
              if (import.meta.env.DEV) {
                console.log(
                  `[API Rate Limit] Waiting ${delayMs}ms before retry ${config._retryCount}/${maxRetries} for ${config.url}`
                )
              }
            } else {
              // Exponential backoff for other errors
              if (import.meta.env.DEV) {
                console.log(
                  `[API Retry] Attempt ${config._retryCount}/${maxRetries} for ${config.url}`
                )
              }
            }
            
            await delay(delayMs)

            return this.client.request(config)
          } else {
            // Max retries exceeded
            if (import.meta.env.DEV && error.response?.status === 429) {
              console.warn(
                `[API Rate Limit] Max retries (${maxRetries}) exceeded for ${config.url}`
              )
            }
          }
        }

        // Handle structured errors
        const errorData: any = error.response?.data
        if (errorData?.error) {
          const apiError: ApiError = {
            code: errorData.error.code || 'UNKNOWN_ERROR',
            message: errorData.error.message || 'Произошла ошибка',
            details: errorData.error.details
          }
          return Promise.reject(apiError)
        }

        // Handle network errors
        if (!error.response) {
          const apiError: ApiError = {
            code: 'NETWORK_ERROR',
            message: 'Ошибка сети. Проверьте подключение к интернету.',
            details: { originalError: error.message }
          }
          return Promise.reject(apiError)
        }

        // Handle 500 errors
        if (error.response.status >= 500) {
          const apiError: ApiError = {
            code: 'SERVER_ERROR',
            message: 'Ошибка сервера. Попробуйте позже.',
            details: { status: error.response.status }
          }
          return Promise.reject(apiError)
        }

        return Promise.reject(error)
      }
    )
  }

  /**
   * GET request with optional caching
   */
  async get<T>(
    url: string,
    config?: InternalAxiosRequestConfig,
    useCache = true
  ): Promise<T> {
    // Check cache for GET requests
    if (useCache && config?.method === undefined) {
      const cacheKey = this.getCacheKey(url, config?.params)
      const cached = cacheService.get<T>(cacheKey)
      if (cached !== null) {
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'H-cache',
            location: 'services/apiService.ts:285',
            message: 'Frontend: API cache hit (GET)',
            data: {
              url,
              cacheKey,
              config_has_params: !!(config as any)?.params,
              config_params: (config as any)?.params || null,
              config_keys: config ? Object.keys(config as any) : []
            },
            timestamp: Date.now()
          })
        }).catch(() => {})
        // #endregion
        if (import.meta.env.DEV) {
          console.log(`[API Cache Hit] ${url}`)
        }
        return cached
      }
    }

    if (import.meta.env.DEV) {
      console.log(`[API Request] GET ${url}`, { config, useCache })
    }

    try {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/e2a91df7-36f3-4ec3-8d36-7745f17b1cac', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: 'debug-session',
          runId: 'run1',
          hypothesisId: 'H-params',
          location: 'services/apiService.ts:309',
          message: 'Frontend: API GET about to request via axios',
          data: {
            url,
            useCache,
            config_has_params: !!(config as any)?.params,
            config_params: (config as any)?.params || null,
            config_keys: config ? Object.keys(config as any) : []
          },
          timestamp: Date.now()
        })
      }).catch(() => {})
      // #endregion
      const response = await this.client.get<ApiResponse<T>>(url, config)
      
      if (import.meta.env.DEV) {
        console.log(`[API Response] GET ${url}`, {
          status: response.status,
          statusText: response.statusText,
          hasData: !!response.data,
          dataKeys: response.data ? Object.keys(response.data) : [],
          dataType: typeof response.data,
          isDataArray: Array.isArray(response.data),
          rawData: response.data
        })
      }
      
      const data = response.data.data || (response.data as unknown as T)
      
      if (import.meta.env.DEV) {
        console.log(`[API Processed] GET ${url}`, {
          extractedData: data,
          dataType: typeof data,
          isDataArray: Array.isArray(data),
          hasDataField: 'data' in (response.data || {}),
          usedFallback: !response.data.data
        })
      }

      // Cache GET responses
      if (useCache && config?.method === undefined) {
        const cacheKey = this.getCacheKey(url, config?.params)
        cacheService.set(cacheKey, data)
      }

      return data
    } catch (error: any) {
      if (import.meta.env.DEV) {
        console.error(`[API Error] GET ${url}`, {
          error,
          message: error?.message,
          response: error?.response,
          status: error?.response?.status,
          statusText: error?.response?.statusText,
          data: error?.response?.data,
          config: error?.config
        })
      }
      throw error
    }
  }

  /**
   * POST request
   */
  async post<T>(
    url: string,
    data?: unknown,
    config?: InternalAxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config)
    return response.data.data || (response.data as unknown as T)
  }

  /**
   * PUT request
   */
  async put<T>(
    url: string,
    data?: unknown,
    config?: InternalAxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config)
    return response.data.data || (response.data as unknown as T)
  }

  /**
   * PATCH request
   */
  async patch<T>(
    url: string,
    data?: unknown,
    config?: InternalAxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.patch<ApiResponse<T>>(url, data, config)
    return response.data.data || (response.data as unknown as T)
  }

  /**
   * DELETE request
   */
  async delete<T>(url: string, config?: InternalAxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url, config)
    return response.data.data || (response.data as unknown as T)
  }

  /**
   * Generate cache key from URL and params
   */
  private getCacheKey(url: string, params?: unknown): string {
    if (!params) {
      return url
    }
    const paramsStr = JSON.stringify(params)
    return `${url}?${paramsStr}`
  }

  /**
   * Get CSRF token from cookies or meta tag
   */
  private getCSRFToken(): string | null {
    // Try cookie first
    const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/)
    if (cookieMatch) return cookieMatch[1] ?? null

    // Fallback to meta tag
    return document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content || null
  }

  /**
   * Clear cache for specific URL pattern
   */
  clearCache(pattern?: string): void {
    if (pattern) {
      // Clear specific cache entries matching pattern
      // This is a simple implementation - can be enhanced
      cacheService.clear()
    } else {
      cacheService.clear()
    }
  }
}

export const apiService = new ApiService()
