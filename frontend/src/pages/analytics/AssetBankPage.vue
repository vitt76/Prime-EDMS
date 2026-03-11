<template>
  <div class="container mx-auto px-4 py-6">
      <div class="flex justify-end mb-4">
        <button
          type="button"
          class="px-4 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          @click="showReportModal = true"
        >
          Сформировать отчёт
        </button>
      </div>

      <FilterBar
        class="mb-6"
        :date-range="analyticsStore.filters.dateRange"
        :asset-type="analyticsStore.filters.assetType"
        :department="analyticsStore.filters.department"
        @apply="handleApplyFilters"
        @clear="handleClearFilters"
      />

      <TopMetricsCard
        :metrics="analyticsStore.assetBankTopMetrics"
        :last-updated="analyticsStore.lastUpdated"
        :is-loading="analyticsStore.isLoading"
        :error="analyticsStore.error"
        @refresh="refreshAll"
      />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <AssetDistributionChart
          :distribution="analyticsStore.assetDistribution"
          :trend="analyticsStore.assetDistributionTrend"
          @select-type="handleSelectAssetType"
        />
        <MostDownloadedAssetsTable
          :rows="analyticsStore.mostDownloadedAssets"
          @select="handleSelectAsset"
        />
      </div>

      <div class="mt-6">
        <AssetReuseMetricsChart
          :monthly-data="analyticsStore.assetReuseMetrics?.monthly_data || []"
          :target-rate="analyticsStore.assetReuseMetrics?.target_rate || 62"
        />
      </div>

      <div class="mt-6">
        <StorageTrendsChart
          :historical="analyticsStore.storageTrends?.historical || []"
          :forecast="analyticsStore.storageTrends?.forecast || []"
          :storage-limit-gb="analyticsStore.storageTrends?.storage_limit_gb || 0"
          :alert-threshold="analyticsStore.storageTrends?.alert_threshold || 0"
        />
      </div>

      <div class="mt-6">
        <div
          v-if="analyticsStore.dashboardGeographyError"
          class="mb-3 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {{ analyticsStore.dashboardGeographyError }}
        </div>
        <GeoMap
          :rows="analyticsStore.dashboardGeography"
          :days="30"
        />
      </div>

      <div class="mt-6">
        <UserAdoptionHeatMap
          :heatmap-data="analyticsStore.userAdoptionHeatmap?.heatmap_data || []"
          :departments="analyticsStore.userAdoptionHeatmap?.departments || []"
          :regions="analyticsStore.userAdoptionHeatmap?.regions || []"
        />
      </div>

      <div class="mt-6">
        <AlertsList :rows="analyticsStore.assetBankAlerts" />
      </div>
  </div>

  <AssetDetailModal
    :open="assetDetailModalOpen"
    :document-id="selectedAsset?.document_id ?? null"
    :document-label="selectedAsset?.document__label ?? null"
    @close="assetDetailModalOpen = false"
  />

  <ReportGenerateModal
    :is-open="showReportModal"
    @close="showReportModal = false"
  />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { buildAnalyticsWebSocketUrl } from '@/utils/constants'

import AssetDistributionChart from '@/components/Analytics/AssetDistributionChart.vue'
import AssetDetailModal from '@/components/Analytics/AssetDetailModal.vue'
import AssetReuseMetricsChart from '@/components/Analytics/AssetReuseMetricsChart.vue'
import AlertsList from '@/components/Analytics/AlertsList.vue'
import FilterBar from '@/components/Analytics/FilterBar.vue'
import GeoMap from '@/components/Analytics/GeoMap.vue'
import MostDownloadedAssetsTable from '@/components/Analytics/MostDownloadedAssetsTable.vue'
import StorageTrendsChart from '@/components/Analytics/StorageTrendsChart.vue'
import TopMetricsCard from '@/components/Analytics/TopMetricsCard.vue'
import ReportGenerateModal from '@/components/Analytics/ReportGenerateModal.vue'
import UserAdoptionHeatMap from '@/components/Analytics/UserAdoptionHeatMap.vue'
import { useAnalyticsStore } from '@/stores/analyticsStore'
import type { MostDownloadedAssetRow } from '@/stores/analyticsStore'

const analyticsStore = useAnalyticsStore()
const selectedAsset = ref<MostDownloadedAssetRow | null>(null)
const assetDetailModalOpen = ref(false)
const showReportModal = ref(false)
let ws: WebSocket | null = null

function getToken(): string | null {
  try {
    return localStorage.getItem('auth_token')
  } catch {
    return null
  }
}

function getOrganizationId(): string | null {
  try {
    return localStorage.getItem('current_organization_id')
  } catch {
    return null
  }
}

async function refreshAll(): Promise<void> {
  await Promise.all([
    analyticsStore.fetchAssetBankAll(),
    analyticsStore.fetchDashboardGeography({ days: 30 }),
  ])
}

async function handleApplyFilters(payload: {
  dateRange: [string, string] | null
  assetType: 'images' | 'videos' | 'documents' | 'other' | null
  department: string | null
}): Promise<void> {
  analyticsStore.setDateRange(payload.dateRange)
  analyticsStore.setAssetType(payload.assetType)
  analyticsStore.setDepartment(payload.department)
  await analyticsStore.applyFilters()
}

async function handleClearFilters(): Promise<void> {
  analyticsStore.setDateRange(null)
  analyticsStore.setAssetType(null)
  analyticsStore.setDepartment(null)
  await analyticsStore.applyFilters()
}

async function handleSelectAssetType(type: 'images' | 'videos' | 'documents' | 'other'): Promise<void> {
  analyticsStore.setAssetType(type)
  await analyticsStore.applyFilters()
}

function handleSelectAsset(row: MostDownloadedAssetRow): void {
  selectedAsset.value = row
  assetDetailModalOpen.value = true
}

onMounted(async () => {
  await refreshAll()

  // Real-time updates (best-effort). Requires backend Channels route: /ws/analytics/
  try {
    ws = new WebSocket(
      buildAnalyticsWebSocketUrl(getToken(), getOrganizationId())
    )
    ws.onmessage = async (event) => {
      try {
        const payload = JSON.parse(event.data || '{}')
        if (
          ['analytics_refresh', 'refresh'].includes(payload?.type) &&
          !analyticsStore.isLoading
        ) {
          await refreshAll()
        }
      } catch {
        // ignore
      }
    }
  } catch {
    ws = null
  }
})

onUnmounted(() => {
  try {
    ws?.close()
  } catch {
    // ignore
  }
  ws = null
})
</script>


