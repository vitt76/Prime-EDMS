<template>
  <div>
    <!-- Normal content when no error -->
    <slot v-if="!hasError" />

    <!-- Error fallback UI -->
    <div
      v-else
      class="error-boundary"
      role="alert"
      aria-live="assertive"
      tabindex="-1"
      ref="errorContainer"
    >
      <Card class="max-w-2xl mx-auto">
        <div class="text-center py-8 px-6">
          <!-- Error Icon -->
          <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/20 mb-6">
            <svg
              class="h-8 w-8 text-red-600 dark:text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>

          <!-- Error Title -->
          <h2 class="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
            {{ title }}
          </h2>

          <!-- Error Message -->
          <p class="text-neutral-600 dark:text-neutral-400 mb-6 max-w-md mx-auto">
            {{ message }}
          </p>

          <!-- Error Details (Development Only) -->
          <details
            v-if="isDevelopment && errorDetails"
            class="mb-6 text-left bg-neutral-50 dark:bg-neutral-800 rounded-lg p-4 max-w-2xl mx-auto"
          >
            <summary class="cursor-pointer text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Error Details (Development)
            </summary>
            <pre class="text-xs text-neutral-600 dark:text-neutral-400 whitespace-pre-wrap overflow-auto max-h-64">{{ errorDetails }}</pre>
          </details>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              variant="primary"
              @click="handleRetry"
              :loading="retrying"
              :disabled="retryCount >= maxRetries"
            >
              {{ retryButtonText }}
            </Button>

            <Button
              variant="outline"
              @click="handleReload"
            >
              Reload Page
            </Button>

            <Button
              v-if="isDevelopment"
              variant="ghost"
              @click="handleReportError"
              class="text-neutral-600 dark:text-neutral-400"
            >
              Report Issue
            </Button>
          </div>

          <!-- Retry Progress -->
          <div v-if="retrying && retryCount > 0" class="mt-4">
            <div class="text-sm text-neutral-500 dark:text-neutral-400 mb-2">
              Retrying... ({{ retryCount }}/{{ maxRetries }})
            </div>
            <div class="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
              <div
                class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${(retryCount / maxRetries) * 100}%` }"
              ></div>
            </div>
          </div>

          <!-- Auto-retry countdown -->
          <div v-if="showAutoRetry" class="mt-4 text-sm text-neutral-500 dark:text-neutral-400">
            Auto-retrying in {{ autoRetryCountdown }}s...
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Global Error Boundary Component
 *
 * Catches and handles all unhandled errors in the component tree.
 * Provides user-friendly error UI with retry functionality.
 * Supports both development (detailed) and production (safe) modes.
 */

import { ref, computed, watch, nextTick, onMounted, onUnmounted, onErrorCaptured } from 'vue'
import Card from '@/components/Common/Card.vue'
import Button from '@/components/Common/Button.vue'
// Simple error logging - avoid circular dependency
const logError = (error: Error, context?: any) => {
  console.error('ErrorBoundary caught error:', error, context)

  // Send to external logging if available
  if (window.Sentry) {
    window.Sentry.captureException(error, { extra: context })
  }
}

const shouldRetry = (error: Error): boolean => {
  // Simple retry logic - retry network and server errors
  return error.name === 'TypeError' || (error as any).status >= 500
}

// Props
interface Props {
  /** Custom error title */
  title?: string
  /** Custom error message */
  message?: string
  /** Maximum retry attempts */
  maxRetries?: number
  /** Auto-retry delay in seconds */
  autoRetryDelay?: number
  /** Show auto-retry countdown */
  showAutoRetry?: boolean
  /** Custom retry handler */
  onRetry?: (attempt: number) => Promise<void> | void
  /** Custom error handler */
  onError?: (error: Error, instance: any, info: string) => void
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Something went wrong',
  message: 'We encountered an unexpected error. Please try again.',
  maxRetries: 3,
  autoRetryDelay: 5,
  showAutoRetry: true
})

// Emits
const emit = defineEmits<{
  error: [error: Error, instance: any, info: string]
  retry: [attempt: number]
  recovered: []
}>()

// Composables - imported at module level

// Reactive state
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorInfo = ref('')
const errorInstance = ref<any>(null)
const retrying = ref(false)
const retryCount = ref(0)
const autoRetryCountdown = ref(0)
const autoRetryTimer = ref<number | null>(null)
const errorContainer = ref<HTMLElement>()

// Computed properties
const isDevelopment = computed(() => import.meta.env.DEV)

const errorDetails = computed(() => {
  if (!error.value) return null

  return `
Error: ${error.value.message}
Stack: ${error.value.stack}
Component: ${errorInstance.value?.$?.type?.name || 'Unknown'}
Info: ${errorInfo.value}
Timestamp: ${new Date().toISOString()}
UserAgent: ${navigator.userAgent}
URL: ${window.location.href}
  `.trim()
})

const retryButtonText = computed(() => {
  if (retryCount.value >= props.maxRetries) {
    return 'Max Retries Reached'
  }
  if (retrying.value) {
    return 'Retrying...'
  }
  return retryCount.value > 0 ? `Retry (${retryCount.value}/${props.maxRetries})` : 'Try Again'
})

/**
 * Handle component error (Vue error boundary)
 */
const handleError = (err: Error, instance: any, info: string) => {
  // Prevent infinite loops
  if (hasError.value) return

  hasError.value = true
  error.value = err
  errorInfo.value = info
  errorInstance.value = instance

  // Log error
  logError(err, {
    component: instance?.$?.type?.name || 'Unknown',
    info,
    stack: err.stack,
    url: window.location.href,
    timestamp: new Date().toISOString()
  })

  // Custom error handler
  props.onError?.(err, instance, info)

  // Emit error event
  emit('error', err, instance, info)

  // Focus error container for accessibility
  nextTick(() => {
    errorContainer.value?.focus()
  })

  // Start auto-retry countdown if enabled and should retry
  if (props.showAutoRetry && shouldRetry(err)) {
    startAutoRetryCountdown()
  }
}

/**
 * Handle manual retry
 */
const handleRetry = async () => {
  if (retrying.value || retryCount.value >= props.maxRetries) return

  retrying.value = true
  retryCount.value++

  try {
    // Stop auto-retry if running
    stopAutoRetry()

    // Custom retry handler or default reload
    if (props.onRetry) {
      await props.onRetry(retryCount.value)
    } else {
      // Default: reload the page
      window.location.reload()
    }

    // Emit retry event
    emit('retry', retryCount.value)

  } catch (retryError) {
    console.error('Retry failed:', retryError)
    // Continue showing error UI
  } finally {
    retrying.value = false
  }
}

/**
 * Handle page reload
 */
const handleReload = () => {
  window.location.reload()
}

/**
 * Handle error reporting (development only)
 */
const handleReportError = () => {
  const reportData = {
    error: error.value?.message,
    stack: error.value?.stack,
    component: errorInstance.value?.$?.type?.name,
    info: errorInfo.value,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
  }

  // Copy to clipboard
  navigator.clipboard.writeText(JSON.stringify(reportData, null, 2))
    .then(() => {
      alert('Error details copied to clipboard')
    })
    .catch(() => {
      console.log('Error report:', reportData)
      alert('Error details logged to console')
    })
}

/**
 * Start auto-retry countdown
 */
const startAutoRetryCountdown = () => {
  if (!props.showAutoRetry) return

  autoRetryCountdown.value = props.autoRetryDelay

  autoRetryTimer.value = window.setInterval(() => {
    autoRetryCountdown.value--

    if (autoRetryCountdown.value <= 0) {
      stopAutoRetry()
      // Auto-retry
      handleRetry()
    }
  }, 1000)
}

/**
 * Stop auto-retry countdown
 */
const stopAutoRetry = () => {
  if (autoRetryTimer.value) {
    clearInterval(autoRetryTimer.value)
    autoRetryTimer.value = null
  }
  autoRetryCountdown.value = 0
}

/**
 * Reset error state
 */
const resetError = () => {
  hasError.value = false
  error.value = null
  errorInfo.value = ''
  errorInstance.value = null
  retryCount.value = 0
  stopAutoRetry()
}

/**
 * Vue 3 Error Boundary API
 * Register the error capturing hook
 */
onErrorCaptured((err: Error, instance: any, info: string) => {
  handleError(err, instance, info)
  return false // Don't propagate the error
})

// Watch for error changes
watch(hasError, (newHasError) => {
  if (!newHasError) {
    emit('recovered')
  }
})

// Cleanup on unmount
onUnmounted(() => {
  stopAutoRetry()
})

// Expose methods for parent components
defineExpose({
  resetError,
  hasError,
  error: error.value,
  retryCount
})
</script>

<style scoped>
.error-boundary:focus {
  outline: 2px solid var(--color-primary-600);
  outline-offset: 2px;
}

/* Ensure error UI is above other content */
.error-boundary {
  z-index: 9999;
  position: relative;
}
</style>
