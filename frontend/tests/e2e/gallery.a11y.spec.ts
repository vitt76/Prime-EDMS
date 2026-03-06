import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

function createAsset(id: number) {
  return {
    id,
    label: `Accessible Asset ${id}`,
    filename: `asset-${id}.jpg`,
    size: 512000,
    mime_type: 'image/jpeg',
    date_added: new Date().toISOString(),
    thumbnail_url: `https://picsum.photos/seed/a11y-${id}/300/200`,
    tags: []
  }
}

async function openGallery(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    localStorage.setItem('auth_token', 'playwright-token')
    localStorage.setItem('dev_authenticated', 'true')
    localStorage.setItem('auth_user', JSON.stringify({
      id: 1,
      username: 'playwright',
      email: 'playwright@example.com',
      is_staff: true,
      is_superuser: false,
      permissions: [],
      groups: []
    }))
  })

  await page.route('**/api/v4/**', async (route) => {
    const url = route.request().url()

    if (url.includes('/api/v4/headless/auth/me/')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: {
            id: 1,
            username: 'playwright',
            email: 'playwright@example.com',
            is_staff: true,
            is_superuser: false,
            permissions: [],
            groups: []
          },
          organization: null,
          organizations: []
        })
      })
      return
    }

    if (url.includes('/api/v4/documents/optimized/')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 3,
          next: null,
          previous: null,
          results: [createAsset(1), createAsset(2), createAsset(3)]
        })
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ count: 0, next: null, previous: null, results: [] })
    })
  })

  await page.goto('/dam')
  await expect(page.getByRole('list', { name: /галерея активов/i })).toBeVisible()
}

test.describe('Gallery accessibility smoke', () => {
  test('has no critical axe violations on main gallery view', async ({ page }) => {
    await openGallery(page)

    const results = await new AxeBuilder({ page })
      .include('[role="list"]')
      .analyze()

    expect(results.violations).toEqual([])
  })
})
