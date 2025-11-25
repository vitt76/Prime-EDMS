import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { ApiResponse, ApiError } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Add CSRF token
        const csrfToken = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content
        if (csrfToken && config.headers) {
          config.headers['X-CSRFToken'] = csrfToken
        }

        // Add auth token
        const token = localStorage.getItem('auth_token')
        if (token && config.headers) {
          config.headers['Authorization'] = `Bearer ${token}`
        }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ApiError>) => {
        if (error.response?.status === 401) {
          // Token expired, redirect to login
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
          return Promise.reject(error)
        }

        // Handle structured errors
        if (error.response?.data?.error) {
          const apiError: ApiError = {
            code: error.response.data.error.code || 'UNKNOWN_ERROR',
            message: error.response.data.error.message || 'An error occurred',
            details: error.response.data.error.details
          }
          return Promise.reject(apiError)
        }

        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: InternalAxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.get<ApiResponse<T>>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: unknown, config?: InternalAxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: unknown, config?: InternalAxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: InternalAxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.delete<ApiResponse<T>>(url, config)
    return response.data
  }
}

export const apiService = new ApiService()


