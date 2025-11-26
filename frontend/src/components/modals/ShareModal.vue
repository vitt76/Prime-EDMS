<template>
  <Modal
    :isOpen="isOpen"
    title="Share asset"
    size="lg"
    @close="handleClose"
    class-name="share-modal"
  >
    <div class="share-modal__container">
      <section class="share-modal__panel">
        <header class="share-modal__header">
          <h3>Create public share link</h3>
          <p class="share-modal__hint">
            Links are read-only by default. Enable download or password protection if needed.
          </p>
        </header>

        <div class="share-modal__form">
          <label class="share-modal__label">
            Permissions
            <div class="share-modal__permissions">
              <label>
                <input
                  type="checkbox"
                  v-model="permissions.view"
                  disabled
                />
                View
              </label>
              <label>
                <input type="checkbox" v-model="permissions.download" />
                Download
              </label>
            </div>
          </label>

          <label class="share-modal__label">
            Expiration
            <div class="share-modal__expiration">
              <select v-model="expirationPreset">
                <option value="never">Never</option>
                <option value="1day">1 day</option>
                <option value="7days">7 days</option>
                <option value="30days">30 days</option>
                <option value="custom">Custom date</option>
              </select>
              <input
                v-if="expirationPreset === 'custom'"
                type="date"
                v-model="customExpiration"
                :min="today"
              />
            </div>
          </label>

          <label class="share-modal__label share-modal__password">
            <span>
              Password protection
              <small v-if="passwordProtected">Password enabled</small>
            </span>
            <div class="share-modal__password-controls">
              <label class="switch">
                <input
                  type="checkbox"
                  v-model="passwordProtected"
                  aria-label="Toggle password protection"
                />
                <span class="slider" />
              </label>
              <div v-if="passwordProtected" class="share-modal__password-inputs">
                <input
                  type="password"
                  v-model="password"
                  placeholder="Enter password"
                  @keydown.enter.prevent
                />
                <button type="button" @click="generatePassword">
                  Generate
                </button>
              </div>
            </div>
          </label>

          <label class="share-modal__label">
            Email recipients (optional)
            <input
              type="text"
              v-model="emailRecipients"
              placeholder="Comma-separated emails"
            />
          </label>

          <div class="share-modal__actions">
            <Button
              variant="primary"
              :loading="isGenerating"
              :disabled="isGenerating"
              @click="handleGenerate"
            >
              Generate link
            </Button>
            <button
              type="button"
              class="share-modal__secondary"
              @click="handleCopyLink"
              :disabled="!currentShare"
            >
              {{ copyStatusText }}
            </button>
          </div>

          <div v-if="currentShare" class="share-modal__result">
            <div class="share-modal__result-row">
              <span class="share-modal__result-label">URL</span>
              <div class="share-modal__result-value">
                <input :value="currentShare.url" readonly />
                <button type="button" @click="copy(currentShare.url)">
                  Copy
                </button>
              </div>
            </div>
            <div class="share-modal__result-row">
              <span class="share-modal__result-label">Token</span>
              <div class="share-modal__result-value">
                <input :value="currentShare.token" readonly />
                <button type="button" @click="toggleTokenVisibility">
                  {{ tokenButtonText }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="share-modal__panel share-modal__list-panel">
        <header class="share-modal__header">
          <h3>Active share links</h3>
          <p class="share-modal__hint">
            Revoke links at any time. Copy or send via email/Slack.
          </p>
        </header>

        <div class="share-modal__list" v-if="shares.length">
          <article
            v-for="share in shares"
            :key="share.id"
            class="share-modal__list-item"
          >
            <div class="share-modal__list-main">
              <p class="share-modal__list-url">
                <input :value="share.url" readonly />
                <button type="button" @click="copy(share.url)">
                  Copy
                </button>
              </p>
              <div class="share-modal__list-meta">
                <span>Created {{ formatDate(share.created_date) }}</span>
                <span v-if="share.expires_at">
                  Expires {{ formatDate(share.expires_at) }}
                </span>
                <span>
                  {{ share.permissions.download ? 'Download' : 'View only' }}
                </span>
              </div>
            </div>
            <div class="share-modal__list-actions">
              <Button variant="ghost" size="sm" @click="copy(share.url)">
                Copy
              </Button>
              <Button
                variant="danger"
                size="sm"
                @click="handleRevoke(share.id)"
                :loading="revokingId === share.id"
              >
                Revoke
              </Button>
            </div>
          </article>
        </div>

        <div v-else class="share-modal__empty">
          <p>No share links yet.</p>
        </div>
      </section>
    </div>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useUIStore } from '@/stores/uiStore'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import { shareService } from '@/services/shareService'
import type { CreateSharePayload, ShareLink } from '@/types/share'

const props = defineProps<{
  isOpen: boolean
  assetId: number
}>()

const emit = defineEmits<{
  close: []
}>()

const uiStore = useUIStore()

const shares = ref<ShareLink[]>([])
const loadingShares = ref(false)
const isGenerating = ref(false)
const revokingId = ref<number | null>(null)
const permissions = ref({
  view: true,
  download: false
})
const expirationPreset = ref<'never' | '1day' | '7days' | '30days' | 'custom'>('never')
const customExpiration = ref('')
const passwordProtected = ref(false)
const password = ref('')
const emailRecipients = ref('')
const currentShare = ref<ShareLink | null>(null)
const copyStatusText = ref('Copy generated link')
const tokenVisible = ref(false)

const today = computed(() => new Date().toISOString().split('T')[0])

const tokenButtonText = computed(() =>
  tokenVisible.value ? 'Hide token' : 'Show token'
)

const handleGenerate = async (): Promise<void> => {
  if (isGenerating.value || !props.assetId) return
  isGenerating.value = true
  try {
    const payload: CreateSharePayload = {
      permissions: permissions.value,
      expires_at: calculateExpiration(),
      password: passwordProtected.value && password.value ? password.value : undefined,
      share_with_users: parseEmails(emailRecipients.value)
    }
    const link = await shareService.createShare(props.assetId, payload)
    currentShare.value = link
    shares.value = [link, ...shares.value]
    uiStore.addNotification({
      type: 'success',
      message: 'Share link generated'
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to generate share link'
    })
  } finally {
    isGenerating.value = false
  }
}

const loadShares = async (): Promise<void> => {
  if (!props.assetId) return
  loadingShares.value = true
  try {
    shares.value = await shareService.listShares(props.assetId)
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to load share links'
    })
  } finally {
    loadingShares.value = false
  }
}

const handleRevoke = async (shareId: number): Promise<void> => {
  revokingId.value = shareId
  try {
    await shareService.revokeShare(shareId)
    shares.value = shares.value.filter((share) => share.id !== shareId)
    if (currentShare.value?.id === shareId) {
      currentShare.value = null
    }
    uiStore.addNotification({
      type: 'success',
      message: 'Share link revoked'
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Unable to revoke link'
    })
  } finally {
    revokingId.value = null
  }
}

const handleClose = (): void => {
  resetState()
  emit('close')
}

const resetState = (): void => {
  isGenerating.value = false
  currentShare.value = null
  passwordProtected.value = false
  password.value = ''
  emailRecipients.value = ''
  expirationPreset.value = 'never'
  customExpiration.value = ''
  copyStatusText.value = 'Copy generated link'
  tokenVisible.value = false
}

const calculateExpiration = (): string | undefined => {
  const now = new Date()
  switch (expirationPreset.value) {
    case '1day':
      now.setDate(now.getDate() + 1)
      return now.toISOString()
    case '7days':
      now.setDate(now.getDate() + 7)
      return now.toISOString()
    case '30days':
      now.setDate(now.getDate() + 30)
      return now.toISOString()
    case 'custom':
      return customExpiration.value ? new Date(customExpiration.value).toISOString() : undefined
    default:
      return undefined
  }
}

const parseEmails = (value: string): string[] | undefined => {
  const emails = value
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item)
  return emails.length ? emails : undefined
}

const copy = async (text: string): Promise<void> => {
  try {
    await navigator.clipboard.writeText(text)
    copyStatusText.value = 'Copied!'
    uiStore.addNotification({
      type: 'success',
      message: 'Link copied to clipboard'
    })
    setTimeout(() => {
      copyStatusText.value = 'Copy generated link'
    }, 2000)
  } catch {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to copy'
    })
  }
}

const handleCopyLink = (): void => {
  if (currentShare.value) {
    copy(currentShare.value.url)
  }
}

const toggleTokenVisibility = (): void => {
  tokenVisible.value = !tokenVisible.value
}

const generatePassword = (): void => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  password.value = Array.from({ length: 12 }, () =>
    chars.charAt(Math.floor(Math.random() * chars.length))
  ).join('')
}

const formatDate = (value: string): string => {
  return new Date(value).toLocaleString()
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      loadShares()
    } else {
      resetState()
    }
  }
)

watch(expirationPreset, (next) => {
  if (next !== 'custom') {
    customExpiration.value = ''
  }
})
</script>

<style scoped>
.share-modal__container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.share-modal__panel {
  padding: 20px;
  border-radius: 12px;
  background: var(--color-surface, #fff);
  border: 1px solid var(--color-border, #e5e7eb);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-modal__header h3 {
  margin: 0;
  font-size: 1.125rem;
}

.share-modal__hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
}

.share-modal__form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.share-modal__label {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--color-text, #111827);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.share-modal__label input,
.share-modal__label select {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--color-border, #e5e7eb);
  font-size: 0.95rem;
}

.share-modal__permissions {
  display: flex;
  gap: 12px;
}

.share-modal__permissions label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.share-modal__expiration {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.share-modal__password {
  gap: 12px;
}

.share-modal__password-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.share-modal__password-inputs {
  display: flex;
  gap: 8px;
}

.share-modal__password-inputs input {
  flex: 1;
}

.share-modal__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.share-modal__secondary {
  padding: 10px 16px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
}

.share-modal__result {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--color-bg-1, #f9fafb);
}

.share-modal__result-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.share-modal__result-value {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.share-modal__result-value input {
  flex: 1;
  border-radius: 6px;
  border: 1px solid var(--color-border, #e5e7eb);
  padding: 8px;
}

.share-modal__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.share-modal__list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-surface, #fff);
}

.share-modal__list-main {
  flex: 1;
}

.share-modal__list-url {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.share-modal__list-url input {
  flex: 1;
  border-radius: 6px;
  border: 1px solid var(--color-border, #e5e7eb);
  padding: 8px;
}

.share-modal__list-meta {
  font-size: 0.8rem;
  color: var(--color-text-secondary, #6b7280);
  display: flex;
  gap: 12px;
  margin-top: 6px;
}

.share-modal__list-actions {
  display: flex;
  gap: 8px;
}

.share-modal__empty {
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
}

@media (max-width: 768px) {
  .share-modal__container {
    grid-template-columns: 1fr;
  }
}
</style>

