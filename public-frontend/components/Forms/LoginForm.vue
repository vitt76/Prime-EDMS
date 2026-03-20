<template>
  <form class="space-y-5" @submit.prevent="onSubmit" novalidate>
    <!-- Email -->
    <FormsFormInput 
      v-model="form.email" 
      name="email" 
      label="Email" 
      type="email"
      :error="errors.email"
      :required="true"
      placeholder="you@company.com"
      autocomplete="email"
      :leading-icon="EnvelopeIcon"
      :validate-on-input="true"
      @validate="validateForm"
    />

    <!-- Password -->
    <FormsFormInput 
      v-model="form.password" 
      name="password" 
      label="Пароль" 
      type="password"
      :error="errors.password"
      :required="true"
      placeholder="Ваш пароль"
      autocomplete="current-password"
      :leading-icon="LockClosedIcon"
      :validate-on-input="true"
      @validate="validateForm"
    />

    <!-- Remember & Forgot -->
    <div class="flex items-center justify-between">
      <label class="flex items-center gap-2">
        <input 
          v-model="form.remember" 
          type="checkbox"
          class="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
        />
        <span class="text-sm text-neutral-600 dark:text-neutral-400">{{ $t('forms.rememberMe') }}</span>
      </label>
      <NuxtLink to="/auth/forgot-password" class="text-sm font-medium text-primary-600 hover:text-primary-700 hover:underline dark:text-primary-400">
        {{ $t('forms.forgotPassword') }}
      </NuxtLink>
    </div>

    <!-- Status Alert -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <CommonAlert v-if="status" :variant="status === 'success' ? 'success' : 'error'">
        {{ message }}
      </CommonAlert>
    </Transition>

    <!-- Submit Button -->
    <CommonButton 
      type="submit" 
      variant="primary" 
      class="w-full"
      :disabled="loading"
    >
      <span v-if="loading" class="flex items-center gap-2">
        <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        {{ $t('auth.loggingIn') }}
      </span>
      <span v-else>{{ $t('auth.login') }}</span>
    </CommonButton>

    <!-- Register Link -->
    <p class="text-center text-sm text-neutral-600 dark:text-neutral-400">
      {{ $t('auth.noAccount') }}
      <NuxtLink to="/auth/register" class="font-medium text-primary-600 hover:text-primary-700 hover:underline dark:text-primary-400">
        {{ $t('auth.register') }}
      </NuxtLink>
    </p>
  </form>
</template>

<script setup lang="ts">
import { EnvelopeIcon, LockClosedIcon } from '@heroicons/vue/24/outline'
import { loginSchema } from '~/utils/validators'

const form = reactive({
  email: '',
  password: '',
  remember: false
})

const { errors, validate } = useForm(loginSchema)
const status = ref<'success' | 'error' | ''>('')
const message = ref('')
const loading = ref(false)

const validateForm = () => {
  validate({ email: form.email, password: form.password })
}

const onSubmit = async () => {
  status.value = ''
  message.value = ''

  const payload = validate({ email: form.email, password: form.password })
  
  if (!payload) {
    status.value = 'error'
    message.value = 'Пожалуйста, заполните все поля.'
    return
  }

  loading.value = true
  
  try {
    const config = useRuntimeConfig()
    const defaultAppUrl = config.public.appUrl || 'http://localhost:5173'
    
    // Attempt login via API (POST, credentials in body, not URL)
    const loginResponse = await $fetch<{ redirect_url?: string }>('/api/v4/public/auth/login/', {
      method: 'POST',
      body: {
        email: form.email,
        password: form.password,
        remember: form.remember
      }
    })
    
    status.value = 'success'
    message.value = 'Вход выполнен! Перенаправляем...'
    
    // Redirect to main app after successful login
    setTimeout(() => {
      window.location.href = loginResponse?.redirect_url || defaultAppUrl
    }, 1000)
  } catch (error: any) {
    status.value = 'error'
    
    if (error?.statusCode === 401 || error?.status === 401) {
      message.value = 'Неверный email или пароль.'
    } else if (error?.data?.message) {
      message.value = error.data.message
    } else {
      // Fallback: redirect to Django login page
      const config = useRuntimeConfig()
      const apiBase = (config.apiBase as string) || 'http://localhost:8080'
      window.location.href = `${apiBase}/authentication/login/`
    }
  } finally {
    loading.value = false
  }
}
</script>
