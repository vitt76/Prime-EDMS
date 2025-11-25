import { ref, watch, onUnmounted, type Ref } from 'vue'

/**
 * Debounce composable for delaying function execution
 * @param value - The value to debounce
 * @param delay - Delay in milliseconds (default: 300ms)
 * @returns Debounced value
 */
export function useDebounce<T>(value: Ref<T>, delay: number = 300) {
  const debouncedValue = ref<T>(value.value) as Ref<T>
  let timeoutId: ReturnType<typeof setTimeout> | null = null

  const updateDebouncedValue = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    timeoutId = setTimeout(() => {
      debouncedValue.value = value.value
    }, delay)
  }

  watch(value, updateDebouncedValue, { immediate: true })

  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
  })

  return debouncedValue
}

