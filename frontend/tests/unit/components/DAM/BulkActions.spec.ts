import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BulkActions from '@/components/DAM/BulkActions.vue'

describe('BulkActions', () => {
  let wrapper: ReturnType<typeof mount>

  beforeEach(() => {
    wrapper = mount(BulkActions, {
      props: {
        selectedCount: 5
      }
    })
  })

  it('renders when selectedCount > 0', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
  })

  it('does not render when selectedCount is 0', async () => {
    await wrapper.setProps({ selectedCount: 0 })
    expect(wrapper.isVisible()).toBe(false)
  })

  it('displays selected count', () => {
    expect(wrapper.text()).toContain('5')
    expect(wrapper.text()).toContain('Выбрано:')
  })

  it('emits tag event when tag button clicked', async () => {
    const buttons = wrapper.findAll('button')
    const tagButton = buttons.find((btn) => btn.text().includes('Теги'))
    if (tagButton) {
      await tagButton.trigger('click')

      const events = wrapper.emitted('tag')
      expect(events).toBeTruthy()
      expect(events?.length).toBe(1)
    }
  })

  it('emits move event when move button clicked', async () => {
    const buttons = wrapper.findAll('button')
    const moveButton = buttons.find((btn) => btn.text().includes('Переместить'))
    if (moveButton) {
      await moveButton.trigger('click')

      const events = wrapper.emitted('move')
      expect(events).toBeTruthy()
    }
  })

  it('emits download event when download button clicked', async () => {
    const buttons = wrapper.findAll('button')
    const downloadButton = buttons.find((btn) => btn.text().includes('Скачать'))
    if (downloadButton) {
      await downloadButton.trigger('click')

      const events = wrapper.emitted('download')
      expect(events).toBeTruthy()
    }
  })

  it('emits share event when share button clicked', async () => {
    const buttons = wrapper.findAll('button')
    const shareButton = buttons.find((btn) => btn.text().includes('Поделиться'))
    if (shareButton) {
      await shareButton.trigger('click')

      const events = wrapper.emitted('share')
      expect(events).toBeTruthy()
    }
  })

  it('emits delete event when delete button clicked', async () => {
    const buttons = wrapper.findAll('button')
    const deleteButton = buttons.find((btn) => btn.text().includes('Удалить'))
    if (deleteButton) {
      await deleteButton.trigger('click')

      const events = wrapper.emitted('delete')
      expect(events).toBeTruthy()
    }
  })

  it('emits clear-selection event when clear button clicked', async () => {
    const buttons = wrapper.findAll('button')
    const clearButton = buttons.find((btn) => btn.text().includes('Снять выделение'))
    if (clearButton) {
      await clearButton.trigger('click')

      const events = wrapper.emitted('clear-selection')
      expect(events).toBeTruthy()
    }
  })
})

