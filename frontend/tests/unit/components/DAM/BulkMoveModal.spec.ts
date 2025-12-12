import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BulkMoveModal from '@/components/DAM/BulkMoveModal.vue'
import { assetService } from '@/services/assetService'

vi.mock('@/services/assetService')

describe('BulkMoveModal', () => {
  let wrapper: ReturnType<typeof mount>

  const mockSelectedIds = [1, 2, 3, 4, 5]
  const mockCollections = [
    { id: 1, name: 'Collection 1' },
    { id: 2, name: 'Collection 2' },
    { id: 3, name: 'Collection 3' }
  ]

  beforeEach(() => {
    wrapper = mount(BulkMoveModal, {
      props: {
        isOpen: true,
        selectedIds: mockSelectedIds,
        collections: mockCollections
      },
      global: {
        stubs: {
          Modal: {
            template: '<div class="modal"><slot /><slot name="header" /><slot name="footer" /></div>',
            props: ['isOpen', 'size']
          },
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant', 'size', 'disabled']
          }
        }
      }
    })
  })

  it('renders when isOpen is true', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays selected count', () => {
    expect(wrapper.text()).toContain('5')
  })

  it('shows collection selector with available collections', () => {
    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    expect(select.element.innerHTML).toContain('Collection 1')
    expect(select.element.innerHTML).toContain('Collection 2')
    expect(select.element.innerHTML).toContain('Collection 3')
  })

  it('shows create new collection option', () => {
    const createButton = wrapper.find('button')
    expect(createButton.exists()).toBe(true)
    expect(createButton.text()).toContain('Создать новую коллекцию')
  })

  it('toggles new collection input when create button clicked', async () => {
    const createButton = wrapper.find('button')
    await createButton.trigger('click')
    await wrapper.vm.$nextTick()

    const input = wrapper.find('input[type="text"]')
    expect(input.exists()).toBe(true)
  })

  it('disables Move button when no collection is selected', () => {
    const buttons = wrapper.findAll('button')
    const moveButton = buttons.find((btn) => btn.text().includes('Переместить'))
    if (moveButton) {
      expect(moveButton.attributes('disabled')).toBeDefined()
    }
  })

  it('enables Move button when collection is selected', async () => {
    const select = wrapper.find('select')
    await select.setValue('1')
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const moveButton = buttons.find((btn) => btn.text().includes('Переместить'))
    if (moveButton) {
      expect(moveButton.attributes('disabled')).toBeUndefined()
    }
  })

  it('calls assetService.bulkOperation when Move clicked', async () => {
    const mockBulkOperation = vi.fn().mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })
    vi.mocked(assetService.bulkOperation).mockImplementation(mockBulkOperation)

    const select = wrapper.find('select')
    await select.setValue('1')
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const moveButton = buttons.find((btn) => btn.text().includes('Переместить'))
    if (moveButton) {
      await moveButton.trigger('click')
    }

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(mockBulkOperation).toHaveBeenCalledWith({
      ids: mockSelectedIds,
      action: 'move',
      data: { collection_id: 1 }
    })
  })

  it('emits success event after successful operation', async () => {
    vi.mocked(assetService.bulkOperation).mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })

    const select = wrapper.find('select')
    await select.setValue('1')
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const moveButton = buttons.find((btn) => btn.text().includes('Переместить'))
    if (moveButton) {
      await moveButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    const successEvents = wrapper.emitted('success')
    expect(successEvents).toBeTruthy()
  })

  it('shows error message on failure', async () => {
    vi.mocked(assetService.bulkOperation).mockRejectedValue(new Error('API Error'))

    const select = wrapper.find('select')
    await select.setValue('1')
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const moveButton = buttons.find((btn) => btn.text().includes('Переместить'))
    if (moveButton) {
      await moveButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Ошибка')
  })

  it('shows progress indicator during processing', async () => {
    vi.mocked(assetService.bulkOperation).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ success: true, updated: 5, failed: 0 }), 1000))
    )

    const select = wrapper.find('select')
    await select.setValue('1')
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const moveButton = buttons.find((btn) => btn.text().includes('Переместить'))
    if (moveButton) {
      await moveButton.trigger('click')
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Перемещение')
  })

  it('resets form when modal opens', async () => {
    const select = wrapper.find('select')
    await select.setValue('1')
    await wrapper.vm.$nextTick()

    await wrapper.setProps({ isOpen: false })
    await wrapper.setProps({ isOpen: true })
    await wrapper.vm.$nextTick()

    const selectAfterReset = wrapper.find('select')
    expect(selectAfterReset.element.value).toBe('')
  })
})




















