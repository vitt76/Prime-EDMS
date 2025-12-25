<template>
  <Modal :is-open="isOpen" @close="$emit('close')" title="Share Links">
    <template #content>
      <div class="share-links-modal">
        <!-- Create New Link -->
        <div class="share-links-modal__create">
          <Button variant="primary" @click="showCreateForm = !showCreateForm">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Create New Link
          </Button>

          <!-- Create Form -->
          <div v-if="showCreateForm" class="share-links-modal__form">
            <div class="share-links-modal__form-group">
              <label class="share-links-modal__label">Expires At (optional)</label>
              <input
                v-model="newLinkExpiresAt"
                type="datetime-local"
                class="share-links-modal__input"
              />
            </div>
            <div class="share-links-modal__form-group">
              <label class="share-links-modal__label">Password (optional)</label>
              <input
                v-model="newLinkPassword"
                type="password"
                class="share-links-modal__input"
                placeholder="Leave empty for no password"
              />
            </div>
            <div class="share-links-modal__form-group">
              <label class="share-links-modal__label">
                <input
                  v-model="newLinkPermissions.view"
                  type="checkbox"
                  class="share-links-modal__checkbox"
                />
                Allow View
              </label>
              <label class="share-links-modal__label">
                <input
                  v-model="newLinkPermissions.download"
                  type="checkbox"
                  class="share-links-modal__checkbox"
                />
                Allow Download
              </label>
            </div>
            <div class="share-links-modal__form-actions">
              <Button variant="primary" @click="handleCreateLink">Create</Button>
              <Button variant="secondary" @click="showCreateForm = false">Cancel</Button>
            </div>
          </div>
        </div>

        <!-- Share Links List -->
        <div v-if="shareLinks.length > 0" class="share-links-modal__list">
          <div
            v-for="link in shareLinks"
            :key="link.id"
            class="share-links-modal__item"
          >
            <div class="share-links-modal__item-info">
              <div class="share-links-modal__item-url">
                <input
                  :value="link.url"
                  readonly
                  class="share-links-modal__url-input"
                  @click="handleCopyUrl(link.url)"
                />
                <Button
                  variant="secondary"
                  size="sm"
                  @click="handleCopyUrl(link.url)"
                  aria-label="Copy link"
                >
                  <svg
                    class="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </Button>
              </div>
              <div class="share-links-modal__item-meta">
                <span v-if="link.expires_at" class="share-links-modal__meta-item">
                  Expires: {{ formatDate(link.expires_at) }}
                </span>
                <span v-if="link.password_protected" class="share-links-modal__meta-item">
                  Password Protected
                </span>
                <span class="share-links-modal__meta-item">
                  Permissions: {{ link.permissions.view ? 'View' : '' }}
                  {{ link.permissions.download ? 'Download' : '' }}
                </span>
              </div>
            </div>
            <Button
              variant="danger"
              size="sm"
              @click="handleDeleteLink(link.id)"
              aria-label="Delete link"
            >
              <svg
                class="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </Button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="share-links-modal__empty">
          <p>No share links created yet</p>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUIStore } from '@/stores/uiStore'
import { distributionService } from '@/services/distributionService'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import type { ShareLink } from '@/types/api'

interface Props {
  publicationId: number
  shareLinks: ShareLink[]
  isOpen?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false
})

const emit = defineEmits<{
  close: []
  'link-created': []
  'link-deleted': []
}>()

const uiStore = useUIStore()
const showCreateForm = ref(false)
const newLinkExpiresAt = ref('')
const newLinkPassword = ref('')
const newLinkPermissions = ref({
  view: true,
  download: false
})

const handleCreateLink = async (): Promise<void> => {
  try {
    await distributionService.createShareLinkForPublication(props.publicationId, {
      expires_at: newLinkExpiresAt.value || undefined,
      password: newLinkPassword.value || undefined,
      permissions: newLinkPermissions.value
    })

    showCreateForm.value = false
    newLinkExpiresAt.value = ''
    newLinkPassword.value = ''
    newLinkPermissions.value = { view: true, download: false }

    emit('link-created')
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Share link created successfully'
    })
  } catch (err) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to create share link'
    })
  }
}

const handleDeleteLink = async (linkId: number): Promise<void> => {
  try {
    await distributionService.deleteShareLinkForPublication(props.publicationId, linkId)
    emit('link-deleted')
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Share link deleted successfully'
    })
  } catch (err) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to delete share link'
    })
  }
}

const handleCopyUrl = async (url: string): Promise<void> => {
  try {
    await navigator.clipboard.writeText(url)
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Link copied to clipboard'
    })
  } catch (err) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to copy link'
    })
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="css">
.share-links-modal {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.share-links-modal__create {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-links-modal__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 8px);
}

.share-links-modal__form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.share-links-modal__label {
  font-size: var(--font-size-sm, 12px);
  font-weight: 500;
  color: var(--color-text, #111827);
}

.share-links-modal__input {
  padding: 8px 12px;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 8px);
  font-size: var(--font-size-base, 14px);
}

.share-links-modal__checkbox {
  margin-right: 8px;
}

.share-links-modal__form-actions {
  display: flex;
  gap: 8px;
}

.share-links-modal__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.share-links-modal__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 8px);
}

.share-links-modal__item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.share-links-modal__item-url {
  display: flex;
  gap: 8px;
}

.share-links-modal__url-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 8px);
  font-size: var(--font-size-sm, 12px);
  cursor: pointer;
}

.share-links-modal__item-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.share-links-modal__meta-item {
  font-size: var(--font-size-xs, 11px);
  color: var(--color-text-secondary, #6b7280);
}

.share-links-modal__empty {
  padding: 32px;
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
}
</style>



