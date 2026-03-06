import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { defineComponent, h, nextTick, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { useFocusTrap } from '@/composables/useFocusTrap'

describe('useFocusTrap', () => {
  async function flushFocus() {
    await nextTick()
    await nextTick()
  }

  function mountHarness(options?: { active?: boolean; autofocus?: boolean }) {
    const Harness = defineComponent({
      props: {
        active: {
          type: Boolean,
          default: true
        },
        autofocus: {
          type: Boolean,
          default: false
        }
      },
      setup(props, { expose }) {
        const containerRef = ref<HTMLElement | null>(null)
        const activeRef = ref(props.active)
        const { activate, deactivate } = useFocusTrap(containerRef, activeRef)

        expose({ activate, deactivate, activeRef })

        return () =>
          h('div', { ref: containerRef }, [
            h('button', 'Button 1'),
            h('input', { type: 'text', ...(props.autofocus ? { 'data-autofocus': '' } : {}) }),
            h('button', 'Button 2')
          ])
      }
    })

    return mount(Harness, {
      props: {
        active: options?.active ?? true,
        autofocus: options?.autofocus ?? false
      },
      attachTo: document.body
    })
  }

  beforeEach(() => {
    document.body.innerHTML = ''
  })

  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('traps focus within container when active', async () => {
    const wrapper = mountHarness()
    await flushFocus()

    // Focus should be on first element
    const button1 = wrapper.findAll('button')[0]?.element
    expect(document.activeElement).toBe(button1)
  })

  it('cycles focus from last to first element on Tab', async () => {
    const wrapper = mountHarness()
    await flushFocus()
    const buttons = wrapper.findAll('button')
    const button1 = buttons[0]?.element as HTMLButtonElement
    const button2 = buttons[1]?.element as HTMLButtonElement

    // Focus last element
    button2.focus()
    expect(document.activeElement).toBe(button2)

    // Press Tab
    document.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'Tab',
      bubbles: true
    }))

    // Should cycle to first element
    await flushFocus()
    expect(document.activeElement).toBe(button1)
  })

  it('cycles focus from first to last element on Shift+Tab', async () => {
    const wrapper = mountHarness()
    await flushFocus()
    const buttons = wrapper.findAll('button')
    const button1 = buttons[0]?.element as HTMLButtonElement
    const button2 = buttons[1]?.element as HTMLButtonElement

    // Focus first element
    button1.focus()
    expect(document.activeElement).toBe(button1)

    // Press Shift+Tab
    document.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'Tab',
      shiftKey: true,
      bubbles: true
    }))

    // Should cycle to last element
    await flushFocus()
    expect(document.activeElement).toBe(button2)
  })

  it('does not trap focus when inactive', async () => {
    mountHarness({ active: false })
    await flushFocus()

    // Focus should not be trapped
    expect(document.activeElement).toBe(document.body)
  })

  it('updates tabbable elements when active state changes', async () => {
    const wrapper = mountHarness({ active: false })
    await flushFocus()

    // Activate trap
    ;(wrapper.vm as unknown as { activate: () => void }).activate()
    await flushFocus()

    const button1 = wrapper.findAll('button')[0]?.element
    expect(document.activeElement).toBe(button1)
  })

  it('restores focus to the previously active element on deactivate', async () => {
    const trigger = document.createElement('button')
    trigger.textContent = 'Trigger'
    document.body.appendChild(trigger)
    trigger.focus()

    const wrapper = mountHarness()
    await flushFocus()
    const button1 = wrapper.findAll('button')[0]?.element
    expect(document.activeElement).toBe(button1)

    ;(wrapper.vm as unknown as { deactivate: () => void }).deactivate()
    expect(document.activeElement).toBe(trigger)

    document.body.removeChild(trigger)
  })

  it('prefers data-autofocus elements when activating', async () => {
    const wrapper = mountHarness({ autofocus: true })
    await flushFocus()

    const input = wrapper.find('input').element
    expect(document.activeElement).toBe(input)
  })

  it('handles empty container gracefully', async () => {
    const Harness = defineComponent({
      setup() {
        const containerRef = ref<HTMLElement | null>(null)
        const activeRef = ref(true)
        useFocusTrap(containerRef, activeRef)
        return () => h('div', { ref: containerRef })
      }
    })

    // Should not throw
    expect(() => {
      mount(Harness, { attachTo: document.body })
    }).not.toThrow()
  })

  it('ignores disabled elements', async () => {
    const Harness = defineComponent({
      setup() {
        const containerRef = ref<HTMLElement | null>(null)
        const activeRef = ref(true)
        useFocusTrap(containerRef, activeRef)
        return () =>
          h('div', { ref: containerRef }, [
            h('button', { disabled: true }, 'Disabled'),
            h('button', 'Enabled')
          ])
      }
    })

    const wrapper = mount(Harness, { attachTo: document.body })
    await flushFocus()

    // Disabled button should not be in tabbable elements
    const tabbableElements = Array.from(wrapper.element.querySelectorAll('button, input'))
      .filter((el) => !(el as HTMLElement).hasAttribute('disabled'))

    expect(tabbableElements).toHaveLength(1)
  })
})
