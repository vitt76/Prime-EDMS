<template>
  <div class="share-step">
    <div class="share-step__header">
      <h2 class="share-step__title">Share & Finish</h2>
      <p class="share-step__description">
        Set sharing permissions and generate links for your uploaded files.
      </p>
    </div>

    <!-- Share Configuration -->
    <div class="share-step__config">
      <div class="share-step__panel">
        <h3 class="share-step__panel-title">Sharing Settings</h3>

        <!-- Permissions -->
        <div class="share-step__permissions">
          <h4 class="share-step__permissions-title">Permissions</h4>

          <div class="share-step__permission-item">
            <label class="share-step__checkbox">
              <input
                type="checkbox"
                v-model="shareConfig.permissions.view"
                disabled
              />
              <span class="share-step__checkbox-label">View files</span>
            </label>
            <p class="share-step__permission-desc">Recipients can view the files</p>
          </div>

          <div class="share-step__permission-item">
            <label class="share-step__checkbox">
              <input
                type="checkbox"
                v-model="shareConfig.permissions.download"
              />
              <span class="share-step__checkbox-label">Download files</span>
            </label>
            <p class="share-step__permission-desc">Recipients can download the files</p>
          </div>

          <div class="share-step__permission-item">
            <label class="share-step__checkbox">
              <input
                type="checkbox"
                v-model="shareConfig.permissions.edit"
                disabled
              />
              <span class="share-step__checkbox-label">Edit metadata (coming soon)</span>
            </label>
            <p class="share-step__permission-desc">Recipients can modify file information</p>
          </div>
        </div>

        <!-- Expiration -->
        <div class="share-step__expiration">
          <h4 class="share-step__expiration-title">Link Expiration</h4>

          <div class="share-step__expiration-options">
            <label
              v-for="option in expirationOptions"
              :key="option.value"
              class="share-step__radio"
            >
              <input
                type="radio"
                :value="option.value"
                v-model="expirationPreset"
              />
              <span class="share-step__radio-label">{{ option.label }}</span>
            </label>
          </div>

          <div v-if="expirationPreset === 'custom'" class="share-step__custom-expiration">
            <label class="share-step__date-label">Expiration Date</label>
            <input
              type="date"
              class="share-step__date-input"
              v-model="customExpiration"
              :min="minDate"
            />
          </div>
        </div>

        <!-- Password Protection -->
        <div class="share-step__password">
          <h4 class="share-step__password-title">Password Protection (Optional)</h4>

          <label class="share-step__checkbox">
            <input
              type="checkbox"
              v-model="usePassword"
            />
            <span class="share-step__checkbox-label">Require password to access</span>
          </label>

          <div v-if="usePassword" class="share-step__password-input">
            <input
              type="password"
              class="share-step__input"
              placeholder="Enter password"
              v-model="shareConfig.password"
            />
            <div class="share-step__password-strength">
              <div class="share-step__strength-bar">
                <div
                  class="share-step__strength-fill"
                  :class="passwordStrengthClass"
                  :style="{ width: passwordStrengthPercent + '%' }"
                ></div>
              </div>
              <span class="share-step__strength-text">{{ passwordStrengthText }}</span>
            </div>
          </div>
        </div>

        <!-- Recipients -->
        <div class="share-step__recipients">
          <h4 class="share-step__recipients-title">Share with specific people</h4>

          <div class="share-step__recipient-input">
            <input
              type="email"
              class="share-step__input"
              placeholder="Enter email addresses"
              v-model="recipientInput"
              @keydown="handleRecipientInput"
              @paste="handleRecipientPaste"
            />
            <Button
              variant="outline"
              size="sm"
              @click="addRecipient"
              :disabled="!recipientInput.trim()"
            >
              Add
            </Button>
          </div>

          <div v-if="shareConfig.recipients.length > 0" class="share-step__recipient-list">
            <div
              v-for="recipient in shareConfig.recipients"
              :key="recipient"
              class="share-step__recipient-tag"
            >
              {{ recipient }}
              <button
                type="button"
                class="share-step__recipient-remove"
                @click="removeRecipient(recipient)"
                :aria-label="`Remove ${recipient}`"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Preview Panel -->
      <div class="share-step__preview">
        <h3 class="share-step__preview-title">Files to Share</h3>

        <div class="share-step__file-list">
          <div
            v-for="file in files"
            :key="file.id"
            class="share-step__file-item"
          >
            <div class="share-step__file-info">
              <div class="share-step__file-preview">
                <img
                  v-if="file.preview"
                  :src="file.preview"
                  :alt="`Preview of ${file.name}`"
                  class="share-step__file-thumbnail"
                />
                <div
                  v-else
                  class="share-step__file-icon"
                >
                  {{ getFileIcon(file.type) }}
                </div>
              </div>

              <div class="share-step__file-details">
                <div class="share-step__file-name">{{ file.name }}</div>
                <div class="share-step__file-size">{{ formatFileSize(file.size) }}</div>
              </div>
            </div>

            <div class="share-step__file-status">
              <span
                v-if="file.uploadStatus === 'completed'"
                class="share-step__status share-step__status--ready"
              >
                Ready to share
              </span>
              <span
                v-else
                class="share-step__status share-step__status--pending"
              >
                {{ file.uploadStatus }}
              </span>
            </div>
          </div>
        </div>

        <div class="share-step__summary">
          <div class="share-step__summary-item">
            <span class="share-step__summary-label">Collection:</span>
            <span class="share-step__summary-value">{{ collection.name }}</span>
          </div>
          <div class="share-step__summary-item">
            <span class="share-step__summary-label">Files:</span>
            <span class="share-step__summary-value">{{ files.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Generated Link (after creation) -->
    <div v-if="generatedLink" class="share-step__result">
      <div class="share-step__result-panel">
        <div class="share-step__result-header">
          <svg class="w-6 h-6 text-green-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <h3 class="share-step__result-title">Sharing link created successfully!</h3>
        </div>

        <div class="share-step__link-section">
          <label class="share-step__link-label">Share Link</label>
          <div class="share-step__link-input-group">
            <input
              type="text"
              readonly
              class="share-step__link-input"
              :value="generatedLink.url"
              ref="linkInput"
            />
            <Button
              variant="outline"
              size="sm"
              @click="copyLink"
            >
              {{ linkCopied ? 'Copied!' : 'Copy' }}
            </Button>
          </div>

          <div class="share-step__link-info">
            <div class="share-step__link-detail">
              <span class="share-step__link-detail-label">Expires:</span>
              <span class="share-step__link-detail-value">
                {{ generatedLink.expiresAt ? formatDate(generatedLink.expiresAt) : 'Never' }}
              </span>
            </div>
            <div class="share-step__link-detail">
              <span class="share-step__link-detail-label">Permissions:</span>
              <span class="share-step__link-detail-value">
                {{ generatedLink.permissions.download ? 'View & Download' : 'View Only' }}
              </span>
            </div>
            <div v-if="generatedLink.passwordProtected" class="share-step__link-detail">
              <span class="share-step__link-detail-label">Password:</span>
              <span class="share-step__link-detail-value">Required</span>
            </div>
          </div>
        </div>

        <div class="share-step__result-actions">
          <Button
            variant="outline"
            @click="revokeLink"
            :loading="revoking"
          >
            Revoke Link
          </Button>
          <Button
            variant="primary"
            @click="$emit('complete')"
          >
            Done
          </Button>
        </div>
      </div>
    </div>

    <!-- Step Controls -->
    <div v-if="!generatedLink" class="share-step__controls">
      <Button
        variant="outline"
        @click="$emit('back')"
      >
        Back
      </Button>

      <Button
        variant="primary"
        @click="handleCreateShare"
        :loading="creating"
        :disabled="!canCreateShare"
      >
        Create Share Link
      </Button>
    </div>

    <!-- Error Alert -->
    <Alert
      v-if="error"
      variant="error"
      class="share-step__error"
      :dismissible="true"
      @dismiss="error = null"
    >
      {{ error }}
    </Alert>
  </div>
</template>

<script setup lang="ts">
/**
 * Share Step Component
 *
 * Final step of the upload workflow - configure sharing permissions
 * and generate secure links for uploaded files.
 */

import { ref, computed, watch, nextTick } from 'vue'
import Button from '@/components/Common/Button.vue'
import Alert from '@/components/Common/Alert.vue'
import { useUploadWorkflowStore, type WorkflowFile, type Collection } from '@/stores/uploadWorkflowStore'

// Props
const props = defineProps<{
  files: WorkflowFile[]
  metadata: Record<string, any>
  collection: Collection
}>()

// Emits
const emit = defineEmits<{
  complete: []
  back: []
  error: [error: string]
}>()

// Composables
const workflowStore = useUploadWorkflowStore()

// Reactive state
const shareConfig = ref(workflowStore.shareConfig)
const expirationPreset = ref('never')
const customExpiration = ref('')
const usePassword = ref(false)
const recipientInput = ref('')
const generatedLink = ref<any>(null)
const creating = ref(false)
const revoking = ref(false)
const error = ref<string | null>(null)
const linkCopied = ref(false)
const linkInput = ref<HTMLInputElement>()

// Computed properties
const expirationOptions = [
  { value: 'never', label: 'Never expires' },
  { value: '1hour', label: '1 hour' },
  { value: '24hours', label: '24 hours' },
  { value: '7days', label: '7 days' },
  { value: '30days', label: '30 days' },
  { value: 'custom', label: 'Custom date' }
]

const minDate = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
})

const passwordStrength = computed(() => {
  const password = shareConfig.value.password || ''
  let score = 0

  if (password.length >= 8) score++
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^A-Za-z0-9]/.test(password)) score++

  return score
})

const passwordStrengthPercent = computed(() => {
  return Math.min((passwordStrength.value / 5) * 100, 100)
})

const passwordStrengthText = computed(() => {
  if (passwordStrength.value < 2) return 'Weak'
  if (passwordStrength.value < 4) return 'Fair'
  if (passwordStrength.value < 5) return 'Good'
  return 'Strong'
})

const passwordStrengthClass = computed(() => {
  if (passwordStrength.value < 2) return 'share-step__strength-fill--weak'
  if (passwordStrength.value < 4) return 'share-step__strength-fill--fair'
  if (passwordStrength.value < 5) return 'share-step__strength-fill--good'
  return 'share-step__strength-fill--strong'
})

const canCreateShare = computed(() => {
  return props.files.length > 0 &&
         props.files.every(f => f.uploadStatus === 'completed') &&
         (!usePassword.value || (shareConfig.value.password && passwordStrength.value >= 2))
})

// Methods
function handleRecipientInput(event: KeyboardEvent) {
  if (event.key === 'Enter' || event.key === ',') {
    event.preventDefault()
    addRecipient()
  }
}

function handleRecipientPaste(event: ClipboardEvent) {
  event.preventDefault()
  const pastedText = event.clipboardData?.getData('text') || ''
  const emails = parseEmailsFromText(pastedText)

  emails.forEach(email => {
    if (isValidEmail(email) && !shareConfig.value.recipients.includes(email)) {
      shareConfig.value.recipients.push(email)
    }
  })

  recipientInput.value = ''
}

function parseEmailsFromText(text: string): string[] {
  // Simple email extraction - split by common separators
  return text.split(/[,\s\n;]+/).filter(email => email.trim())
}

function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email.trim())
}

function addRecipient() {
  const email = recipientInput.value.trim()
  if (email && isValidEmail(email) && !shareConfig.value.recipients.includes(email)) {
    shareConfig.value.recipients.push(email)
    recipientInput.value = ''
  }
}

function removeRecipient(email: string) {
  const index = shareConfig.value.recipients.indexOf(email)
  if (index > -1) {
    shareConfig.value.recipients.splice(index, 1)
  }
}

async function handleCreateShare() {
  if (!canCreateShare.value) return

  creating.value = true
  error.value = null

  try {
    // Update expiration based on preset
    if (expirationPreset.value !== 'custom') {
      shareConfig.value.expiration = calculateExpiration(expirationPreset.value)
    } else {
      shareConfig.value.expiration = customExpiration.value ? new Date(customExpiration.value) : undefined
    }

    shareConfig.value.isPublic = shareConfig.value.recipients.length === 0

    await workflowStore.createShare()

    // Generate share link (mock for now)
    generatedLink.value = {
      url: `https://dam.example.com/share/${crypto.randomUUID()}`,
      expiresAt: shareConfig.value.expiration,
      permissions: shareConfig.value.permissions,
      passwordProtected: usePassword.value && shareConfig.value.password
    }

  } catch (err: any) {
    error.value = err.message || 'Failed to create share link'
    emit('error', error.value)
  } finally {
    creating.value = false
  }
}

function calculateExpiration(preset: string): Date | undefined {
  if (preset === 'never') return undefined

  const now = new Date()
  switch (preset) {
    case '1hour': now.setHours(now.getHours() + 1); break
    case '24hours': now.setHours(now.getHours() + 24); break
    case '7days': now.setDate(now.getDate() + 7); break
    case '30days': now.setDate(now.getDate() + 30); break
  }

  return now
}

async function copyLink() {
  if (!generatedLink.value?.url) return

  try {
    await navigator.clipboard.writeText(generatedLink.value.url)
    linkCopied.value = true

    setTimeout(() => {
      linkCopied.value = false
    }, 2000)
  } catch (err) {
    // Fallback for older browsers
    if (linkInput.value) {
      linkInput.value.select()
      document.execCommand('copy')
      linkCopied.value = true

      setTimeout(() => {
        linkCopied.value = false
      }, 2000)
    }
  }
}

async function revokeLink() {
  if (!generatedLink.value) return

  revoking.value = true

  try {
    // In a real app, this would call an API to revoke the link
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API call

    generatedLink.value = null
    shareConfig.value = {
      permissions: { view: true, download: false, edit: false },
      recipients: [],
      isPublic: false
    }

  } catch (err: any) {
    error.value = err.message || 'Failed to revoke link'
  } finally {
    revoking.value = false
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

function getFileIcon(fileType: string): string {
  if (fileType.startsWith('image/')) return '🖼️'
  if (fileType.startsWith('video/')) return '🎥'
  if (fileType.startsWith('audio/')) return '🎵'
  if (fileType.includes('pdf')) return '📄'
  if (fileType.includes('document') || fileType.includes('word')) return '📝'
  if (fileType.includes('spreadsheet') || fileType.includes('excel')) return '📊'
  if (fileType.includes('presentation') || fileType.includes('powerpoint')) return '📽️'
  if (fileType.includes('zip') || fileType.includes('archive')) return '📦'

  return '📄'
}

// Watch for expiration changes
watch(expirationPreset, (newValue) => {
  if (newValue !== 'custom') {
    customExpiration.value = ''
  }
})

watch(usePassword, (newValue) => {
  if (!newValue) {
    shareConfig.value.password = undefined
  }
})
</script>

<style scoped>
.share-step {
  @apply space-y-6;
}

.share-step__header {
  @apply text-center mb-8;
}

.share-step__title {
  @apply text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2;
}

.share-step__description {
  @apply text-neutral-600 dark:text-neutral-400;
}

.share-step__config {
  @apply grid grid-cols-1 lg:grid-cols-2 gap-6;
}

.share-step__panel {
  @apply bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-6 space-y-6;
}

.share-step__panel-title {
  @apply text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4;
}

.share-step__permissions,
.share-step__expiration,
.share-step__password,
.share-step__recipients {
  @apply space-y-3;
}

.share-step__permissions-title,
.share-step__expiration-title,
.share-step__password-title,
.share-step__recipients-title {
  @apply text-sm font-medium text-neutral-700 dark:text-neutral-300;
}

.share-step__permission-item,
.share-step__expiration-options {
  @apply space-y-2;
}

.share-step__checkbox {
  @apply flex items-center space-x-2 cursor-pointer;
}

.share-step__checkbox input[type="checkbox"] {
  @apply w-4 h-4 text-primary-600 bg-neutral-100 border-neutral-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-neutral-800 focus:ring-2 dark:bg-neutral-700 dark:border-neutral-600;
}

.share-step__checkbox-label {
  @apply text-sm text-neutral-700 dark:text-neutral-300;
}

.share-step__permission-desc {
  @apply text-xs text-neutral-500 dark:text-neutral-400 ml-6;
}

.share-step__radio {
  @apply flex items-center space-x-2 cursor-pointer;
}

.share-step__radio input[type="radio"] {
  @apply w-4 h-4 text-primary-600 bg-neutral-100 border-neutral-300 focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-neutral-800 focus:ring-2 dark:bg-neutral-700 dark:border-neutral-600;
}

.share-step__radio-label {
  @apply text-sm text-neutral-700 dark:text-neutral-300;
}

.share-step__custom-expiration {
  @apply space-y-2;
}

.share-step__date-label {
  @apply block text-sm font-medium text-neutral-700 dark:text-neutral-300;
}

.share-step__date-input {
  @apply block w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:placeholder-neutral-400 dark:focus:ring-primary-600 dark:focus:border-primary-600 sm:text-sm;
}

.share-step__password-input {
  @apply space-y-2;
}

.share-step__password-strength {
  @apply flex items-center space-x-2;
}

.share-step__strength-bar {
  @apply flex-1 h-2 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden;
}

.share-step__strength-fill {
  @apply h-full transition-all duration-300;
}

.share-step__strength-fill--weak {
  @apply bg-red-500;
}

.share-step__strength-fill--fair {
  @apply bg-yellow-500;
}

.share-step__strength-fill--good {
  @apply bg-blue-500;
}

.share-step__strength-fill--strong {
  @apply bg-green-500;
}

.share-step__strength-text {
  @apply text-xs font-medium;
}

.share-step__recipient-input {
  @apply flex space-x-2;
}

.share-step__input {
  @apply flex-1 px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:placeholder-neutral-400 dark:focus:ring-primary-600 dark:focus:border-primary-600 sm:text-sm;
}

.share-step__recipient-list {
  @apply flex flex-wrap gap-2;
}

.share-step__recipient-tag {
  @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800 dark:bg-primary-900/20 dark:text-primary-400;
}

.share-step__recipient-remove {
  @apply ml-1 text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300 focus:outline-none;
}

.share-step__preview {
  @apply bg-neutral-50 dark:bg-neutral-900/50 rounded-lg p-6 space-y-4;
}

.share-step__preview-title {
  @apply text-lg font-semibold text-neutral-900 dark:text-neutral-100;
}

.share-step__file-list {
  @apply space-y-3 max-h-60 overflow-y-auto;
}

.share-step__file-item {
  @apply flex items-center justify-between p-3 bg-white dark:bg-neutral-800 rounded-md border border-neutral-200 dark:border-neutral-700;
}

.share-step__file-info {
  @apply flex items-center space-x-3 flex-1;
}

.share-step__file-preview {
  @apply flex-shrink-0;
}

.share-step__file-thumbnail {
  @apply w-8 h-8 object-cover rounded;
}

.share-step__file-icon {
  @apply w-8 h-8 bg-neutral-100 dark:bg-neutral-700 rounded flex items-center justify-center text-lg;
}

.share-step__file-details {
  @apply flex-1 min-w-0;
}

.share-step__file-name {
  @apply text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate;
}

.share-step__file-size {
  @apply text-xs text-neutral-500 dark:text-neutral-400;
}

.share-step__file-status {
  @apply flex-shrink-0;
}

.share-step__status {
  @apply inline-flex items-center px-2 py-1 rounded-full text-xs font-medium;
}

.share-step__status--ready {
  @apply bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400;
}

.share-step__status--pending {
  @apply bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400;
}

.share-step__summary {
  @apply space-y-2 pt-4 border-t border-neutral-200 dark:border-neutral-700;
}

.share-step__summary-item {
  @apply flex justify-between text-sm;
}

.share-step__summary-label {
  @apply text-neutral-600 dark:text-neutral-400;
}

.share-step__summary-value {
  @apply font-medium text-neutral-900 dark:text-neutral-100;
}

.share-step__result {
  @apply mt-8;
}

.share-step__result-panel {
  @apply bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800 rounded-lg p-6 space-y-6;
}

.share-step__result-header {
  @apply flex items-center;
}

.share-step__result-title {
  @apply text-lg font-semibold text-green-900 dark:text-green-100;
}

.share-step__link-section {
  @apply space-y-4;
}

.share-step__link-label {
  @apply block text-sm font-medium text-neutral-700 dark:text-neutral-300;
}

.share-step__link-input-group {
  @apply flex space-x-2;
}

.share-step__link-input {
  @apply flex-1 px-3 py-2 bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 rounded-md text-sm font-mono;
}

.share-step__link-info {
  @apply grid grid-cols-1 md:grid-cols-3 gap-4 text-sm;
}

.share-step__link-detail {
  @apply flex justify-between;
}

.share-step__link-detail-label {
  @apply text-neutral-600 dark:text-neutral-400;
}

.share-step__link-detail-value {
  @apply font-medium text-neutral-900 dark:text-neutral-100;
}

.share-step__result-actions {
  @apply flex justify-end space-x-3;
}

.share-step__controls {
  @apply flex justify-between pt-6 border-t border-neutral-200 dark:border-neutral-700;
}

.share-step__error {
  @apply fixed bottom-4 right-4 z-50 max-w-md;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .share-step__config {
    @apply grid-cols-1;
  }

  .share-step__link-input-group {
    @apply flex-col space-x-0 space-y-2;
  }

  .share-step__result-actions {
    @apply flex-col space-y-2;
  }

  .share-step__controls {
    @apply flex-col space-y-4;
  }
}
</style>







