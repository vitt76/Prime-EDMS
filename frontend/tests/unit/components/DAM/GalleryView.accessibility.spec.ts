import { describe, it, expect, beforeEach } from 'vitest'
import { render } from '@testing-library/vue'
import { axe } from 'vitest-axe'
import { createPinia, setActivePinia } from 'pinia'
import GalleryView from '@/components/DAM/GalleryView.vue'
import { useAssetStore } from '@/stores/assetStore'

describe('GalleryView Accessibility', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should have no accessibility violations with empty state', async () => {
    const { container } = render(GalleryView)
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper ARIA labels for gallery grid', async () => {
    const assetStore = useAssetStore()
    // Mock some assets
    assetStore.assets = [
      {
        id: 1,
        label: 'Test Asset',
        size: 1024,
        date_added: '2025-01-01',
        thumbnail_url: 'https://example.com/thumb.jpg'
      }
    ] as any

    const { container } = render(GalleryView)
    
    const grid = container.querySelector('[role="grid"]')
    expect(grid).toHaveAttribute('aria-label', 'Галерея активов')
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper keyboard navigation support', async () => {
    const { container } = render(GalleryView)
    
    const selectAllCheckbox = container.querySelector('input[type="checkbox"][aria-label*="Выбрать все"]')
    expect(selectAllCheckbox).toBeInTheDocument()
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})

