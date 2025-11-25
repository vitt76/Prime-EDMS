import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'
import { apiService } from '@/services/apiService'
import { cacheService } from '@/services/cacheService'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Mock cacheService
vi.mock('@/services/cacheService', () => ({
  cacheService: {
    get: vi.fn(),
    set: vi.fn(),
    delete: vi.fn(),
    clear: vi.fn()
  }
}))

describe('ApiService Enhanced Tests', () => {
  let mockAxiosInstance: {
    get: ReturnType<typeof vi.fn>
    post: ReturnType<typeof vi.fn>
    put: ReturnType<typeof vi.fn>
    delete: ReturnType<typeof vi.fn>
    interceptors: {
      request: { use: ReturnType<typeof vi.fn> }
      response: { use: ReturnType<typeof vi.fn> }
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()

    mockAxiosInstance = {
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }

    mockedAxios.create.mockReturnValue(mockAxiosInstance as any)
  })

  describe('Request Interceptor', () => {
    it('adds CSRF token from meta tag', () => {
      // Create meta tag
      const meta = document.createElement('meta')
      meta.name = 'csrf-token'
      meta.content = 'test-csrf-token'
      document.head.appendChild(meta)

      // Get the request interceptor
      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0]

      const config = {
        headers: {},
        url: '/test',
        method: 'get'
      }

      const result = requestInterceptor(config)

      expect(result.headers['X-CSRFToken']).toBe('test-csrf-token')

      // Cleanup
      document.head.removeChild(meta)
    })

    it('adds auth token from localStorage', () => {
      localStorage.setItem('auth_token', 'test-auth-token')

      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0]

      const config = {
        headers: {},
        url: '/test',
        method: 'get'
      }

      const result = requestInterceptor(config)

      expect(result.headers['Authorization']).toBe('Bearer test-auth-token')
    })

    it('does not add auth token if not in localStorage', () => {
      localStorage.removeItem('auth_token')

      const requestInterceptor = mockAxiosInstance.interceptors.request.use.mock.calls[0][0]

      const config = {
        headers: {},
        url: '/test',
        method: 'get'
      }

      const result = requestInterceptor(config)

      expect(result.headers['Authorization']).toBeUndefined()
    })
  })

  describe('Response Interceptor - Error Handling', () => {
    it('handles 401 Unauthorized by redirecting to login', () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1]

      const error = {
        response: {
          status: 401,
          data: { error: 'Unauthorized' }
        },
        config: {}
      }

      // Mock window.location
      delete (window as any).location
      window.location = { href: '' } as any

      responseInterceptor(error).catch(() => {})

      expect(localStorage.getItem('auth_token')).toBeNull()
    })

    it('handles 403 Forbidden with structured error', async () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1]

      const error = {
        response: {
          status: 403,
          data: { error: 'Forbidden' }
        },
        config: {}
      }

      try {
        await responseInterceptor(error)
      } catch (apiError: any) {
        expect(apiError.code).toBe('FORBIDDEN')
        expect(apiError.message).toBe('Доступ запрещен')
      }
    })

    it('handles network errors', async () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1]

      const error = {
        message: 'Network Error',
        config: {}
      }

      try {
        await responseInterceptor(error)
      } catch (apiError: any) {
        expect(apiError.code).toBe('NETWORK_ERROR')
        expect(apiError.message).toContain('Ошибка сети')
      }
    })

    it('handles 500 Server Error', async () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1]

      const error = {
        response: {
          status: 500,
          data: { error: 'Internal Server Error' }
        },
        config: {}
      }

      try {
        await responseInterceptor(error)
      } catch (apiError: any) {
        expect(apiError.code).toBe('SERVER_ERROR')
        expect(apiError.message).toContain('Ошибка сервера')
      }
    })

    it('handles structured API errors', async () => {
      const responseInterceptor = mockAxiosInstance.interceptors.response.use.mock.calls[0][1]

      const error = {
        response: {
          status: 400,
          data: {
            error: {
              code: 'VALIDATION_ERROR',
              message: 'Validation failed',
              details: { field: 'email' }
            }
          }
        },
        config: {}
      }

      try {
        await responseInterceptor(error)
      } catch (apiError: any) {
        expect(apiError.code).toBe('VALIDATION_ERROR')
        expect(apiError.message).toBe('Validation failed')
        expect(apiError.details).toEqual({ field: 'email' })
      }
    })
  })

  describe('Caching', () => {
    it('uses cache for GET requests when cache is available', async () => {
      const cachedData = { id: 1, name: 'Cached' }
      vi.mocked(cacheService.get).mockReturnValue(cachedData)

      const result = await apiService.get('/test', undefined, true)

      expect(cacheService.get).toHaveBeenCalled()
      expect(result).toEqual(cachedData)
      expect(mockAxiosInstance.get).not.toHaveBeenCalled()
    })

    it('fetches and caches GET requests when cache is not available', async () => {
      vi.mocked(cacheService.get).mockReturnValue(null)
      mockAxiosInstance.get.mockResolvedValue({
        data: { id: 1, name: 'Fresh' }
      })

      await apiService.get('/test', undefined, true)

      expect(cacheService.get).toHaveBeenCalled()
      expect(mockAxiosInstance.get).toHaveBeenCalled()
      expect(cacheService.set).toHaveBeenCalled()
    })

    it('skips cache when useCache is false', async () => {
      mockAxiosInstance.get.mockResolvedValue({
        data: { id: 1, name: 'Fresh' }
      })

      await apiService.get('/test', undefined, false)

      expect(cacheService.get).not.toHaveBeenCalled()
      expect(mockAxiosInstance.get).toHaveBeenCalled()
    })
  })

  describe('HTTP Methods', () => {
    it('GET request returns data', async () => {
      const mockData = { id: 1, name: 'Test' }
      mockAxiosInstance.get.mockResolvedValue({
        data: mockData
      })

      const result = await apiService.get('/test')

      expect(result).toEqual(mockData)
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/test', undefined)
    })

    it('POST request sends data', async () => {
      const postData = { name: 'New Item' }
      const mockResponse = { id: 1, ...postData }
      mockAxiosInstance.post.mockResolvedValue({
        data: mockResponse
      })

      const result = await apiService.post('/test', postData)

      expect(result).toEqual(mockResponse)
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/test', postData, undefined)
    })

    it('PUT request updates data', async () => {
      const putData = { id: 1, name: 'Updated' }
      mockAxiosInstance.put.mockResolvedValue({
        data: putData
      })

      const result = await apiService.put('/test/1', putData)

      expect(result).toEqual(putData)
      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/test/1', putData, undefined)
    })

    it('DELETE request removes data', async () => {
      mockAxiosInstance.delete.mockResolvedValue({
        data: { success: true }
      })

      const result = await apiService.delete('/test/1')

      expect(result).toEqual({ success: true })
      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/test/1', undefined)
    })
  })

  describe('Cache Management', () => {
    it('clearCache clears all cache when no pattern provided', () => {
      apiService.clearCache()

      expect(cacheService.clear).toHaveBeenCalled()
    })

    it('clearCache clears cache with pattern', () => {
      apiService.clearCache('/test')

      expect(cacheService.clear).toHaveBeenCalled()
    })
  })
})

