import { apiService } from './apiService'
import type {
  Publication,
  CreatePublicationRequest,
  UpdatePublicationRequest,
  PaginatedResponse,
  ShareLink
} from '@/types/api'

class DistributionService {
  /**
   * Get paginated list of publications
   */
  async getPublications(params?: {
    page?: number
    page_size?: number
    status?: Publication['status']
    search?: string
  }): Promise<PaginatedResponse<Publication>> {
    const queryParams: Record<string, string | number> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.status) {
      queryParams.status = params.status
    }
    if (params?.search) {
      queryParams.search = params.search
    }

    return apiService.get<PaginatedResponse<Publication>>(
      '/v4/distribution/publications/',
      { params: queryParams },
      false // Don't cache publication lists
    )
  }

  /**
   * Get single publication by ID
   */
  async getPublication(id: number): Promise<Publication> {
    return apiService.get<Publication>(
      `/v4/distribution/publications/${id}/`,
      undefined,
      true // Cache publication details for 5 minutes
    )
  }

  /**
   * Create a new publication
   */
  async createPublication(
    publication: CreatePublicationRequest
  ): Promise<Publication> {
    return apiService.post<Publication>(
      '/v4/distribution/publications/',
      publication
    )
  }

  /**
   * Update an existing publication
   */
  async updatePublication(
    id: number,
    publication: UpdatePublicationRequest
  ): Promise<Publication> {
    return apiService.put<Publication>(
      `/v4/distribution/publications/${id}/`,
      publication
    )
  }

  /**
   * Delete a publication
   */
  async deletePublication(id: number): Promise<void> {
    return apiService.delete<void>(`/v4/distribution/publications/${id}/`)
  }

  /**
   * Publish a publication
   */
  async publishPublication(id: number): Promise<Publication> {
    return apiService.post<Publication>(
      `/v4/distribution/publications/${id}/publish/`
    )
  }

  /**
   * Get share links for a publication
   */
  async getShareLinks(publicationId: number): Promise<ShareLink[]> {
    const response = await apiService.get<PaginatedResponse<ShareLink>>(
      `/v4/distribution/publications/${publicationId}/links/`
    )
    return response.results || []
  }

  /**
   * Create a share link for a publication
   */
  async createShareLink(
    publicationId: number,
    options?: {
      expires_at?: string
      password?: string
      permissions?: {
        view: boolean
        download: boolean
      }
    }
  ): Promise<ShareLink> {
    return apiService.post<ShareLink>(
      `/v4/distribution/publications/${publicationId}/links/`,
      options
    )
  }

  /**
   * Delete a share link
   */
  async deleteShareLink(
    publicationId: number,
    linkId: number
  ): Promise<void> {
    return apiService.delete<void>(
      `/v4/distribution/publications/${publicationId}/links/${linkId}/`
    )
  }

  /**
   * Get available channels
   */
  async getChannels(): Promise<Publication['channels']> {
    const response = await apiService.get<PaginatedResponse<Publication['channels'][0]>>(
      '/v4/distribution/channels/'
    )
    return response.results || []
  }
}

export const distributionService = new DistributionService()

