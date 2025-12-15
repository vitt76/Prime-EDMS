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
  // The web editor already outputs the desired format. Do NOT ask backend to
  // reconvert via `format` to avoid BytesIO conversion edge cases.
  const extension = (options?.format || 'jpeg').toLowerCase()
  formData.append('file', blob, `edited.${extension}`)
  formData.append('comment', options?.comment || 'Edited via Web Editor')

  const data = await apiService.post<SaveEditedImageResponse>(
    `/api/v4/headless/documents/${documentId}/versions/new_from_edit/`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    } as any
  )

  return data
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

  const docResp: any = await apiService.post('/api/v4/documents/', docPayload)
  const documentId = docResp?.id || docResp?.data?.id
  if (!documentId) {
    throw new Error('Не удалось создать документ для копии')
  }

  // 2) upload file
  const extension = (options?.format || 'jpeg').toLowerCase()
  const formData = new FormData()
  // Mayan expects `file_new` for document file upload.
  formData.append('file_new', blob, filename || `copy.${extension}`)
  formData.append('action', '1') // DocumentFileActionUseNewPages.action_id
  formData.append('filename', filename || `copy.${extension}`)
  if (options?.comment) formData.append('comment', options.comment)

  await apiService.post(
    `/api/v4/documents/${documentId}/files/`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    } as any
  )

  // Upload is async (202). Poll until the first file appears.
  let fileId: number = 0
  const maxAttempts = 12
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    await new Promise((r) => setTimeout(r, 1500))
    try {
      const filesResponse: any = await apiService.get(
        `/api/v4/documents/${documentId}/files/`,
        { params: { page_size: 5 } } as any,
        false
      )
      const results = Array.isArray(filesResponse?.results)
        ? filesResponse.results
        : (Array.isArray(filesResponse) ? filesResponse : [])
      if (results.length) {
        // newest first
        results.sort((a: any, b: any) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        fileId = Number(results[0]?.id) || 0
        break
      }
    } catch {
      // keep polling
    }
  }

  return {
    documentId,
    fileId
  }
}

export default {
  saveEditedImage,
  createAssetFromImage
}

