import { test, expect } from '@playwright/test'

const login = async (page: Parameters<typeof test.beforeEach>[0]['page']) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill('admin@example.com')
  await page.getByLabel('Password').fill('password')
  await page.getByRole('button', { name: 'Sign In' }).click()
  await page.waitForURL('/', { waitUntil: 'networkidle' })
}

test.describe('Admin reports export flow', () => {
  let exportRequests: string[] = []

  test.beforeEach(async ({ page }) => {
    exportRequests = []

    const usageMetrics = {
      totalAssets: 120,
      assetsByType: {
        images: 60,
        videos: 20,
        documents: 30,
        audio: 5,
        other: 5
      },
      storageUsed: 5 * 1024 * 1024 * 1024,
      storageLimit: 10 * 1024 * 1024 * 1024,
      storagePercentage: 50
    }

    const downloadMetrics = [
      {
        date: new Date().toISOString(),
        downloads: 120,
        uniqueUsers: 42
      },
      {
        date: new Date(Date.now() - 86400000).toISOString(),
        downloads: 95,
        uniqueUsers: 31
      }
    ]

    const activityMetrics = [
      {
        username: 'alice',
        email: 'alice@example.com',
        action: 'upload',
        asset_id: 1,
        asset_name: 'hero.png',
        timestamp: new Date().toISOString()
      }
    ]

    const storageBreakdown = [
      {
        category: 'images',
        size: 2 * 1024 * 1024 * 1024,
        count: 60,
        percentage: 40
      },
      {
        category: 'videos',
        size: 1 * 1024 * 1024 * 1024,
        count: 20,
        percentage: 20
      }
    ]
    const usageMetrics = {
      totalAssets: 120,
      assetsByType: {
        images: 60,
        videos: 20,
        documents: 30,
        audio: 5,
        other: 5
      },
      storageUsed: 5 * 1024 * 1024 * 1024,
      storageLimit: 10 * 1024 * 1024 * 1024,
      storagePercentage: 50
    }

    const downloadMetrics = [
      {
        date: new Date().toISOString(),
        downloads: 120,
        uniqueUsers: 42
      },
      {
        date: new Date(Date.now() - 86400000).toISOString(),
        downloads: 95,
        uniqueUsers: 31
      }
    ]

    const activityMetrics = [
      {
        username: 'alice',
        email: 'alice@example.com',
        action: 'upload',
        asset_id: 1,
        asset_name: 'hero.png',
        timestamp: new Date().toISOString()
      }
    ]

    const storageBreakdown = [
      {
        category: 'images',
        size: 2 * 1024 * 1024 * 1024,
        count: 60,
        percentage: 40
      },
      {
        category: 'videos',
        size: 1 * 1024 * 1024 * 1024,
        count: 20,
        percentage: 20
      }
    ]

    const exportCalls: string[] = []

    await page.route('**/api/v4/reports/**', async (route) => {
      const url = route.request().url()
      const method = route.request().method()

      if (url.endsWith('/usage/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(usageMetrics)
        })
        return
      }

      if (url.endsWith('/downloads/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(downloadMetrics)
        })
        return
      }

      if (url.endsWith('/activity/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(activityMetrics)
        })
        return
      }

      if (url.endsWith('/storage/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(storageBreakdown)
        })
        return
      }

      if (method === 'POST' && url.endsWith('/reports/')) {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 42,
            name: 'Automated Report',
            type: 'usage',
            timeRange: {
              type: 'week',
              startDate: new Date().toISOString(),
              endDate: new Date().toISOString()
            },
            metrics: usageMetrics,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            created_by: 1
          })
        })
        return
      }

      if (url.includes('/export/')) {
        exportRequests.push(url)
        await route.fulfill({
          status: 200,
          headers: { 'Content-Type': 'application/octet-stream' },
          body: 'report-binary'
        })
        return
      }

      await route.continue()
    })

    test.info().annotations.push({
      type: 'exportCalls',
      description: JSON.stringify(exportCalls)
    })
  })

    test('opens export menu and downloads CSV/PDF without console errors', async ({ page }) => {
    const consoleErrors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })

    await login(page)
    await page.goto('/admin/reports')

    await expect(page.getByText('Analytics & Reports')).toBeVisible()

    await page.getByLabel('Period').click()
    await page.getByRole('option', { name: 'This Week' }).click()

    const exportTrigger = page.getByTestId('reports-export-trigger')
    await exportTrigger.click()
    await page.getByTestId('export-csv').click()
    await expect(page.getByText('Report exported as CSV')).toBeVisible()

    await exportTrigger.click()
    await page.getByTestId('export-pdf').click()
    await expect(page.getByText('Report exported as PDF')).toBeVisible()

    expect(consoleErrors).toHaveLength(0)
    expect(exportRequests).toHaveLength(2)
  })
})

