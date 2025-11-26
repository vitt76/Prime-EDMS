<template>
  <div class="auth-page">
    <main class="auth-card" role="main" aria-labelledby="forgot-password-title">
      <h1 id="forgot-password-title" class="auth-card__title">Forgot password</h1>
      <p class="auth-card__description">
        Enter your email and we will send a link to reset your password.
      </p>

      <form class="auth-form" @submit.prevent="handleSubmit" novalidate>
        <label class="auth-form__label" for="email">
          Email
          <span class="auth-form__required">*</span>
        </label>
        <input
          id="email"
          type="email"
          class="auth-form__input"
          v-model="email"
          :disabled="isSubmitting || cooldown > 0"
          required
          autocomplete="email"
          aria-invalid="emailError ? true : false"
          aria-describedby="email-error"
        />
        <p v-if="emailError" id="email-error" class="auth-form__error">{{ emailError }}</p>

        <button
          type="submit"
          class="auth-form__submit"
          :disabled="isSubmitting || cooldown > 0 || confirmationSent"
          aria-live="polite"
        >
          <span v-if="cooldown > 0">
            Try again in {{ cooldown }}s
          </span>
          <span v-else>Send reset link</span>
        </button>
      </form>

      <p v-if="confirmationSent" class="auth-form__success">
        If this email exists, we sent a reset link. Check your inbox.
      </p>

      <div v-if="errorMessage" class="auth-form__error auth-form__error--global">
        {{ errorMessage }}
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { authService } from '@/services/authService'
import { formatApiError } from '@/utils/errors'

const email = ref('')
const emailError = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)
const confirmationSent = ref(false)
const cooldown = ref(0)
let cooldownTimer: ReturnType<typeof setInterval> | null = null

const validateEmail = (value: string): boolean => {
  const pattern =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!value) {
    emailError.value = 'Email is required'
    return false
  }
  if (!pattern.test(value)) {
    emailError.value = 'Enter a valid email address'
    return false
  }
  emailError.value = ''
  return true
}

const startCooldown = (): void => {
  cooldown.value = 60
  cooldownTimer = setInterval(() => {
    cooldown.value -= 1
    if (cooldown.value <= 0) {
      cooldown.value = 0
      if (cooldownTimer) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    }
  }, 1000)
}

const handleSubmit = async (): Promise<void> => {
  if (!validateEmail(email.value) || confirmationSent.value) {
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    await authService.requestPasswordReset(email.value)
    confirmationSent.value = true
    startCooldown()
  } catch (err) {
    errorMessage.value = formatApiError(err)
  } finally {
    isSubmitting.value = false
  }
}

onBeforeUnmount(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background, #f5f5f5);
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.1);
}

.auth-card__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
}

.auth-card__description {
  margin: 0 0 24px;
  color: #4b5563;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-form__label {
  font-weight: 500;
}

.auth-form__required {
  color: #ef4444;
  margin-left: 4px;
}

.auth-form__input {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 1rem;
}

.auth-form__error {
  color: #dc2626;
  font-size: 0.875rem;
}

.auth-form__error--global {
  margin-top: 12px;
}

.auth-form__success {
  margin-top: 16px;
  color: #16a34a;
  font-weight: 500;
}

.auth-form__submit {
  margin-top: 16px;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: var(--color-primary, #2563eb);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.auth-form__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
<template>
  <div class="auth-page">
    <div class="auth-page__container">
      <div class="auth-page__header">
        <h1 class="auth-page__title">Forgot Password?</h1>
        <p class="auth-page__subtitle">
          Enter your email and we'll send you a link to reset your password
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-page__form">
        <div class="form-group">
          <Input
            v-model="email"
            type="email"
            label="Email"
            placeholder="Enter your email"
            required
            :error="errors.email"
            :disabled="isSubmitting"
            autocomplete="email"
          />
        </div>

        <div v-if="successMessage" class="alert alert--success">
          <p>{{ successMessage }}</p>
        </div>

        <div v-if="errorMessage" class="alert alert--error">
          <p>{{ errorMessage }}</p>
        </div>

        <Button
          type="submit"
          variant="primary"
          :loading="isSubmitting"
          :disabled="!email.trim()"
          class="auth-page__submit"
        >
          Send Reset Link
        </Button>
      </form>

      <div class="auth-page__footer">
        <p class="auth-page__footer-text">
          Remember your password?
          <router-link to="/login" class="auth-page__link">
            Back to Login
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/authService'
import Input from '@/components/Common/Input.vue'
import Button from '@/components/Common/Button.vue'

const router = useRouter()

const email = ref('')
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const errors = reactive<{ email?: string }>({})

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])
  errorMessage.value = ''

  if (!email.value.trim()) {
    errors.email = 'Email is required'
    return false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    errors.email = 'Please enter a valid email address'
    return false
  }

  return true
}

const handleSubmit = async (): Promise<void> => {
  if (!validate()) return

  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await authService.forgotPassword(email.value)
    successMessage.value =
      'If an account with that email exists, we have sent a password reset link.'

    // Auto-redirect after 3 seconds
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 3000)
  } catch (error: any) {
    // Handle different error types
    if (error.response?.status === 429) {
      errorMessage.value =
        'Too many requests. Please wait before requesting another reset link.'
    } else if (error.response?.status === 400) {
      errorMessage.value = 'Invalid email address'
    } else {
      // Security: don't reveal if email exists
      errorMessage.value =
        'If an account with that email exists, we have sent a password reset link.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped lang="css">
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: var(--color-bg-1, #f9fafb);
}

.auth-page__container {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface, #ffffff);
  border-radius: var(--radius-lg, 8px);
  padding: 32px;
  box-shadow: var(--shadow-md, 0 4px 6px rgba(0, 0, 0, 0.1));
}

.auth-page__header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-page__title {
  font-size: var(--font-size-2xl, 24px);
  font-weight: 600;
  color: var(--color-text, #111827);
  margin-bottom: 8px;
}

.auth-page__subtitle {
  font-size: var(--font-size-base, 14px);
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.5;
}

.auth-page__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert {
  padding: 12px;
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-sm, 12px);
}

.alert--success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success, #10b981);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.alert--error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error, #ef4444);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.auth-page__submit {
  width: 100%;
  margin-top: 8px;
}

.auth-page__footer {
  margin-top: 24px;
  text-align: center;
}

.auth-page__footer-text {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
}

.auth-page__link {
  color: var(--color-primary, #3b82f6);
  text-decoration: none;
  font-weight: 500;
}

.auth-page__link:hover {
  text-decoration: underline;
}
</style>



