/**
 * Upload Service
 *
 * Handles file uploads with progress tracking, chunking support,
 * and error recovery for the DAM system.
 */

import { apiService } from './apiService'
import { withRetry, ApiError } from '@/utils/retry'

export interface UploadOptions {
  onProgress?: (progress: number) => void
  onChunkComplete?: (chunkIndex: number, totalChunks: number) => void
  signal?: AbortSignal
  chunkSize?: number
  retryOptions?: Parameters<typeof withRetry>[1]
}

export interface UploadResult {
  assetId: string
  filename: string
  size: number
  mimeType: string
  url: string
  thumbnailUrl?: string
  checksum: string
}

export interface ChunkUploadResult {
  chunkIndex: number
  totalChunks: number
  uploadedBytes: number
  checksum: string
}

class UploadService {
  private readonly DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024 // 5MB
  private readonly MAX_FILE_SIZE = 500 * 1024 * 1024 // 500MB
  private readonly MAX_TOTAL_SIZE = 2 * 1024 * 1024 * 1024 // 2GB

  /**
   * Upload a single file with progress tracking and retry logic
   */
  async uploadFile(file: File, options: UploadOptions = {}): Promise<UploadResult> {
    this.validateFile(file)

    const {
      onProgress,
      signal,
      chunkSize = this.DEFAULT_CHUNK_SIZE,
      retryOptions
    } = options

    // For small files, use simple upload
    if (file.size <= chunkSize) {
      return this.uploadSimple(file, onProgress, signal, retryOptions)
    }

    // For large files, use chunked upload
    return this.uploadChunked(file, chunkSize, onProgress, signal, retryOptions)
  }

  /**
   * Upload multiple files concurrently with progress aggregation
   */
  async uploadFiles(files: File[], options: UploadOptions & {
    concurrency?: number
    onFileProgress?: (fileIndex: number, progress: number) => void
    onFileComplete?: (fileIndex: number, result: UploadResult) => void
  } = {}): Promise<UploadResult[]> {
    const {
      concurrency = 3,
      onProgress,
      onFileProgress,
      onFileComplete,
      ...uploadOptions
    } = options

    const results: UploadResult[] = []
    const totalSize = files.reduce((sum, file) => sum + file.size, 0)

    if (totalSize > this.MAX_TOTAL_SIZE) {
      throw new ApiError(
        `Total upload size (${this.formatBytes(totalSize)}) exceeds limit (${this.formatBytes(this.MAX_TOTAL_SIZE)})`,
        413
      )
    }

    // Process files in batches to control concurrency
    for (let i = 0; i < files.length; i += concurrency) {
      const batch = files.slice(i, i + concurrency)

      const batchPromises = batch.map(async (file, batchIndex) => {
        const fileIndex = i + batchIndex

        try {
          const result = await this.uploadFile(file, {
            ...uploadOptions,
            onProgress: (progress) => {
              onFileProgress?.(fileIndex, progress)

              // Calculate overall progress
              if (onProgress) {
                const completedFiles = fileIndex
                const currentFileProgress = progress / 100
                const overallProgress = ((completedFiles + currentFileProgress) / files.length) * 100
                onProgress(Math.round(overallProgress))
              }
            }
          })

          onFileComplete?.(fileIndex, result)
          return result

        } catch (error) {
          // Mark file as failed but continue with others
          console.error(`Upload failed for ${file.name}:`, error)
          throw error
        }
      })

      const batchResults = await Promise.allSettled(batchPromises)

      batchResults.forEach((result) => {
        if (result.status === 'fulfilled') {
          results.push(result.value)
        } else {
          // Handle failed uploads
          results.push(null as any) // Will be filtered out by caller
        }
      })
    }

    return results.filter(Boolean)
  }

  /**
   * Simple upload for smaller files
   */
  private async uploadSimple(
    file: File,
    onProgress?: (progress: number) => void,
    signal?: AbortSignal,
    retryOptions?: Parameters<typeof withRetry>[1]
  ): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('filename', file.name)
    formData.append('mime_type', file.type || 'application/octet-stream')

    const operation = async (): Promise<UploadResult> => {
      const response = await apiService.post<UploadResult>('/v4/assets/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100)
            onProgress(progress)
          }
        },
        signal
      })

      return response
    }

    const result = await withRetry(operation, {
      maxAttempts: 3,
      initialDelay: 1000,
      ...retryOptions
    })

    if (!result.success) {
      throw result.error
    }

    return result.data!
  }

  /**
   * Chunked upload for larger files
   */
  private async uploadChunked(
    file: File,
    chunkSize: number,
    onProgress?: (progress: number) => void,
    signal?: AbortSignal,
    retryOptions?: Parameters<typeof withRetry>[1]
  ): Promise<UploadResult> {
    const totalChunks = Math.ceil(file.size / chunkSize)
    const uploadId = crypto.randomUUID()

    // Initialize chunked upload
    await apiService.post('/v4/assets/upload/init/', {
      filename: file.name,
      mime_type: file.type || 'application/octet-stream',
      total_size: file.size,
      total_chunks: totalChunks,
      upload_id: uploadId
    })

    let uploadedBytes = 0

    // Upload chunks
    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
      const start = chunkIndex * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const chunk = file.slice(start, end)

      const operation = async (): Promise<ChunkUploadResult> => {
        const formData = new FormData()
        formData.append('chunk', chunk)
        formData.append('chunk_index', chunkIndex.toString())
        formData.append('upload_id', uploadId)

        return apiService.post<ChunkUploadResult>('/v4/assets/upload/chunk/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          signal
        })
      }

      const result = await withRetry(operation, {
        maxAttempts: 3,
        initialDelay: 1000,
        ...retryOptions
      })

      if (!result.success) {
        throw result.error
      }

      uploadedBytes += chunk.size

      if (onProgress) {
        const progress = Math.round((uploadedBytes / file.size) * 100)
        onProgress(progress)
      }

      options.onChunkComplete?.(chunkIndex + 1, totalChunks)
    }

    // Finalize upload
    const finalizeResult = await apiService.post<UploadResult>('/v4/assets/upload/finalize/', {
      upload_id: uploadId
    })

    return finalizeResult
  }

  /**
   * Validate file before upload
   */
  private validateFile(file: File): void {
    if (file.size > this.MAX_FILE_SIZE) {
      throw new ApiError(
        `File size (${this.formatBytes(file.size)}) exceeds maximum allowed size (${this.formatBytes(this.MAX_FILE_SIZE)})`,
        413
      )
    }

    // Check file type (basic validation)
    const allowedTypes = [
      'image/',
      'video/',
      'audio/',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'application/zip',
      'application/x-rar-compressed',
      'text/'
    ]

    const isAllowed = allowedTypes.some(type => file.type.startsWith(type) || type.endsWith(file.type.split('/')[1]))
    if (!isAllowed && file.type !== '') {
      throw new ApiError(`File type ${file.type} is not allowed`, 415)
    }

    // Check filename
    if (!file.name || file.name.trim().length === 0) {
      throw new ApiError('Filename cannot be empty', 400)
    }

    // Check for potentially dangerous filenames
    const dangerousPatterns = [
      /\.\./,  // Directory traversal
      /^[.-]/, // Hidden files starting with . or -
      /[<>:"|?*\x00-\x1f]/, // Invalid characters
    ]

    if (dangerousPatterns.some(pattern => pattern.test(file.name))) {
      throw new ApiError('Filename contains invalid characters', 400)
    }
  }

  /**
   * Format bytes to human readable format
   */
  private formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B'

    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  /**
   * Resume interrupted chunked upload
   */
  async resumeUpload(uploadId: string, file: File, options: UploadOptions = {}): Promise<UploadResult> {
    // Check upload status
    const status = await apiService.get(`/v4/assets/upload/status/${uploadId}/`)

    if (status.completed) {
      // Upload already completed
      return status.result
    }

    // Resume from next chunk
    const nextChunk = status.uploaded_chunks + 1
    const chunkSize = options.chunkSize || this.DEFAULT_CHUNK_SIZE

    // Continue chunked upload from next chunk
    return this.uploadChunkedFrom(file, nextChunk, chunkSize, uploadId, options)
  }

  /**
   * Upload chunks starting from specific chunk index
   */
  private async uploadChunkedFrom(
    file: File,
    startChunk: number,
    chunkSize: number,
    uploadId: string,
    options: UploadOptions
  ): Promise<UploadResult> {
    const totalChunks = Math.ceil(file.size / chunkSize)

    for (let chunkIndex = startChunk; chunkIndex < totalChunks; chunkIndex++) {
      const start = chunkIndex * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const chunk = file.slice(start, end)

      const operation = async (): Promise<ChunkUploadResult> => {
        const formData = new FormData()
        formData.append('chunk', chunk)
        formData.append('chunk_index', chunkIndex.toString())
        formData.append('upload_id', uploadId)

        return apiService.post<ChunkUploadResult>('/v4/assets/upload/chunk/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          signal: options.signal
        })
      }

      const result = await withRetry(operation, {
        maxAttempts: 3,
        initialDelay: 1000,
        ...options.retryOptions
      })

      if (!result.success) {
        throw result.error
      }

      options.onChunkComplete?.(chunkIndex + 1, totalChunks)
    }

    // Finalize upload
    const finalizeResult = await apiService.post<UploadResult>('/v4/assets/upload/finalize/', {
      upload_id: uploadId
    })

    return finalizeResult
  }
}

export const uploadService = new UploadService()





