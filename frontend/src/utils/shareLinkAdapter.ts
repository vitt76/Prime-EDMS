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
  
  return {
    id: apiLink.id,
    uuid: apiLink.token,
    name: fullName,
    slug: apiLink.token.substring(0, 12), // Short slug for display
    url: publicUrl,
    asset_ids: apiLink.document_file_id ? [apiLink.document_file_id] : [],
    assets: undefined, // Will be loaded separately if needed
    is_public: true, // ShareLinks are always public (token-based access)
    password_protected: false, // Not implemented in current model
    created_date: apiLink.created,
    updated_date: apiLink.last_accessed || undefined,
    expires_date: apiLink.expires_at,
    created_by: apiLink.owner_username || 'Unknown',
    created_by_id: 0, // Not available in current API
    views: apiLink.downloads_count, // Using downloads_count as views proxy
    downloads: apiLink.downloads_count,
    unique_visitors: 0, // Not tracked in current model
    status,
    allow_download: true, // ShareLinks always allow download
    allow_comment: false, // Not implemented
    max_downloads: apiLink.max_downloads,
  }
}

/**
 * Convert multiple API ShareLinks to Vue SharedLinks
 */
export function adaptShareLinks(apiLinks: APIShareLink[], baseUrl?: string): SharedLink[] {
  return apiLinks.map(link => adaptShareLink(link, baseUrl))
}

