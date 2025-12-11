import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BulkDownloadModal from '@/components/DAM/BulkDownloadModal.vue'
import { assetService } from '@/services/assetService'

vi.mock('@/services/assetService')

describe('BulkDownloadModal', () => {
  let wrapper: ReturnType<typeof mount>

  const mockSelectedIds = [1, 2, 3, 4, 5]

  beforeEach(() => {
    wrapper = mount(BulkDownloadModal, {
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

  it('displays selected count', () => {
    expect(wrapper.text()).toContain('5')
  })

  it('shows format selector with ZIP and TAR options', () => {
    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    expect(select.element.innerHTML).toContain('ZIP архив')
    expect(select.element.innerHTML).toContain('TAR архив')
  })

  it('has default format as ZIP', () => {
    const select = wrapper.find('select')
    expect(select.element.value).toBe('zip')
  })

  it('shows metadata and structure options', () => {
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThanOrEqual(2)
  })

  it('has includeMetadata checked by default', () => {
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    const metadataCheckbox = checkboxes.find((cb) => cb.attributes('value') === undefined && cb.element.checked)
    expect(metadataCheckbox).toBeDefined()
  })

  it('calls assetService.bulkOperation when Create Archive clicked', async () => {
    const mockBulkOperation = vi.fn().mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })
    vi.mocked(assetService.bulkOperation).mockImplementation(mockBulkOperation)

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать архив'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(mockBulkOperation).toHaveBeenCalledWith({
      ids: mockSelectedIds,
      action: 'export',
      data: {
        format: 'zip',
        include_metadata: true,
        preserve_structure: false
      }
    })
  })

  it('shows progress indicator during processing', async () => {
    vi.mocked(assetService.bulkOperation).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ success: true, updated: 5, failed: 0 }), 1000))
    )

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать архив'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Создание архива')
  })

  it('shows download link after archive creation', async () => {
    vi.mocked(assetService.bulkOperation).mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать архив'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Архив готов')
  })

  it('emits success event after successful operation', async () => {
    vi.mocked(assetService.bulkOperation).mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать архив'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    const successEvents = wrapper.emitted('success')
    expect(successEvents).toBeTruthy()
  })

  it('shows error message on failure', async () => {
    vi.mocked(assetService.bulkOperation).mockRejectedValue(new Error('API Error'))

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать архив'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Не удалось')
  })

  it('resets form when modal opens', async () => {
    const select = wrapper.find('select')
    await select.setValue('tar')
    await wrapper.vm.$nextTick()

    await wrapper.setProps({ isOpen: false })
    await wrapper.setProps({ isOpen: true })
    await wrapper.vm.$nextTick()

    const selectAfterReset = wrapper.find('select')
    expect(selectAfterReset.element.value).toBe('zip')
  })
})



















