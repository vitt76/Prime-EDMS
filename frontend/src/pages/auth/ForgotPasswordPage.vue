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

