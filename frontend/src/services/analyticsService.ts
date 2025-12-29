import { apiService } from './apiService'

import type {
  AssetBankTopMetrics,
  AssetDistributionItem,
  MostDownloadedAssetRow,
} from '@/stores/analyticsStore'

class AnalyticsService {
  async getAssetBankTopMetrics(): Promise<AssetBankTopMetrics> {
    return apiService.get<AssetBankTopMetrics>(
      '/api/v4/headless/analytics/dashboard/assets/top-metrics/',
      undefined,
      false
    )
  }

  async getAssetDistribution(): Promise<AssetDistributionItem[]> {
    const data = await apiService.get<{ distribution: AssetDistributionItem[] }>(
      '/api/v4/headless/analytics/dashboard/assets/distribution/',
      undefined,
      false
    )

    return data?.distribution || []
  }

  async getMostDownloadedAssets(params?: {
    date_from?: string
    date_to?: string
  }): Promise<MostDownloadedAssetRow[]> {
    const data = await apiService.get<{ results: MostDownloadedAssetRow[] }>(
      '/api/v4/headless/analytics/dashboard/assets/most-downloaded/',
      params ? ({ params } as any) : undefined,
      false
    )

    return data?.results || []
  }
}

export const analyticsService = new AnalyticsService()


