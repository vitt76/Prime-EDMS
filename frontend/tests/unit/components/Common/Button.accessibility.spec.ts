import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/vue'
import { axe } from 'vitest-axe'
import Button from '@/components/Common/Button.vue'

describe('Button Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(Button, {
      slots: {
        default: 'Test Button'
      }
    })
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper ARIA attributes when loading', async () => {
    const { container } = render(Button, {
      props: {
        loading: true
      },
      slots: {
        default: 'Loading...'
      }
    })
    
    const button = container.querySelector('button')
    expect(button).toHaveAttribute('aria-busy', 'true')
    expect(button).toHaveAttribute('aria-disabled', 'true')
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper ARIA attributes when disabled', async () => {
    const { container } = render(Button, {
      props: {
        disabled: true
      },
      slots: {
        default: 'Disabled Button'
      }
    })
    
    const button = container.querySelector('button')
    expect(button).toHaveAttribute('aria-disabled', 'true')
    
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have minimum touch target size (44x44px)', () => {
    const { container } = render(Button, {
      props: {
        size: 'sm'
      },
      slots: {
        default: 'Small Button'
      }
    })
    
    const button = container.querySelector('button')
    const styles = window.getComputedStyle(button!)
    
    // Check that min-height and min-width are at least 44px
    expect(button?.classList.contains('min-h-[44px]')).toBe(true)
    expect(button?.classList.contains('min-w-[44px]')).toBe(true)
  })
})























