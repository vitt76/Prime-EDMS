<template>
  <div class="error-page error-page--401">
    <div class="error-page__content">
      <div class="error-page__icon">
        <svg
          class="w-24 h-24 text-warning"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
          />
        </svg>
      </div>

      <h1 class="error-page__code">401</h1>
      <h2 class="error-page__title">Unauthorized</h2>
      <p class="error-page__message">
        Your session has expired. Please log in again to continue.
      </p>

      <div v-if="autoRedirectCountdown > 0" class="error-page__countdown">
        <p class="error-page__countdown-text">
          Redirecting to login in {{ autoRedirectCountdown }} seconds...
        </p>
      </div>

      <div class="error-page__actions">
        <Button variant="primary" @click="handleGoToLogin">
          Go to Login
        </Button>
        <Button variant="secondary" @click="handleGoHome">
          Go Home
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import Button from '@/components/Common/Button.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const autoRedirectCountdown = ref(5)
const countdownInterval = ref<number | null>(null)

const returnTo = computed(() => {
  return (route.query.returnTo as string) || '/'
})

const handleGoToLogin = (): void => {
  // Clear auth state
  authStore.logout()
  router.push({
    name: 'login',
    query: { returnTo: returnTo.value }
  })
}

const handleGoHome = (): void => {
  router.push('/')
}

onMounted(() => {
  // Auto-redirect after 5 seconds
  countdownInterval.value = window.setInterval(() => {
    autoRedirectCountdown.value--
    if (autoRedirectCountdown.value <= 0) {
      if (countdownInterval.value) {
        clearInterval(countdownInterval.value)
      }
      handleGoToLogin()
    }
  }, 1000)

  // Clear auth state
  authStore.logout()
})

onUnmounted(() => {
  if (countdownInterval.value) {
    clearInterval(countdownInterval.value)
  }
})
</script>

<script lang="ts">
import { computed } from 'vue'

// Export computed for use in template
export { computed }
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

.error-page__countdown {
  margin-bottom: 24px;
}

.error-page__countdown-text {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
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



