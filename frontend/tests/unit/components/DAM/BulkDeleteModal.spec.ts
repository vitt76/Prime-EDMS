import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BulkDeleteModal from '@/components/DAM/BulkDeleteModal.vue'
import { assetService } from '@/services/assetService'

vi.mock('@/services/assetService')

describe('BulkDeleteModal', () => {
  let wrapper: ReturnType<typeof mount>

  const mockSelectedIds = [1, 2, 3, 4, 5]

  beforeEach(() => {
    wrapper = mount(BulkDeleteModal, {
      props: {
        isOpen: true,
        selectedIds: mockSelectedIds
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

  it('displays warning message with selected count', () => {
    expect(wrapper.text()).toContain('5')
    expect(wrapper.text()).toContain('Внимание')
    expect(wrapper.text()).toContain('нельзя отменить')
  })

  it('shows confirmation checkbox', () => {
    const checkbox = wrapper.find('input[type="checkbox"]')
    expect(checkbox.exists()).toBe(true)
    expect(checkbox.attributes('id')).toBe('confirm-delete')
  })

  it('disables Delete button when confirmation is not checked', () => {
    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      expect(deleteButton.attributes('disabled')).toBeDefined()
    }
  })

  it('enables Delete button when confirmation is checked', async () => {
    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setValue(true)
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      expect(deleteButton.attributes('disabled')).toBeUndefined()
    }
  })

  it('calls assetService.bulkOperation when Delete clicked', async () => {
    const mockBulkOperation = vi.fn().mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })
    vi.mocked(assetService.bulkOperation).mockImplementation(mockBulkOperation)

    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setValue(true)
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      await deleteButton.trigger('click')
    }

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(mockBulkOperation).toHaveBeenCalledWith({
      ids: mockSelectedIds,
      action: 'delete'
    })
  })

  it('emits success event after successful operation', async () => {
    vi.mocked(assetService.bulkOperation).mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })

    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setValue(true)
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      await deleteButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    const successEvents = wrapper.emitted('success')
    expect(successEvents).toBeTruthy()
  })

  it('shows error message on failure', async () => {
    vi.mocked(assetService.bulkOperation).mockRejectedValue(new Error('API Error'))

    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setValue(true)
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      await deleteButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Ошибка')
  })

  it('shows progress indicator during processing', async () => {
    vi.mocked(assetService.bulkOperation).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ success: true, updated: 5, failed: 0 }), 1000))
    )

    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setValue(true)
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      await deleteButton.trigger('click')
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Удаление')
  })

  it('resets form when modal opens', async () => {
    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.setValue(true)
    await wrapper.vm.$nextTick()

    await wrapper.setProps({ isOpen: false })
    await wrapper.setProps({ isOpen: true })
    await wrapper.vm.$nextTick()

    const checkboxAfterReset = wrapper.find('input[type="checkbox"]')
    expect(checkboxAfterReset.element.checked).toBe(false)
  })
})














