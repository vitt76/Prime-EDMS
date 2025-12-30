import { apiService } from './apiService'

import type {
  AssetBankTopMetrics,
  AssetDistributionItem,
  AssetDistributionTrendMonth,
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

  async getAssetDistributionTrend(): Promise<AssetDistributionTrendMonth[]> {
    const data = await apiService.get<{ trend: AssetDistributionTrendMonth[] }>(
      '/api/v4/headless/analytics/dashboard/assets/distribution-trend/',
      undefined,
      false
    )
    return data?.trend || []
  }

  async getAssetDetail(params: { document_id: number; days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/assets/detail/',
      ({ params } as any) ?? undefined,
      false
    )
  }

  async getMostDownloadedAssets(params?: {
    date_from?: string
    date_to?: string
    asset_type?: 'images' | 'videos' | 'documents' | 'other'
    department?: string
    owner?: string
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

  async getUserLoginPatterns(params?: { days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/users/login-patterns/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getUserCohorts(params?: { cohort_weeks?: number; retention_weeks?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/users/cohorts/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getFeatureAdoption(params?: { days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/users/feature-adoption/',
      params ? ({ params } as any) : undefined,
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

  async getCampaignGeography(params?: { campaign_id?: string; days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/campaigns/geography/',
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

  async getApprovalSummary(params?: { days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/approvals/summary/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getApprovalTimeseries(params?: { days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/approvals/timeseries/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getApprovalRecommendations(params?: { days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/approvals/recommendations/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async postCampaignEngagement(campaignId: string, payload: { duration_seconds: number; session_start?: string; session_end?: string }): Promise<any> {
    return apiService.post<any>(`/api/v4/headless/analytics/campaigns/${campaignId}/engagement/`, payload)
  }

  async trackSearchClick(payload: {
    document_id: number
    search_query_id?: number | null
    search_session_id?: string | null
    click_position?: number | null
    time_to_click_seconds?: number | null
  }): Promise<void> {
    await apiService.post('/api/v4/headless/analytics/track/search/click/', payload)
  }

  // Release 3 foundation: Distribution Analytics
  async getDistributionDashboard(params?: { days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/distribution/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async ingestDistributionEvents(payload: { channel: string; events: any[] }): Promise<any> {
    return apiService.post<any>('/api/v4/headless/analytics/ingest/distribution-events/', payload)
  }

  // Release 3 foundation: Content Intelligence (MVP)
  async getContentGaps(params?: { days?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/content-intel/content-gaps/',
      params ? ({ params } as any) : undefined,
      false
    )
  }

  async getMetadataComplianceAlerts(params?: { limit?: number }): Promise<any> {
    return apiService.get<any>(
      '/api/v4/headless/analytics/dashboard/content-intel/compliance/metadata/',
      params ? ({ params } as any) : undefined,
      false
    )
  }
}

export const analyticsService = new AnalyticsService()


