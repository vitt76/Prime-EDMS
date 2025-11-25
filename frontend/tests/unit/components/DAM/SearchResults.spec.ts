import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import SearchResults from '@/components/DAM/SearchResults.vue'
import type { Asset } from '@/types/api'

// Mock formatters
vi.mock('@/utils/formatters', () => ({
  formatFileSize: (size: number) => `${(size / 1024).toFixed(1)} KB`,
  formatDate: (date: string) => new Date(date).toLocaleDateString()
}))

describe('SearchResults', () => {
  const mockAssets: Asset[] = [
    {
      id: 1,
      label: 'Test Image 1',
      size: 1024 * 100,
      date_added: '2023-01-01T10:00:00Z',
      mime_type: 'image/jpeg',
      thumbnail_url: 'https://example.com/thumb1.jpg'
    },
    {
      id: 2,
      label: 'Test Image 2',
      size: 1024 * 200,
      date_added: '2023-01-02T10:00:00Z',
      mime_type: 'image/png',
      thumbnail_url: 'https://example.com/thumb2.jpg'
    }
  ]

  it('renders correctly with results', () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 2
      }
    })

    expect(wrapper.findAll('[role="option"]').length).toBe(2)
    expect(wrapper.text()).toContain('Test Image 1')
    expect(wrapper.text()).toContain('Test Image 2')
  })

  it('highlights selected result', () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: 1,
        totalCount: 2
      }
    })

    const options = wrapper.findAll('[role="option"]')
    expect(options[1].attributes('aria-selected')).toBe('true')
  })

  it('displays thumbnail images', () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 2
      }
    })

    const images = wrapper.findAll('img')
    expect(images.length).toBe(2)
    expect(images[0].attributes('src')).toBe('https://example.com/thumb1.jpg')
    expect(images[0].attributes('alt')).toBe('Test Image 1')
  })

  it('shows placeholder icon when thumbnail is missing', () => {
    const assetsWithoutThumb: Asset[] = [
      {
        id: 3,
        label: 'No Thumb',
        size: 1024,
        date_added: '2023-01-01T10:00:00Z',
        mime_type: 'image/jpeg'
      }
    ]

    const wrapper = mount(SearchResults, {
      props: {
        results: assetsWithoutThumb,
        selectedIndex: -1,
        totalCount: 1
      }
    })

    const images = wrapper.findAll('img')
    expect(images.length).toBe(0) // No img tag when no thumbnail_url
    expect(wrapper.find('svg').exists()).toBe(true) // Placeholder icon
  })

  it('displays file metadata correctly', () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 2
      }
    })

    expect(wrapper.text()).toContain('100.0 KB')
    expect(wrapper.text()).toContain('200.0 KB')
  })

  it('emits select event when result is clicked', async () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 2
      }
    })

    const firstResult = wrapper.findAll('[role="option"]')[0]
    await firstResult.trigger('click')

    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')?.[0][0]).toBe(1)
  })

  it('shows "View all results" link when totalCount > results.length', () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 10
      }
    })

    expect(wrapper.text()).toContain('Показать все результаты (10)')
  })

  it('does not show "View all results" link when totalCount === results.length', () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 2
      }
    })

    expect(wrapper.text()).not.toContain('Показать все результаты')
  })

  it('emits view-all event when "View all" button is clicked', async () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 10
      }
    })

    const viewAllButton = wrapper.find('button')
    await viewAllButton.trigger('click')

    expect(wrapper.emitted('view-all')).toBeTruthy()
  })

  it('handles image error gracefully', async () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 2
      }
    })

    const image = wrapper.find('img')
    await image.trigger('error')

    // Image should be hidden on error
    expect((image.element as HTMLImageElement).style.display).toBe('none')
  })

  it('displays correct file type labels', () => {
    const assetsWithTypes: Asset[] = [
      {
        id: 1,
        label: 'Image',
        size: 1024,
        date_added: '2023-01-01T10:00:00Z',
        mime_type: 'image/jpeg'
      },
      {
        id: 2,
        label: 'Video',
        size: 2048,
        date_added: '2023-01-01T10:00:00Z',
        mime_type: 'video/mp4'
      },
      {
        id: 3,
        label: 'PDF',
        size: 3072,
        date_added: '2023-01-01T10:00:00Z',
        mime_type: 'application/pdf'
      }
    ]

    const wrapper = mount(SearchResults, {
      props: {
        results: assetsWithTypes,
        selectedIndex: -1,
        totalCount: 3
      }
    })

    expect(wrapper.text()).toContain('Изображение')
    expect(wrapper.text()).toContain('Видео')
    expect(wrapper.text()).toContain('PDF')
  })

  it('emits hover event when mouse enters result', async () => {
    const wrapper = mount(SearchResults, {
      props: {
        results: mockAssets,
        selectedIndex: -1,
        totalCount: 2
      }
    })

    const firstResult = wrapper.findAll('[role="option"]')[0]
    await firstResult.trigger('mouseenter')

    expect(wrapper.emitted('hover')).toBeTruthy()
    expect(wrapper.emitted('hover')?.[0][0]).toBe(0)
  })
})

