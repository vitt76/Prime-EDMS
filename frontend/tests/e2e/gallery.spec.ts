import { test, expect } from '@playwright/test'

function createAsset(id: number) {
  return {
    id,
    label: `Asset ${id}`,
    filename: `asset-${id}.jpg`,
    size: 1024000,
    mime_type: 'image/jpeg',
    date_added: new Date().toISOString(),
    thumbnail_url: `https://picsum.photos/seed/${id}/300/200`,
    tags: []
  }
}

async function bootstrapAuthenticatedGallery(page: import('@playwright/test').Page, options?: {
  empty?: boolean
  failAssets?: boolean
}) {
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
      if (options?.failAssets) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal server error' })
        })
        return
      }

      const assets = options?.empty ? [] : [createAsset(1), createAsset(2), createAsset(3)]
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: assets.length,
          next: null,
          previous: null,
          results: assets
        })
      })
      return
    }

    if (
      url.includes('/api/v4/headless/saved-searches/') ||
      url.includes('/api/v4/recently-viewed/') ||
      url.includes('/api/v4/folders/') ||
      url.includes('/api/v4/cabinets/')
    ) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ count: 0, next: null, previous: null, results: [] })
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({})
    })
  })

  await page.goto('/dam')
}

test.describe('Gallery View', () => {
  test('loads gallery page and displays assets', async ({ page }) => {
    await bootstrapAuthenticatedGallery(page)

    await expect(page.getByRole('list', { name: /галерея активов/i })).toBeVisible()
    await expect(page.locator('[data-testid="asset-card"]').first()).toBeVisible()
    await expect(page.locator('[data-testid="asset-card"]')).toHaveCount(3)
  })

  test('opens asset detail on double click', async ({ page }) => {
    await bootstrapAuthenticatedGallery(page)

    const firstCard = page.locator('[data-testid="asset-card"]').first()
    await expect(firstCard).toBeVisible()
    await firstCard.evaluate((node) => {
      node.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }))
    })

    await expect(page).toHaveURL(/\/dam\/assets\/1$/)
  })

  test('displays empty state when no assets', async ({ page }) => {
    await bootstrapAuthenticatedGallery(page, { empty: true })

    await expect(page.getByText('Библиотека пуста')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Загрузить файлы' })).toBeVisible()
  })

  test('displays error state on API failure', async ({ page }) => {
    await bootstrapAuthenticatedGallery(page, { failAssets: true })

    await expect(page.getByText('Ошибка загрузки')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Повторить загрузку активов' })).toBeVisible()
  })
})

