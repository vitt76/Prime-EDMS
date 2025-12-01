import { ref, onMounted, onUnmounted, type Ref } from 'vue'

/**
 * Intersection Observer composable for lazy loading
 */
export function useIntersectionObserver(
  elementRef: Ref<HTMLElement | null>,
  options?: IntersectionObserverInit
) {
  const isIntersecting = ref(false)
  const hasIntersected = ref(false)

  let observer: IntersectionObserver | null = null

  const defaultOptions: IntersectionObserverInit = {
    root: null,
    rootMargin: '50px',
    threshold: 0.1,
    ...options
  }

  onMounted(() => {
    if (!elementRef.value) return

    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        isIntersecting.value = entry.isIntersecting
        if (entry.isIntersecting && !hasIntersected.value) {
          hasIntersected.value = true
        }
      })
    }, defaultOptions)

    observer.observe(elementRef.value)
  })

  onUnmounted(() => {
    if (observer && elementRef.value) {
      observer.unobserve(elementRef.value)
      observer.disconnect()
    }
  })

  return {
    isIntersecting,
    hasIntersected
  }
}

