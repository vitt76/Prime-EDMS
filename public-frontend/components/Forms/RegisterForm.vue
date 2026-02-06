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
    <FormsPasswordInput 
      v-model="form.password" 
      name="password" 
      label="Пароль" 
      type="password" 
      :error="errors.password"
      :required="true"
      placeholder="Минимум 8 символов"
      autocomplete="new-password"
      :leading-icon="LockClosedIcon"
      hint="Минимум 8 символов, включая цифру и спецсимвол"
      :show-strength-meter="true"
      :validate-on-input="true"
      @validate="validateForm"
    />

    <!-- Organization -->
    <FormsFormInput
      v-model="form.organization_name"
      name="organization_name"
      label="Организация"
      :error="errors.organization_name"
      :required="true"
      placeholder="Название вашей компании"
      autocomplete="organization"
      :leading-icon="BuildingOfficeIcon"
      :validate-on-input="true"
      @validate="validateForm"
    />

    <!-- Name Row -->
    <div class="grid gap-4 sm:grid-cols-2">
      <FormsFormInput 
        v-model="form.first_name" 
        name="first_name" 
        label="Имя" 
        :error="errors.first_name"
        placeholder="Иван"
        autocomplete="given-name"
        :leading-icon="UserIcon"
        :validate-on-input="true"
        @validate="validateForm"
      />
      <FormsFormInput 
        v-model="form.last_name" 
        name="last_name" 
        label="Фамилия" 
        :error="errors.last_name"
        placeholder="Иванов"
        autocomplete="family-name"
        :leading-icon="UserIcon"
        :validate-on-input="true"
        @validate="validateForm"
      />
    </div>

    <!-- Terms Checkbox -->
    <div class="space-y-2">
      <label class="flex items-start gap-3">
        <input 
          v-model="form.agree_terms" 
          type="checkbox"
          class="mt-0.5 h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
          :aria-invalid="!!errors.agree_terms"
          :aria-describedby="errors.agree_terms ? 'terms-error' : undefined"
        />
        <span class="text-sm text-neutral-600">
          Я соглашаюсь с 
          <NuxtLink to="/terms" class="text-primary-600 hover:underline" target="_blank">условиями использования</NuxtLink>
          и
          <NuxtLink to="/privacy" class="text-primary-600 hover:underline" target="_blank">политикой конфиденциальности</NuxtLink>
        </span>
      </label>
      <p 
        v-if="errors.agree_terms" 
        id="terms-error" 
        class="text-xs text-error"
        role="alert"
      >
        {{ errors.agree_terms }}
      </p>
    </div>

    <!-- Status Alert -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <CommonAlert v-if="status" :variant="status === 'success' ? 'success' : 'error'">
        <template #icon>
          <CheckCircleIcon v-if="status === 'success'" class="h-5 w-5" />
          <ExclamationCircleIcon v-else class="h-5 w-5" />
        </template>
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
        Создание аккаунта...
      </span>
      <span v-else>Создать аккаунт</span>
    </CommonButton>

    <!-- Login Link -->
    <p class="text-center text-sm text-neutral-600">
      Уже есть аккаунт? 
      <NuxtLink to="/auth/login" class="font-medium text-primary-600 hover:text-primary-700 hover:underline">
        Войти
      </NuxtLink>
    </p>
  </form>
</template>

<script setup lang="ts">
import { 
  EnvelopeIcon, 
  LockClosedIcon, 
  BuildingOfficeIcon,
  UserIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import { registerSchema } from '~/utils/validators'

const { register } = useAuth()
const authStore = useAuthStore()
const { locale } = useI18n()

const form = reactive({
  email: '',
  password: '',
  organization_name: '',
  first_name: '',
  last_name: '',
  agree_terms: false
})

const { errors, validate } = useForm(registerSchema)
const status = ref<'success' | 'error' | ''>('')
const message = ref('')
const loading = ref(false)

const validateForm = () => {
  validate({ ...form })
}

const onSubmit = async () => {
  status.value = ''
  message.value = ''

  const payload = validate({
    ...form,
    lang: locale.value
  })
  
  if (!payload) {
    status.value = 'error'
    message.value = 'Пожалуйста, исправьте ошибки в форме.'
    return
  }

  loading.value = true
  
  try {
    const response = await register(payload)
    authStore.markRegistered(response.email)
    status.value = 'success'
    message.value = response.message || 'Аккаунт создан! Проверьте email для подтверждения.'
    
    // Clear form on success
    Object.assign(form, {
      email: '',
      password: '',
      organization_name: '',
      first_name: '',
      last_name: '',
      agree_terms: false
    })
  } catch (error: any) {
    status.value = 'error'
    message.value = error?.data?.message || error?.data?.email?.[0] || 'Ошибка регистрации. Попробуйте позже.'
  } finally {
    loading.value = false
  }
}
</script>
