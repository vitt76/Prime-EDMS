import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BulkTagModal from '@/components/DAM/BulkTagModal.vue'
import { assetService } from '@/services/assetService'

vi.mock('@/services/assetService')

describe('BulkTagModal', () => {
  let wrapper: ReturnType<typeof mount>

  const mockSelectedIds = [1, 2, 3, 4, 5]

  beforeEach(() => {
    wrapper = mount(BulkTagModal, {
      props: {
        isOpen: true,
        selectedIds: mockSelectedIds
      },
      global: {
        stubs: {
          Modal: {
            template: '<div class="modal"><slot /><slot name="header" /><slot name="footer" /></div>',
            props: ['isOpen', 'size']
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

  it('has operation selector with add/remove/replace options', () => {
    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    expect(select.element.innerHTML).toContain('Добавить теги')
    expect(select.element.innerHTML).toContain('Удалить теги')
    expect(select.element.innerHTML).toContain('Заменить все теги')
  })

  it('disables Apply button when no tags are selected', () => {
    const applyButton = wrapper.findAll('button').find((btn) => btn.text().includes('Применить'))
    if (applyButton) {
      expect(applyButton.attributes('disabled')).toBeDefined()
    }
  })

  it('calls assetService.bulkOperation when Apply clicked', async () => {
    const mockBulkOperation = vi.fn().mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })
    vi.mocked(assetService.bulkOperation).mockImplementation(mockBulkOperation)

    // Add a tag
    const tagInput = wrapper.findComponent({ name: 'TagInput' })
    await tagInput.vm.$emit('update:modelValue', ['test-tag'])

    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const applyButton = buttons.find((btn) => btn.text().includes('Применить'))
    if (applyButton) {
      await applyButton.trigger('click')
    }

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(mockBulkOperation).toHaveBeenCalledWith({
      ids: mockSelectedIds,
      action: 'add_tags',
      data: { tags: ['test-tag'] }
    })
  })

  it('emits success event after successful operation', async () => {
    vi.mocked(assetService.bulkOperation).mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })

    const tagInput = wrapper.findComponent({ name: 'TagInput' })
    await tagInput.vm.$emit('update:modelValue', ['test-tag'])

    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const applyButton = buttons.find((btn) => btn.text().includes('Применить'))
    if (applyButton) {
      await applyButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    const successEvents = wrapper.emitted('success')
    expect(successEvents).toBeTruthy()
  })

  it('shows error message on failure', async () => {
    vi.mocked(assetService.bulkOperation).mockRejectedValue(new Error('API Error'))

    const tagInput = wrapper.findComponent({ name: 'TagInput' })
    await tagInput.vm.$emit('update:modelValue', ['test-tag'])

    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const applyButton = buttons.find((btn) => btn.text().includes('Применить'))
    if (applyButton) {
      await applyButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Ошибка')
  })

  it('shows progress indicator during processing', async () => {
    vi.mocked(assetService.bulkOperation).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ success: true, updated: 5, failed: 0 }), 1000))
    )

    const tagInput = wrapper.findComponent({ name: 'TagInput' })
    await tagInput.vm.$emit('update:modelValue', ['test-tag'])

    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const applyButton = buttons.find((btn) => btn.text().includes('Применить'))
    if (applyButton) {
      await applyButton.trigger('click')
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Обработка')
  })
})

