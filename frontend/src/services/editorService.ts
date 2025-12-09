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

export async function createAssetFromImage(
  documentTypeId: number,
  blob: Blob,
  filename: string,
  options?: {
    format?: string
    comment?: string
  }
): Promise<{ documentId: number; fileId: number }> {
  // 1) create document
  const docPayload = {
    document_type_id: documentTypeId,
    label: filename,
    description: options?.comment || 'Создано из копии'
  }

  const docResp = await apiService.post('/api/v4/documents/', docPayload)
  const documentId = docResp.data?.id
  if (!documentId) {
    throw new Error('Не удалось создать документ для копии')
  }

  // 2) upload file
  const extension = (options?.format || 'jpeg').toLowerCase()
  const formData = new FormData()
  formData.append('file', blob, filename || `copy.${extension}`)
  formData.append('action', '1') // DocumentFileActionUseNewPages.backend_id

  const fileResp = await apiService.post(
    `/api/v4/documents/${documentId}/files/`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  )

  return {
    documentId,
    fileId: fileResp.data?.id
  }
}

export default {
  saveEditedImage,
  createAssetFromImage
}

