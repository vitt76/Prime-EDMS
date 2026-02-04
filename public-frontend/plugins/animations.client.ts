/**
 * Animations Plugin
 * 
 * Provides scroll-based reveal animations and other animation utilities
 */

export default defineNuxtPlugin((nuxtApp) => {
  // IntersectionObserver for scroll animations
  if (typeof window !== 'undefined' && 'IntersectionObserver' in window) {
    const observerOptions: IntersectionObserverInit = {
      root: null,
      rootMargin: '0px 0px -50px 0px',
      threshold: 0.1
    }

    const animateOnScroll = (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in')
          entry.target.classList.remove('animate-out')
        }
      })
    }

    const observer = new IntersectionObserver(animateOnScroll, observerOptions)

    // Directive for scroll animation
    nuxtApp.vueApp.directive('animate-on-scroll', {
      mounted(el: HTMLElement, binding) {
        // Add initial hidden state
        el.classList.add('animate-out')
        
        // Set animation type
        const animationType = binding.value || 'fade-up'
        el.dataset.animation = animationType
        
        // Set delay if provided
        if (binding.arg) {
          el.style.transitionDelay = `${binding.arg}ms`
        }
        
        observer.observe(el)
      },
      unmounted(el: HTMLElement) {
        observer.unobserve(el)
      }
    })

    // Stagger animation for lists
    nuxtApp.vueApp.directive('stagger', {
      mounted(el: HTMLElement, binding) {
        const children = el.children
        const baseDelay = binding.value || 100

        Array.from(children).forEach((child, index) => {
          const htmlChild = child as HTMLElement
          htmlChild.classList.add('animate-out')
          htmlChild.style.transitionDelay = `${index * baseDelay}ms`
          observer.observe(htmlChild)
        })
      }
    })
  }

  // Add animation styles
  useHead({
    style: [
      {
        children: `
          /* Animation base styles */
          .animate-out {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease-out, transform 0.6s ease-out;
          }

          .animate-in {
            opacity: 1;
            transform: translateY(0);
          }

          /* Animation variants */
          [data-animation="fade-up"].animate-out {
            opacity: 0;
            transform: translateY(30px);
          }

          [data-animation="fade-down"].animate-out {
            opacity: 0;
            transform: translateY(-30px);
          }

          [data-animation="fade-left"].animate-out {
            opacity: 0;
            transform: translateX(30px);
          }

          [data-animation="fade-right"].animate-out {
            opacity: 0;
            transform: translateX(-30px);
          }

          [data-animation="scale"].animate-out {
            opacity: 0;
            transform: scale(0.95);
          }

          [data-animation="fade"].animate-out {
            opacity: 0;
            transform: none;
          }

          /* Reset transforms for animated-in state */
          [data-animation="fade-left"].animate-in,
          [data-animation="fade-right"].animate-in {
            transform: translateX(0);
          }

          [data-animation="scale"].animate-in {
            transform: scale(1);
          }
        `
      }
    ]
  })

  // Provide animation utilities
  return {
    provide: {
      animations: {
        /**
         * Trigger a CSS animation on an element
         */
        animate(el: HTMLElement, animation: string, duration = 300) {
          return new Promise<void>((resolve) => {
            el.style.animation = `${animation} ${duration}ms ease-out`
            el.addEventListener('animationend', () => {
              el.style.animation = ''
              resolve()
            }, { once: true })
          })
        },

        /**
         * Smooth scroll to element
         */
        scrollTo(selector: string, offset = 80) {
          const el = document.querySelector(selector)
          if (el) {
            const top = el.getBoundingClientRect().top + window.scrollY - offset
            window.scrollTo({ top, behavior: 'smooth' })
          }
        }
      }
    }
  }
})
