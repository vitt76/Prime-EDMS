export type FileUploadStatus = 'pending' | 'uploading' | 'success' | 'failed' | 'cancelled'

export interface FileUploadProgress {
  file: File
  hash: string
  name: string
  size: number
  type: string
  status: FileUploadStatus
  progress: number
  uploadedBytes: number
  speed: string
  eta: string
  error: string | null
  startedAt?: number
  lastProgressAt?: number
  abortController?: AbortController
}

