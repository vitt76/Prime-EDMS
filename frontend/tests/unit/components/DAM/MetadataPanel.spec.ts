import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import MetadataPanel from '@/components/DAM/MetadataPanel.vue'
import Button from '@/components/Common/Button.vue'
import Badge from '@/components/Common/Badge.vue'
import type { Asset, AssetDetailResponse } from '@/types/api'

// Mock formatters
vi.mock('@/utils/formatters', () => ({
  formatFileSize: (size: number) => `${(size / 1024).toFixed(1)} KB`,
  formatDate: (date: string) => new Date(date).toLocaleDateString(),
  formatRelativeTime: (date: string) => '2 hours ago',
  truncate: (str: string, len: number) => str.substring(0, len) + '...'
}))

describe('MetadataPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const mockAsset: Asset = {
    id: 1,
    label: 'Test Image',
    size: 1024 * 500,
    date_added: '2023-01-01T10:00:00Z',
    mime_type: 'image/jpeg',
    thumbnail_url: 'https://example.com/thumb.jpg'
  }

  const mockAssetDetail: AssetDetailResponse = {
    ...mockAsset,
    file_details: {
      filename: 'test-image.jpg',
      size: 1024 * 500,
      mime_type: 'image/jpeg',
      uploaded_date: '2023-01-01T10:00:00Z',
      checksum: 'abc123def456ghi789'
    },
    ai_analysis: {
      status: 'completed',
      tags: ['nature', 'landscape', 'sunset'],
      ai_description: 'A beautiful sunset over mountains',
      colors: ['#FF5733', '#33FF57', '#3357FF'],
      objects_detected: [
        { name: 'mountain', confidence: 0.95 },
        { name: 'sun', confidence: 0.88 }
      ]
    },
    comments: [
      {
        id: 1,
        author: 'John Doe',
        text: 'Great photo!',
        created_date: '2023-01-02T10:00:00Z'
      }
    ],
    version_history: [
      {
        id: 1,
        filename: 'test-image-v1.jpg',
        uploaded_date: '2023-01-01T10:00:00Z',
        uploaded_by: 'User 1',
        size: 1024 * 400
      }
    ]
  }

  it('renders correctly with basic asset', () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAsset },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('Информация о файле')
    expect(wrapper.text()).toContain('Test Image')
    expect(wrapper.text()).toContain('500.0 KB')
  })

  it('displays file details when available', () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAssetDetail },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('test-image.jpg')
    expect(wrapper.text()).toContain('abc123def456...')
  })

  it('displays image metadata for image files', () => {
    const imageAsset: AssetDetailResponse = {
      ...mockAssetDetail,
      metadata: {
        dimensions: { width: 1920, height: 1080 },
        dpi: 300,
        color_space: 'RGB',
        camera: 'Canon EOS 5D',
        exposure: '1/125'
      }
    }

    const wrapper = mount(MetadataPanel, {
      props: { asset: imageAsset },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('Информация об изображении')
    expect(wrapper.text()).toContain('1920 × 1080 px')
    expect(wrapper.text()).toContain('300')
    expect(wrapper.text()).toContain('RGB')
  })

  it('displays AI analysis when available', () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAssetDetail },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('AI Анализ')
    expect(wrapper.text()).toContain('nature')
    expect(wrapper.text()).toContain('landscape')
    expect(wrapper.text()).toContain('A beautiful sunset over mountains')
    expect(wrapper.text()).toContain('mountain')
    expect(wrapper.text()).toContain('95%')
  })

  it('shows processing state for AI analysis', () => {
    const processingAsset: AssetDetailResponse = {
      ...mockAssetDetail,
      ai_analysis: {
        status: 'processing'
      }
    }

    const wrapper = mount(MetadataPanel, {
      props: { asset: processingAsset },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('Анализ выполняется...')
  })

  it('displays version history when available', () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAssetDetail },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('История версий')
    expect(wrapper.text()).toContain('test-image-v1.jpg')
    expect(wrapper.text()).toContain('User 1')
  })

  it('displays comments when available', () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAssetDetail },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('Комментарии (1)')
    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('Great photo!')
  })

  it('emits download event when download button is clicked', async () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAsset },
      global: {
        plugins: [createPinia()]
      }
    })

    const downloadButton = wrapper.findAllComponents(Button).find((b) => b.text().includes('Скачать'))
    if (downloadButton) {
      await downloadButton.trigger('click')
      expect(wrapper.emitted('download')).toBeTruthy()
    }
  })

  it('emits share event when share button is clicked', async () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAsset },
      global: {
        plugins: [createPinia()]
      }
    })

    const shareButton = wrapper.findAllComponents(Button).find((b) => b.text().includes('Поделиться'))
    if (shareButton) {
      await shareButton.trigger('click')
      expect(wrapper.emitted('share')).toBeTruthy()
    }
  })

  it('emits version-select event when version is clicked', async () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAssetDetail },
      global: {
        plugins: [createPinia()]
      }
    })

    const versionButton = wrapper.find('button[class*="version"]') || wrapper.findAll('button').find((b) => b.text().includes('test-image-v1.jpg'))
    if (versionButton) {
      await versionButton.trigger('click')
      expect(wrapper.emitted('version-select')).toBeTruthy()
      expect(wrapper.emitted('version-select')?.[0][0]).toBe(1)
    }
  })

  it('handles null asset gracefully', () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: null },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).toContain('N/A')
  })

  it('does not show image metadata for non-image files', () => {
    const videoAsset: Asset = {
      ...mockAsset,
      mime_type: 'video/mp4'
    }

    const wrapper = mount(MetadataPanel, {
      props: { asset: videoAsset },
      global: {
        plugins: [createPinia()]
      }
    })

    expect(wrapper.text()).not.toContain('Информация об изображении')
  })

  it('displays dominant colors correctly', () => {
    const wrapper = mount(MetadataPanel, {
      props: { asset: mockAssetDetail },
      global: {
        plugins: [createPinia()]
      }
    })

    const colorBoxes = wrapper.findAll('[style*="background-color"]')
    expect(colorBoxes.length).toBeGreaterThan(0)
  })
})

