/**
 * Upload Service
 * ==============
 * 
 * Handles file uploads to Mayan EDMS using two strategies:
 * 
 * 1. SIMPLE UPLOAD (files < 50MB):
 *    - Create Document Container (POST /api/v4/documents/)
 *    - Upload File Binary (POST /api/v4/documents/{id}/files/)
 * 
 * 2. CHUNKED UPLOAD (files >= 50MB):
 *    - Initialize upload session (POST /api/v4/uploads/init/)
 *    - Upload chunks sequentially (POST /api/v4/uploads/append/)
 *    - Complete upload and create document (POST /api/v4/uploads/complete/)
 * 
 * Features:
 * - Automatic strategy selection based on file size
 * - Progress tracking via Axios onUploadProgress
 * - Automatic cleanup on failure (delete orphan document)
 * - Cancellation support via AbortSignal
 * - Non-blocking async operations
 * - Retry logic for failed chunks
 */

import axios, { AxiosProgressEvent } from 'axios'
import { getToken } from './authService'
import { getDocumentTypeConfig, validateMetadata } from './documentTypeService'

// ============================================================================
// CONSTANTS
// ============================================================================

/** Files smaller than this use simple upload, larger use chunked */
const CHUNKED_UPLOAD_THRESHOLD = 50 * 1024 * 1024 // 50MB

/** Size of each chunk for chunked upload */
const CHUNK_SIZE = 5 * 1024 * 1024 // 5MB

/** Max retries for failed chunk uploads */
const MAX_CHUNK_RETRIES = 3

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
  /** Current step: 'creating' | 'uploading' | 'processing' | 'chunking' */
  step: 'creating' | 'uploading' | 'processing' | 'chunking'
  /** Current chunk number (for chunked uploads) */
  currentChunk?: number
  /** Total chunks (for chunked uploads) */
  totalChunks?: number
}

export interface UploadOptions {
  /** Callback for progress updates */
  onProgress?: (progress: UploadProgress) => void
  /** AbortSignal for cancellation */
  signal?: AbortSignal
  /** Document type ID (defaults to 1 = "Default" type) */
  documentTypeId?: number
  /** Optional document label (defaults to file name) */
  label?: string
  /** Optional description */
  description?: string
  /** Optional folder (cabinet) ID to place the document */
  cabinetId?: number
  /** Optional language (ISO code) */
  language?: string
  /** Optional metadata payload for dynamic validation */
  metadata?: Record<string, string>
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

// Chunked Upload API Responses
interface ChunkedUploadInitResponse {
  upload_id: string
  s3_key: string
  parts: any[]
}

interface ChunkedUploadAppendResponse {
  part_number: number
  etag: string
}

interface ChunkedUploadCompleteResponse {
  document_id: number
  file_id: number
  label: string
  download_url?: string
}

// ============================================================================
// UPLOAD SERVICE
// ============================================================================

class UploadService {
  private baseUrl = `${import.meta.env.VITE_API_URL || ''}/api/v4`
  private readonly isBffEnabled = import.meta.env.VITE_BFF_ENABLED === 'true'
  
  /**
   * Main upload method - automatically selects strategy based on file size
   * 
   * - Files < 50MB: Simple 2-step upload
   * - Files >= 50MB: Chunked upload for reliability
   * 
   * @param file - File to upload
   * @param options - Upload options (progress callback, document type, etc.)
   * @returns UploadResult with document and file IDs
   */
  async uploadFile(file: File, options: UploadOptions = {}): Promise<UploadResult> {
    // Validate metadata against headless config when available
    await this.validateMetadataIfNeeded(options)

    if (file.size >= CHUNKED_UPLOAD_THRESHOLD) {
      console.log(`[UploadService] File ${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB) - using chunked upload`)
      return this.uploadChunked(file, options)
    } else {
      console.log(`[UploadService] File ${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB) - using simple upload`)
      return this.uploadAsset(file, options)
    }
  }
  
  /**
   * Simple 2-step upload for smaller files (< 50MB)
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
          label: options.label || file.name,
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
      // Mayan expects file_new and an allowed action value; use '1' (DocumentFileActionUseNewPages)
      formData.append('action', '1')
      formData.append('file_new', file)
      formData.append('file', file)
      
      // Track upload progress
      let lastLoaded = 0
      let lastTime = Date.now()
      
      const fileResponse = await axios.post<MayanFileResponse>(
        `${this.baseUrl}/documents/${documentId}/files/`,
        formData,
        {
          headers: headers,
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
        label: options.label || file.name,
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
        let detail: any = error.response?.data?.detail || error.response?.data || error.message
        if (detail && typeof detail === 'object') {
          try {
            detail = JSON.stringify(detail)
          } catch {
            detail = 'Upload failed'
          }
        }
        throw new Error(detail || 'Upload failed')
      }
    }
  }

  /**
   * Validate metadata using headless config when BFF is enabled.
   */
  private async validateMetadataIfNeeded(options: UploadOptions): Promise<void> {
    if (!this.isBffEnabled) return
    if (!options.documentTypeId) return

    try {
      const config = await getDocumentTypeConfig(options.documentTypeId)
      const errors = validateMetadata(config, options.metadata || {})
      if (errors.length > 0) {
        const error = new Error(errors.join('; '))
        error.name = 'UploadMetadataValidationError'
        throw error
      }
    } catch (err) {
      // Surface validation errors; for unreachable headless API fall back gracefully
      if ((err as Error).name === 'UploadMetadataValidationError') {
        throw err
      }
      console.warn('[UploadService] Metadata validation skipped:', err)
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
      
      const file = files[i]
      if (!file) continue
      
      try {
        const result = await this.uploadAsset(file, {
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
   * Chunked upload for large files (>= 50MB)
   * 
   * Uses the backend's chunked upload API (Phase B3):
   * 1. POST /api/v4/uploads/init/ - Initialize upload session
   * 2. POST /api/v4/uploads/append/ - Upload each chunk
   * 3. POST /api/v4/uploads/complete/ - Finalize and create document
   * 
   * @param file - File to upload
   * @param options - Upload options
   * @returns UploadResult with document and file IDs
   */
  async uploadChunked(file: File, options: UploadOptions = {}): Promise<UploadResult> {
    const token = getToken()
    
    if (!token) {
      throw new Error('Not authenticated. Please login first.')
    }
    
    const headers = {
      'Authorization': `Token ${token}`,
    }
    
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE)
    let uploadId: string | null = null
    
    // Track progress
    let uploadedBytes = 0
    let lastTime = Date.now()
    let lastBytes = 0
    
    const reportProgress = (loaded: number, step: UploadProgress['step'], currentChunk?: number) => {
      const now = Date.now()
      const timeDiff = (now - lastTime) / 1000 || 0.1
      const bytesDiff = loaded - lastBytes
      const speed = bytesDiff / timeDiff
      const remaining = file.size - loaded
      const eta = speed > 0 ? remaining / speed : 0
      
      lastTime = now
      lastBytes = loaded
      
      options.onProgress?.({
        percent: Math.min(95, Math.round((loaded / file.size) * 95)),
        loaded,
        total: file.size,
        speed,
        eta,
        step,
        currentChunk,
        totalChunks
      })
    }
    
    try {
      // =======================================================================
      // STEP 1: Initialize Chunked Upload
      // =======================================================================
      options.onProgress?.({
        percent: 0,
        loaded: 0,
        total: file.size,
        speed: 0,
        eta: 0,
        step: 'creating',
        currentChunk: 0,
        totalChunks
      })
      
      console.log('[UploadService] Chunked: Initializing upload session...')
      
      if (options.signal?.aborted) {
        throw new Error('Upload cancelled')
      }
      
      const initResponse = await axios.post<ChunkedUploadInitResponse>(
        `${this.baseUrl}/uploads/init/`,
        {
          filename: options.label || file.name,
          total_size: file.size,
          content_type: file.type || 'application/octet-stream'
        },
        {
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          signal: options.signal
        }
      )
      
      uploadId = initResponse.data.upload_id
      console.log('[UploadService] Chunked: Upload session initialized:', uploadId)
      
      // =======================================================================
      // STEP 2: Upload Chunks
      // =======================================================================
      const parts: { part_number: number; etag: string }[] = []
      
      for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        if (options.signal?.aborted) {
          throw new Error('Upload cancelled')
        }
        
        const start = chunkIndex * CHUNK_SIZE
        const end = Math.min(start + CHUNK_SIZE, file.size)
        const chunk = file.slice(start, end)
        const partNumber = chunkIndex + 1
        
        console.log(`[UploadService] Chunked: Uploading part ${partNumber}/${totalChunks} (${start}-${end})`)
        
        // Retry logic for chunks
        let lastError: Error | null = null
        for (let retry = 0; retry < MAX_CHUNK_RETRIES; retry++) {
          try {
            const chunkFormData = new FormData()
            chunkFormData.append('upload_id', uploadId)
            chunkFormData.append('part_number', String(partNumber))
            chunkFormData.append('chunk', chunk, file.name)
            
            const appendResponse = await axios.post<ChunkedUploadAppendResponse>(
              `${this.baseUrl}/uploads/append/`,
              chunkFormData,
              {
                headers: {
                  ...headers,
                  'Content-Type': 'multipart/form-data'
                },
                signal: options.signal,
                onUploadProgress: (event: AxiosProgressEvent) => {
                  const chunkLoaded = event.loaded || 0
                  const totalLoaded = uploadedBytes + chunkLoaded
                  reportProgress(totalLoaded, 'chunking', partNumber)
                }
              }
            )
            
            parts.push({
              part_number: partNumber,
              etag: appendResponse.data.etag
            })
            
            uploadedBytes = end
            lastError = null
            break // Success - exit retry loop
            
          } catch (error: any) {
            lastError = error
            console.warn(`[UploadService] Chunk ${partNumber} failed, retry ${retry + 1}/${MAX_CHUNK_RETRIES}:`, error.message)
            
            if (retry < MAX_CHUNK_RETRIES - 1) {
              // Wait before retry (exponential backoff)
              await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retry)))
            }
          }
        }
        
        if (lastError) {
          throw new Error(`Chunk ${partNumber} failed after ${MAX_CHUNK_RETRIES} retries: ${lastError.message}`)
        }
      }
      
      // =======================================================================
      // STEP 3: Complete Upload
      // =======================================================================
      reportProgress(file.size, 'processing')
      
      console.log('[UploadService] Chunked: Completing upload...')
      
      const documentTypeId = options.documentTypeId || 1
      
      const completeResponse = await axios.post<ChunkedUploadCompleteResponse>(
        `${this.baseUrl}/uploads/complete/`,
        {
          upload_id: uploadId,
          label: options.label || file.name,
          description: options.description || '',
          document_type_id: documentTypeId,
          parts
        },
        {
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          signal: options.signal
        }
      )
      
      console.log('[UploadService] Chunked: Upload completed, document ID:', completeResponse.data.document_id)
      
      // Final progress
      options.onProgress?.({
        percent: 100,
        loaded: file.size,
        total: file.size,
        speed: 0,
        eta: 0,
        step: 'processing'
      })
      
      // Add to cabinet if specified
      if (options.cabinetId) {
        await this.addToCabinet(completeResponse.data.document_id, options.cabinetId, token)
      }
      
      return {
        documentId: completeResponse.data.document_id,
        fileId: completeResponse.data.file_id,
        label: options.label || file.name,
        documentUrl: `${this.baseUrl}/documents/${completeResponse.data.document_id}/`,
        downloadUrl: completeResponse.data.download_url
      }
      
    } catch (error: any) {
      console.error('[UploadService] Chunked upload failed:', error)
      
      // TODO: Could call abort endpoint to cleanup partial upload on server
      // if (uploadId) { await this.abortChunkedUpload(uploadId, token) }
      
      // Re-throw with meaningful message
      if (error.response?.status === 413) {
        throw new Error('File too large. Maximum size exceeded.')
      } else if (error.response?.status === 401) {
        throw new Error('Session expired. Please login again.')
      } else if (error.response?.status === 507) {
        throw new Error('Server storage full. Contact administrator.')
      } else if (error.message === 'Upload cancelled') {
        throw error
      } else {
        throw new Error(error.response?.data?.detail || error.message || 'Chunked upload failed')
      }
    }
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
