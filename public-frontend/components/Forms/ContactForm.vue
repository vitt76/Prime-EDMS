<template>
  <!-- Success State -->
  <div v-if="status === 'success'" class="rounded-2xl border border-green-200 bg-green-50 p-8 text-center dark:border-green-800 dark:bg-green-950/30">
    <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/50">
      <CheckCircleIcon class="h-8 w-8 text-green-600 dark:text-green-400" />
    </div>
    <h3 class="text-xl font-semibold text-green-800 dark:text-green-200">
      {{ $t('contact.form.successTitle') }}
    </h3>
    <p class="mt-2 text-sm text-green-700 dark:text-green-300">
      {{ $t('contact.form.successDesc') }}
    </p>
    <button
      type="button"
      class="mt-6 inline-flex items-center gap-2 rounded-lg border border-green-300 px-4 py-2 text-sm font-medium text-green-700 transition hover:bg-green-100 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-900/30"
      @click="resetForm"
    >
      <ArrowPathIcon class="h-4 w-4" />
      {{ $t('contact.form.sendAnother') }}
    </button>
  </div>

  <!-- Form -->
  <form v-else class="space-y-5" @submit.prevent="onSubmit" novalidate>
    <!-- Name & Email Row -->
    <div class="grid gap-4 sm:grid-cols-2">
      <FormsFormInput
        v-model="form.name"
        name="name"
        :label="$t('contact.form.name')"
        :error="errors.name"
        :required="true"
        :placeholder="$t('contact.form.namePlaceholder')"
        autocomplete="name"
        :leading-icon="UserIcon"
        :validate-on-input="true"
        @validate="validateForm"
      />
      <FormsFormInput
        v-model="form.email"
        name="email"
        :label="$t('contact.form.email')"
        type="email"
        :error="errors.email"
        :required="true"
        :placeholder="$t('contact.form.emailPlaceholder')"
        autocomplete="email"
        :leading-icon="EnvelopeIcon"
        :validate-on-input="true"
        @validate="validateForm"
      />
    </div>

    <!-- Phone & Company Row -->
    <div class="grid gap-4 sm:grid-cols-2">
      <FormsFormInput
        v-model="form.phone"
        name="phone"
        :label="$t('contact.form.phone')"
        type="tel"
        :error="errors.phone"
        :placeholder="$t('contact.form.phonePlaceholder')"
        autocomplete="tel"
        :leading-icon="PhoneIcon"
        :validate-on-input="true"
        @validate="validateForm"
      />
      <FormsFormInput
        v-model="form.company"
        name="company"
        :label="$t('contact.form.company')"
        :placeholder="$t('contact.form.companyPlaceholder')"
        autocomplete="organization"
        :leading-icon="BuildingOfficeIcon"
      />
    </div>

    <!-- Subject -->
    <div class="space-y-1.5">
      <label for="contact-subject" class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
        {{ $t('contact.form.subject') }}
      </label>
      <select
        id="contact-subject"
        v-model="form.subject"
        class="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 dark:border-neutral-700 dark:bg-neutral-800 dark:text-neutral-100"
      >
        <option value="general">{{ $t('contact.form.subjectGeneral') }}</option>
        <option value="sales">{{ $t('contact.form.subjectSales') }}</option>
        <option value="support">{{ $t('contact.form.subjectSupport') }}</option>
        <option value="partnership">{{ $t('contact.form.subjectPartnership') }}</option>
        <option value="other">{{ $t('contact.form.subjectOther') }}</option>
      </select>
    </div>

    <!-- Message -->
    <div class="space-y-1.5">
      <label for="contact-message" class="flex items-center gap-1 text-sm font-medium text-neutral-700 dark:text-neutral-300">
        {{ $t('contact.form.message') }}
        <span class="text-error">*</span>
      </label>
      <textarea
        id="contact-message"
        v-model="form.message"
        rows="5"
        required
        maxlength="2000"
        :aria-invalid="!!errors.message"
        :placeholder="$t('contact.form.messagePlaceholder')"
        class="w-full rounded-lg border px-3 py-2.5 text-sm transition focus:outline-none focus:ring-2 dark:bg-neutral-800 dark:text-neutral-100 dark:placeholder-neutral-500"
        :class="errors.message
          ? 'border-error focus:border-error focus:ring-error/20'
          : 'border-neutral-200 focus:border-primary-500 focus:ring-primary-500/20 dark:border-neutral-700'"
        @input="validateForm"
      ></textarea>
      <div class="flex items-center justify-between">
        <p
          v-if="errors.message"
          class="text-xs text-error"
          role="alert"
        >
          {{ errors.message }}
        </p>
        <span v-else />
        <p class="text-xs text-neutral-400 dark:text-neutral-500">
          {{ charsRemaining }} {{ $t('contact.form.charsRemaining') }}
        </p>
      </div>
    </div>

    <!-- Privacy Consent -->
    <label class="flex items-start gap-3 cursor-pointer group">
      <input
        v-model="form.consent"
        type="checkbox"
        required
        class="mt-0.5 h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500 dark:border-neutral-600 dark:bg-neutral-800"
      />
      <span class="text-sm text-neutral-600 dark:text-neutral-400 group-hover:text-neutral-800 dark:group-hover:text-neutral-200 transition">
        {{ $t('contact.form.consent') }}
        <NuxtLink to="/privacy" class="text-primary-600 hover:underline dark:text-primary-400" target="_blank">
          {{ $t('contact.form.consentLink') }}
        </NuxtLink>
      </span>
    </label>

    <!-- Error Alert -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
    >
      <div
        v-if="status === 'error'"
        class="flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/30 dark:text-red-300"
        role="alert"
      >
        <ExclamationCircleIcon class="h-5 w-5 flex-shrink-0" />
        {{ message }}
      </div>
    </Transition>

    <!-- Submit Button -->
    <button
      type="submit"
      :disabled="loading"
      class="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
    >
      <template v-if="loading">
        <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        {{ $t('contact.form.submitting') }}
      </template>
      <template v-else>
        <PaperAirplaneIcon class="h-4 w-4" />
        {{ $t('contact.form.submit') }}
      </template>
    </button>
  </form>
</template>

<script setup lang="ts">
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  BuildingOfficeIcon,
  PaperAirplaneIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'
import { contactSchema } from '~/utils/validators'

const { t } = useI18n()
const { submitLead } = useApi()
const status = ref<'success' | 'error' | ''>('')
const message = ref('')
const loading = ref(false)

const form = reactive({
  name: '',
  email: '',
  phone: '',
  company: '',
  subject: 'general',
  message: '',
  consent: false,
  source: 'contact'
})

const { errors, validate } = useForm(contactSchema)

const charsRemaining = computed(() => 2000 - (form.message?.length || 0))

const validateForm = () => {
  validate({ name: form.name, email: form.email, phone: form.phone, message: form.message })
}

const resetForm = () => {
  status.value = ''
  message.value = ''
  Object.assign(form, {
    name: '',
    email: '',
    phone: '',
    company: '',
    subject: 'general',
    message: '',
    consent: false
  })
}

const onSubmit = async () => {
  status.value = ''
  message.value = ''

  if (!form.consent) {
    status.value = 'error'
    message.value = t('contact.form.errorConsent')
    return
  }

  const payload = validate({ name: form.name, email: form.email, phone: form.phone, message: form.message })

  if (!payload) {
    status.value = 'error'
    message.value = t('contact.form.errorValidation')
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
  } catch (error: any) {
    status.value = 'error'
    message.value = error?.data?.message || t('contact.form.errorServer')
  } finally {
    loading.value = false
  }
}
</script>
