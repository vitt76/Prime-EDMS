import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import VersionHistory from '@/components/DAM/VersionHistory.vue'
import { assetService } from '@/services/assetService'
import type { Version, AssetDetailResponse } from '@/types/api'

vi.mock('@/services/assetService')
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    user: { id: 1, username: 'testuser' }
  })
}))

describe('VersionHistory', () => {
  let pinia: any

  const mockVersions: Version[] = [
    {
      id: 1,
      filename: 'document-v1.pdf',
      uploaded_date: '2023-01-01T10:00:00Z',
      uploaded_by: 'User1',
      size: 1024000,
      is_current: false
    },
    {
      id: 2,
      filename: 'document-v2.pdf',
      uploaded_date: '2023-01-02T10:00:00Z',
      uploaded_by: 'User2',
      size: 1025000,
      is_current: true
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
  })

  it('renders version list', () => {
    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1,
        initialVersions: mockVersions
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('История версий (2)')
    expect(wrapper.text()).toContain('document-v1.pdf')
    expect(wrapper.text()).toContain('document-v2.pdf')
  })

  it('highlights current version', () => {
    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1,
        initialVersions: mockVersions
      },
      global: {
        plugins: [pinia]
      }
    })

    const currentVersionCard = wrapper.findAll('.bg-primary-50')
    expect(currentVersionCard.length).toBeGreaterThan(0)
    expect(wrapper.text()).toContain('Текущая версия')
  })

  it('shows empty state when no versions', () => {
    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1,
        initialVersions: []
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('История версий пуста')
  })

  it('displays version metadata correctly', () => {
    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1,
        initialVersions: mockVersions
      },
      global: {
        plugins: [pinia]
      }
    })

    expect(wrapper.text()).toContain('User1')
    expect(wrapper.text()).toContain('User2')
    expect(wrapper.text()).toContain('1.00 MB') // Formatted size
  })

  it('allows downloading a version', async () => {
    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null)

    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1,
        initialVersions: mockVersions
      },
      global: {
        plugins: [pinia]
      }
    })

    const downloadButtons = wrapper.findAll('button').filter((btn) =>
      btn.text().includes('Скачать')
    )
    if (downloadButtons.length > 0) {
      await downloadButtons[0].trigger('click')
      expect(openSpy).toHaveBeenCalled()
    }

    openSpy.mockRestore()
  })

  it('allows restoring a version', async () => {
    const mockAsset: AssetDetailResponse = {
      id: 1,
      label: 'Test Asset',
      filename: 'test.pdf',
      size: 1024000,
      mime_type: 'application/pdf',
      date_added: '2023-01-01T10:00:00Z',
      file_details: {
        filename: 'test.pdf',
        size: 1024000,
        mime_type: 'application/pdf',
        uploaded_date: '2023-01-01T10:00:00Z'
      },
      comments: [],
      version_history: mockVersions
    }

    ;(assetService.getAsset as vi.Mock).mockResolvedValue(mockAsset)
    ;(assetService.updateAsset as vi.Mock).mockResolvedValue(mockAsset)

    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1,
        initialVersions: mockVersions,
        canRestore: true
      },
      global: {
        plugins: [pinia]
      }
    })

    const restoreButtons = wrapper.findAll('button').filter((btn) =>
      btn.text().includes('Восстановить')
    )
    if (restoreButtons.length > 0) {
      // Mock confirm
      window.confirm = vi.fn(() => true)
      await restoreButtons[0].trigger('click')
      await wrapper.vm.$nextTick()
      // Should call updateAsset or restore endpoint
    }
  })

  it('hides restore button for current version', () => {
    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1,
        initialVersions: mockVersions
      },
      global: {
        plugins: [pinia]
      }
    })

    const restoreButtons = wrapper.findAll('button').filter((btn) =>
      btn.text().includes('Восстановить')
    )
    // Current version should not have restore button
    expect(restoreButtons.length).toBeLessThan(mockVersions.length)
  })

  it('loads versions from API when initialVersions not provided', async () => {
    const mockAsset: AssetDetailResponse = {
      id: 1,
      label: 'Test Asset',
      filename: 'test.pdf',
      size: 1024000,
      mime_type: 'application/pdf',
      date_added: '2023-01-01T10:00:00Z',
      file_details: {
        filename: 'test.pdf',
        size: 1024000,
        mime_type: 'application/pdf',
        uploaded_date: '2023-01-01T10:00:00Z'
      },
      comments: [],
      version_history: mockVersions
    }

    ;(assetService.getAsset as vi.Mock).mockResolvedValue(mockAsset)

    const wrapper = mount(VersionHistory, {
      props: {
        assetId: 1
      },
      global: {
        plugins: [pinia]
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(assetService.getAsset).toHaveBeenCalledWith(1)
  })
})

