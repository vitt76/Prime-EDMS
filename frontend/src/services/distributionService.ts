import { apiService } from './apiService'
import type {
  Publication,
  CreatePublicationRequest,
  UpdatePublicationRequest,
  PaginatedResponse,
  ShareLink,
  PublicationAnalytics
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

    const searchParams = new URLSearchParams()
    Object.entries(queryParams).forEach(([key, value]) => {
      searchParams.append(key, String(value))
    })

    const endpoint =
      searchParams.toString().length > 0
        ? `/v4/distribution/publications/?${searchParams}`
        : '/v4/distribution/publications/'

    return apiService.get<PaginatedResponse<Publication>>(endpoint, undefined, false)
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

  /**
   * Get analytics for a publication
   */
  async getPublicationAnalytics(publicationId: number): Promise<PublicationAnalytics> {
    return apiService.get<PublicationAnalytics>(
      `/v4/distribution/publications/${publicationId}/analytics/`,
      undefined,
      true // Cache analytics for 5 minutes
    )
  }

  /**
   * Get public publication using token (portal access)
   */
  async getPublicationByToken(token: string): Promise<Publication> {
    return apiService.get<Publication>(
      `/v4/distribution/publications/portal/${token}/`,
      undefined,
      false
    )
  }

  /**
   * Track a view for the public publication
   */
  async trackPublicView(token: string): Promise<void> {
    await apiService.post<void>(
      `/v4/distribution/publications/portal/${token}/events/`,
      { event: 'view' }
    )
  }

  /**
   * Track a download for a public asset
   */
  async trackPublicDownload(token: string, assetId?: number): Promise<void> {
    await apiService.post<void>(
      `/v4/distribution/publications/portal/${token}/events/`,
      {
        event: 'download',
        asset_id: assetId
      }
    )
  }
}

export const distributionService = new DistributionService()

