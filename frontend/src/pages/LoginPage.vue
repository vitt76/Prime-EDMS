<template>
  <div class="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-50 px-4">
    <Card class="w-full max-w-md">
      <h1 class="text-3xl font-semibold mb-6 text-center">Login</h1>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <Input
          v-model="email"
          type="email"
          label="Email"
          placeholder="Enter your email"
          required
        />
        <Input
          v-model="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          required
        />
        <Button type="submit" variant="primary" class="w-full" :loading="loading">
          Sign In
        </Button>
      </form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import Card from '@/components/Common/Card.vue'
import Input from '@/components/Common/Input.vue'
import Button from '@/components/Common/Button.vue'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(email.value, password.value)

    // Redirect to return URL or dashboard
    const returnTo = router.currentRoute.value.query.returnTo as string || '/'
    router.push(returnTo)
  } catch (error) {
    console.error('Login failed:', error)
    // TODO: Show error message to user
  } finally {
    loading.value = false
  }
}
</script>


