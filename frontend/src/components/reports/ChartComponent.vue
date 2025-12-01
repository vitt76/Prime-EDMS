<template>
  <div class="chart-component">
    <h3 v-if="title" class="chart-component__title">{{ title }}</h3>
    <div class="chart-component__container" ref="chartContainerRef">
      <canvas ref="chartCanvasRef" :aria-label="title || 'Chart'" />
    </div>
    <div v-if="chartError" class="chart-component__error" role="alert">
      <p>{{ chartError }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { ChartData } from '@/types/reports'

interface Props {
  type: 'pie' | 'line' | 'bar'
  data: ChartData
  title?: string
}

const props = defineProps<Props>()

const chartCanvasRef = ref<HTMLCanvasElement | null>(null)
const chartContainerRef = ref<HTMLDivElement | null>(null)
const chartError = ref<string | null>(null)
let chartInstance: import('chart.js').Chart | null = null

// Dynamic import of Chart.js
const loadChart = async (): Promise<any> => {
  try {
    // Try to import Chart.js
    const chartModule = await import('chart.js/auto')
    return chartModule.default || chartModule.Chart
  } catch (error) {
    console.warn('Chart.js not found. Please install: npm install chart.js', error)
    chartError.value =
      'Chart.js library is not installed. Please install it: npm install chart.js'
    return null
  }
}

const createChart = async (): Promise<void> => {
  if (!chartCanvasRef.value || !props.data) return

  // Clear existing chart
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  const Chart = await loadChart()
  if (!Chart) return

  try {
    const ctx = chartCanvasRef.value.getContext('2d')
    if (!ctx) return

    const chartOptions: any = {
      type: props.type,
      data: props.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 12,
              usePointStyle: true
            }
          },
          tooltip: {
            enabled: true,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: {
              size: 14,
              weight: 'bold'
            },
            bodyFont: {
              size: 13
            }
          }
        },
        scales:
          props.type !== 'pie'
            ? {
                x: {
                  grid: {
                    display: true,
                    color: 'rgba(0, 0, 0, 0.05)'
                  },
                  ticks: {
                    font: {
                      size: 12
                    }
                  }
                },
                y: {
                  beginAtZero: true,
                  grid: {
                    display: true,
                    color: 'rgba(0, 0, 0, 0.05)'
                  },
                  ticks: {
                    font: {
                      size: 12
                    }
                  }
                }
              }
            : undefined
      }
    }

    chartInstance = new Chart(ctx, chartOptions)
    chartError.value = null
  } catch (error) {
    console.error('Error creating chart:', error)
    chartError.value = 'Failed to render chart. Please check the console for details.'
  }
}

// Watch for data changes
watch(
  () => props.data,
  async () => {
    await nextTick()
    await createChart()
  },
  { deep: true }
)

// Lifecycle
onMounted(async () => {
  await nextTick()
  await createChart()
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
</script>

<style scoped lang="css">
.chart-component {
  position: relative;
  width: 100%;
}

.chart-component__title {
  margin: 0 0 16px 0;
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.chart-component__container {
  position: relative;
  height: 300px;
  width: 100%;
}

.chart-component__container canvas {
  max-width: 100%;
  height: 100% !important;
}

.chart-component__error {
  padding: 16px;
  background: var(--color-error, #fee2e2);
  border: 1px solid var(--color-error-border, #fecaca);
  border-radius: var(--radius-base, 8px);
  color: var(--color-error-text, #991b1b);
  font-size: var(--font-size-sm, 12px);
  text-align: center;
}

.chart-component__error p {
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-component__container {
    height: 250px;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .chart-component__container {
    animation: none;
  }
}
</style>

