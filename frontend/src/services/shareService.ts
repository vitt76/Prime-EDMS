import type { CreateSharePayload, ShareLink } from '@/types/share'
import { apiService } from './apiService'

class ShareService {
  async listShares(assetId: number): Promise<ShareLink[]> {
    return apiService.get<ShareLink[]>(`/v4/assets/${assetId}/shares/`, undefined, false)
  }

  async createShare(assetId: number, payload: CreateSharePayload): Promise<ShareLink> {
    return apiService.post<ShareLink>(`/v4/assets/${assetId}/shares/`, payload)
  }

  async revokeShare(shareId: number): Promise<void> {
    return apiService.delete<void>(`/v4/shares/${shareId}/`)
  }
}

export const shareService = new ShareService()

