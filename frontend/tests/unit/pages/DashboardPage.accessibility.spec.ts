import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { render } from '@testing-library/vue'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import DashboardPage from '@/pages/DashboardPage.vue'
import { useDashboardStore } from '@/stores/dashboardStore'
import { useAssetStore } from '@/stores/assetStore'
import { useAuthStore } from '@/stores/authStore'
import { axe, toHaveNoViolations } from 'vitest-axe'
import type { DashboardStats, StorageMetrics } from '@/services/dashboardService'
import type { Asset } from '@/types/api'

expect.extend(toHaveNoViolations)

vi.mock('@/services/dashboardService')

describe('DashboardPage Accessibility', () => {
  let pinia: any
  let router: any
  let container: HTMLElement

  const mockStats: DashboardStats = {
    documents: {
      total: 150,
      with_analysis: 120,
      without_analysis: 30
    },
    analyses: {
      completed: 120,
      processing: 5,
      pending: 25,
      failed: 3
    },
    providers: [
      { provider: 'yandex', count: 100 },
      { provider: 'gigachat', count: 20 }
    ]
  }

  const mockStorageMetrics: StorageMetrics = {
    total_size: 100 * 1024 * 1024 * 1024,
    used_size: 30 * 1024 * 1024 * 1024,
    available_size: 70 * 1024 * 1024 * 1024,
    usage_percentage: 30,
    by_type: []
  }

  const mockAssets: Asset[] = [
    {
      id: 1,
      label: 'test-asset-1.jpg',
      size: 1024000,
      date_added: '2025-01-27T10:00:00Z',
      thumbnail_url: 'https://example.com/thumb1.jpg',
      mime_type: 'image/jpeg'
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: DashboardPage }
      ]
    })

    vi.clearAllMocks()

    const dashboardStore = useDashboardStore()
    const assetStore = useAssetStore()
    const authStore = useAuthStore()

    dashboardStore.stats = mockStats
    dashboardStore.storageMetrics = mockStorageMetrics
    dashboardStore.activityFeed = []
    dashboardStore.isLoading = false
    dashboardStore.error = null

    assetStore.assets = mockAssets
    assetStore.isLoading = false

    authStore.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      is_active: true
    }
  })

  afterEach(() => {
    if (container) {
      container.remove()
    }
  })

  it('should have no accessibility violations', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper ARIA labels for stats region', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    const statsRegion = container.querySelector('[role="region"][aria-label="Статистика системы"]')
    expect(statsRegion).toBeTruthy()
  })

  it('should have proper ARIA labels for activity feed', async () => {
    const dashboardStore = useDashboardStore()
    dashboardStore.activityFeed = [
      {
        id: 1,
        type: 'upload',
        user: 'John Doe',
        user_id: 1,
        timestamp: '2025-01-27T10:00:00Z',
        description: 'загрузил новый актив',
        asset_id: 101,
        asset_label: 'campaign_banner.jpg'
      }
    ]

    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    const activityList = container.querySelector('[role="list"][aria-label="Лента активности"]')
    expect(activityList).toBeTruthy()
  })

  it('should have proper ARIA attributes for progress bar', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    const progressBar = container.querySelector('[role="progressbar"]')
    expect(progressBar).toBeTruthy()
    expect(progressBar?.getAttribute('aria-valuenow')).toBe('30')
    expect(progressBar?.getAttribute('aria-valuemin')).toBe('0')
    expect(progressBar?.getAttribute('aria-valuemax')).toBe('100')
    expect(progressBar?.getAttribute('aria-label')).toContain('хранилища')
  })

  it('should have proper ARIA labels for interactive elements', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    const retryButton = container.querySelector('button[aria-label="Повторить загрузку"]')
    // Retry button only shows on error, so it might not exist
    // But if it exists, it should have proper label

    const assetCards = container.querySelectorAll('[role="gridcell"]')
    assetCards.forEach(card => {
      expect(card.getAttribute('aria-label')).toBeTruthy()
      expect(card.getAttribute('tabindex')).toBe('0')
    })
  })

  it('should have proper semantic HTML structure', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    // Check for heading hierarchy
    const h1 = container.querySelector('h1')
    expect(h1).toBeTruthy()

    const h2s = container.querySelectorAll('h2')
    expect(h2s.length).toBeGreaterThan(0)
  })

  it('should have proper color contrast (WCAG AA)', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    const results = await axe(container, {
      rules: {
        'color-contrast': { enabled: true }
      }
    })

    // Check for color contrast violations
    const contrastViolations = results.violations.filter(
      v => v.id === 'color-contrast'
    )
    expect(contrastViolations.length).toBe(0)
  })

  it('should have keyboard navigation support', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    // Check that interactive elements are keyboard accessible
    const interactiveElements = container.querySelectorAll(
      'button, a, [role="button"], [tabindex="0"]'
    )
    
    interactiveElements.forEach(element => {
      // All interactive elements should be focusable
      expect(element.getAttribute('tabindex')).not.toBe('-1')
    })
  })

  it('should have proper focus indicators', async () => {
    const { container: renderedContainer } = render(DashboardPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          Card: { template: '<div class="card"><slot /></div>' },
          RouterLink: { template: '<a><slot /></a>' }
        }
      }
    })

    container = renderedContainer

    const results = await axe(container, {
      rules: {
        'focus-order-semantics': { enabled: true },
        'focusable-content': { enabled: true }
      }
    })

    const focusViolations = results.violations.filter(
      v => v.id === 'focus-order-semantics' || v.id === 'focusable-content'
    )
    expect(focusViolations.length).toBe(0)
  })
})

