import { apiService } from './apiService'

export interface YandexDiskEntry {
  name: string
  path: string
  type: 'dir' | 'file'
  size?: number
}

export interface YandexDiskFolderResponse {
  path: string
  folders: YandexDiskEntry[]
  files: YandexDiskEntry[]
  total_count: number
}

class YandexDiskService {
  encodePath(path: string): string {
    // Base64 URL-safe encoding with proper UTF-8 support
    // Convert string to UTF-8 bytes, then to base64 URL-safe
    const utf8Bytes = new TextEncoder().encode(path)
    // Convert bytes to binary string in chunks to avoid "Maximum call stack size exceeded"
    let binaryString = ''
    for (let i = 0; i < utf8Bytes.length; i += 8192) {
      const chunk = utf8Bytes.slice(i, i + 8192)
      binaryString += String.fromCharCode(...chunk)
    }
    const base64 = btoa(binaryString)
    return base64
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/u, '')
  }

  async getFolderContents(path: string): Promise<YandexDiskFolderResponse> {
    const safePath = path || 'disk:/'
    const encodedPath = this.encodePath(safePath)
    const result = await apiService.get<YandexDiskFolderResponse>(
      `/api/v4/dam/yandex-disk/folders/${encodedPath}/`
    )
    return result as unknown as YandexDiskFolderResponse
  }

  async copyToDAM(payload: {
    yandexPath: string
    documentTypeId?: number
    cabinetId?: number
    label?: string
  }): Promise<{ documentId: number }> {
    const body: any = {
      yandex_path: payload.yandexPath,
      document_type_id: payload.documentTypeId,
      cabinet_id: payload.cabinetId,
      label: payload.label
    }

    const result: any = await apiService.post(
      '/api/v4/dam/yandex-disk/copy-to-dam/',
      body
    )

    return {
      documentId: result.document_id ?? result.documentId
    }
  }

  async copyFromDAM(payload: {
    documentId: number
    yandexPath: string
    filename?: string
  }): Promise<{ path: string }> {
    const body: any = {
      document_id: payload.documentId,
      yandex_path: payload.yandexPath,
      filename: payload.filename
    }

    const result: any = await apiService.post(
      '/api/v4/dam/yandex-disk/copy-from-dam/',
      body
    )

    return {
      path: result.path
    }
  }
}

export const yandexDiskService = new YandexDiskService()


