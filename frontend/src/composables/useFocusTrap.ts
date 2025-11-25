import { onMounted, onUnmounted, Ref } from 'vue'

/**
 * Focus trap composable for modals and dialogs
 * Traps focus within the specified element
 */
export function useFocusTrap(elementRef: Ref<HTMLElement | null>, isActive: Ref<boolean>) {
  let previousActiveElement: HTMLElement | null = null

  function getFocusableElements(): HTMLElement[] {
    if (!elementRef.value) return []

    const focusableSelectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])'
    ].join(', ')

    return Array.from(
      elementRef.value.querySelectorAll<HTMLElement>(focusableSelectors)
    ).filter((el) => {
      // Filter out hidden elements
      const style = window.getComputedStyle(el)
      return style.display !== 'none' && style.visibility !== 'hidden'
    })
  }

  function trapFocus(event: KeyboardEvent) {
    if (!isActive.value || !elementRef.value) return

    const focusableElements = getFocusableElements()
    if (focusableElements.length === 0) return

    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    if (!firstElement || !lastElement) return

    // Tab key
    if (event.key === 'Tab') {
      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault()
          lastElement.focus()
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault()
          firstElement.focus()
        }
      }
    }

    // Escape key handled by parent component
  }

  function activate() {
    if (!elementRef.value) return

    // Store current active element
    previousActiveElement = document.activeElement as HTMLElement

    // Focus first focusable element
    const focusableElements = getFocusableElements()
    if (focusableElements.length > 0 && focusableElements[0]) {
      focusableElements[0].focus()
    } else {
      // If no focusable elements, focus the container
      elementRef.value.focus()
    }

    // Add event listener
    document.addEventListener('keydown', trapFocus)
  }

  function deactivate() {
    // Remove event listener
    document.removeEventListener('keydown', trapFocus)

    // Restore previous focus
    if (previousActiveElement && previousActiveElement instanceof HTMLElement) {
      previousActiveElement.focus()
    }
  }

  onMounted(() => {
    if (isActive.value) {
      activate()
    }
  })

  onUnmounted(() => {
    deactivate()
  })

  return {
    activate,
    deactivate
  }
}

