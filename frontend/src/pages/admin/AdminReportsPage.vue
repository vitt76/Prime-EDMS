<template>
  <div class="reports-page">
    <!-- Toolbar -->
    <div class="reports-toolbar">
      <h1 class="reports-toolbar__title">Analytics & Reports</h1>

      <div class="reports-toolbar__controls">
        <!-- Time Range Selector -->
        <Select
          v-model="selectedTimeRange"
          :options="timeRangeOptions"
          label="Period"
          class="reports-toolbar__select"
        />

        <!-- Custom Date Range (if 'custom' selected) -->
        <DateRangePicker
          v-if="selectedTimeRange === 'custom'"
          v-model="customDateRange"
          class="reports-toolbar__date-picker"
        />

        <!-- Export Button -->
        <div class="reports-toolbar__export" ref="exportMenuRef">
          <Button
            variant="secondary"
            @click="showExportMenu = !showExportMenu"
            aria-label="Export report"
            aria-haspopup="true"
            :aria-expanded="showExportMenu"
            data-testid="reports-export-trigger"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Export
          </Button>

          <!-- Export Menu -->
          <Transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="showExportMenu"
              class="export-menu"
              role="menu"
              aria-label="Export options"
            >
              <button
                class="export-menu__item"
                @click="handleExport('csv')"
                role="menuitem"
                aria-label="Export as CSV"
                data-testid="export-csv"
              >
                <svg
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Export CSV
              </button>
              <button
                class="export-menu__item"
                @click="handleExport('pdf')"
                role="menuitem"
                aria-label="Export as PDF"
                data-testid="export-pdf"
              >
                <svg
                  class="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                  />
                </svg>
                Export PDF
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="reports-loading" role="status" aria-live="polite">
      <div
        v-for="i in 4"
        :key="i"
        class="reports-loading__skeleton"
        :aria-label="`Loading report ${i}`"
      />
    </div>

    <!-- Charts Grid -->
    <div v-else class="reports-grid">
      <!-- Usage Metrics Card -->
      <Card class="reports-card" variant="elevated">
        <template #header>
          <h2 class="reports-card__title">Storage & Assets</h2>
        </template>

        <div class="metrics-summary">
          <div class="metric">
            <span class="metric-label">Total Assets</span>
            <span class="metric-value">{{ usageMetrics?.totalAssets || 0 }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Storage Used</span>
            <span class="metric-value">{{ formatBytes(usageMetrics?.storageUsed || 0) }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Storage Limit</span>
            <span class="metric-value">
              {{
                usageMetrics?.storageLimit
                  ? formatBytes(usageMetrics.storageLimit)
                  : 'Unlimited'
              }}
            </span>
          </div>
          <div class="metric">
            <span class="metric-label">Usage</span>
            <span class="metric-value">{{ usageMetrics?.storagePercentage || 0 }}%</span>
          </div>
        </div>

        <!-- Storage Breakdown Pie Chart -->
        <ChartComponent
          v-if="storageChartData"
          type="pie"
          :data="storageChartData"
          title="Storage by File Type"
        />
        <div v-else class="chart-empty">
          <p>No storage data available</p>
        </div>
      </Card>

      <!-- Downloads Chart Card -->
      <Card class="reports-card" variant="elevated">
        <template #header>
          <h2 class="reports-card__title">Downloads Trend</h2>
        </template>

        <ChartComponent
          v-if="downloadChartData"
          type="line"
          :data="downloadChartData"
          title="Downloads Over Time"
        />
        <div v-else class="chart-empty">
          <p>No download data available</p>
        </div>
      </Card>

      <!-- Activity Stats Card -->
      <Card class="reports-card" variant="elevated">
        <template #header>
          <h2 class="reports-card__title">User Activity</h2>
        </template>

        <!-- Activity Table -->
        <ActivityTable
          :activities="recentActivity"
          :is-loading="isLoading"
          :page-size="10"
          :show-pagination="true"
        />
      </Card>

      <!-- Storage Breakdown Card -->
      <Card class="reports-card" variant="elevated">
        <template #header>
          <h2 class="reports-card__title">Storage Breakdown</h2>
        </template>

        <ChartComponent
          v-if="storageBarChartData"
          type="bar"
          :data="storageBarChartData"
          title="Storage by Category"
        />
        <div v-else class="chart-empty">
          <p>No storage breakdown data available</p>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import { useAuthStore } from '@/stores/authStore'
import { useReportsStore } from '@/stores/reportsStore'
import { useUIStore } from '@/stores/uiStore'
import Card from '@/components/Common/Card.vue'
import Button from '@/components/Common/Button.vue'
import Select from '@/components/Common/Select.vue'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'
import ChartComponent from '@/components/reports/ChartComponent.vue'
import ActivityTable from '@/components/reports/ActivityTable.vue'
import type { ReportTimeRange } from '@/types/reports'

// Hooks
const router = useRouter()
const authStore = useAuthStore()
const reportsStore = useReportsStore()
const uiStore = useUIStore()

// State
const selectedTimeRange = ref<string>('month')
const customDateRange = ref<[string, string] | null>(null)
const showExportMenu = ref(false)
const isLoading = ref(false)
const exportMenuRef = ref<HTMLElement | null>(null)

// Time range options
const timeRangeOptions = [
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'quarter', label: 'Last 3 Months' },
  { value: 'custom', label: 'Custom Range' }
]

// Close export menu when clicking outside
onClickOutside(exportMenuRef, () => {
  showExportMenu.value = false
})

// Computed
const usageMetrics = computed(() => reportsStore.usageMetrics)
const recentActivity = computed(() => reportsStore.recentActivity)
const storageBreakdown = computed(() => reportsStore.storageBreakdown)
const downloadHistory = computed(() => reportsStore.downloadHistory)

const timeRange = computed<ReportTimeRange>(() => {
  if (selectedTimeRange.value === 'custom' && customDateRange.value) {
    return {
      type: 'custom',
      startDate: customDateRange.value[0],
      endDate: customDateRange.value[1]
    }
  }

  const today = new Date()
  let startDate = new Date(today)

  switch (selectedTimeRange.value) {
    case 'today':
      startDate.setHours(0, 0, 0, 0)
      break
    case 'week':
      startDate.setDate(today.getDate() - 7)
      startDate.setHours(0, 0, 0, 0)
      break
    case 'month':
      startDate.setMonth(today.getMonth() - 1)
      startDate.setHours(0, 0, 0, 0)
      break
    case 'quarter':
      startDate.setMonth(today.getMonth() - 3)
      startDate.setHours(0, 0, 0, 0)
      break
    default:
      startDate.setHours(0, 0, 0, 0)
  }

  const endDate = new Date(today)
  endDate.setHours(23, 59, 59, 999)

  return {
    type: selectedTimeRange.value as ReportTimeRange['type'],
    startDate: startDate.toISOString(),
    endDate: endDate.toISOString()
  }
})

const storageChartData = computed(() => {
  if (!storageBreakdown.value.length) return null

  return {
    labels: storageBreakdown.value.map((s) => s.category),
    datasets: [
      {
        label: 'Storage (GB)',
        data: storageBreakdown.value.map((s) => s.size / (1024 * 1024 * 1024)),
        backgroundColor: [
          'rgba(59, 130, 246, 0.7)', // blue - images
          'rgba(239, 68, 68, 0.7)', // red - videos
          'rgba(16, 185, 129, 0.7)', // green - documents
          'rgba(245, 158, 11, 0.7)', // yellow - audio
          'rgba(139, 92, 246, 0.7)' // purple - other
        ].slice(0, storageBreakdown.value.length)
      }
    ]
  }
})

const downloadChartData = computed(() => {
  if (!downloadHistory.value.length) return null

  return {
    labels: downloadHistory.value.map((d) => {
      const date = new Date(d.date)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }),
    datasets: [
      {
        label: 'Downloads',
        data: downloadHistory.value.map((d) => d.downloads),
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Unique Users',
        data: downloadHistory.value.map((d) => d.uniqueUsers),
        borderColor: 'rgba(16, 185, 129, 1)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const storageBarChartData = computed(() => {
  if (!storageBreakdown.value.length) return null

  return {
    labels: storageBreakdown.value.map((s) => s.category),
    datasets: [
      {
        label: 'File Count',
        data: storageBreakdown.value.map((s) => s.count),
        backgroundColor: 'rgba(54, 162, 235, 0.7)'
      }
    ]
  }
})

// Methods
const fetchReports = async (): Promise<void> => {
  isLoading.value = true
  try {
    await Promise.all([
      reportsStore.fetchUsageReport(timeRange.value),
      reportsStore.fetchDownloadReport(timeRange.value),
      reportsStore.fetchActivityReport(timeRange.value, 50),
      reportsStore.fetchStorageReport(timeRange.value)
    ])
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to load reports'
    })
  } finally {
    isLoading.value = false
  }
}

watch(
  () => selectedTimeRange.value,
  (value) => {
    if (value !== 'custom') {
      customDateRange.value = null
    }
    fetchReports()
  }
)

watch(
  () => customDateRange.value,
  () => {
    if (selectedTimeRange.value === 'custom' && customDateRange.value) {
      fetchReports()
    }
  }
)

const handleExport = async (format: 'csv' | 'pdf'): Promise<void> => {
  try {
    showExportMenu.value = false

    // Check if we have a current report
    if (!reportsStore.currentReport?.id) {
      // For export without saved report, we can export current data directly
      // This is a simpler approach - export current view without saving
      uiStore.addNotification({
        type: 'info',
        title: 'Info',
        message: 'Exporting current report data...'
      })

      // Create a temporary report for export
      let reportType = 'usage'
      if (downloadHistory.value.length > 0) {
        reportType = 'downloads'
      } else if (recentActivity.value.length > 0) {
        reportType = 'activity'
      } else if (storageBreakdown.value.length > 0) {
        reportType = 'storage'
      }

      const savedReport = await reportsStore.saveReport(
        `Report ${new Date().toLocaleDateString()}`,
        reportType
      )

      if (!savedReport.id) {
        throw new Error('Failed to create report for export')
      }

      reportsStore.setCurrentReport(savedReport)
    }

    const reportId = reportsStore.currentReport?.id
    if (!reportId) {
      throw new Error('No report available for export')
    }

    const blob = await reportsStore.exportReport(format)

    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `report-${new Date().toISOString().split('T')[0]}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: `Report exported as ${format.toUpperCase()}`
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to export report'
    })
  }
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// Lifecycle
onMounted(async () => {
  // Permission check
  if (!authStore.hasPermission('admin.reports_view')) {
    router.push({
      name: 'forbidden',
      query: {
        returnTo: '/admin/reports',
        requiredPermission: 'admin.reports_view'
      }
    })
    return
  }

  // Set initial time range
  reportsStore.setTimeRange(timeRange.value)

  await fetchReports()
})

onUnmounted(() => {
  showExportMenu.value = false
})
</script>

<style scoped lang="css">
.reports-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--color-background, #f9fafb);
  min-height: 100vh;
}

.reports-toolbar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  background: var(--color-surface, #ffffff);
  border-radius: var(--radius-base, 8px);
  border: 1px solid var(--color-border, #e5e7eb);
}

.reports-toolbar__title {
  margin: 0;
  font-size: var(--font-size-3xl, 30px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.reports-toolbar__controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.reports-toolbar__select {
  min-width: 180px;
}

.reports-toolbar__date-picker {
  min-width: 300px;
}

.reports-toolbar__export {
  position: relative;
  margin-left: auto;
}

.export-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 8px);
  box-shadow: var(--shadow-md, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
  z-index: 10;
  min-width: 180px;
  overflow: hidden;
}

.export-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: var(--color-text, #111827);
  cursor: pointer;
  text-align: left;
  font-size: var(--font-size-base, 14px);
  transition: all 200ms ease;
}

.export-menu__item:hover {
  background: var(--color-bg-1, #f9fafb);
}

.export-menu__item:focus {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: -2px;
}

.reports-loading {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.reports-loading__skeleton {
  height: 400px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.reports-card {
  min-height: 300px;
}

.reports-card__title {
  margin: 0;
  font-size: var(--font-size-xl, 20px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.metrics-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
}

.metric-label {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  font-weight: 500;
}

.metric-value {
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--color-text-secondary, #6b7280);
  font-size: var(--font-size-base, 14px);
}

/* Responsive */
@media (max-width: 1024px) {
  .reports-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .reports-toolbar {
    padding: 16px;
  }

  .reports-toolbar__controls {
    flex-direction: column;
    align-items: stretch;
  }

  .reports-toolbar__select,
  .reports-toolbar__date-picker {
    width: 100%;
    min-width: unset;
  }

  .reports-toolbar__export {
    margin-left: 0;
  }

  .export-menu {
    right: auto;
    left: 0;
  }

  .metrics-summary {
    grid-template-columns: 1fr;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .export-menu,
  .reports-loading__skeleton {
    animation: none;
  }
}
</style>

