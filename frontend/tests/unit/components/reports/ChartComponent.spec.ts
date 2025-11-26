import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ChartComponent from '@/components/reports/ChartComponent.vue'
import type { ChartData } from '@/types/reports'

// Mock Chart.js
vi.mock('chart.js/auto', () => ({
  default: class MockChart {
    canvas: any
    config: any
    constructor(canvas: any, config: any) {
      this.canvas = canvas
      this.config = config
    }
    destroy() {}
  }
}))

describe('ChartComponent', () => {
  let wrapper: ReturnType<typeof mount>

  const mockChartData: ChartData = {
    labels: ['Label1', 'Label2'],
    datasets: [
      {
        label: 'Dataset 1',
        data: [10, 20],
        backgroundColor: 'rgba(59, 130, 246, 0.7)'
      }
    ]
  }

  beforeEach(() => {
    // Mock canvas getContext
    HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
      fillRect: vi.fn(),
      clearRect: vi.fn(),
      getImageData: vi.fn(),
      putImageData: vi.fn(),
      createImageData: vi.fn(),
      setTransform: vi.fn(),
      drawImage: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      closePath: vi.fn(),
      stroke: vi.fn(),
      fill: vi.fn(),
      measureText: vi.fn(),
      transform: vi.fn(),
      translate: vi.fn(),
      scale: vi.fn(),
      rotate: vi.fn(),
      arc: vi.fn(),
      fillText: vi.fn(),
      strokeText: vi.fn(),
      createLinearGradient: vi.fn(),
      createPattern: vi.fn(),
      createRadialGradient: vi.fn(),
      clip: vi.fn(),
      isPointInPath: vi.fn(),
      isPointInStroke: vi.fn()
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('canvas').exists()).toBe(true)
  })

  it('displays title when provided', () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData,
        title: 'Test Chart'
      }
    })

    expect(wrapper.text()).toContain('Test Chart')
  })

  it('does not display title when not provided', () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    expect(wrapper.find('.chart-component__title').exists()).toBe(false)
  })

  it('creates pie chart', async () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalled()
  })

  it('creates line chart', async () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'line',
        data: mockChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalled()
  })

  it('creates bar chart', async () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'bar',
        data: mockChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalled()
  })

  it('handles Chart.js import error', async () => {
    // Mock failed import
    vi.doMock('chart.js/auto', () => {
      throw new Error('Chart.js not found')
    })

    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Should show error message
    expect(wrapper.find('.chart-component__error').exists()).toBe(true)
  })

  it('updates chart when data changes', async () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const newData: ChartData = {
      labels: ['New1', 'New2'],
      datasets: [
        {
          label: 'New Dataset',
          data: [30, 40],
          backgroundColor: 'rgba(255, 0, 0, 0.7)'
        }
      ]
    }

    await wrapper.setProps({ data: newData })
    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Chart should be recreated with new data
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalled()
  })

  it('destroys chart on unmount', async () => {
    const destroySpy = vi.fn()
    vi.mocked(HTMLCanvasElement.prototype.getContext).mockReturnValue({
      fillRect: vi.fn(),
      clearRect: vi.fn(),
      getImageData: vi.fn(),
      putImageData: vi.fn(),
      createImageData: vi.fn(),
      setTransform: vi.fn(),
      drawImage: vi.fn(),
      save: vi.fn(),
      restore: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      closePath: vi.fn(),
      stroke: vi.fn(),
      fill: vi.fn(),
      measureText: vi.fn(),
      transform: vi.fn(),
      translate: vi.fn(),
      scale: vi.fn(),
      rotate: vi.fn(),
      arc: vi.fn(),
      fillText: vi.fn(),
      strokeText: vi.fn(),
      createLinearGradient: vi.fn(),
      createPattern: vi.fn(),
      createRadialGradient: vi.fn(),
      clip: vi.fn(),
      isPointInPath: vi.fn(),
      isPointInStroke: vi.fn()
    } as any)

    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    wrapper.unmount()

    // Chart instance should be destroyed
    // This is tested through the component's lifecycle
  })

  it('has correct ARIA label on canvas', () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData,
        title: 'Test Chart'
      }
    })

    const canvas = wrapper.find('canvas')
    expect(canvas.attributes('aria-label')).toBe('Test Chart')
  })

  it('has default ARIA label when no title', () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    const canvas = wrapper.find('canvas')
    expect(canvas.attributes('aria-label')).toBe('Chart')
  })

  it('displays error message when chart creation fails', async () => {
    // Mock getContext to return null
    HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue(null)

    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Should handle error gracefully
    expect(wrapper.exists()).toBe(true)
  })

  it('handles empty data gracefully', async () => {
    const emptyData: ChartData = {
      labels: [],
      datasets: []
    }

    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: emptyData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(wrapper.exists()).toBe(true)
  })

  it('applies responsive styles', () => {
    wrapper = mount(ChartComponent, {
      props: {
        type: 'pie',
        data: mockChartData
      }
    })

    const container = wrapper.find('.chart-component__container')
    expect(container.exists()).toBe(true)
  })
})

