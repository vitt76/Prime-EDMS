import { test, expect } from '@playwright/test'

const mockCollections = [
  {
    id: 1,
    name: 'Campaign Assets',
    parent_id: null,
    is_favorite: false,
    is_shared: false,
    visibility: 'private',
    asset_count: 12,
    created_by: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    cover_image_id: null
  },
  {
    id: 2,
    name: 'Guidelines',
    parent_id: null,
    is_favorite: false,
    is_shared: false,
    visibility: 'private',
    asset_count: 4,
    created_by: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    cover_image_id: null
  },
  {
    id: 3,
    name: 'Images',
    parent_id: 1,
    is_favorite: false,
    is_shared: false,
    visibility: 'private',
    asset_count: 18,
    created_by: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    cover_image_id: null
  }
]

test.describe('Collections drag & drop flow', () => {
  test.beforeEach(async ({ page }) => {
    let collectionsState = [...mockCollections]

    await page.route('**/api/v4/dam/collections/**', async (route) => {
      const url = route.request().url()
      const method = route.request().method()

      if (url.includes('/special/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            favorites: [],
            recent: [],
            shared_with_me: [],
            my_uploads: [],
            public_collections: []
          })
        })
        return
      }

      if (method === 'GET') {
        if (url.endsWith('/collections/')) {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              count: collectionsState.length,
              next: null,
              previous: null,
              results: collectionsState
            })
          })
          return
        }

        const detailMatch = url.match(/\/collections\/(\d+)\//)
        if (detailMatch) {
          const id = Number(detailMatch[1])
          const collection = collectionsState.find((c) => c.id === id)
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(collection)
          })
          return
        }
      }

      if (method === 'POST' && url.endsWith('/move/')) {
        const payload = JSON.parse(route.request().postData() || '{}')
        const moved = collectionsState.find((c) => c.id === payload.collection_id)
        if (moved) {
          moved.parent_id = payload.new_parent_id
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(moved ?? {})
        })
        return
      }

      await route.continue()
    })
  })

  const login = async (page: Parameters<typeof test.beforeEach>[0]['page']) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill('admin@example.com')
    await page.getByLabel('Password').fill('password')
    await page.getByRole('button', { name: 'Sign In' }).click()
    await page.waitForURL('/', { waitUntil: 'networkidle' })
  }

  test('allows dragging a child collection to a new parent', async ({ page }) => {
    const consoleErrors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })

    await login(page)
    await page.goto('/collections')

    await page.waitForSelector('[data-testid^="collection-node-"]')

    await page.getByTestId('collection-toggle-1').click()
    const childNode = page.getByTestId('collection-node-3')
    const targetNode = page.getByTestId('collection-node-2')
    const moveRequestPromise = page.waitForRequest('**/api/v4/dam/collections/3/move/')
    await childNode.dragTo(targetNode)
    await expect(moveRequestPromise).resolves.toBeTruthy()

    await expect(page.getByText('Collection moved successfully')).toBeVisible()
    await expect(childNode).toBeVisible()
    expect(consoleErrors).toHaveLength(0)
  })
})

