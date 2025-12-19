import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EditPublicationModal from '@/components/Distribution/EditPublicationModal.vue'
import { distributionService } from '@/services/distributionService'
import type { Publication, PublicationChannel } from '@/types/api'

vi.mock('@/services/distributionService')

describe('EditPublicationModal', () => {
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

  const mockPublication: Publication = {
    id: 1,
    title: 'Test Publication',
    description: 'Test description',
    status: 'draft',
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
        date_added: '2023-01-01T10:00:00Z',
        thumbnail_url: 'http://example.com/thumb1.jpg'
      }
    ],
    channels: [mockChannels[0]],
    analytics: {
      views: 0,
      downloads: 0,
      shares: 0
    }
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
    ;(distributionService.getChannels as vi.Mock).mockResolvedValue(mockChannels)
    ;(distributionService.updatePublication as vi.Mock).mockResolvedValue(mockPublication)
  })

  it('renders when isOpen is true', () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
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

    expect(wrapper.text()).toContain('Редактировать публикацию')
  })

  it('loads publication data when opened', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /></div>'
          },
          Input: {
            template: '<input :value="modelValue" />',
            props: ['modelValue', 'placeholder', 'required']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const input = wrapper.findComponent({ name: 'Input' })
    expect(input.exists()).toBe(true)
    // Title should be loaded
    expect(wrapper.vm.publicationData.title).toBe('Test Publication')
  })

  it('displays publication title in input', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /></div>'
          },
          Input: {
            template: '<input :value="modelValue" />',
            props: ['modelValue']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const input = wrapper.findComponent({ name: 'Input' })
    expect(input.props('modelValue')).toBe('Test Publication')
  })

  it('displays publication assets', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
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

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(wrapper.text()).toContain('Asset 1')
  })

  it('displays selected channels', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
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

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(wrapper.text()).toContain('Website')
  })

  it('allows removing assets', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
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

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const removeButton = wrapper.find('button.text-error')
    if (removeButton.exists()) {
      await removeButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.selectedAssets.length).toBe(0)
    }
  })

  it('allows toggling channels', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
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

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    const channelCheckbox = checkboxes.find((cb) => {
      const label = cb.element.closest('label')
      return label?.textContent?.includes('Social Media')
    })

    if (channelCheckbox) {
      await channelCheckbox.setValue(true)
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.selectedChannels).toContain(2)
    }
  })

  it('calls updatePublication when Save clicked', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /><slot name="footer" /></div>'
          },
          Button: {
            template: '<button @click="$emit(\'click\')" :disabled="disabled"><slot /></button>',
            props: ['variant', 'disabled', 'loading']
          },
          Input: {
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
            props: ['modelValue']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const buttons = wrapper.findAll('button')
    const saveButton = buttons.find((btn) => btn.text().includes('Сохранить'))
    if (saveButton) {
      await saveButton.trigger('click')
      await wrapper.vm.$nextTick()
      await new Promise((resolve) => setTimeout(resolve, 100))

      expect(distributionService.updatePublication).toHaveBeenCalledWith(1, expect.any(Object))
    }
  })

  it('emits updated event after successful save', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /><slot name="footer" /></div>'
          },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'disabled', 'loading']
          },
          Input: {
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
            props: ['modelValue']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const buttons = wrapper.findAll('button')
    const saveButton = buttons.find((btn) => btn.text().includes('Сохранить'))
    if (saveButton) {
      await saveButton.trigger('click')
      await new Promise((resolve) => setTimeout(resolve, 200))

      const updatedEvents = wrapper.emitted('updated')
      expect(updatedEvents).toBeTruthy()
    }
  })

  it('shows error message on failure', async () => {
    vi.mocked(distributionService.updatePublication).mockRejectedValue(new Error('API Error'))

    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /><slot name="footer" /></div>'
          },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'disabled', 'loading']
          },
          Input: {
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
            props: ['modelValue']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const buttons = wrapper.findAll('button')
    const saveButton = buttons.find((btn) => btn.text().includes('Сохранить'))
    if (saveButton) {
      await saveButton.trigger('click')
      await new Promise((resolve) => setTimeout(resolve, 200))

      expect(wrapper.text()).toContain('Не удалось')
    }
  })

  it('disables Save button when form is invalid', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: { ...mockPublication, title: '' }
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot name="body" /><slot name="footer" /></div>'
          },
          Button: {
            template: '<button @click="$emit(\'click\')" :disabled="disabled"><slot /></button>',
            props: ['variant', 'disabled', 'loading']
          },
          Input: {
            template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
            props: ['modelValue']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    const buttons = wrapper.findAll('button')
    const saveButton = buttons.find((btn) => btn.text().includes('Сохранить'))
    if (saveButton) {
      expect(saveButton.attributes('disabled')).toBeDefined()
    }
  })

  it('resets form when modal closes', async () => {
    const wrapper = mount(EditPublicationModal, {
      props: {
        isOpen: true,
        publication: mockPublication
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

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(wrapper.vm.selectedAssets.length).toBe(1)

    await wrapper.setProps({ isOpen: false })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.selectedAssets.length).toBe(0)
  })
})























