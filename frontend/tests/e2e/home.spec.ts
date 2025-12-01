import { test, expect } from '@playwright/test'

test('home page loads correctly', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/DAM System/)
  await expect(page.locator('h1')).toContainText('DAM System')
})

test('navigation works', async ({ page }) => {
  await page.goto('/')
  // Add navigation tests here
})


