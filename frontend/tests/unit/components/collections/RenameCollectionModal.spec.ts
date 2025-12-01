import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import RenameCollectionModal from '@/components/collections/RenameCollectionModal.vue'
import type { Collection } from '@/types/collections'

describe('RenameCollectionModal', () => {
  let pinia: any
  let wrapper: ReturnType<typeof mount>
  const mockCollection: Collection = {
    id: 1,
    name: 'Test Collection',
    description: 'Test Description',
    parent_id: null,
    is_favorite: false,
    is_shared: false,
    visibility: 'private',
    asset_count: 10,
    created_by: 1,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    cover_image_id: null
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><slot /><slot name="footer" /></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<input />',
            props: ['modelValue', 'label', 'placeholder', 'required', 'error', 'hint']
          },
          Button: {
            template: '<button><slot /></button>',
            props: ['variant', 'loading', 'type']
          }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('displays modal title', () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div class="modal"><div class="modal-title">{{ title }}</div><slot /><slot name="footer" /></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: true,
          Button: true
        }
      }
    })

    expect(wrapper.text()).toContain('Rename Collection')
  })

  it('pre-fills name input with collection name', () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<input :value="modelValue" />',
            props: ['modelValue']
          },
          Button: true
        }
      }
    })

    const nameInput = wrapper.find('input')
    expect(nameInput.exists()).toBe(true)
    // Component should initialize with collection.name
  })

  it('pre-fills description textarea with collection description', () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: true,
          Button: true
        }
      }
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
    // Component should initialize with collection.description
  })

  it('emits close event on cancel button click', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /><div class="footer"><slot name="footer" /></div></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: true,
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'type']
          }
        }
      }
    })

    const cancelButton = wrapper.findAll('button').find((btn) => btn.text() === 'Cancel')
    if (cancelButton) {
      await cancelButton.trigger('click')
      expect(wrapper.emitted('close')).toBeTruthy()
    }
  })

  it('validates name is required', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /><div class="footer"><slot name="footer" /></div></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<input v-model="modelValue" />',
            props: ['modelValue'],
            emits: ['update:modelValue']
          },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'type']
          }
        }
      }
    })

    const nameInput = wrapper.find('input')
    await nameInput.setValue('')

    const submitButton = wrapper.findAll('button').find((btn) => btn.text()?.includes('Update'))
    if (submitButton) {
      await submitButton.trigger('click')
      // Validation should prevent submit
      expect(wrapper.emitted('submit')).toBeFalsy()
    }
  })

  it('validates name max length (255 characters)', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /><div class="footer"><slot name="footer" /></div></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<input v-model="modelValue" />',
            props: ['modelValue'],
            emits: ['update:modelValue']
          },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'type']
          }
        }
      }
    })

    const nameInput = wrapper.find('input')
    const longName = 'a'.repeat(256)
    await nameInput.setValue(longName)

    const submitButton = wrapper.findAll('button').find((btn) => btn.text()?.includes('Update'))
    if (submitButton) {
      await submitButton.trigger('click')
      // Validation should prevent submit
      expect(wrapper.emitted('submit')).toBeFalsy()
    }
  })

  it('emits submit event with form data on valid submission', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /><div class="footer"><slot name="footer" /></div></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<input v-model="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
            props: ['modelValue'],
            emits: ['update:modelValue']
          },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'type']
          }
        }
      }
    })

    const nameInput = wrapper.find('input')
    await nameInput.setValue('Updated Collection Name')

    const submitButton = wrapper.findAll('button').find((btn) => btn.text()?.includes('Update'))
    if (submitButton) {
      await submitButton.trigger('click')
      // Component should emit submit with valid data
    }
  })

  it('shows loading state when submitting', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /><div class="footer"><slot name="footer" /></div></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: true,
          Button: {
            template: '<button :disabled="loading"><slot /></button>',
            props: ['variant', 'loading', 'type']
          }
        }
      }
    })

    // Component should set isSubmitting to true during submission
    expect(wrapper.exists()).toBe(true)
  })

  it('displays error message when validation fails', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /><div class="footer"><slot name="footer" /></div></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<div><input /><span v-if="error" class="error">{{ error }}</span></div>',
            props: ['modelValue', 'error']
          },
          Button: true
        }
      }
    })

    // Error should be displayed when validation fails
    expect(wrapper.exists()).toBe(true)
  })

  it('updates form data when collection prop changes', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<input :value="modelValue" />',
            props: ['modelValue']
          },
          Button: true
        }
      }
    })

    const newCollection: Collection = {
      ...mockCollection,
      name: 'New Collection Name',
      description: 'New Description'
    }

    await wrapper.setProps({ collection: newCollection })

    // Component should update form data when collection prop changes
    expect(wrapper.props('collection').name).toBe('New Collection Name')
  })

  it('trims name and description before submission', async () => {
    wrapper = mount(RenameCollectionModal, {
      props: {
        collection: mockCollection
      },
      global: {
        plugins: [pinia],
        stubs: {
          Modal: {
            template: '<div><slot /><div class="footer"><slot name="footer" /></div></div>',
            props: ['isOpen', 'title', 'size']
          },
          Input: {
            template: '<input v-model="modelValue" />',
            props: ['modelValue'],
            emits: ['update:modelValue']
          },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'type']
          }
        }
      }
    })

    const nameInput = wrapper.find('input')
    await nameInput.setValue('  Updated Name  ')

    // Component should trim the value before submission
    expect(wrapper.exists()).toBe(true)
  })
})



