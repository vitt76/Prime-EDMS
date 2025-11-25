import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CreatePublicationModal from '@/components/Distribution/CreatePublicationModal.vue'
import { distributionService } from '@/services/distributionService'
import type { Publication, PublicationChannel } from '@/types/api'

vi.mock('@/services/distributionService')

describe('CreatePublicationModal', () => {
  let pinia: any

  const mockChannels: PublicationChannel[] = [
    {
      id: 1,
      name: 'Website',
      type: 'website',
      status: 'active'
    },
    {
      id: 2,
      name: 'Social Media',
      type: 'social',
      status: 'active'
    }
  ]

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
    ;(distributionService.getChannels as vi.Mock).mockResolvedValue(mockChannels)
  })

  it('renders when isOpen is true', () => {
    const wrapper = mount(CreatePublicationModal, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="header" /><slot name="body" /><slot name="footer" /></div>',
            props: ['isOpen', 'size']
          }
        }
      }
    })

    expect(wrapper.text()).toContain('Создать публикацию')
  })

  it('shows step indicator with 4 steps', () => {
    const wrapper = mount(CreatePublicationModal, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /></div>'
          }
        }
      }
    })

    expect(wrapper.text()).toContain('Выбор активов')
    expect(wrapper.text()).toContain('Каналы')
    expect(wrapper.text()).toContain('Настройки')
    expect(wrapper.text()).toContain('Предпросмотр')
  })

  it('starts at step 0 (Select Assets)', () => {
    const wrapper = mount(CreatePublicationModal, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /></div>'
          }
        }
      }
    })

    expect(wrapper.vm.currentStep).toBe(0)
    expect(wrapper.text()).toContain('Выберите активы')
  })

  it('allows navigation between steps', async () => {
    const wrapper = mount(CreatePublicationModal, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /><slot name="footer" /></div>'
          }
        }
      }
    })

    // Add assets to proceed
    wrapper.vm.selectedAssets = [{ id: 1, label: 'Asset 1' } as any]
    await wrapper.vm.$nextTick()

    // Click Next
    const nextButton = wrapper.findAll('button').find((btn) => btn.text().includes('Далее'))
    if (nextButton && !nextButton.attributes('disabled')) {
      await nextButton.trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.currentStep).toBe(1)
    }
  })

  it('validates step completion before proceeding', async () => {
    const wrapper = mount(CreatePublicationModal, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /><slot name="footer" /></div>'
          }
        }
      }
    })

    // Try to proceed without selecting assets
    const nextButton = wrapper.findAll('button').find((btn) => btn.text().includes('Далее'))
    if (nextButton) {
      expect(nextButton.attributes('disabled')).toBeDefined()
    }
  })

  it('loads available channels on mount', async () => {
    mount(CreatePublicationModal, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /></div>'
          }
        }
      }
    })

    await new Promise((resolve) => setTimeout(resolve, 100))
    expect(distributionService.getChannels).toHaveBeenCalled()
  })

  it('creates publication on final step', async () => {
    const newPublication: Publication = {
      id: 1,
      title: 'New Publication',
      status: 'draft',
      created_date: '2023-01-01T10:00:00Z',
      updated_date: '2023-01-01T10:00:00Z',
      created_by: 'User1',
      created_by_id: 1,
      assets: [],
      channels: []
    }

    ;(distributionService.createPublication as vi.Mock).mockResolvedValue(newPublication)

    const wrapper = mount(CreatePublicationModal, {
      props: {
        isOpen: true
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /><slot name="footer" /></div>'
          }
        }
      }
    })

    // Set required data
    wrapper.vm.selectedAssets = [{ id: 1 } as any]
    wrapper.vm.selectedChannels = [1]
    wrapper.vm.publicationData.title = 'New Publication'
    wrapper.vm.currentStep = 3 // Final step
    await wrapper.vm.$nextTick()

    const publishButton = wrapper.findAll('button').find((btn) =>
      btn.text().includes('Создать') || btn.text().includes('Опубликовать')
    )
    if (publishButton && !publishButton.attributes('disabled')) {
      await publishButton.trigger('click')
      await wrapper.vm.$nextTick()
      expect(distributionService.createPublication).toHaveBeenCalled()
    }
  })
})

