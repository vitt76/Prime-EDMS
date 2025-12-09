import { apiService } from './apiService'

interface SaveEditedImageResponse {
  success: boolean
  document_id: number
  file_id: number
  version_id: number | null
  version?: any
}

export async function saveEditedImage(
  documentId: number,
  blob: Blob,
  options?: {
    format?: string
    comment?: string
  }
): Promise<SaveEditedImageResponse> {
  const formData = new FormData()
  const extension = (options?.format || 'jpeg').toLowerCase()
  formData.append('file', blob, `edited.${extension}`)
  if (options?.format) formData.append('format', options.format)
  formData.append('comment', options?.comment || 'Edited via Web Editor')

  const { data } = await apiService.post(
    `/api/v4/headless/documents/${documentId}/versions/new_from_edit/`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  )

  return data as SaveEditedImageResponse
}

export default {
  saveEditedImage
}

