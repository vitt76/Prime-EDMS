import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BulkShareModal from '@/components/DAM/BulkShareModal.vue'
import { assetService } from '@/services/assetService'

vi.mock('@/services/assetService')

describe('BulkShareModal', () => {
  let wrapper: ReturnType<typeof mount>

  const mockSelectedIds = [1, 2, 3, 4, 5]

  beforeEach(() => {
    wrapper = mount(BulkShareModal, {
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

  it('shows share type selector with link/users/team options', () => {
    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    expect(select.element.innerHTML).toContain('Публичная ссылка')
    expect(select.element.innerHTML).toContain('Конкретные пользователи')
    expect(select.element.innerHTML).toContain('Команда')
  })

  it('shows permissions checkboxes', () => {
    const checkboxes = wrapper.findAll('input[type="checkbox"][value]')
    expect(checkboxes.length).toBeGreaterThanOrEqual(3)
    expect(wrapper.text()).toContain('Просмотр')
    expect(wrapper.text()).toContain('Скачивание')
    expect(wrapper.text()).toContain('Комментирование')
  })

  it('has view permission checked by default', () => {
    const viewCheckbox = wrapper.find('input[value="view"]')
    expect(viewCheckbox.exists()).toBe(true)
    expect(viewCheckbox.element.checked).toBe(true)
  })

  it('disables Create Link button when no permissions selected', async () => {
    // Uncheck all permissions
    const checkboxes = wrapper.findAll('input[type="checkbox"][value]')
    for (const checkbox of checkboxes) {
      await checkbox.setValue(false)
    }
    await wrapper.vm.$nextTick()

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать ссылку'))
    if (createButton) {
      expect(createButton.attributes('disabled')).toBeDefined()
    }
  })

  it('shows expiration date input when expiration is enabled', async () => {
    const expirationCheckbox = wrapper.find('input[type="checkbox"]:not([value])')
    await expirationCheckbox.setValue(true)
    await wrapper.vm.$nextTick()

    const dateInput = wrapper.find('input[type="date"]')
    expect(dateInput.exists()).toBe(true)
  })

  it('shows password input when password protection is enabled', async () => {
    const passwordCheckboxes = wrapper.findAll('input[type="checkbox"]')
    const passwordCheckbox = passwordCheckboxes.find((cb) => {
      const label = cb.element.closest('label')
      return label?.textContent?.includes('Защитить паролем')
    })

    if (passwordCheckbox) {
      await passwordCheckbox.setValue(true)
      await wrapper.vm.$nextTick()

      const passwordInput = wrapper.find('input[type="password"]')
      expect(passwordInput.exists()).toBe(true)
    }
  })

  it('calls assetService.bulkOperation when Create Link clicked', async () => {
    const mockBulkOperation = vi.fn().mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })
    vi.mocked(assetService.bulkOperation).mockImplementation(mockBulkOperation)

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать ссылку'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    expect(mockBulkOperation).toHaveBeenCalled()
  })

  it('emits success event with share link after successful operation', async () => {
    vi.mocked(assetService.bulkOperation).mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать ссылку'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    const successEvents = wrapper.emitted('success')
    expect(successEvents).toBeTruthy()
    if (successEvents && successEvents[0]) {
      expect(successEvents[0][0]).toBeTruthy()
    }
  })

  it('shows generated share link after creation', async () => {
    vi.mocked(assetService.bulkOperation).mockResolvedValue({
      success: true,
      updated: 5,
      failed: 0
    })

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать ссылку'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Ссылка создана')
  })

  it('shows error message on failure', async () => {
    vi.mocked(assetService.bulkOperation).mockRejectedValue(new Error('API Error'))

    const buttons = wrapper.findAll('button')
    const createButton = buttons.find((btn) => btn.text().includes('Создать ссылку'))
    if (createButton) {
      await createButton.trigger('click')
    }

    await new Promise((resolve) => setTimeout(resolve, 200))

    expect(wrapper.text()).toContain('Не удалось')
  })

  it('resets form when modal opens', async () => {
    const select = wrapper.find('select')
    await select.setValue('users')
    await wrapper.vm.$nextTick()

    await wrapper.setProps({ isOpen: false })
    await wrapper.setProps({ isOpen: true })
    await wrapper.vm.$nextTick()

    const selectAfterReset = wrapper.find('select')
    expect(selectAfterReset.element.value).toBe('link')
  })
})




















