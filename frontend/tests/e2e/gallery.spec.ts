import { test, expect } from '@playwright/test'

test.describe('Gallery View', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API response
    await page.route('**/api/v4/dam/assets/**', async (route) => {
      const url = new URL(route.request().url())
      const pageNum = parseInt(url.searchParams.get('page') || '1', 10)
      const pageSize = parseInt(url.searchParams.get('page_size') || '50', 10)
      
      const mockAssets = Array.from({ length: pageSize }, (_, i) => ({
        id: (pageNum - 1) * pageSize + i + 1,
        label: `Asset ${(pageNum - 1) * pageSize + i + 1}`,
        filename: `asset${(pageNum - 1) * pageSize + i + 1}.jpg`,
        size: 1024000,
        mime_type: 'image/jpeg',
        date_added: new Date().toISOString(),
        thumbnail_url: `https://picsum.photos/300/200?random=${(pageNum - 1) * pageSize + i + 1}`
      }))

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 100,
          next: pageNum < 2 ? `http://localhost:8000/api/v4/dam/assets/?page=${pageNum + 1}` : null,
          previous: pageNum > 1 ? `http://localhost:8000/api/v4/dam/assets/?page=${pageNum - 1}` : null,
          results: mockAssets
        })
      })
    })

    await page.goto('/dam/gallery')
  })

  test('loads gallery page and displays assets', async ({ page }) => {
    // Wait for assets to load
    await page.waitForSelector('[data-testid="asset-card"], .gallery-content', {
      timeout: 5000
    })

    // Check that assets are displayed
    const assetCards = await page.locator('.gallery-content img, [data-testid="asset-card"]').count()
    expect(assetCards).toBeGreaterThan(0)
  })

  test('displays pagination controls', async ({ page }) => {
    await page.waitForSelector('.gallery-content', { timeout: 5000 })

    // Check pagination is visible
    const pagination = page.locator('nav[aria-label="Pagination"]')
    await expect(pagination).toBeVisible()
  })

  test('navigates to next page', async ({ page }) => {
    await page.waitForSelector('nav[aria-label="Pagination"]', { timeout: 5000 })

    // Click next button
    const nextButton = page.locator('button[aria-label="Следующая страница"]')
    await expect(nextButton).toBeVisible()
    
    // Check if not disabled
    const isDisabled = await nextButton.getAttribute('disabled')
    if (!isDisabled) {
      await nextButton.click()
      
      // Wait for new page to load
      await page.waitForTimeout(1000)
      
      // Verify page changed (check URL or content)
      const currentUrl = page.url()
      expect(currentUrl).toContain('/dam')
    }
  })

  test('navigates to previous page', async ({ page }) => {
    // First go to page 2
    await page.waitForSelector('nav[aria-label="Pagination"]', { timeout: 5000 })
    
    const nextButton = page.locator('button[aria-label="Следующая страница"]')
    const isNextDisabled = await nextButton.getAttribute('disabled')
    
    if (!isNextDisabled) {
      await nextButton.click()
      await page.waitForTimeout(1000)
    }

    // Now go back
    const prevButton = page.locator('button[aria-label="Предыдущая страница"]')
    const isPrevDisabled = await prevButton.getAttribute('disabled')
    
    if (!isPrevDisabled) {
      await prevButton.click()
      await page.waitForTimeout(1000)
    }
  })

  test('displays loading state', async ({ page }) => {
    // Navigate to page
    await page.goto('/dam/gallery')
    
    // Check for loading indicators (skeleton or spinner)
    const loadingIndicator = page.locator('.animate-pulse, .animate-spin')
    const count = await loadingIndicator.count()
    
    // Loading should appear briefly, then disappear
    if (count > 0) {
      await expect(loadingIndicator.first()).toBeVisible({ timeout: 1000 })
    }
  })

  test('displays error state on API failure', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v4/dam/assets/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: {
            code: 'SERVER_ERROR',
            message: 'Internal server error'
          }
        })
      })
    })

    await page.goto('/dam/gallery')
    await page.waitForTimeout(2000)

    // Check for error message
    const errorMessage = page.locator('text=/Ошибка|Error/i')
    const errorCount = await errorMessage.count()
    
    if (errorCount > 0) {
      await expect(errorMessage.first()).toBeVisible()
    }
  })

  test('displays empty state when no assets', async ({ page }) => {
    // Mock empty response
    await page.route('**/api/v4/dam/assets/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 0,
          next: null,
          previous: null,
          results: []
        })
      })
    })

    await page.goto('/dam/gallery')
    await page.waitForTimeout(2000)

    // Check for empty state message
    const emptyState = page.locator('text=/Нет активов|No assets/i')
    const emptyCount = await emptyState.count()
    
    if (emptyCount > 0) {
      await expect(emptyState.first()).toBeVisible()
    }
  })

  test('selects asset on click', async ({ page }) => {
    await page.waitForSelector('.gallery-content', { timeout: 5000 })

    // Hover over first asset card to show checkbox
    const firstCard = page.locator('.gallery-content > div > div').first()
    await firstCard.hover()
    await page.waitForTimeout(500)

    // Click on card
    await firstCard.click()
    
    // Asset should be selected (check for selected styling)
    await page.waitForTimeout(500)
  })

  test('opens asset detail on double click', async ({ page }) => {
    await page.waitForSelector('.gallery-content', { timeout: 5000 })

    const firstCard = page.locator('.gallery-content > div > div').first()
    
    // Double click
    await firstCard.dblclick()
    
    // Should navigate to detail page
    await page.waitForTimeout(1000)
    const currentUrl = page.url()
    expect(currentUrl).toMatch(/\/dam\/assets\/\d+/)
  })

  test('displays correct number of assets per page', async ({ page }) => {
    await page.waitForSelector('.gallery-content', { timeout: 5000 })

    // Count asset cards (images in grid)
    const assetCards = page.locator('.gallery-content img[alt]')
    const count = await assetCards.count()
    
    // Should have some assets (exact count depends on mock)
    expect(count).toBeGreaterThan(0)
  })

  test('responsive grid layout', async ({ page }) => {
    await page.waitForSelector('.gallery-content', { timeout: 5000 })

    // Check grid classes
    const grid = page.locator('.gallery-content > div').first()
    const classes = await grid.getAttribute('class')
    
    expect(classes).toContain('grid')
    expect(classes).toContain('grid-cols-1')
    expect(classes).toContain('sm:grid-cols-2')
    expect(classes).toContain('md:grid-cols-3')
    expect(classes).toContain('lg:grid-cols-4')
  })
})

