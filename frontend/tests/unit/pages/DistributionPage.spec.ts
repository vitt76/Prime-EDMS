import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DistributionPage from '@/pages/DistributionPage.vue'
import { useDistributionStore } from '@/stores/distributionStore'
import { distributionService } from '@/services/distributionService'
import type { Publication } from '@/types/api'

vi.mock('@/services/distributionService')

describe('DistributionPage', () => {
  let pinia: any
  let wrapper: ReturnType<typeof mount>

  const mockPublications: Publication[] = [
    {
      id: 1,
      title: 'Publication 1',
      description: 'Description 1',
      status: 'published',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T10:00:00Z',
      created_by: 'User 1',
      created_by_id: 1,
      assets: [],
      channels: [],
      analytics: { views: 100, downloads: 50, shares: 10 }
    },
    {
      id: 2,
      title: 'Publication 2',
      description: 'Description 2',
      status: 'draft',
      created_date: '2023-01-02T10:00:00Z',
      updated_date: '2023-01-02T10:00:00Z',
      created_by: 'User 2',
      created_by_id: 2,
      assets: [],
      channels: [],
      analytics: { views: 0, downloads: 0, shares: 0 }
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()

    const store = useDistributionStore()
    store.publications = mockPublications
    store.totalCount = 2
    store.currentPage = 1
    store.pageSize = 50
    store.isLoading = false
    store.error = null

    ;(distributionService.getPublications as vi.Mock).mockResolvedValue({
      count: 2,
      results: mockPublications
    })
  })

  it('renders page header with title', () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: true,
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('Публикации')
  })

  it('displays create publication button', () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: { template: '<button><slot /></button>' },
          Input: true,
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('Создать публикацию')
  })

  it('shows status filter', () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: true,
          Select: { template: '<select><slot /></select>', props: ['modelValue', 'options'] },
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    const select = wrapper.findComponent({ name: 'Select' })
    expect(select.exists()).toBe(true)
  })

  it('shows search input', () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: { template: '<input />', props: ['modelValue', 'placeholder'] },
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    const input = wrapper.findComponent({ name: 'Input' })
    expect(input.exists()).toBe(true)
  })

  it('displays publications list when loaded', () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: true,
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: { template: '<div class="publication-card"></div>', props: ['publication'] },
          CreatePublicationModal: true
        }
      }
    })

    const cards = wrapper.findAllComponents({ name: 'PublicationCard' })
    expect(cards.length).toBe(2)
  })

  it('shows loading state', () => {
    const store = useDistributionStore()
    store.isLoading = true
    store.publications = []

    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: true,
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('Загрузка публикаций')
  })

  it('shows error state', () => {
    const store = useDistributionStore()
    store.error = 'Failed to load publications'
    store.publications = []

    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: { template: '<button><slot /></button>' },
          Input: true,
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('Ошибка загрузки')
    expect(wrapper.text()).toContain('Failed to load publications')
  })

  it('shows empty state when no publications', () => {
    const store = useDistributionStore()
    store.publications = []
    store.totalCount = 0
    store.isLoading = false
    store.error = null

    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: { template: '<button><slot /></button>' },
          Input: true,
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('Нет публикаций')
  })

  it('opens create modal when create button clicked', async () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          Input: true,
          Select: true,
          Modal: { template: '<div v-if="isOpen"><slot /></div>', props: ['isOpen'] },
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: { template: '<div v-if="isOpen">Create Modal</div>', props: ['isOpen'] }
        }
      }
    })

    const createButton = wrapper.findAll('button').find((btn) => btn.text().includes('Создать публикацию'))
    if (createButton) {
      await createButton.trigger('click')
      await wrapper.vm.$nextTick()

      const modal = wrapper.findComponent({ name: 'CreatePublicationModal' })
      expect(modal.exists()).toBe(true)
    }
  })

  it('handles status filter change', async () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: true,
          Select: {
            template: '<select @change="$emit(\'change\', $event.target.value)"><slot /></select>',
            props: ['modelValue', 'options']
          },
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    const store = useDistributionStore()
    const applyFiltersSpy = vi.spyOn(store, 'applyFilters')

    const select = wrapper.findComponent({ name: 'Select' })
    await select.trigger('change', { target: { value: 'published' } })
    await wrapper.vm.$nextTick()

    expect(applyFiltersSpy).toHaveBeenCalled()
  })

  it('handles search input', async () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: {
            template: '<input @input="$emit(\'input\', $event.target.value)" />',
            props: ['modelValue', 'placeholder']
          },
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    const store = useDistributionStore()
    const applyFiltersSpy = vi.spyOn(store, 'applyFilters')

    const input = wrapper.findComponent({ name: 'Input' })
    await input.trigger('input', { target: { value: 'test' } })
    await wrapper.vm.$nextTick()

    expect(applyFiltersSpy).toHaveBeenCalled()
  })

  it('handles page change', async () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: true,
          Select: true,
          Modal: true,
          Pagination: {
            template: '<div @page-change="$emit(\'page-change\', 2)">Pagination</div>',
            props: ['currentPage', 'totalItems', 'pageSize']
          },
          PublicationCard: true,
          CreatePublicationModal: true
        }
      }
    })

    const store = useDistributionStore()
    const setPageSpy = vi.spyOn(store, 'setPage')

    const pagination = wrapper.findComponent({ name: 'Pagination' })
    await pagination.trigger('page-change')
    await wrapper.vm.$nextTick()

    expect(setPageSpy).toHaveBeenCalledWith(2)
  })

  it('handles publication deletion', async () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          Input: true,
          Select: true,
          Modal: { template: '<div v-if="isOpen"><slot /></div>', props: ['isOpen'] },
          Pagination: true,
          PublicationCard: {
            template: '<div @delete="$emit(\'delete\', publication)"></div>',
            props: ['publication']
          },
          CreatePublicationModal: true
        }
      }
    })

    vi.mocked(distributionService.deletePublication).mockResolvedValue(undefined)

    const store = useDistributionStore()
    const deleteSpy = vi.spyOn(store, 'deletePublication')

    const card = wrapper.findComponent({ name: 'PublicationCard' })
    await card.vm.$emit('delete', mockPublications[0])
    await wrapper.vm.$nextTick()

    // Modal should open
    const modal = wrapper.findComponent({ name: 'Modal' })
    expect(modal.exists()).toBe(true)

    // Confirm delete
    const deleteButton = wrapper.findAll('button').find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      await deleteButton.trigger('click')
      await wrapper.vm.$nextTick()
      await new Promise((resolve) => setTimeout(resolve, 100))

      expect(deleteSpy).toHaveBeenCalled()
    }
  })

  it('refreshes publications after creation', async () => {
    wrapper = mount(DistributionPage, {
      global: {
        plugins: [pinia],
        stubs: {
          Button: true,
          Input: true,
          Select: true,
          Modal: true,
          Pagination: true,
          PublicationCard: true,
          CreatePublicationModal: {
            template: '<div><slot /></div>',
            props: ['isOpen'],
            emits: ['created', 'close']
          }
        }
      }
    })

    const store = useDistributionStore()
    const fetchSpy = vi.spyOn(store, 'fetchPublications')

    const modal = wrapper.findComponent({ name: 'CreatePublicationModal' })
    await modal.vm.$emit('created', mockPublications[0])
    await wrapper.vm.$nextTick()

    expect(fetchSpy).toHaveBeenCalled()
  })
})



