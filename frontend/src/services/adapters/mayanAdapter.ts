// @ts-nocheck
/**
 * Mayan Adapter - Optimized API Transformation Layer
 * ===========================================================================
 * 
 * This adapter transforms Mayan EDMS Optimized API responses to Frontend Asset format.
 * Specifically designed for the high-performance `/api/v4/documents/optimized/` endpoint.
 * 
 * Phase A2 Implementation (TRANSFORMATION_PLAN.md)
 * 
 * @module mayanAdapter
 */

import type { Asset, AIAnalysis, PaginatedResponse } from '@/types/api'

// ============================================================================
// BACKEND TYPES (from /api/v4/documents/optimized/)
// ============================================================================

/**
 * Tag object from Mayan EDMS
 */
export interface BackendTag {
  id: number
  label: string
  color: string
  url?: string
}

/**
 * Document File from Mayan EDMS
 */
export interface BackendDocumentFile {
  id: number
  document: number
  filename: string
  mimetype: string
  size: number
  timestamp: string
  checksum?: string
  download_url: string
  thumbnail_url?: string
  preview_url?: string
  pages_count?: number
}

/**
 * Document Type from Mayan EDMS
 */
export interface BackendDocumentType {
  id: number
  label: string
  url?: string
}

/**
 * AI Analysis from DAM extension
 */
export interface BackendAIAnalysis {
  id?: number
  ai_description?: string | null
  ai_tags?: string[] | null
  categories?: string[] | null
  people?: string[] | null
  locations?: string[] | null
  dominant_colors?: Array<{ hex: string; name: string; percentage?: number }> | null
  copyright_notice?: string | null
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed'
  ai_provider?: string | null
  progress?: number
  current_step?: string | null
  error_message?: string | null
  task_id?: string | null
  analysis_completed?: string | null
  created?: string
  updated?: string
}

/**
 * Metadata value from Mayan EDMS
 */
export interface BackendMetadata {
  id: number
  metadata_type: {
    id: number
    name: string
    label: string
  }
  value: string
}

/**
 * Optimized Document response from /api/v4/documents/optimized/
 */
export interface BackendOptimizedDocument {
  id: number
  uuid: string
  label: string
  description: string
  datetime_created: string
  language: string
  in_trash: boolean
  is_stub: boolean
  document_type: BackendDocumentType
  file_latest?: BackendDocumentFile | null
  // Separate file fields from OptimizedDocumentListSerializer (list view)
  file_latest_id?: number
  file_latest_filename?: string
  file_latest_size?: number
  file_latest_mimetype?: string
  file_latest_download_url?: string
  file_latest_url?: string
  files_count?: number
  version_active?: {
    id: number
    timestamp: string
  }
  version_active_id?: number
  version_active_file_id?: number
  // DAM Extension fields
  ai_analysis?: BackendAIAnalysis | null
  tags?: BackendTag[]
  metadata?: BackendMetadata[]
  cabinets?: Array<{ id: number; label: string; full_path: string }>
  // Processing state from Phase B4
  processing_state?: 'pending' | 'processing' | 'complete' | 'failed'
  // URL fields
  url?: string
  thumbnail_url?: string
  preview_url?: string
  download_url?: string
}

/**
 * Paginated response from Mayan EDMS
 */
export interface BackendPaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ============================================================================
// CONFIGURATION
// ============================================================================

/** Default placeholder for missing thumbnails */
const PLACEHOLDER_THUMBNAIL = '/placeholder-document.svg'

/** Base URL for API (prefers VITE_API_BASE_URL, then VITE_API_URL, then origin) */
const DEFAULT_BASE_URL =
  (import.meta as any)?.env?.VITE_API_BASE_URL ||
  (import.meta as any)?.env?.VITE_API_URL ||
  (typeof window !== 'undefined' ? window.location.origin : '')

let baseUrl = DEFAULT_BASE_URL.replace(/\/$/, '')

/**
 * Set the base URL for API calls
 */
export function setBaseUrl(url: string): void {
  baseUrl = url.replace(/\/$/, '')
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Ensure URL is absolute
 */
function toAbsoluteUrl(url: string | undefined | null): string | undefined {
  if (!url) return undefined
  if (url.startsWith('data:image')) return url
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  const effectiveBase = baseUrl || (typeof window !== 'undefined' ? window.location.origin : '')
  return `${effectiveBase}${url.startsWith('/') ? '' : '/'}${url}`
}

/**
 * Get asset type from MIME type
 */
function getAssetTypeFromMime(mimeType: string | undefined): string {
  if (!mimeType) return 'document'
  
  const mime = mimeType.toLowerCase()
  if (mime.startsWith('image/')) return 'image'
  if (mime.startsWith('video/')) return 'video'
  if (mime.startsWith('audio/')) return 'audio'
  if (mime === 'application/pdf') return 'document'
  if (mime.includes('spreadsheet') || mime.includes('excel')) return 'spreadsheet'
  if (mime.includes('presentation') || mime.includes('powerpoint')) return 'presentation'
  if (mime.includes('document') || mime.includes('word')) return 'document'
  if (mime.includes('zip') || mime.includes('archive') || mime.includes('tar') || mime.includes('rar')) return 'archive'
  
  return 'document'
}

/**
 * Generate thumbnail URL with fallback
 * 
 * Note on S3/Beget URLs:
 * - Beget S3 generates presigned URLs that work directly in <img> tags
 * - These URLs include signature and don't require Authorization header
 * - For Mayan-generated page images, auth token is handled by apiService interceptor
 */
function getThumbnailUrl(doc: BackendOptimizedDocument): string {
  // Priority 1: Document-level thumbnail_url (computed by backend)
  // This could be a presigned S3 URL or Mayan-generated URL
  if (doc.thumbnail_url) {
    return toAbsoluteUrl(doc.thumbnail_url) || PLACEHOLDER_THUMBNAIL
  }
  
  // Priority 2: File latest thumbnail (presigned S3 URL from backend)
  if (doc.file_latest?.thumbnail_url) {
    return toAbsoluteUrl(doc.file_latest.thumbnail_url) || PLACEHOLDER_THUMBNAIL
  }
  
  // Priority 3: File download URL as fallback for images
  // S3 presigned URLs work directly, Mayan URLs need auth
  if (doc.file_latest?.download_url) {
    const mimeType = doc.file_latest.mimetype?.toLowerCase() || ''
    // Only use download URL for images (browsers can display them)
    if (mimeType.startsWith('image/')) {
      return toAbsoluteUrl(doc.file_latest.download_url) || PLACEHOLDER_THUMBNAIL
    }
  }
  
  // Priority 4: Generate download URL для файла активной версии (для изображений)
  // Используем прямой download URL, так как браузер может отображать изображения напрямую
  if (doc.id) {
    const fileId = (doc as any).version_active_file_id || doc.file_latest?.id
    if (fileId) {
      // Проверяем, является ли файл изображением
      const mimeType = doc.file_latest?.mimetype?.toLowerCase() || ''
      if (mimeType.startsWith('image/')) {
        return `${baseUrl}/api/v4/documents/${doc.id}/files/${fileId}/download/`
      }
    }
  }
  
  // Fallback to placeholder
  return PLACEHOLDER_THUMBNAIL
}

/**
 * Generate preview URL
 */
function getPreviewUrl(doc: BackendOptimizedDocument): string | undefined {
  // Priority 1: Document-level preview_url
  if (doc.preview_url) {
    return toAbsoluteUrl(doc.preview_url)
  }
  
  // Priority 2: File preview URL
  if (doc.file_latest?.preview_url) {
    return toAbsoluteUrl(doc.file_latest.preview_url)
  }
  
  // Priority 3: File download URL
  if (doc.file_latest?.download_url) {
    return toAbsoluteUrl(doc.file_latest.download_url)
  }
  
  // Priority 4: Generate download URL для файла активной версии
  // Используем прямой download URL, так как браузер может отображать изображения напрямую
  // Это более надёжно, чем /files/{file_id}/pages/{page_id}/image/, который требует ID страницы
  if (doc.id) {
    const fileId = (doc as any).version_active_file_id || doc.file_latest?.id
    if (fileId) {
      // Проверяем, является ли файл изображением
      const mimeType = doc.file_latest?.mimetype?.toLowerCase() || ''
      if (mimeType.startsWith('image/')) {
        return `${baseUrl}/api/v4/documents/${doc.id}/files/${fileId}/download/`
      }
    }
  }
  
  return undefined
}

/**
 * Map processing state to frontend status
 */
function mapProcessingState(
  processingState?: string,
  aiStatus?: string
): 'pending' | 'processing' | 'complete' | 'failed' {
  // Check processing_state first (Phase B4)
  if (processingState) {
    switch (processingState) {
      case 'processing':
        return 'processing'
      case 'complete':
      case 'completed':
        return 'complete'
      case 'failed':
        return 'failed'
      default:
        return 'pending'
    }
  }
  
  // Fallback to AI analysis status
  if (aiStatus) {
    switch (aiStatus) {
      case 'processing':
        return 'processing'
      case 'completed':
        return 'complete'
      case 'failed':
        return 'failed'
      default:
        return 'pending'
    }
  }
  
  return 'complete' // Default to complete if no status info
}

// ============================================================================
// MAIN ADAPTER FUNCTIONS
// ============================================================================

/**
 * Transform Backend AI Analysis to Frontend AI Analysis
 */
export function adaptBackendAIAnalysis(ai: BackendAIAnalysis | null | undefined): AIAnalysis | undefined {
  if (!ai) return undefined
  
  return {
    status: ai.analysis_status || 'pending',
    tags: ai.ai_tags || undefined,
    ai_description: ai.ai_description || undefined,
    colors: ai.dominant_colors?.map(c => c.hex) || undefined,
    provider: ai.ai_provider || undefined,
    confidence: undefined, // Not provided by backend
    objects_detected: [
      ...(ai.categories || []).map(cat => ({ name: cat, confidence: 0.85 })),
      ...(ai.people || []).map(person => ({ name: `Person: ${person}`, confidence: 0.9 })),
      ...(ai.locations || []).map(loc => ({ name: `Location: ${loc}`, confidence: 0.8 })),
    ].slice(0, 10),
  }
}

/**
 * Transform Backend Tags to Frontend Tags array
 */
export function adaptBackendTags(tags: BackendTag[] | undefined): string[] {
  if (!tags || !Array.isArray(tags)) return []
  return tags.map(t => t.label).filter(Boolean)
}

/**
 * Transform Backend Metadata to Frontend Record
 */
export function adaptBackendMetadata(
  metadata: BackendMetadata[] | undefined,
  docType?: BackendDocumentType
): Record<string, unknown> {
  const result: Record<string, unknown> = {}
  
  // Add document type info
  if (docType) {
    result.document_type = docType.label
    result.document_type_id = docType.id
  }
  
  // Add metadata values
  if (metadata && Array.isArray(metadata)) {
    for (const m of metadata) {
      if (m.metadata_type?.name) {
        result[m.metadata_type.name] = m.value
      }
    }
  }
  
  return result
}

function extractMetadataTags(metadata: BackendMetadata[] | undefined): string[] {
  if (!metadata || !Array.isArray(metadata)) return []
  const collected: string[] = []
  for (const m of metadata) {
    if (m.metadata_type?.name?.toLowerCase() === 'tags' && m.value) {
      const parts = m.value.split(',').map(p => p.trim()).filter(Boolean)
      collected.push(...parts)
    }
  }
  return collected
}

/**
 * Transform a single Backend Document to Frontend Asset
 * 
 * This is the main adapter function for converting Mayan EDMS optimized
 * document responses to the Frontend Asset format.
 * 
 * @param backendDoc - Raw document from /api/v4/documents/optimized/
 * @returns Transformed Asset for Frontend consumption
 */
function inferMimeFromFilename(filename?: string, fallback = 'application/octet-stream'): string {
  if (!filename) return fallback
  const lower = filename.toLowerCase()
  if (lower.match(/\.(jpg|jpeg)$/)) return 'image/jpeg'
  if (lower.match(/\.(png)$/)) return 'image/png'
  if (lower.match(/\.(gif)$/)) return 'image/gif'
  if (lower.match(/\.(webp)$/)) return 'image/webp'
  if (lower.match(/\.(bmp)$/)) return 'image/bmp'
  if (lower.match(/\.(heic|heif)$/)) return 'image/heic'
  if (lower.match(/\.(mp4|mov|mkv|avi)$/)) return 'video/mp4'
  if (lower.match(/\.(mp3|wav|flac)$/)) return 'audio/mpeg'
  if (lower.match(/\.(pdf)$/)) return 'application/pdf'
  return fallback
}

export function adaptBackendAsset(backendDoc: BackendOptimizedDocument): Asset {
  const rawMime = backendDoc.file_latest?.mimetype
  const inferredMime = inferMimeFromFilename(
    backendDoc.file_latest?.filename || backendDoc.label,
    'application/octet-stream'
  )
  const mimeType = rawMime && rawMime !== 'application/octet-stream' ? rawMime : inferredMime
  const assetType = getAssetTypeFromMime(mimeType)
  
  // Combine manual tags and AI tags
  const manualTags = adaptBackendTags(backendDoc.tags)
  const metadataTags = extractMetadataTags(backendDoc.metadata)
  const aiTags = backendDoc.ai_analysis?.ai_tags || []
  const allTags = [...new Set([...manualTags, ...metadataTags, ...aiTags])]
  
  // Build metadata
  const metadata = adaptBackendMetadata(backendDoc.metadata, backendDoc.document_type)
  metadata.type = assetType
  metadata.language = backendDoc.language
  metadata.uuid = backendDoc.uuid
  
  // Extract document_type_id from backend response (could be in document_type object or as separate field)
  const documentTypeId = (backendDoc as any)?.document_type_id || backendDoc.document_type?.id
  
  // Determine processing status
  const status = mapProcessingState(
    backendDoc.processing_state,
    backendDoc.ai_analysis?.analysis_status
  )
  
  // Get file information with fallback logic
  // OptimizedDocumentListSerializer returns separate fields (file_latest_filename, file_latest_size, etc.)
  // instead of a file_latest object, so we need to handle both cases
  let filename = backendDoc.label
  let size = 0
  let mime_type = mimeType
  let file_details = undefined
  let date_added = backendDoc.datetime_created
  let file_latest_id = backendDoc.file_latest?.id || (backendDoc as any)?.file_latest_id

  // Check if we have separate file fields from OptimizedDocumentListSerializer
  const hasFileFields = !!(backendDoc as any)?.file_latest_filename || !!(backendDoc as any)?.file_latest_size
  
  // Priority: version_active_file_id > file_latest
  // This ensures we use the active version file, not just the latest by timestamp
  const activeFileId = (backendDoc as any)?.version_active_file_id
  const shouldUseActiveFile = activeFileId && activeFileId !== file_latest_id

  if (backendDoc.file_latest) {
    // Full file_latest object (from OptimizedDocumentSerializer detail view)
    filename = backendDoc.file_latest.filename || backendDoc.label
    size = backendDoc.file_latest.size || 0
    mime_type = backendDoc.file_latest.mimetype || mimeType
    file_details = {
      filename: backendDoc.file_latest.filename,
      size: backendDoc.file_latest.size,
      mime_type: backendDoc.file_latest.mimetype,
      uploaded_date: backendDoc.file_latest.timestamp,
      checksum: backendDoc.file_latest.checksum,
    }
    if (backendDoc.file_latest.timestamp) {
      date_added = backendDoc.file_latest.timestamp
    }
    file_latest_id = backendDoc.file_latest.id
  } else if (hasFileFields) {
    // Separate file fields from OptimizedDocumentListSerializer (list view)
    const docAny = backendDoc as any
    filename = docAny.file_latest_filename || backendDoc.label
    size = docAny.file_latest_size || 0
    mime_type = docAny.file_latest_mimetype || mimeType
    file_latest_id = docAny.file_latest_id || file_latest_id
    file_details = {
      filename: docAny.file_latest_filename,
      size: docAny.file_latest_size,
      mime_type: docAny.file_latest_mimetype,
      uploaded_date: undefined, // Not available in list view
      checksum: undefined, // Not available in list view
    }
  } else {
    // No file information available
    filename = backendDoc.label
    size = 0
    mime_type = mimeType
  }

  // If we have version_active_file_id that differs from file_latest_id,
  // we should use it, but for list view we'll keep file_latest data
  // and let getAssetDetail fetch the correct active file if needed
  if (shouldUseActiveFile && !hasFileFields && !backendDoc.file_latest) {
    // Only log if we don't have file data at all
    console.log('[MayanAdapter] Active file ID differs from file_latest:', {
      activeFileId,
      file_latest_id,
      documentId: backendDoc.id
    })
  }

  return {
    id: backendDoc.id,
    version_active_id: (backendDoc as any)?.version_active?.id || (backendDoc as any)?.version_active_id || (backendDoc as any)?.version?.id,
    version_active_file_id: (backendDoc as any)?.version_active_file_id || undefined,
    label: backendDoc.label,
    description: backendDoc.description,
    filename: filename,
    size: size,
    mime_type: mime_type,
    date_added: date_added,
    thumbnail_url: getThumbnailUrl(backendDoc),
    preview_url: getPreviewUrl(backendDoc),
    download_url: toAbsoluteUrl(backendDoc.file_latest?.download_url || backendDoc.download_url),
    file_latest_id: backendDoc.file_latest?.id,
    tags: allTags,
    metadata: {
      ...metadata,
      status, // Processing status for UI indicators
    },
    ai_analysis: adaptBackendAIAnalysis(backendDoc.ai_analysis),
    access_level: 'internal',
    file_details: file_details,
    // Add document_type_id and document_type for workflow widget
    document_type_id: documentTypeId,
    document_type: backendDoc.document_type ? {
      id: backendDoc.document_type.id,
      label: backendDoc.document_type.label,
      internal_name: (backendDoc.document_type as any)?.internal_name
    } : undefined,
  } as Asset & { document_type_id?: number; document_type?: { id: number; label: string; internal_name?: string } }
}

/**
 * Transform array of Backend Documents to Frontend Assets
 */
export function adaptBackendAssets(docs: BackendOptimizedDocument[]): Asset[] {
  if (!Array.isArray(docs)) {
    console.warn('[MayanAdapter] Expected array of documents, got:', typeof docs)
    return []
  }
  return docs.map(adaptBackendAsset)
}

/**
 * Transform Backend Paginated Response to Frontend PaginatedResponse
 */
export function adaptBackendPaginatedResponse(
  response: BackendPaginatedResponse<BackendOptimizedDocument>
): PaginatedResponse<Asset> {
  const results = adaptBackendAssets(response.results)
  const pageSize = results.length || 24
  const totalPages = Math.ceil(response.count / pageSize)
  
  return {
    count: response.count,
    next: response.next,
    previous: response.previous,
    results,
    page_size: pageSize,
    total_pages: totalPages,
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export type {
  BackendOptimizedDocument,
  BackendDocumentFile,
  BackendDocumentType,
  BackendAIAnalysis,
  BackendTag,
  BackendMetadata,
  BackendPaginatedResponse,
}

