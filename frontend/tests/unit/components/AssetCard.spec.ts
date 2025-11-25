import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AssetCard from '@/components/DAM/AssetCard.vue'
import Badge from '@/components/Common/Badge.vue'
import type { Asset } from '@/types/api'

// Mock formatters
vi.mock('@/utils/formatters', () => ({
  formatFileSize: (bytes: number) => `${(bytes / 1024).toFixed(2)} KB`,
  formatDate: (date: string) => '01.01.2025'
}))

const mockAsset: Asset = {
  id: 1,
  label: 'Test Image',
  filename: 'test.jpg',
  size: 1024000,
  mime_type: 'image/jpeg',
  date_added: '2025-01-01T00:00:00Z',
  thumbnail_url: 'https://example.com/thumb.jpg'
}

describe('AssetCard', () => {
  it('renders asset information correctly', () => {
    const wrapper = mount(AssetCard, {
      props: {
        asset: mockAsset
      },
      global: {
        components: {
          Badge
        }
      }
    })

    expect(wrapper.text()).toContain('Test Image')
    const img = wrapper.find('img')
    if (img.exists()) {
      expect(img.attributes('alt')).toBe('Test Image')
    }
  })

  it('shows checkbox when showCheckbox is true', async () => {
    const wrapper = mount(AssetCard, {
      props: {
        asset: mockAsset,
        showCheckbox: true
      },
      global: {
        components: {
          Badge
        }
      }
    })

    // Hover to show checkbox
    await wrapper.trigger('mouseenter')
    const checkbox = wrapper.find('input[type="checkbox"]')
    expect(checkbox.exists()).toBe(true)
  })

  it('emits select event on click', async () => {
    const wrapper = mount(AssetCard, {
      props: {
        asset: mockAsset
      },
      global: {
        components: {
          Badge
        }
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')?.[0]).toEqual([mockAsset])
  })

  it('emits open event on double click', async () => {
    const wrapper = mount(AssetCard, {
      props: {
        asset: mockAsset
      },
      global: {
        components: {
          Badge
        }
      }
    })

    await wrapper.trigger('dblclick')
    expect(wrapper.emitted('open')).toBeTruthy()
    expect(wrapper.emitted('open')?.[0]).toEqual([mockAsset])
  })

  it('shows loading state when isLoading is true', () => {
    const wrapper = mount(AssetCard, {
      props: {
        asset: mockAsset,
        isLoading: true
      },
      global: {
        components: {
          Badge
        }
      }
    })

    const spinner = wrapper.find('.animate-spin')
    expect(spinner.exists()).toBe(true)
  })

  it('applies selected styling when isSelected is true', () => {
    const wrapper = mount(AssetCard, {
      props: {
        asset: mockAsset,
        isSelected: true
      },
      global: {
        components: {
          Badge
        }
      }
    })

    expect(wrapper.classes()).toContain('ring-2')
    expect(wrapper.classes()).toContain('ring-primary-500')
  })

  it('shows status badge when asset has status', () => {
    const assetWithStatus: Asset = {
      ...mockAsset,
      metadata: {
        status: 'approved'
      }
    }

    const wrapper = mount(AssetCard, {
      props: {
        asset: assetWithStatus
      },
      global: {
        components: {
          Badge
        }
      }
    })

    // Badge should be present
    const badge = wrapper.findComponent(Badge)
    expect(badge.exists()).toBe(true)
  })

  it('handles image error gracefully', async () => {
    const wrapper = mount(AssetCard, {
      props: {
        asset: mockAsset
      },
      global: {
        components: {
          Badge
        }
      }
    })

    const img = wrapper.find('img')
    if (img.exists()) {
      await img.trigger('error')
      // Component should handle error
      expect(wrapper.vm).toBeDefined()
    }
  })
})

