<template>
  <form class="space-y-5" @submit.prevent="onSubmit" novalidate>
    <!-- Name & Email Row -->
    <div class="grid gap-4 sm:grid-cols-2">
      <FormsFormInput 
        v-model="form.name" 
        name="name" 
        label="Имя" 
        :error="errors.name"
        :required="true"
        placeholder="Ваше имя"
        autocomplete="name"
        :leading-icon="UserIcon"
        :validate-on-input="true"
        @validate="validateForm"
      />
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
    </div>

    <!-- Company -->
    <FormsFormInput 
      v-model="form.company" 
      name="company" 
      label="Компания"
      placeholder="Название компании"
      autocomplete="organization"
      :leading-icon="BuildingOfficeIcon"
      :validate-on-input="true"
      @validate="validateForm"
    />

    <!-- Subject -->
    <div class="space-y-1.5">
      <label for="subject" class="text-sm font-medium text-neutral-700">
        Тема обращения
      </label>
      <select
        id="subject"
        v-model="form.subject"
        class="w-full rounded-lg border border-neutral-200 px-3 py-2.5 text-sm transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
      >
        <option value="general">Общий вопрос</option>
        <option value="sales">Продажи</option>
        <option value="support">Техническая поддержка</option>
        <option value="partnership">Партнерство</option>
        <option value="other">Другое</option>
      </select>
    </div>

    <!-- Message -->
    <div class="space-y-1.5">
      <label for="message" class="flex items-center gap-1 text-sm font-medium text-neutral-700">
        Сообщение
        <span class="text-error">*</span>
      </label>
      <textarea
        id="message"
        v-model="form.message"
        rows="5"
        required
        :aria-invalid="!!errors.message"
        placeholder="Опишите ваш вопрос или предложение..."
        class="w-full rounded-lg border px-3 py-2.5 text-sm transition focus:outline-none focus:ring-2"
        :class="errors.message 
          ? 'border-error focus:border-error focus:ring-error/20' 
          : 'border-neutral-200 focus:border-primary-500 focus:ring-primary-500/20'"
        @input="validateForm"
      ></textarea>
      <p 
        v-if="errors.message" 
        class="text-xs text-error"
        role="alert"
      >
        {{ errors.message }}
      </p>
    </div>

    <!-- Privacy Consent -->
    <label class="flex items-start gap-3">
      <input 
        v-model="form.consent" 
        type="checkbox"
        required
        class="mt-0.5 h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
      />
      <span class="text-sm text-neutral-600">
        Я согласен на обработку персональных данных в соответствии с 
        <NuxtLink to="/privacy" class="text-primary-600 hover:underline" target="_blank">политикой конфиденциальности</NuxtLink>
      </span>
    </label>

    <!-- Status Alert -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
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
      :disabled="loading"
    >
      <span v-if="loading" class="flex items-center gap-2">
        <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        Отправка...
      </span>
      <span v-else class="flex items-center gap-2">
        <PaperAirplaneIcon class="h-4 w-4" />
        Отправить сообщение
      </span>
    </CommonButton>
  </form>
</template>

<script setup lang="ts">
import { 
  UserIcon, 
  EnvelopeIcon, 
  BuildingOfficeIcon,
  PaperAirplaneIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import { contactSchema } from '~/utils/validators'

const { submitLead } = useApi()
const status = ref<'success' | 'error' | ''>('')
const message = ref('')
const loading = ref(false)

const form = reactive({
  name: '',
  email: '',
  company: '',
  subject: 'general',
  message: '',
  consent: false,
  source: 'contact'
})

const { errors, validate } = useForm(contactSchema)

const validateForm = () => {
  validate({ name: form.name, email: form.email, message: form.message })
}

const onSubmit = async () => {
  status.value = ''
  message.value = ''

  if (!form.consent) {
    status.value = 'error'
    message.value = 'Необходимо согласие на обработку данных.'
    return
  }

  const payload = validate({ name: form.name, email: form.email, message: form.message })
  
  if (!payload) {
    status.value = 'error'
    message.value = 'Пожалуйста, исправьте ошибки в форме.'
    return
  }

  loading.value = true

  try {
    const response = await submitLead({
      ...form,
      metadata: {
        subject: form.subject
      }
    })
    status.value = 'success'
    message.value = response.message || 'Спасибо! Мы получили ваше сообщение и свяжемся с вами в ближайшее время.'
    
    // Clear form on success
    Object.assign(form, {
      name: '',
      email: '',
      company: '',
      subject: 'general',
      message: '',
      consent: false
    })
  } catch (error: any) {
    status.value = 'error'
    message.value = error?.data?.message || 'Ошибка отправки формы. Попробуйте позже.'
  } finally {
    loading.value = false
  }
}
</script>
