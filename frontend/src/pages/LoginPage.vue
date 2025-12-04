<template>
  <div class="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-50 px-4">
    <Card class="w-full max-w-md">
      <h1 class="text-3xl font-semibold mb-6 text-center">Вход в систему</h1>
      
      <!-- Error message -->
      <div v-if="errorMessage" class="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-md text-sm">
        {{ errorMessage }}
      </div>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <Input
          v-model="username"
          type="text"
          label="Имя пользователя"
          placeholder="Введите имя пользователя"
          required
          autocomplete="username"
        />
        <Input
          v-model="password"
          type="password"
          label="Пароль"
          placeholder="Введите пароль"
          required
          autocomplete="current-password"
        />
        <Button type="submit" variant="primary" class="w-full" :loading="loading">
          Войти
        </Button>
      </form>
      
      <!-- Dev hint -->
      <div v-if="isDev" class="mt-4 p-3 bg-blue-50 border border-blue-200 text-blue-700 rounded-md text-xs">
        <strong>Dev mode:</strong> Backend на localhost:8000<br>
        По умолчанию: admin / (см. консоль Django при первом запуске)
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import Card from '@/components/Common/Card.vue'
import Input from '@/components/Common/Input.vue'
import Button from '@/components/Common/Button.vue'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const isDev = computed(() => import.meta.env.DEV)

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''
  
  try {
    await authStore.login(username.value, password.value)

    // Redirect to return URL or dashboard
    const returnTo = router.currentRoute.value.query.returnTo as string || '/'
    router.push(returnTo)
  } catch (error: any) {
    console.error('Login failed:', error)
    errorMessage.value = error.message || 'Ошибка входа. Проверьте учетные данные.'
  } finally {
    loading.value = false
  }
}
</script>


