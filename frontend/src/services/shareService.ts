/**
 * Share Service
 *
 * Handles sharing operations for assets and collections including
 * link generation, permissions management, and access control.
 */

import { apiService } from './apiService'
import { withRetry } from '@/utils/retry'

export interface SharePermissions {
  view: boolean
  download: boolean
  edit: boolean
  share?: boolean
}

export interface ShareConfig {
  permissions: SharePermissions
  expiration?: Date
  password?: string
  recipients: string[]
  isPublic: boolean
  maxViews?: number
  allowComments?: boolean
  watermarkText?: string
}

export interface ShareLink {
  id: string
  share_url: string
  short_code?: string
  created_at: string
  expires_at?: string
  last_accessed_at?: string
  access_count: number
  max_views?: number
  is_active: boolean
  is_password_protected: boolean
  permissions: SharePermissions
  creator: {
    id: string
    name: string
    email: string
  }
  assets?: Array<{
    id: string
    name: string
    type: string
  }>
  collection?: {
    id: string
    name: string
  }
}

export interface CreateShareRequest extends ShareConfig {
  asset_ids?: string[]
  collection_id?: string
  title?: string
  description?: string
}

export interface BulkShareRequest extends ShareConfig {
  asset_ids: string[]
  collection_id?: string
  title?: string
  description?: string
}

export interface ShareAnalytics {
  total_views: number
  unique_visitors: number
  downloads: number
  shares: number
  bounce_rate: number
  avg_session_duration: number
  top_referrers: Array<{
    source: string
    count: number
  }>
  geographic_data: Array<{
    country: string
    views: number
  }>
  device_types: Array<{
    type: string
    count: number
  }>
  time_series: Array<{
    date: string
    views: number
    downloads: number
  }>
}

class ShareService {
  /**
   * Create share link for individual asset
   */
  async createAssetShare(assetId: string, config: ShareConfig): Promise<ShareLink> {
    const operation = () => apiService.post<ShareLink>(`/v4/assets/${assetId}/share/`, config)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Create share link for collection
   */
  async createCollectionShare(collectionId: string, config: ShareConfig): Promise<ShareLink> {
    const operation = () => apiService.post<ShareLink>(`/v4/collections/${collectionId}/share/`, config)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Create bulk share for multiple assets
   */
  async createBulkShare(assetIds: string[], config: ShareConfig): Promise<ShareLink> {
    const operation = () => apiService.post<ShareLink>('/v4/shares/bulk/', {
      asset_ids: assetIds,
      ...config
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get all share links for current user
   */
  async getUserShares(options: {
    limit?: number
    offset?: number
    asset_id?: string
    collection_id?: string
    is_active?: boolean
    sort_by?: 'created_at' | 'last_accessed' | 'access_count'
    sort_order?: 'asc' | 'desc'
  } = {}): Promise<ShareLink[]> {
    const operation = () => apiService.get<ShareLink[]>('/v4/shares/', { params: options })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get share link details
   */
  async getShareDetails(shareId: string): Promise<ShareLink> {
    const operation = () => apiService.get<ShareLink>(`/v4/shares/${shareId}/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Update share link configuration
   */
  async updateShare(shareId: string, updates: Partial<ShareConfig>): Promise<ShareLink> {
    const operation = () => apiService.patch<ShareLink>(`/v4/shares/${shareId}/`, updates)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Revoke/delete share link
   */
  async revokeShare(shareId: string): Promise<void> {
    const operation = () => apiService.delete(`/v4/shares/${shareId}/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Bulk revoke multiple share links
   */
  async bulkRevokeShares(shareIds: string[]): Promise<void> {
    const operation = () => apiService.post('/v4/shares/bulk/revoke/', {
      share_ids: shareIds
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Get share analytics
   */
  async getShareAnalytics(shareId: string, dateRange?: {
    start_date: string
    end_date: string
  }): Promise<ShareAnalytics> {
    const operation = () => apiService.get<ShareAnalytics>(`/v4/shares/${shareId}/analytics/`, {
      params: dateRange
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Validate share password
   */
  async validateSharePassword(shareId: string, password: string): Promise<boolean> {
    const operation = () => apiService.post<{ valid: boolean }>(`/v4/shares/${shareId}/validate-password/`, {
      password
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!.valid
  }

  /**
   * Access shared content (for public shares)
   */
  async accessShare(shareId: string, password?: string): Promise<{
    share: ShareLink
    assets?: any[]
    collection?: any
    can_download: boolean
    can_edit: boolean
  }> {
    const operation = () => apiService.post(`/v4/shares/${shareId}/access/`, {
      password
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Download shared assets
   */
  async downloadSharedAssets(shareId: string, assetIds?: string[], format: 'zip' | 'individual' = 'zip'): Promise<string> {
    const operation = () => apiService.post<{ download_url: string }>(`/v4/shares/${shareId}/download/`, {
      asset_ids: assetIds,
      format
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!.download_url
  }

  /**
   * Add recipients to existing share
   */
  async addShareRecipients(shareId: string, recipients: string[]): Promise<ShareLink> {
    const operation = () => apiService.post<ShareLink>(`/v4/shares/${shareId}/recipients/`, {
      recipients
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Remove recipients from share
   */
  async removeShareRecipients(shareId: string, recipients: string[]): Promise<ShareLink> {
    const operation = () => apiService.delete(`/v4/shares/${shareId}/recipients/`, {
      data: { recipients }
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Generate share preview (for creator to see what recipients will see)
   */
  async generateSharePreview(shareId: string): Promise<{
    title: string
    description?: string
    thumbnail_urls: string[]
    asset_count: number
    total_size: string
    permissions: SharePermissions
    expires_at?: string
  }> {
    const operation = () => apiService.get(`/v4/shares/${shareId}/preview/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Check if share link is still valid
   */
  async validateShareLink(shareId: string): Promise<{
    is_valid: boolean
    reason?: 'expired' | 'revoked' | 'max_views_reached' | 'not_found'
    expires_at?: string
    views_remaining?: number
  }> {
    const operation = () => apiService.get(`/v4/shares/${shareId}/validate/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Extend share expiration
   */
  async extendShareExpiration(shareId: string, newExpiration: Date): Promise<ShareLink> {
    const operation = () => apiService.post<ShareLink>(`/v4/shares/${shareId}/extend/`, {
      expires_at: newExpiration.toISOString()
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get share activity log
   */
  async getShareActivityLog(shareId: string, options: {
    limit?: number
    offset?: number
    action?: 'view' | 'download' | 'share'
  } = {}): Promise<Array<{
    id: string
    timestamp: string
    action: 'view' | 'download' | 'share'
    user_agent?: string
    ip_address?: string
    location?: {
      country: string
      city: string
    }
    recipient_email?: string
  }>> {
    const operation = () => apiService.get(`/v4/shares/${shareId}/activity/`, {
      params: options
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Create share from template
   */
  async createShareFromTemplate(templateId: string, target: {
    asset_ids?: string[]
    collection_id?: string
  }): Promise<ShareLink> {
    const operation = () => apiService.post<ShareLink>('/v4/shares/from-template/', {
      template_id: templateId,
      ...target
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get share templates
   */
  async getShareTemplates(): Promise<Array<{
    id: string
    name: string
    description?: string
    config: ShareConfig
    created_by: string
    is_public: boolean
    usage_count: number
  }>> {
    const operation = () => apiService.get('/v4/shares/templates/')
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Create share template
   */
  async createShareTemplate(data: {
    name: string
    description?: string
    config: ShareConfig
    is_public?: boolean
  }): Promise<any> {
    const operation = () => apiService.post('/v4/shares/templates/', data)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Export share report
   */
  async exportShareReport(shareId: string, format: 'pdf' | 'csv' | 'json' = 'pdf'): Promise<string> {
    const operation = () => apiService.post<{ download_url: string }>(`/v4/shares/${shareId}/export-report/`, {
      format
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!.download_url
  }
}

export const shareService = new ShareService()