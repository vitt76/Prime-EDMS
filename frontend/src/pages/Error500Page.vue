<template>
  <div class="error-page error-page--500">
    <div class="error-page__content">
      <div class="error-page__icon">
        <svg
          class="w-24 h-24 text-error"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>

      <h1 class="error-page__code">500</h1>
      <h2 class="error-page__title">Server Error</h2>
      <p class="error-page__message">
        Something went wrong on our end. We're working to fix the issue.
      </p>

      <div v-if="errorId" class="error-page__error-id">
        <p class="error-page__error-id-label">Error ID:</p>
        <code class="error-page__error-id-value">{{ errorId }}</code>
      </div>

      <div v-if="isDevelopment && stackTrace" class="error-page__stack-trace">
        <details>
          <summary class="error-page__stack-trace-summary">Stack Trace</summary>
          <pre class="error-page__stack-trace-content">{{ stackTrace }}</pre>
        </details>
      </div>

      <div class="error-page__actions">
        <Button variant="primary" @click="handleRetry" :loading="isRetrying">
          Retry
        </Button>
        <Button variant="secondary" @click="handleGoHome">
          Go Home
        </Button>
        <Button variant="ghost" @click="handleReportIssue">
          Report Issue
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Button from '@/components/Common/Button.vue'

const router = useRouter()
const route = useRoute()

const isRetrying = ref(false)
const errorId = ref<string | null>(
  (route.query.error_id as string) || null
)
const stackTrace = ref<string | null>(
  (route.query.stack_trace as string) || null
)

const isDevelopment = computed(() => {
  return import.meta.env.DEV || import.meta.env.MODE === 'development'
})

const handleRetry = async (): Promise<void> => {
  isRetrying.value = true
  try {
    // Try to go back or reload
    if (window.history.length > 1) {
      router.go(-1)
    } else {
      window.location.reload()
    }
  } finally {
    isRetrying.value = false
  }
}

const handleGoHome = (): void => {
  router.push('/')
}

const handleReportIssue = (): void => {
  // Open email client or support form
  const subject = encodeURIComponent('Server Error Report')
  const body = encodeURIComponent(
    `Error ID: ${errorId.value || 'N/A'}\n\nPlease describe what you were doing when the error occurred:`
  )
  window.location.href = `mailto:support@example.com?subject=${subject}&body=${body}`
}
</script>

<style scoped lang="css">
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--color-bg-1, #f9fafb);
}

.error-page__content {
  text-align: center;
  max-width: 600px;
}

.error-page__icon {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.error-page__code {
  font-size: 72px;
  font-weight: 700;
  color: var(--color-text, #111827);
  margin-bottom: 8px;
  line-height: 1;
}

.error-page__title {
  font-size: var(--font-size-2xl, 24px);
  font-weight: 600;
  color: var(--color-text, #111827);
  margin-bottom: 16px;
}

.error-page__message {
  font-size: var(--font-size-base, 14px);
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 32px;
  line-height: 1.5;
}

.error-page__error-id {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
  padding: 12px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 6px);
}

.error-page__error-id-label {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

.error-page__error-id-value {
  font-size: var(--font-size-sm, 12px);
  font-family: monospace;
  color: var(--color-text, #111827);
  background: var(--color-surface, #ffffff);
  padding: 4px 8px;
  border-radius: var(--radius-sm, 4px);
}

.error-page__stack-trace {
  margin-bottom: 24px;
  text-align: left;
}

.error-page__stack-trace-summary {
  cursor: pointer;
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  padding: 8px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 6px);
}

.error-page__stack-trace-content {
  margin-top: 8px;
  padding: 12px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-xs, 11px);
  font-family: monospace;
  color: var(--color-text, #111827);
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

.error-page__actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 640px) {
  .error-page__code {
    font-size: 48px;
  }

  .error-page__actions {
    flex-direction: column;
  }
}
</style>



