/**
 * Adapter for converting API ShareLink format to Vue SharedLink format
 */

import type { SharedLink } from '@/stores/distributionStore'

/**
 * API ShareLink format (from backend)
 */
export interface APIShareLink {
  id: number
  rendition: number
  token: string
  recipient: number | null
  expires_at: string | null
  max_downloads: number | null
  downloads_count: number
  views_count: number
  max_views: number | null
  password_hash?: string | null
  allow_download: boolean
  unique_visitors_count?: number
  password_protected?: boolean
  created: string
  last_accessed: string | null
  // Extended fields from serializer
  publication_title?: string | null
  publication_id?: number | null
  rendition_preset_name?: string | null
  rendition_preset_format?: string | null
  document_file_id?: number | null
  document_id?: number | null
  is_valid?: boolean
  public_url?: string | null
  owner_username?: string | null
}

/**
 * Convert API ShareLink to Vue SharedLink format
 */
export function adaptShareLink(apiLink: APIShareLink, baseUrl: string = ''): SharedLink {
  const now = new Date()
  const expiresAt = apiLink.expires_at ? new Date(apiLink.expires_at) : null
  
  // Determine status
  let status: 'active' | 'expired' | 'revoked' = 'active'
  if (!apiLink.is_valid) {
    status = 'expired'
  }
  // Note: 'revoked' status would need to be tracked separately in the backend
  
  // Generate public URL (root level: /{token}/)
  const publicUrl = apiLink.public_url || `${baseUrl}/${apiLink.token}/`
  
  // Create name from publication title and preset
  const name = apiLink.publication_title || `Share Link ${apiLink.id}`
  const presetInfo = apiLink.rendition_preset_name 
    ? ` (${apiLink.rendition_preset_name}${apiLink.rendition_preset_format ? ` ${apiLink.rendition_preset_format.toUpperCase()}` : ''})`
    : ''
  const fullName = `${name}${presetInfo}`
  
  // Create assets array from document_id and document_file_id
  const assets = apiLink.document_id && apiLink.document_file_id ? [{
    id: apiLink.document_id,
    document_id: apiLink.document_id,
    document_file_id: apiLink.document_file_id,
    version_active_file_id: apiLink.document_file_id, // Use document_file_id as active version
    file_latest_id: apiLink.document_file_id,
    file_id: apiLink.document_file_id,
    label: `Document #${apiLink.document_id}`,
    thumbnail_url: undefined, // Will be loaded separately
    preview_url: undefined,
    download_url: undefined
  }] : []

  return {
    id: apiLink.id,
    uuid: apiLink.token,
    name: fullName,
    slug: apiLink.token, // Full UUID for display
    url: publicUrl,
    asset_ids: apiLink.document_file_id ? [apiLink.document_file_id] : [],
    assets: assets, // Create assets array from document_id and document_file_id
    is_public: true, // ShareLinks are always public (token-based access)
    password_protected: apiLink.password_protected || false,
    created_date: apiLink.created,
    updated_date: apiLink.last_accessed || undefined,
    expires_date: apiLink.expires_at,
    created_by: apiLink.owner_username || 'Unknown',
    created_by_id: 0, // Not available in current API
    views: apiLink.views_count || 0,
    downloads: apiLink.downloads_count,
    unique_visitors: apiLink.unique_visitors_count || 0,
    status,
    allow_download: apiLink.allow_download !== false, // Default to true if not specified
    allow_comment: false, // Not implemented
    max_downloads: apiLink.max_downloads,
    max_views: apiLink.max_views,
    // Store document info for preview loading
    document_id: apiLink.document_id,
    document_file_id: apiLink.document_file_id,
  } as SharedLink & { document_id?: number, document_file_id?: number, max_views?: number | null }
}

/**
 * Convert multiple API ShareLinks to Vue SharedLinks
 */
export function adaptShareLinks(apiLinks: APIShareLink[], baseUrl?: string): SharedLink[] {
  return apiLinks.map(link => adaptShareLink(link, baseUrl))
}

