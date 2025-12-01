/**
 * Upload Service
 * ==============
 * 
 * Handles file uploads to Mayan EDMS using the 2-step process:
 * 1. Create Document Container (POST /api/v4/documents/)
 * 2. Upload File Binary (POST /api/v4/documents/{id}/files/)
 * 
 * Features:
 * - Progress tracking via Axios onUploadProgress
 * - Automatic cleanup on failure (delete orphan document)
 * - Cancellation support via AbortSignal
 * - Non-blocking async operations
 */

import axios, { AxiosProgressEvent, CancelTokenSource } from 'axios'
import { getToken } from './authService'

// ============================================================================
// TYPES
// ============================================================================

export interface UploadProgress {
  /** Progress percentage (0-100) */
  percent: number
  /** Bytes uploaded so far */
  loaded: number
  /** Total bytes to upload */
  total: number
  /** Current upload speed in bytes/second */
  speed: number
  /** Estimated time remaining in seconds */
  eta: number
  /** Current step: 'creating' | 'uploading' | 'processing' */
  step: 'creating' | 'uploading' | 'processing'
}

export interface UploadOptions {
  /** Callback for progress updates */
  onProgress?: (progress: UploadProgress) => void
  /** AbortSignal for cancellation */
  signal?: AbortSignal
  /** Document type ID (defaults to 1 = "Default" type) */
  documentTypeId?: number
  /** Optional description */
  description?: string
  /** Optional folder (cabinet) ID to place the document */
  cabinetId?: number
  /** Optional language (ISO code) */
  language?: string
}

export interface UploadResult {
  /** Document ID in Mayan */
  documentId: number
  /** File ID in Mayan */
  fileId: number
  /** Document label (filename) */
  label: string
  /** Full API URL to the document */
  documentUrl: string
  /** Download URL for the file */
  downloadUrl?: string
}

interface MayanDocumentResponse {
  id: number
  label: string
  datetime_created: string
  document_type: {
    id: number
    label: string
  }
  url: string
  file_latest?: {
    id: number
    download_url: string
    filename: string
  }
}

interface MayanFileResponse {
  id: number
  filename: string
  mimetype: string
  size: number
  download_url: string
  document_url: string
}

// ============================================================================
// UPLOAD SERVICE
// ============================================================================

class UploadService {
  private baseUrl = '/api/v4'
  
  /**
   * Main upload method - handles the complete 2-step Mayan upload process
   * 
   * @param file - File to upload
   * @param options - Upload options (progress callback, document type, etc.)
   * @returns UploadResult with document and file IDs
   */
  async uploadAsset(file: File, options: UploadOptions = {}): Promise<UploadResult> {
    const token = getToken()
    
    if (!token) {
      throw new Error('Not authenticated. Please login first.')
    }
    
    const headers = {
      'Authorization': `Token ${token}`,
    }
    
    let documentId: number | null = null
    
    try {
      // =======================================================================
      // STEP 1: Create Document Container
      // =======================================================================
      options.onProgress?.({
        percent: 0,
        loaded: 0,
        total: file.size,
        speed: 0,
        eta: 0,
        step: 'creating'
      })
      
      console.log('[UploadService] Step 1: Creating document container...')
      
      // Check for cancellation
      if (options.signal?.aborted) {
        throw new Error('Upload cancelled')
      }
      
      const documentTypeId = options.documentTypeId || 1 // Default document type
      
      const createResponse = await axios.post<MayanDocumentResponse>(
        `${this.baseUrl}/documents/`,
        {
          document_type_id: documentTypeId,
          label: file.name,
          description: options.description || '',
          language: options.language || 'rus', // Russian by default
        },
        {
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          signal: options.signal
        }
      )
      
      documentId = createResponse.data.id
      console.log('[UploadService] Document created:', documentId)
      
      // =======================================================================
      // STEP 2: Upload File Binary
      // =======================================================================
      options.onProgress?.({
        percent: 5,
        loaded: 0,
        total: file.size,
        speed: 0,
        eta: 0,
        step: 'uploading'
      })
      
      console.log('[UploadService] Step 2: Uploading file binary...')
      
      // Check for cancellation
      if (options.signal?.aborted) {
        throw new Error('Upload cancelled')
      }
      
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file_new', file)
      
      // Track upload progress
      let lastLoaded = 0
      let lastTime = Date.now()
      
      const fileResponse = await axios.post<MayanFileResponse>(
        `${this.baseUrl}/documents/${documentId}/files/`,
        formData,
        {
          headers: {
            ...headers,
            'Content-Type': 'multipart/form-data'
          },
          signal: options.signal,
          onUploadProgress: (event: AxiosProgressEvent) => {
            const loaded = event.loaded || 0
            const total = event.total || file.size
            
            // Calculate speed
            const now = Date.now()
            const timeDiff = (now - lastTime) / 1000 || 0.1
            const bytesDiff = loaded - lastLoaded
            const speed = bytesDiff / timeDiff
            
            // Calculate ETA
            const remaining = total - loaded
            const eta = speed > 0 ? remaining / speed : 0
            
            // Update tracking
            lastLoaded = loaded
            lastTime = now
            
            // Report progress (5-95% range for file upload)
            const percent = Math.min(95, 5 + Math.round((loaded / total) * 90))
            
            options.onProgress?.({
              percent,
              loaded,
              total,
              speed,
              eta,
              step: 'uploading'
            })
          }
        }
      )
      
      console.log('[UploadService] File uploaded:', fileResponse.data.id)
      
      // =======================================================================
      // STEP 3: Processing Complete
      // =======================================================================
      options.onProgress?.({
        percent: 100,
        loaded: file.size,
        total: file.size,
        speed: 0,
        eta: 0,
        step: 'processing'
      })
      
      // If cabinet specified, add document to cabinet
      if (options.cabinetId) {
        await this.addToCabinet(documentId, options.cabinetId, token)
      }
      
      return {
        documentId,
        fileId: fileResponse.data.id,
        label: file.name,
        documentUrl: `${this.baseUrl}/documents/${documentId}/`,
        downloadUrl: fileResponse.data.download_url
      }
      
    } catch (error: any) {
      console.error('[UploadService] Upload failed:', error)
      
      // =======================================================================
      // CLEANUP: Delete orphan document if Step 1 succeeded but Step 2 failed
      // =======================================================================
      if (documentId && !options.signal?.aborted) {
        console.log('[UploadService] Cleaning up orphan document:', documentId)
        try {
          await axios.delete(`${this.baseUrl}/documents/${documentId}/`, {
            headers
          })
          console.log('[UploadService] Orphan document deleted')
        } catch (cleanupError) {
          console.error('[UploadService] Failed to cleanup orphan document:', cleanupError)
        }
      }
      
      // Re-throw with meaningful message
      if (error.response?.status === 413) {
        throw new Error('File too large. Maximum size is 500MB.')
      } else if (error.response?.status === 415) {
        throw new Error('Unsupported file type.')
      } else if (error.response?.status === 401) {
        throw new Error('Session expired. Please login again.')
      } else if (error.message === 'Upload cancelled') {
        throw error
      } else {
        throw new Error(error.response?.data?.detail || error.message || 'Upload failed')
      }
    }
  }
  
  /**
   * Upload multiple files with batch progress tracking
   */
  async uploadMultiple(
    files: File[],
    options: Omit<UploadOptions, 'onProgress'> & {
      onFileProgress?: (fileIndex: number, progress: UploadProgress) => void
      onFileComplete?: (fileIndex: number, result: UploadResult) => void
      onFileError?: (fileIndex: number, error: Error) => void
      onBatchProgress?: (completed: number, total: number) => void
    } = {}
  ): Promise<{ results: UploadResult[]; errors: { index: number; error: Error }[] }> {
    const results: UploadResult[] = []
    const errors: { index: number; error: Error }[] = []
    
    for (let i = 0; i < files.length; i++) {
      // Check for batch cancellation
      if (options.signal?.aborted) {
        errors.push({ index: i, error: new Error('Upload cancelled') })
        continue
      }
      
      try {
        const result = await this.uploadAsset(files[i], {
          ...options,
          onProgress: (progress) => options.onFileProgress?.(i, progress)
        })
        
        results.push(result)
        options.onFileComplete?.(i, result)
        
      } catch (error: any) {
        errors.push({ index: i, error })
        options.onFileError?.(i, error)
      }
      
      options.onBatchProgress?.(i + 1, files.length)
    }
    
    return { results, errors }
  }
  
  /**
   * Add document to a cabinet (folder)
   */
  private async addToCabinet(documentId: number, cabinetId: number, token: string): Promise<void> {
    try {
      await axios.post(
        `${this.baseUrl}/cabinets/${cabinetId}/documents/`,
        { document: documentId },
        {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )
      console.log('[UploadService] Document added to cabinet:', cabinetId)
    } catch (error) {
      console.warn('[UploadService] Failed to add document to cabinet:', error)
      // Don't throw - cabinet assignment is optional
    }
  }
  
  /**
   * Get available document types for upload
   */
  async getDocumentTypes(): Promise<{ id: number; label: string }[]> {
    const token = getToken()
    
    if (!token) {
      throw new Error('Not authenticated')
    }
    
    const response = await axios.get<{ results: { id: number; label: string }[] }>(
      `${this.baseUrl}/document_types/`,
      {
        headers: {
          'Authorization': `Token ${token}`
        }
      }
    )
    
    return response.data.results
  }
}

// ============================================================================
// METADATA SERVICE (PATCH operations)
// ============================================================================

export interface UpdateMetadataOptions {
  label?: string
  description?: string
  language?: string
}

/**
 * Update document metadata
 * 
 * @param documentId - Document ID
 * @param data - Fields to update
 */
export async function updateDocumentMetadata(
  documentId: number,
  data: UpdateMetadataOptions
): Promise<MayanDocumentResponse> {
  const token = getToken()
  
  if (!token) {
    throw new Error('Not authenticated')
  }
  
  const response = await axios.patch<MayanDocumentResponse>(
    `/api/v4/documents/${documentId}/`,
    data,
    {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    }
  )
  
  return response.data
}

/**
 * Delete a document
 * 
 * @param documentId - Document ID to delete
 */
export async function deleteDocument(documentId: number): Promise<void> {
  const token = getToken()
  
  if (!token) {
    throw new Error('Not authenticated')
  }
  
  await axios.delete(`/api/v4/documents/${documentId}/`, {
    headers: {
      'Authorization': `Token ${token}`
    }
  })
}

/**
 * Add tags to a document
 */
export async function addDocumentTags(
  documentId: number,
  tagIds: number[]
): Promise<void> {
  const token = getToken()
  
  if (!token) {
    throw new Error('Not authenticated')
  }
  
  for (const tagId of tagIds) {
    await axios.post(
      `/api/v4/documents/${documentId}/tags/`,
      { tag: tagId },
      {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )
  }
}

/**
 * Remove tag from a document
 */
export async function removeDocumentTag(
  documentId: number,
  tagId: number
): Promise<void> {
  const token = getToken()
  
  if (!token) {
    throw new Error('Not authenticated')
  }
  
  await axios.delete(`/api/v4/documents/${documentId}/tags/${tagId}/`, {
    headers: {
      'Authorization': `Token ${token}`
    }
  })
}

// ============================================================================
// EXPORT
// ============================================================================

export const uploadService = new UploadService()
