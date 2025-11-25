import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { useFocusTrap } from '@/composables/useFocusTrap'

describe('useFocusTrap', () => {
  let container: HTMLElement
  let button1: HTMLButtonElement
  let button2: HTMLButtonElement
  let input: HTMLInputElement

  beforeEach(() => {
    container = document.createElement('div')
    button1 = document.createElement('button')
    button1.textContent = 'Button 1'
    button2 = document.createElement('button')
    button2.textContent = 'Button 2'
    input = document.createElement('input')
    input.type = 'text'

    container.appendChild(button1)
    container.appendChild(input)
    container.appendChild(button2)
    document.body.appendChild(container)
  })

  afterEach(() => {
    document.body.removeChild(container)
  })

  it('traps focus within container when active', async () => {
    const targetRef = ref<HTMLElement | null>(container)
    const isActive = ref(true)

    useFocusTrap(targetRef, isActive)

    await nextTick()

    // Focus should be on first element
    expect(document.activeElement).toBe(button1)
  })

  it('cycles focus from last to first element on Tab', async () => {
    const targetRef = ref<HTMLElement | null>(container)
    const isActive = ref(true)

    useFocusTrap(targetRef, isActive)

    await nextTick()

    // Focus last element
    button2.focus()
    expect(document.activeElement).toBe(button2)

    // Press Tab
    const tabEvent = new KeyboardEvent('keydown', {
      key: 'Tab',
      bubbles: true
    })
    button2.dispatchEvent(tabEvent)

    // Should cycle to first element
    await nextTick()
    expect(document.activeElement).toBe(button1)
  })

  it('cycles focus from first to last element on Shift+Tab', async () => {
    const targetRef = ref<HTMLElement | null>(container)
    const isActive = ref(true)

    useFocusTrap(targetRef, isActive)

    await nextTick()

    // Focus first element
    button1.focus()
    expect(document.activeElement).toBe(button1)

    // Press Shift+Tab
    const shiftTabEvent = new KeyboardEvent('keydown', {
      key: 'Tab',
      shiftKey: true,
      bubbles: true
    })
    button1.dispatchEvent(shiftTabEvent)

    // Should cycle to last element
    await nextTick()
    expect(document.activeElement).toBe(button2)
  })

  it('does not trap focus when inactive', async () => {
    const targetRef = ref<HTMLElement | null>(container)
    const isActive = ref(false)

    useFocusTrap(targetRef, isActive)

    await nextTick()

    // Focus should not be trapped
    expect(document.activeElement).not.toBe(button1)
  })

  it('updates tabbable elements when active state changes', async () => {
    const targetRef = ref<HTMLElement | null>(container)
    const isActive = ref(false)

    const { activate } = useFocusTrap(targetRef, isActive)

    await nextTick()

    // Activate trap
    activate()
    await nextTick()

    expect(document.activeElement).toBe(button1)
  })

  it('handles empty container gracefully', async () => {
    const emptyContainer = document.createElement('div')
    const targetRef = ref<HTMLElement | null>(emptyContainer)
    const isActive = ref(true)

    // Should not throw
    expect(() => {
      useFocusTrap(targetRef, isActive)
    }).not.toThrow()
  })

  it('ignores disabled elements', async () => {
    const disabledButton = document.createElement('button')
    disabledButton.disabled = true
    disabledButton.textContent = 'Disabled'
    container.appendChild(disabledButton)

    const targetRef = ref<HTMLElement | null>(container)
    const isActive = ref(true)

    useFocusTrap(targetRef, isActive)

    await nextTick()

    // Disabled button should not be in tabbable elements
    const tabbableElements = Array.from(container.querySelectorAll('button, input'))
      .filter((el) => !(el as HTMLElement).hasAttribute('disabled'))
    
    expect(tabbableElements).not.toContain(disabledButton)
  })
})
