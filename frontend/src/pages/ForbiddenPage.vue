<template>
  <div class="forbidden-page min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-50">
    <div class="text-center max-w-md px-4">
      <div class="mb-6">
        <svg
          class="w-24 h-24 mx-auto text-error"
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
      <h1 class="text-4xl font-bold text-neutral-900 dark:text-neutral-900 mb-4">
        403
      </h1>
      <h2 class="text-2xl font-semibold text-neutral-800 dark:text-neutral-800 mb-4">
        Access Forbidden
      </h2>
      <p class="text-lg text-neutral-600 dark:text-neutral-600 mb-8">
        You don't have permission to access this page. Please contact your administrator if you believe this is an error.
      </p>
      <div v-if="requiredPermission" class="mb-6">
        <p class="text-sm text-neutral-500 dark:text-neutral-500">
          Required permission: <code class="font-mono">{{ requiredPermission }}</code>
        </p>
      </div>

      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <Button
          variant="primary"
          @click="handleRequestAccess"
          class="min-h-[44px]"
        >
          Request Access
        </Button>
        <Button
          variant="secondary"
          @click="handleGoHome"
          class="min-h-[44px]"
        >
          Go Home
        </Button>
        <Button
          variant="outline"
          @click="handleContactAdmin"
          class="min-h-[44px]"
        >
          Contact Admin
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Button from '@/components/Common/Button.vue'

const router = useRouter()
const route = useRoute()

const requiredPermission = computed(() => {
  return (route.query.requiredPermission as string) || null
})

function handleGoHome(): void {
  router.push('/')
}

function handleGoBack(): void {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

function handleRequestAccess(): void {
  // TODO: Open request access form or navigate to request page
  // For now, redirect to contact admin
  handleContactAdmin()
}

function handleContactAdmin(): void {
  // Open email client or support form
  const subject = encodeURIComponent('Access Request')
  const body = encodeURIComponent(
    `I need access to: ${route.query.returnTo || route.path}\n\nRequired permission: ${requiredPermission.value || 'N/A'}\n\nPlease describe why you need access:`
  )
  window.location.href = `mailto:admin@example.com?subject=${subject}&body=${body}`
}
</script>

<style scoped>
.forbidden-page {
  padding: 2rem 1rem;
}

@media (prefers-reduced-motion: reduce) {
  .forbidden-page {
    animation: none;
  }
}
</style>

