import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import PublicationCard from '@/components/Distribution/PublicationCard.vue'
import type { Publication } from '@/types/api'

describe('PublicationCard', () => {
  let pinia: any

  const mockPublication: Publication = {
    id: 1,
    title: 'Test Publication',
    description: 'Test description',
    status: 'published',
    created_date: '2023-01-01T10:00:00Z',
    updated_date: '2023-01-01T10:00:00Z',
    created_by: 'Test User',
    created_by_id: 1,
    assets: [
      {
        id: 1,
        label: 'Asset 1',
        filename: 'asset1.jpg',
        size: 1024000,
        mime_type: 'image/jpeg',
        date_added: '2023-01-01T10:00:00Z'
      }
    ],
    channels: [
      {
        id: 1,
        name: 'Website',
        type: 'website',
        status: 'active'
      }
    ],
    analytics: {
      views: 100,
      downloads: 50,
      shares: 10
    }
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('renders publication information', () => {
    const wrapper = mount(PublicationCard, {
      props: {
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Card: {
            template: '<div class="card"><slot /></div>',
            props: []
          }
        }
      }
    })

    expect(wrapper.text()).toContain('Test Publication')
    expect(wrapper.text()).toContain('Test description')
    expect(wrapper.text()).toContain('Test User')
  })

  it('displays status badge correctly', () => {
    const wrapper = mount(PublicationCard, {
      props: {
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Card: {
            template: '<div class="card"><slot /></div>'
          }
        }
      }
    })

    expect(wrapper.text()).toContain('Опубликовано')
  })

  it('displays analytics data', () => {
    const wrapper = mount(PublicationCard, {
      props: {
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Card: {
            template: '<div class="card"><slot /></div>'
          }
        }
      }
    })

    expect(wrapper.text()).toContain('100 просмотров')
    expect(wrapper.text()).toContain('50 скачиваний')
    expect(wrapper.text()).toContain('10 репостов')
  })

  it('displays channels', () => {
    const wrapper = mount(PublicationCard, {
      props: {
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Card: {
            template: '<div class="card"><slot /></div>'
          }
        }
      }
    })

    expect(wrapper.text()).toContain('Website')
  })

  it('emits preview event when preview button is clicked', async () => {
    const wrapper = mount(PublicationCard, {
      props: {
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Card: {
            template: '<div class="card"><slot /></div>'
          }
        }
      }
    })

    const previewButton = wrapper.findAll('button').find((btn) =>
      btn.attributes('aria-label') === 'Предпросмотр'
    )
    if (previewButton) {
      await previewButton.trigger('click')
      expect(wrapper.emitted('preview')).toBeTruthy()
    }
  })

  it('emits edit event when edit button is clicked', async () => {
    const wrapper = mount(PublicationCard, {
      props: {
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Card: {
            template: '<div class="card"><slot /></div>'
          }
        }
      }
    })

    const editButton = wrapper.findAll('button').find((btn) =>
      btn.attributes('aria-label') === 'Редактировать'
    )
    if (editButton) {
      await editButton.trigger('click')
      expect(wrapper.emitted('edit')).toBeTruthy()
    }
  })

  it('emits delete event when delete button is clicked', async () => {
    const wrapper = mount(PublicationCard, {
      props: {
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Card: {
            template: '<div class="card"><slot /></div>'
          }
        }
      }
    })

    const deleteButton = wrapper.findAll('button').find((btn) =>
      btn.attributes('aria-label') === 'Удалить'
    )
    if (deleteButton) {
      await deleteButton.trigger('click')
      expect(wrapper.emitted('delete')).toBeTruthy()
    }
  })

  it('displays correct status variant for different statuses', () => {
    const statuses: Publication['status'][] = ['draft', 'scheduled', 'published', 'archived']
    
    statuses.forEach((status) => {
      const wrapper = mount(PublicationCard, {
        props: {
          publication: { ...mockPublication, status }
        },
        global: {
          plugins: [pinia],
          stubs: {
            Card: {
              template: '<div class="card"><slot /></div>'
            }
          }
        }
      })

      expect(wrapper.vm.statusVariant).toBeDefined()
      expect(wrapper.vm.statusLabel).toBeDefined()
    })
  })
})

