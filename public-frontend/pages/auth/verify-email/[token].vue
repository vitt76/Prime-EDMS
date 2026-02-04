<template>
  <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-sm">
    <h1 class="text-2xl font-semibold">Email verification</h1>
    <p class="mt-2 text-sm text-neutral-600">{{ statusMessage }}</p>
    <CommonAlert v-if="status === 'error'" variant="error" class="mt-4">
      {{ statusMessage }}
    </CommonAlert>
    <CommonAlert v-if="status === 'success'" variant="success" class="mt-4">
      {{ statusMessage }}
    </CommonAlert>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const route = useRoute()
const { verifyEmail } = useAuth()
const status = ref<'pending' | 'success' | 'error'>('pending')
const statusMessage = ref('Проверяем токен...')
const redirectUrl = ref<string | null>(null)

try {
  const response = await verifyEmail({ token: route.params.token as string })
  status.value = 'success'
  statusMessage.value = response.message || 'Email подтвержден.'
  if (response.redirect_url) {
    redirectUrl.value = response.redirect_url
  }
} catch (error: any) {
  status.value = 'error'
  statusMessage.value = error?.data?.message || 'Ошибка подтверждения email.'
}

onMounted(() => {
  if (redirectUrl.value) {
    window.setTimeout(() => {
      window.location.href = redirectUrl.value as string
    }, 1500)
  }
})
</script>
