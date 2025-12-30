import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { analyticsService } from '@/services/analyticsService'

export interface AssetBankTopMetrics {
  total_assets: number
  storage_used_bytes: number
  mau: number
  search_success_rate: number
  avg_find_time_minutes: number | null
  cdn_cost_per_month?: number | null
}

export interface AssetDistributionItem {
  type: 'images' | 'videos' | 'documents' | 'other'
  count: number
  size_bytes: number
}

export interface AssetDistributionTrendMonth {
  month: string
  distribution: Array<{ type: AssetDistributionItem['type']; count: number }>
}

export interface MostDownloadedAssetRow {
  document_id: number
  document__label: string
  downloads: number
  views: number
  shares: number
}

export interface AssetReuseMonthlyPoint {
  month: string
  reuse_rate: number
  reused_assets: number
  total_assets: number
}

export interface AssetReuseMetrics {
  monthly_data: AssetReuseMonthlyPoint[]
  current_rate: number
  target_rate: number
  estimated_savings_usd: number
  production_cost_per_asset_usd: number
}

export interface StorageTrendsPoint {
  month: string
  total_gb: number
  by_type: Record<'images' | 'videos' | 'documents' | 'other', number>
}

export interface StorageTrendsResponse {
  historical: StorageTrendsPoint[]
  forecast: StorageTrendsPoint[]
  current_storage_gb: number
  storage_limit_gb: number
  alert_threshold: number
}

export interface UserAdoptionHeatmapCell {
  department: string
  region: string
  mau: number
}

export interface UserAdoptionHeatmapResponse {
  heatmap_data: UserAdoptionHeatmapCell[]
  departments: string[]
  regions: string[]
}

// Campaign Performance (Phase 2)
export interface CampaignListItem {
  id: string
  label: string
  status: string
  start_date?: string | null
  end_date?: string | null
  updated_at?: string | null
  cost_amount?: string | null
  revenue_amount?: string | null
  currency?: string | null
}

export interface CampaignDashboardResponse {
  campaign: {
    id: string
    label: string
    status: string
    assets_count: number
    roi: number | null
    avg_engagement_minutes?: number | null
    cost_amount: any
    revenue_amount: any
    currency: string
    updated_at: string
  } | null
  timeline: Array<{ timestamp__date: string; views: number; downloads: number }>
  channels: Array<{ channel: string; views: number; downloads: number }>
  baseline?: {
    campaign: { id: string; label: string }
    timeline: Array<{ timestamp__date: string; views: number; downloads: number }>
  } | null
}

export interface CampaignTopAssetRow {
  document_id: number
  document__label: string
  downloads: number
  views: number
  shares: number
  bandwidth_gb: number
  engagement_score: number | null
  sparkline_data: number[]
}

export interface CampaignTopAssetsResponse {
  campaign: { id: string; label: string } | null
  results: CampaignTopAssetRow[]
}

export interface CampaignTimelineResponse {
  campaign: { id: string; label: string; status: string } | null
  milestones: Array<{ type: string; date: string; label: string; views?: number; downloads?: number }>
  velocity: Record<string, number>
}

export interface AnalyticsAlertRow {
  id: number
  alert_type: string
  severity: 'critical' | 'warning' | 'info'
  title: string
  message: string
  document_id: number | null
  campaign_id: string | null
  created_at: string
  metadata: Record<string, any>
}

export interface RoiSummaryResponse {
  assumptions: Record<string, any>
  measured: { mau: number; reuse_rate: number }
  breakdown: {
    time_savings_usd: number
    reuse_savings_usd: number
    compliance_savings_usd: number
    storage_savings_usd: number
  }
  total_benefits_usd: number
  dam_monthly_cost_usd: number
  roi_percent: number | null
}

export const useAnalyticsStore = defineStore('analytics', () => {
  // Asset Bank state
  const assetBankTopMetrics = ref<AssetBankTopMetrics | null>(null)
  const assetDistribution = ref<AssetDistributionItem[]>([])
  const assetDistributionTrend = ref<AssetDistributionTrendMonth[]>([])
  const mostDownloadedAssets = ref<MostDownloadedAssetRow[]>([])
  const assetReuseMetrics = ref<AssetReuseMetrics | null>(null)
  const storageTrends = ref<StorageTrendsResponse | null>(null)
  const userAdoptionHeatmap = ref<UserAdoptionHeatmapResponse | null>(null)
  const assetBankAlerts = ref<AnalyticsAlertRow[]>([])
  const roiSummary = ref<RoiSummaryResponse | null>(null)

  // Campaign Performance state
  const campaigns = ref<CampaignListItem[]>([])
  const selectedCampaignId = ref<string | null>(null)
  const campaignDashboard = ref<CampaignDashboardResponse | null>(null)
  const campaignTopAssets = ref<CampaignTopAssetRow[]>([])
  const campaignTimeline = ref<CampaignTimelineResponse | null>(null)

  // Release 3 foundation: Distribution + Content Intelligence
  const distributionDashboard = ref<any | null>(null)
  const contentGaps = ref<any | null>(null)
  const metadataComplianceAlerts = ref<any | null>(null)

  // Common state
  const isLoading = ref(false)
  const lastUpdated = ref<Date | null>(null)
  const error = ref<string | null>(null)

  // User activity state (Release 2)
  const userLoginPatterns = ref<any | null>(null)
  const userCohorts = ref<any | null>(null)
  const featureAdoption = ref<any | null>(null)

  // Approval analytics state (Release 2)
  const approvalSummary = ref<any | null>(null)
  const approvalTimeseries = ref<any | null>(null)
  const approvalRecommendations = ref<any | null>(null)

  // Cross-chart filters (Asset Bank)
  const filters = ref<{
    dateRange: [string, string] | null
    assetType: 'images' | 'videos' | 'documents' | 'other' | null
    department: string | null
    owner: string | null
  }>({
    dateRange: null,
    assetType: null,
    department: null,
    owner: null,
  })

  const hasData = computed(() => {
    return (
      !!assetBankTopMetrics.value ||
      assetDistribution.value.length > 0 ||
      assetDistributionTrend.value.length > 0 ||
      mostDownloadedAssets.value.length > 0 ||
      !!assetReuseMetrics.value ||
      !!storageTrends.value ||
      !!userAdoptionHeatmap.value ||
      assetBankAlerts.value.length > 0
    )
  })

  async function fetchAssetBankTopMetrics(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      assetBankTopMetrics.value = await analyticsService.getAssetBankTopMetrics()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить метрики'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAssetDistribution(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      assetDistribution.value = await analyticsService.getAssetDistribution()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить распределение ассетов'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAssetDistributionTrend(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      assetDistributionTrend.value = await analyticsService.getAssetDistributionTrend()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить тренд распределения'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMostDownloadedAssets(params?: {
    date_from?: string
    date_to?: string
    asset_type?: 'images' | 'videos' | 'documents' | 'other'
    department?: string
    owner?: string
  }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const effectiveParams = params || {}
      if (!effectiveParams.date_from && !effectiveParams.date_to && filters.value.dateRange) {
        effectiveParams.date_from = filters.value.dateRange[0]
        effectiveParams.date_to = filters.value.dateRange[1]
      }
      if (!effectiveParams.asset_type && filters.value.assetType) {
        effectiveParams.asset_type = filters.value.assetType
      }
      if (!effectiveParams.department && filters.value.department) {
        effectiveParams.department = filters.value.department
      }
      if (!effectiveParams.owner && filters.value.owner) {
        effectiveParams.owner = filters.value.owner
      }

      mostDownloadedAssets.value = await analyticsService.getMostDownloadedAssets(effectiveParams)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить топ скачиваний'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAssetReuseMetrics(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      assetReuseMetrics.value = await analyticsService.getAssetReuseMetrics()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить метрики переиспользования'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchStorageTrends(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      storageTrends.value = await analyticsService.getStorageTrends()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить тренды хранилища'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUserAdoptionHeatmap(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      userAdoptionHeatmap.value = await analyticsService.getUserAdoptionHeatmap()
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить adoption heatmap'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUserLoginPatterns(params?: { days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      userLoginPatterns.value = await analyticsService.getUserLoginPatterns(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить login patterns'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUserCohorts(params?: { cohort_weeks?: number; retention_weeks?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      userCohorts.value = await analyticsService.getUserCohorts(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить cohorts'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchFeatureAdoption(params?: { days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      featureAdoption.value = await analyticsService.getFeatureAdoption(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить feature adoption'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchDistributionDashboard(params?: { days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      distributionDashboard.value = await analyticsService.getDistributionDashboard(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить Distribution dashboard'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchContentGaps(params?: { days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      contentGaps.value = await analyticsService.getContentGaps(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить Content Gaps'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMetadataComplianceAlerts(params?: { limit?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      metadataComplianceAlerts.value = await analyticsService.getMetadataComplianceAlerts(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить metadata compliance alerts'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCampaigns(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      campaigns.value = (await analyticsService.getCampaigns()) as CampaignListItem[]
      if (!selectedCampaignId.value && campaigns.value.length > 0) {
        selectedCampaignId.value = campaigns.value[0].id
      }
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить кампании'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCampaignDashboard(params?: { campaign_id?: string; days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const campaign_id = params?.campaign_id || selectedCampaignId.value || undefined
      campaignDashboard.value = (await analyticsService.getCampaignDashboard({
        ...params,
        campaign_id,
      })) as CampaignDashboardResponse
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить дашборд кампании'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCampaignTopAssets(params?: { campaign_id?: string; days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const campaign_id = params?.campaign_id || selectedCampaignId.value || undefined
      const data = (await analyticsService.getCampaignTopAssets({
        ...params,
        campaign_id,
      })) as CampaignTopAssetsResponse
      campaignTopAssets.value = data?.results || []
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить топ ассетов кампании'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCampaignTimeline(params?: { campaign_id?: string; days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const campaign_id = params?.campaign_id || selectedCampaignId.value || undefined
      campaignTimeline.value = (await analyticsService.getCampaignTimeline({
        ...params,
        campaign_id,
      })) as CampaignTimelineResponse
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить timeline кампании'
    } finally {
      isLoading.value = false
    }
  }

  async function selectCampaign(campaignId: string | null): Promise<void> {
    selectedCampaignId.value = campaignId
    await Promise.all([fetchCampaignDashboard(), fetchCampaignTopAssets(), fetchCampaignTimeline()])
  }

  async function fetchAssetBankAlerts(params?: { limit?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      assetBankAlerts.value = (await analyticsService.getAssetBankAlerts(params)) as AnalyticsAlertRow[]
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить alerts'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRoiSummary(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      roiSummary.value = (await analyticsService.getRoiSummary()) as RoiSummaryResponse
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить ROI'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchApprovalSummary(params?: { days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      approvalSummary.value = await analyticsService.getApprovalSummary(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить approvals summary'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchApprovalTimeseries(params?: { days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      approvalTimeseries.value = await analyticsService.getApprovalTimeseries(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить approvals timeseries'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchApprovalRecommendations(params?: { days?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      approvalRecommendations.value = await analyticsService.getApprovalRecommendations(params)
      lastUpdated.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Не удалось загрузить approvals recommendations'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchAssetBankAll(): Promise<void> {
    await Promise.all([
      fetchAssetBankTopMetrics(),
      fetchAssetDistribution(),
      fetchAssetDistributionTrend(),
      fetchMostDownloadedAssets(),
      fetchAssetReuseMetrics(),
      fetchStorageTrends(),
      fetchUserAdoptionHeatmap(),
      fetchAssetBankAlerts(),
    ])
  }

  function setDateRange(range: [string, string] | null): void {
    filters.value.dateRange = range
  }

  function setAssetType(type: 'images' | 'videos' | 'documents' | 'other' | null): void {
    filters.value.assetType = type
  }

  function setDepartment(department: string | null): void {
    filters.value.department = department
  }

  function setOwner(owner: string | null): void {
    filters.value.owner = owner
  }

  async function applyFilters(): Promise<void> {
    await fetchAssetBankAll()
  }

  return {
    // state
    assetBankTopMetrics,
    assetDistribution,
    assetDistributionTrend,
    mostDownloadedAssets,
    assetReuseMetrics,
    storageTrends,
    userAdoptionHeatmap,
    assetBankAlerts,
    roiSummary,
    userLoginPatterns,
    userCohorts,
    featureAdoption,
    approvalSummary,
    approvalTimeseries,
    approvalRecommendations,
    distributionDashboard,
    contentGaps,
    metadataComplianceAlerts,
    isLoading,
    lastUpdated,
    error,
    filters,
    // computed
    hasData,
    // actions
    fetchAssetBankTopMetrics,
    fetchAssetDistribution,
    fetchAssetDistributionTrend,
    fetchMostDownloadedAssets,
    fetchAssetReuseMetrics,
    fetchStorageTrends,
    fetchUserAdoptionHeatmap,
    fetchAssetBankAlerts,
    fetchRoiSummary,
    fetchUserLoginPatterns,
    fetchUserCohorts,
    fetchFeatureAdoption,
    fetchApprovalSummary,
    fetchApprovalTimeseries,
    fetchApprovalRecommendations,
    fetchDistributionDashboard,
    fetchContentGaps,
    fetchMetadataComplianceAlerts,
    fetchAssetBankAll,
    setDateRange,
    setAssetType,
    setDepartment,
    setOwner,
    applyFilters,

    // Campaign Performance state
    campaigns,
    selectedCampaignId,
    campaignDashboard,
    campaignTopAssets,
    campaignTimeline,
    // Campaign Performance actions
    fetchCampaigns,
    fetchCampaignDashboard,
    fetchCampaignTopAssets,
    fetchCampaignTimeline,
    selectCampaign,
  }
})


