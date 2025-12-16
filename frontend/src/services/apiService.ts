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
const RETRY_DELAY = 1000 // 1 second

const shouldDebugLog = (): boolean => {
  try {
    return import.meta.env.DEV && localStorage.getItem('maddam_debug') === '1'
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
  return status >= 500 && status < 600
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
          // Clear token and redirect to login
          clearToken()
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login'
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

        // Retry logic for network errors and 5xx
        if (shouldRetry(error) && config && !config._retry) {
          config._retry = true
          config._retryCount = (config._retryCount || 0) + 1

          if (config._retryCount <= MAX_RETRIES) {
            // Exponential backoff
            const delayMs = RETRY_DELAY * Math.pow(2, config._retryCount - 1)
            await delay(delayMs)

            if (import.meta.env.DEV) {
              console.log(
                `[API Retry] Attempt ${config._retryCount}/${MAX_RETRIES} for ${config.url}`
              )
            }

            return this.client.request(config)
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
        if (import.meta.env.DEV) {
          console.log(`[API Cache Hit] ${url}`)
        }
        return cached
      }
    }

    const response = await this.client.get<ApiResponse<T>>(url, config)
    const data = response.data.data || (response.data as unknown as T)

    // Cache GET responses
    if (useCache && config?.method === undefined) {
      const cacheKey = this.getCacheKey(url, config?.params)
      cacheService.set(cacheKey, data)
    }

    return data
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
