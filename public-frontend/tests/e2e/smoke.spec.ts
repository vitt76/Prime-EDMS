/**
 * E2E Smoke Tests
 * 
 * Basic tests to ensure main pages load correctly
 */
import { test, expect } from '@playwright/test'

test.describe('Homepage', () => {
  test('should display hero section', async ({ page }) => {
    await page.goto('/')
    
    // Check hero heading exists
    await expect(page.locator('h1')).toBeVisible()
    
    // Check CTA buttons exist
    await expect(page.locator('a[href="/auth/register"]').first()).toBeVisible()
  })

  test('should have working navigation', async ({ page }) => {
    await page.goto('/')
    
    // Check navigation links
    await expect(page.locator('nav a[href="/pricing"]')).toBeVisible()
    await expect(page.locator('nav a[href="/blog"]')).toBeVisible()
    await expect(page.locator('nav a[href="/about"]')).toBeVisible()
    await expect(page.locator('nav a[href="/contact"]')).toBeVisible()
  })

  test('should navigate to pricing page', async ({ page }) => {
    await page.goto('/')
    
    // Click pricing link
    await page.click('nav a[href="/pricing"]')
    
    // Verify navigation
    await expect(page).toHaveURL(/.*pricing/)
    await expect(page.locator('h1')).toContainText(/тариф|pricing/i)
  })
})

test.describe('Pricing Page', () => {
  test('should display pricing plans', async ({ page }) => {
    await page.goto('/pricing')
    
    // Check page title
    await expect(page.locator('h1')).toContainText(/ценообразование|тариф|pricing/i)
    
    // Check plan cards exist
    const planCards = page.locator('[class*="rounded-2xl"]')
    await expect(planCards.first()).toBeVisible()
  })

  test('should toggle billing period', async ({ page }) => {
    await page.goto('/pricing')
    
    // Find and click billing toggle
    const toggle = page.locator('button[role="switch"]')
    if (await toggle.isVisible()) {
      await toggle.click()
      // Toggle should change state
      await expect(toggle).toHaveAttribute('aria-checked', 'true')
    }
  })
})

test.describe('Blog Page', () => {
  test('should display blog posts', async ({ page }) => {
    await page.goto('/blog')
    
    // Check page title
    await expect(page.locator('h1')).toContainText(/блог|blog/i)
    
    // Check search input exists
    await expect(page.locator('input[type="search"]')).toBeVisible()
  })

  test('should filter posts with search', async ({ page }) => {
    await page.goto('/blog')
    
    // Find search input and type
    const searchInput = page.locator('input[type="search"]')
    await searchInput.fill('test')
    
    // Submit search
    await page.locator('button:has-text("Найти")').click()
    
    // URL should include search param
    await expect(page).toHaveURL(/q=test/)
  })
})

test.describe('Contact Page', () => {
  test('should display contact form', async ({ page }) => {
    await page.goto('/contact')
    
    // Check form exists
    await expect(page.locator('form')).toBeVisible()
    
    // Check required fields
    await expect(page.locator('input[name="name"]')).toBeVisible()
    await expect(page.locator('input[name="email"]')).toBeVisible()
    await expect(page.locator('textarea')).toBeVisible()
  })
})

test.describe('Public Auth Flow', () => {
  test('should submit login form against canonical public auth endpoint', async ({ page }) => {
    await page.route('**/api/v4/public/auth/login/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          token: 'demo-token',
          redirect_url: 'http://localhost:5173'
        })
      })
    })

    await page.goto('/auth/login')
    await page.locator('input[name="email"]').fill('demo@example.com')
    await page.locator('input[name="password"]').fill('Password123!')
    await page.locator('button[type="submit"]').click()

    await expect(page.locator('text=Вход выполнен')).toBeVisible()
  })

  test('should resolve verify-email page via canonical endpoint', async ({ page }) => {
    await page.route('**/api/v4/public/auth/verify-email/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Email verified successfully',
          redirect_url: '/auth/login'
        })
      })
    })

    await page.goto('/auth/verify-email/test-token')
    await expect(page.locator('text=Email verified successfully')).toBeVisible()
  })
})

test.describe('Mobile Navigation', () => {
  test.use({ viewport: { width: 375, height: 667 } })

  test('should toggle mobile menu', async ({ page }) => {
    await page.goto('/')
    
    // Find and click hamburger menu
    const menuButton = page.locator('button[aria-label*="menu"]')
    await expect(menuButton).toBeVisible()
    
    await menuButton.click()
    
    // Mobile menu should be visible
    await expect(page.locator('nav a[href="/pricing"]')).toBeVisible()
    
    // Close menu
    await menuButton.click()
  })
})

test.describe('Accessibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/')
    
    // Should have exactly one h1
    const h1Count = await page.locator('h1').count()
    expect(h1Count).toBe(1)
  })

  test('should have alt text on images', async ({ page }) => {
    await page.goto('/')
    
    // All images should have alt attributes
    const images = page.locator('img')
    const count = await images.count()
    
    for (let i = 0; i < count; i++) {
      const img = images.nth(i)
      await expect(img).toHaveAttribute('alt')
    }
  })

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/')
    
    // Tab through navigation
    await page.keyboard.press('Tab')
    
    // Focus should be on first focusable element
    const focusedElement = page.locator(':focus')
    await expect(focusedElement).toBeVisible()
  })
})

test.describe('Language Switching', () => {
  test('should switch to English', async ({ page }) => {
    await page.goto('/')
    
    // Find language switcher
    const langButton = page.locator('button:has(svg)').filter({ hasText: /ru|рус/i })
    if (await langButton.isVisible()) {
      await langButton.click()
      
      // Click English option
      const enOption = page.locator('a:has-text("English")')
      if (await enOption.isVisible()) {
        await enOption.click()
        
        // URL should include /en
        await expect(page).toHaveURL(/\/en/)
      }
    }
  })
})

test.describe('SEO', () => {
  test('should have meta tags', async ({ page }) => {
    await page.goto('/')
    
    // Check title
    const title = await page.title()
    expect(title).toBeTruthy()
    
    // Check meta description
    const description = await page.locator('meta[name="description"]').getAttribute('content')
    expect(description).toBeTruthy()
  })

  test('should have Open Graph tags', async ({ page }) => {
    await page.goto('/')
    
    // Check OG title
    const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content')
    expect(ogTitle).toBeTruthy()
  })
})
