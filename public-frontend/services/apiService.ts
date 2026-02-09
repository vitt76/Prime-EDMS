import { API_ENDPOINTS } from '~/utils/constants'
import type { PublicPage, PublicPlan, PublicPost } from '~/types/content'

/** Paginated response shape returned by DRF */
interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export class ApiService {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  private async fetch<T>(url: string, options?: RequestInit & { params?: Record<string, any> }): Promise<T> {
    try {
      return await $fetch<T>(url, { baseURL: this.baseURL, ...options })
    } catch (error: any) {
      // Log concisely — avoid spamming the console when backend is unavailable
      if (error?.message?.includes('Failed to fetch') || error?.message?.includes('fetch failed')) {
        console.warn(`[API] Backend unavailable: ${url}`)
      } else {
        console.error('[API] Error:', error?.statusCode || error?.message || error)
      }
      throw this.handleError(error)
    }
  }

  private handleError(error: any) {
    if (error?.statusCode === 404) {
      return new Error('Resource not found')
    }
    if (error?.statusCode >= 500) {
      return new Error('Server error, please try again later')
    }
    return error
  }

  async getPage(slug: string, lang: string = 'ru'): Promise<PublicPage> {
    return this.fetch<PublicPage>(`${API_ENDPOINTS.PAGES}/${slug}/`, {
      params: { lang }
    })
  }

  async getPosts(params: { page?: number; limit?: number; search?: string; lang?: string; category?: string }) {
    return this.fetch(`${API_ENDPOINTS.POSTS}/`, { params })
  }

  async getPost(slug: string, lang: string = 'ru'): Promise<PublicPost> {
    return this.fetch<PublicPost>(`${API_ENDPOINTS.POSTS}/${slug}/`, {
      params: { lang }
    })
  }

  async getPlans(lang: string = 'ru'): Promise<PublicPlan[]> {
    const response = await this.fetch<PublicPlan[] | PaginatedResponse<PublicPlan>>(
      `${API_ENDPOINTS.PLANS}/`,
      { params: { lang } }
    )

    // Normalize: backend may return a paginated object {count, next, previous, results}
    // or a plain array — handle both cases gracefully
    if (Array.isArray(response)) {
      return response
    }
    if (response && typeof response === 'object' && 'results' in response) {
      return (response as PaginatedResponse<PublicPlan>).results
    }
    return []
  }

  async getFaq(params?: Record<string, any>) {
    return this.fetch(`${API_ENDPOINTS.FAQ}/`, {
      params
    })
  }

  async submitLead(data: Record<string, any>) {
    return this.fetch(`${API_ENDPOINTS.LEADS}/`, {
      method: 'POST',
      body: data
    })
  }

  async subscribeNewsletter(email: string) {
    return this.fetch(`${API_ENDPOINTS.NEWSLETTER}/`, {
      method: 'POST',
      body: { email }
    })
  }

  async register(payload: Record<string, any>) {
    return this.fetch(`${API_ENDPOINTS.AUTH.REGISTER}/`, {
      method: 'POST',
      body: payload
    })
  }

  async verifyEmail(payload: Record<string, any>) {
    return this.fetch(`${API_ENDPOINTS.AUTH.VERIFY}/`, {
      method: 'POST',
      body: payload
    })
  }
}

export const createApiService = (baseURL: string) => new ApiService(baseURL)
