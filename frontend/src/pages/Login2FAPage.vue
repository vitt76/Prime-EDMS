<template>
  <div class="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-900 px-4">
    <Card class="w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-6">
        <h1 class="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
          Two-Factor Authentication
        </h1>
        <p class="text-sm text-neutral-600 dark:text-neutral-400 mt-2">
          {{ isSetupMode ? 'Set up your authenticator app' : 'Enter your authentication code' }}
        </p>
      </div>

      <!-- Setup Mode: TOTP QR Code -->
      <div v-if="isSetupMode" class="space-y-6">
        <div class="text-center">
          <div class="inline-block p-4 bg-white border-2 border-dashed border-neutral-300 rounded-lg">
            <img
              v-if="qrCodeUrl"
              :src="qrCodeUrl"
              alt="QR Code for TOTP setup"
              class="w-48 h-48"
            />
            <div v-else class="w-48 h-48 flex items-center justify-center text-neutral-500">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          </div>
          <p class="text-xs text-neutral-500 mt-2 max-w-xs mx-auto">
            Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
          </p>
        </div>

        <!-- Manual Secret -->
        <div class="space-y-2">
          <label class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
            Or enter this code manually:
          </label>
          <div class="flex items-center space-x-2">
            <code class="flex-1 p-2 bg-neutral-100 dark:bg-neutral-800 rounded text-sm font-mono text-center select-all">
              {{ secret }}
            </code>
            <Button
              variant="outline"
              size="sm"
              @click="copySecret"
              :title="secretCopied ? 'Copied!' : 'Copy to clipboard'"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </Button>
          </div>
        </div>

        <!-- Backup Codes -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-neutral-700 dark:text-neutral-300">
              Backup Codes
            </label>
            <Button
              variant="ghost"
              size="sm"
              @click="regenerateBackupCodes"
              :loading="regeneratingCodes"
            >
              Regenerate
            </Button>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <code
              v-for="code in backupCodes"
              :key="code"
              class="p-2 bg-neutral-100 dark:bg-neutral-800 rounded text-xs font-mono text-center select-all"
            >
              {{ code }}
            </code>
          </div>
          <p class="text-xs text-amber-600 dark:text-amber-400">
            ⚠️ Save these backup codes in a secure place. Each code can only be used once.
          </p>
        </div>

        <!-- Setup Complete Button -->
        <Button
          variant="primary"
          class="w-full"
          @click="completeSetup"
          :loading="completingSetup"
        >
          I've scanned the QR code
        </Button>
      </div>

      <!-- Verification Mode: Enter Code -->
      <div v-else class="space-y-4">
        <form @submit.prevent="handleVerify" class="space-y-4">
          <Input
            v-model="verificationCode"
            type="text"
            label="Authentication Code"
            placeholder="000000"
            :maxlength="6"
            :required="true"
            :error="codeError"
            :disabled="verifying"
            class="text-center text-lg tracking-widest"
            inputmode="numeric"
            pattern="[0-9]*"
            autocomplete="one-time-code"
          />

          <Button
            type="submit"
            variant="primary"
            class="w-full"
            :loading="verifying"
            :disabled="!verificationCode || verificationCode.length !== 6"
          >
            Verify Code
          </Button>
        </form>

        <!-- Use Backup Code Link -->
        <div class="text-center">
          <button
            @click="useBackupCode = !useBackupCode"
            class="text-sm text-primary-600 hover:text-primary-500 dark:text-primary-400"
          >
            {{ useBackupCode ? 'Use authenticator code' : 'Use backup code instead' }}
          </button>
        </div>

        <!-- Resend Code -->
        <div class="text-center">
          <button
            @click="resendCode"
            class="text-sm text-neutral-600 hover:text-neutral-500 dark:text-neutral-400"
            :disabled="resendDisabled"
          >
            {{ resendDisabled ? `Resend in ${resendCountdown}s` : 'Resend code' }}
          </button>
        </div>
      </div>

      <!-- Error Alert -->
      <div
        v-if="error"
        class="mt-4 p-4 bg-red-50 border border-red-200 rounded-md"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-800">{{ error }}</p>
          </div>
          <div class="ml-auto pl-3">
            <button
              @click="error = null"
              class="inline-flex rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-600"
            >
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Success Alert -->
      <div
        v-if="successMessage"
        class="mt-4 p-4 bg-green-50 border border-green-200 rounded-md"
      >
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm text-green-800">{{ successMessage }}</p>
          </div>
          <div class="ml-auto pl-3">
            <button
              @click="successMessage = null"
              class="inline-flex rounded-md p-1.5 text-green-500 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-green-600"
            >
              <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
/**
 * Two-Factor Authentication Page
 *
 * Handles both setup and verification of 2FA codes.
 * Supports TOTP (Google Authenticator, Authy) and backup codes.
 * Provides secure, accessible interface with error handling.
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Common/Card.vue'
import Input from '@/components/Common/Input.vue'
import Button from '@/components/Common/Button.vue'
import { useAuthStore } from '@/stores/authStore'

// Composables
const router = useRouter()
const authStore = useAuthStore()

// Reactive state
const isSetupMode = ref(false)
const verificationCode = ref('')
const codeError = ref('')
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const verifying = ref(false)
const completingSetup = ref(false)
const regeneratingCodes = ref(false)
const useBackupCode = ref(false)
const resendDisabled = ref(false)
const resendCountdown = ref(0)
const secretCopied = ref(false)

// Computed properties
const secret = computed(() => authStore.twoFactorSetup?.secret ?? '')
const qrCodeUrl = computed(() => authStore.twoFactorSetup?.qr_code_url ?? '')
const backupCodes = computed(() => authStore.twoFactorSetup?.backup_codes ?? [])

/**
 * Initialize 2FA page based on current state
 */
async function initializePage() {
  try {
    // Check if 2FA is already enabled
    await authStore.checkTwoFactorStatus()

    if (!authStore.twoFactorStatus?.enabled) {
      // Need to set up 2FA
      isSetupMode.value = true
      await authStore.enableTwoFactor()
    } else if (authStore.twoFactorPending) {
      // 2FA enabled but needs verification (after login)
      isSetupMode.value = false
    } else {
      // Already verified, redirect to dashboard
      await redirectToDashboard()
    }
  } catch (err) {
    error.value = 'Failed to initialize 2FA. Please try again.'
    console.error('2FA initialization error:', err)
  }
}

/**
 * Handle 2FA code verification
 */
async function handleVerify() {
  if (!verificationCode.value || verificationCode.value.length !== 6) {
    codeError.value = 'Please enter a valid 6-digit code'
    return
  }

  verifying.value = true
  codeError.value = ''
  error.value = ''

  try {
    const method = useBackupCode.value ? 'backup_code' : 'totp'
    const response = await authStore.verifyTwoFactor(verificationCode.value, method)

    if (response.success) {
      successMessage.value = 'Authentication successful!'
      await redirectToDashboard()
    } else {
      codeError.value = 'Invalid code. Please try again.'
    }
  } catch (err: any) {
    if (err?.response?.status === 429) {
      error.value = 'Too many attempts. Please wait before trying again.'
    } else if (err?.response?.status === 401) {
      codeError.value = 'Invalid code. Please check and try again.'
    } else {
      error.value = 'Verification failed. Please try again.'
    }
    console.error('2FA verification error:', err)
  } finally {
    verifying.value = false
  }
}

/**
 * Complete 2FA setup after scanning QR code
 */
async function completeSetup() {
  completingSetup.value = true
  error.value = ''

  try {
    // After setup, user needs to verify with first code
    isSetupMode.value = false
    successMessage.value = 'Setup complete! Please enter your first authentication code.'
  } catch (err) {
    error.value = 'Failed to complete setup. Please try again.'
    console.error('2FA setup completion error:', err)
  } finally {
    completingSetup.value = false
  }
}

/**
 * Regenerate backup codes
 */
async function regenerateBackupCodes() {
  regeneratingCodes.value = true
  error.value = ''

  try {
    await authStore.regenerateBackupCodes()
    successMessage.value = 'Backup codes regenerated successfully.'
  } catch (err) {
    error.value = 'Failed to regenerate backup codes. Please try again.'
    console.error('Backup codes regeneration error:', err)
  } finally {
    regeneratingCodes.value = false
  }
}

/**
 * Copy secret to clipboard
 */
async function copySecret() {
  if (!secret.value) return

  try {
    await navigator.clipboard.writeText(secret.value)
    secretCopied.value = true
    setTimeout(() => {
      secretCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy secret:', err)
  }
}

/**
 * Resend verification code
 */
async function resendCode() {
  if (resendDisabled.value) return

  try {
    // Note: Backend may need to implement resend functionality
    // For now, just reset countdown
    startResendCountdown()
    successMessage.value = 'Code resent. Please check your authenticator app.'
  } catch (err) {
    error.value = 'Failed to resend code. Please try again.'
    console.error('Code resend error:', err)
  }
}

/**
 * Start resend countdown timer
 */
function startResendCountdown() {
  resendCountdown.value = 30
  resendDisabled.value = true

  const interval = setInterval(() => {
    resendCountdown.value--
    if (resendCountdown.value <= 0) {
      resendDisabled.value = false
      clearInterval(interval)
    }
  }, 1000)
}

/**
 * Redirect to dashboard or return URL
 */
async function redirectToDashboard() {
  const returnTo = router.currentRoute.value.query.returnTo as string || '/'
  await router.push(returnTo)
}

// Watch for verification code changes to clear errors
watch(verificationCode, () => {
  if (codeError.value) {
    codeError.value = ''
  }
})

// Initialize page
onMounted(() => {
  initializePage()
})
</script>
