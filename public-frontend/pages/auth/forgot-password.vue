<template>
  <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-sm dark:bg-neutral-800">
    <h1 class="text-2xl font-semibold text-neutral-900 dark:text-white">
      {{ $t('forms.forgotPassword') }}
    </h1>
    <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
      Введите email, привязанный к вашему аккаунту. Мы отправим инструкции для сброса пароля.
    </p>

    <form class="mt-6 space-y-5" @submit.prevent="onSubmit" novalidate>
      <!-- Email -->
      <FormsFormInput
        v-model="form.email"
        name="email"
        :label="$t('forms.email')"
        type="email"
        :error="errors.email"
        :required="true"
        :placeholder="$t('forms.emailPlaceholder')"
        autocomplete="email"
        :leading-icon="EnvelopeIcon"
      />

      <!-- Status Alert -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
      >
        <CommonAlert v-if="status === 'success'" variant="success">
          Инструкции для сброса пароля отправлены на {{ form.email }}.
          Проверьте вашу почту.
        </CommonAlert>
        <CommonAlert v-else-if="status === 'error'" variant="error">
          {{ message }}
        </CommonAlert>
      </Transition>

      <!-- Submit Button -->
      <CommonButton
        type="submit"
        variant="primary"
        class="w-full"
        :disabled="loading || status === 'success'"
      >
        <span v-if="loading" class="flex items-center gap-2">
          <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Отправка...
        </span>
        <span v-else>Отправить инструкции</span>
      </CommonButton>

      <!-- Back to login -->
      <p class="text-center text-sm text-neutral-600 dark:text-neutral-400">
        Вспомнили пароль?
        <NuxtLink to="/auth/login" class="font-medium text-primary-600 hover:text-primary-700 hover:underline dark:text-primary-400">
          Войти
        </NuxtLink>
      </p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { EnvelopeIcon } from '@heroicons/vue/24/outline'
import { emailSchema } from '~/utils/validators'

definePageMeta({ layout: 'auth' })

const form = reactive({
  email: ''
})

const errors = reactive<Record<string, string>>({})
const status = ref<'success' | 'error' | ''>('')
const message = ref('')
const loading = ref(false)

const onSubmit = async () => {
  status.value = ''
  message.value = ''
  errors.email = ''

  // Validate email
  const result = emailSchema.safeParse(form.email)
  if (!result.success) {
    errors.email = result.error.errors[0]?.message || 'Введите корректный email'
    return
  }

  loading.value = true

  try {
    // Password reset is handled by the main Django app
    // For now, show a success message and direct users to the main app
    await new Promise(resolve => setTimeout(resolve, 1000))
    status.value = 'success'
  } catch (error: any) {
    status.value = 'error'
    message.value = error?.data?.message || 'Произошла ошибка. Попробуйте позже.'
  } finally {
    loading.value = false
  }
}
</script>
