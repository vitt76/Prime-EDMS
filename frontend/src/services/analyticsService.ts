import { apiService } from './apiService'

import type {
  AssetBankTopMetrics,
  AssetDistributionItem,
  AssetReuseMetrics,
  MostDownloadedAssetRow,
  StorageTrendsResponse,
  UserAdoptionHeatmapResponse,
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
    asset_type?: 'images' | 'videos' | 'documents' | 'other'
  }): Promise<MostDownloadedAssetRow[]> {
    const data = await apiService.get<{ results: MostDownloadedAssetRow[] }>(
      '/api/v4/headless/analytics/dashboard/assets/most-downloaded/',
      params ? ({ params } as any) : undefined,
      false
    )

    return data?.results || []
  }

  async getAssetReuseMetrics(): Promise<AssetReuseMetrics> {
    return apiService.get<AssetReuseMetrics>(
      '/api/v4/headless/analytics/dashboard/assets/reuse-metrics/',
      undefined,
      false
    )
  }

  async getStorageTrends(): Promise<StorageTrendsResponse> {
    return apiService.get<StorageTrendsResponse>(
      '/api/v4/headless/analytics/dashboard/assets/storage-trends/',
      undefined,
      false
    )
  }

  async getUserAdoptionHeatmap(): Promise<UserAdoptionHeatmapResponse> {
    return apiService.get<UserAdoptionHeatmapResponse>(
      '/api/v4/headless/analytics/dashboard/users/adoption-heatmap/',
      undefined,
      false
    )
  }

  async getCampaigns(): Promise<any[]> {
    const data = await apiService.get<{ results: any[] }>(
      '/api/v4/headless/analytics/campaigns/',
      undefined,
      false
    )
    return data?.results || []
  }

  async getCampaignDashboard(params?: { campaign_id?: string; days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/campaigns/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getCampaignTopAssets(params?: { campaign_id?: string; days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/campaigns/top-assets/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getCampaignTimeline(params?: { campaign_id?: string; days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/campaigns/timeline/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getAssetBankAlerts(params?: { limit?: number }): Promise<any[]> {
    const data = await apiService.get<{ results: any[] }>(
      '/api/v4/headless/analytics/dashboard/assets/alerts/',
      params ? ({ params } as any) : undefined,
      false
    )
    return data?.results || []
  }

  async getRoiSummary(): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/roi/summary/',
      undefined,
      false
    )
  }
}

export const analyticsService = new AnalyticsService()


