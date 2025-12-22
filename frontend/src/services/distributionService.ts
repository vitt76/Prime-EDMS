import { apiService } from './apiService'
import type {
  Publication,
  CreatePublicationRequest,
  UpdatePublicationRequest,
  PaginatedResponse,
  ShareLink,
  PublicationAnalytics,
  DistributionCampaign,
  CreateCampaignRequest
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
        ? `/api/v4/distribution/publications/?${searchParams}`
        : '/api/v4/distribution/publications/'

    return apiService.get<PaginatedResponse<Publication>>(endpoint, undefined, false)
  }

  /**
   * Get single publication by ID
   */
  async getPublication(id: number): Promise<Publication> {
    return apiService.get<Publication>(
      `/api/v4/distribution/publications/${id}/`,
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
      '/api/v4/distribution/publications/',
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
      `/api/v4/distribution/publications/${id}/`,
      publication
    )
  }

  /**
   * Delete a publication
   */
  async deletePublication(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v4/distribution/publications/${id}/`)
  }

  /**
   * Publish a publication
   */
  async publishPublication(id: number): Promise<Publication> {
    return apiService.post<Publication>(
      `/api/v4/distribution/publications/${id}/publish/`
    )
  }

  /**
   * Get all share links (for current user)
   */
  async getAllShareLinks(params?: {
    page?: number
    page_size?: number
  }): Promise<PaginatedResponse<any>> {
    const queryParams: Record<string, string | number> = {}
    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }

    const searchParams = new URLSearchParams()
    Object.entries(queryParams).forEach(([key, value]) => {
      searchParams.append(key, String(value))
    })

    const endpoint =
      searchParams.toString().length > 0
        ? `/api/v4/distribution/share_links/?${searchParams}`
        : '/api/v4/distribution/share_links/'

    console.log('[DistributionService] Calling API:', endpoint)
    const response = await apiService.get<PaginatedResponse<any>>(endpoint, undefined, false)
    console.log('[DistributionService] API response received:', {
      count: response.count,
      resultsLength: response.results?.length || 0
    })
    return response
  }

  /**
   * Get single share link by ID
   */
  async getShareLinkById(id: number): Promise<any> {
    return apiService.get<any>(`/api/v4/distribution/share_links/${id}/`, undefined, false)
  }

  /**
   * Create a new share link (requires rendition_id)
   */
  async createShareLink(data: {
    rendition: number
    expires_at?: string | null
    max_downloads?: number | null
  }): Promise<any> {
    return apiService.post<any>('/api/v4/distribution/share_links/', data)
  }

  /**
   * Create a share link directly from document files (simplified)
   * This automatically creates publication, adds files, generates renditions, and creates share link
   */
  async createShareLinkSimple(data: {
    document_file_ids: number[]
    title?: string
    expires_at?: string | null
    max_downloads?: number | null
    preset_id?: number
  }): Promise<any> {
    return apiService.post<any>('/api/v4/distribution/share_links/create_simple/', data)
  }

  /**
   * Update a share link
   */
  async updateShareLink(id: number, data: {
    expires_at?: string | null
    max_downloads?: number | null
  }): Promise<any> {
    return apiService.patch<any>(`/api/v4/distribution/share_links/${id}/`, data)
  }

  /**
   * Delete (revoke) a share link
   */
  async deleteShareLink(id: number): Promise<void> {
    return apiService.delete<void>(`/api/v4/distribution/share_links/${id}/`)
  }

  /**
   * Get share links for a publication
   */
  async getShareLinks(publicationId: number): Promise<ShareLink[]> {
    const response = await apiService.get<PaginatedResponse<ShareLink>>(
      `/api/v4/distribution/publications/${publicationId}/links/`
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
      `/api/v4/distribution/publications/${publicationId}/links/`,
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
      `/api/v4/distribution/publications/${publicationId}/links/${linkId}/`
    )
  }

  /**
   * Get available channels
   */
  async getChannels(): Promise<Publication['channels']> {
    const response = await apiService.get<PaginatedResponse<Publication['channels'][0]>>(
      '/api/v4/distribution/channels/'
    )
    return response.results || []
  }

  /**
   * Get analytics for a publication
   */
  async getPublicationAnalytics(publicationId: number): Promise<PublicationAnalytics> {
    return apiService.get<PublicationAnalytics>(
      `/api/v4/distribution/publications/${publicationId}/analytics/`,
      undefined,
      true // Cache analytics for 5 minutes
    )
  }

  /**
   * Get public publication using token (portal access)
   */
  async getPublicationByToken(token: string): Promise<Publication> {
    return apiService.get<Publication>(
      `/api/v4/distribution/publications/portal/${token}/`,
      undefined,
      false
    )
  }

  /**
   * Track a view for the public publication
   */
  async trackPublicView(token: string): Promise<void> {
    await apiService.post<void>(
      `/api/v4/distribution/publications/portal/${token}/events/`,
      { event: 'view' }
    )
  }

  /**
   * Track a download for a public asset
   */
  async trackPublicDownload(token: string, assetId?: number): Promise<void> {
    await apiService.post<void>(
      `/api/v4/distribution/publications/portal/${token}/events/`,
      {
        event: 'download',
        asset_id: assetId
      }
    )
  }

  /**
   * Get list of distribution campaigns for current user
   */
  async getCampaigns(params?: {
    page?: number
    page_size?: number
    state?: DistributionCampaign['state'] | 'all'
    search?: string
  }): Promise<PaginatedResponse<DistributionCampaign>> {
    const queryParams: Record<string, string | number> = {}

    if (params?.page) {
      queryParams.page = params.page
    }
    if (params?.page_size) {
      queryParams.page_size = params.page_size
    }
    if (params?.state && params.state !== 'all') {
      queryParams.state = params.state
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
        ? `/api/v4/distribution/campaigns/?${searchParams}`
        : '/api/v4/distribution/campaigns/'

    return apiService.get<PaginatedResponse<DistributionCampaign>>(endpoint, undefined, false)
  }

  /**
   * Get single distribution campaign by ID
   */
  async getCampaign(id: number): Promise<DistributionCampaign> {
    return apiService.get<DistributionCampaign>(
      `/api/v4/distribution/campaigns/${id}/`,
      undefined,
      false
    )
  }

  /**
   * Create a distribution campaign
   */
  async createCampaign(payload: CreateCampaignRequest): Promise<DistributionCampaign> {
    return apiService.post<DistributionCampaign>(
      '/api/v4/distribution/campaigns/',
      payload
    )
  }
}

export const distributionService = new DistributionService()

