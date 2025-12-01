<template>
  <Modal
    :is-open="isOpen"
    size="md"
    @close="$emit('close')"
  >
    <template #header>
      <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-900">
        Поделиться активами
      </h2>
    </template>

    <template #default>
      <div class="space-y-4">
        <!-- Share Type -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Тип доступа
          </label>
          <select
            v-model="shareType"
            class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="link">Публичная ссылка</option>
            <option value="users">Конкретные пользователи</option>
            <option value="team">Команда</option>
          </select>
        </div>

        <!-- Permissions -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Права доступа
          </label>
          <div class="space-y-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="permissions"
                type="checkbox"
                value="view"
                class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
              />
              <span class="text-sm text-neutral-700 dark:text-neutral-700">Просмотр</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="permissions"
                type="checkbox"
                value="download"
                class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
              />
              <span class="text-sm text-neutral-700 dark:text-neutral-700">Скачивание</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="permissions"
                type="checkbox"
                value="comment"
                class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
              />
              <span class="text-sm text-neutral-700 dark:text-neutral-700">Комментирование</span>
            </label>
          </div>
        </div>

        <!-- Expiration -->
        <div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="hasExpiration"
              type="checkbox"
              class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
            />
            <span class="text-sm text-neutral-700 dark:text-neutral-700">Ограничить срок действия</span>
          </label>
          <input
            v-if="hasExpiration"
            v-model="expirationDate"
            type="date"
            :min="minDate"
            class="mt-2 w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Password Protection -->
        <div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              v-model="hasPassword"
              type="checkbox"
              class="w-4 h-4 rounded border-neutral-300 text-primary-500 focus:ring-primary-500"
            />
            <span class="text-sm text-neutral-700 dark:text-neutral-700">Защитить паролем</span>
          </label>
          <input
            v-if="hasPassword"
            v-model="password"
            type="password"
            placeholder="Введите пароль"
            class="mt-2 w-full px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <!-- Generated Link (after sharing) -->
        <div v-if="shareLink" class="p-3 bg-primary-50 dark:bg-primary-50 rounded-md">
          <p class="text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Ссылка создана:
          </p>
          <div class="flex items-center gap-2">
            <input
              :value="shareLink"
              type="text"
              readonly
              class="flex-1 px-3 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md text-sm bg-neutral-0 dark:bg-neutral-0 text-neutral-900 dark:text-neutral-900"
            />
            <Button
              variant="outline"
              size="sm"
              @click="copyLink"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </Button>
          </div>
        </div>

        <!-- Info -->
        <div class="p-3 bg-neutral-50 dark:bg-neutral-50 rounded-md">
          <p class="text-sm text-neutral-600 dark:text-neutral-600">
            <strong>{{ selectedCount }}</strong> активов будет доступно по созданной ссылке.
          </p>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="p-3 bg-error-50 dark:bg-error-50 rounded-md">
          <p class="text-sm font-medium text-error">{{ error }}</p>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          variant="outline"
          size="md"
          @click="$emit('close')"
          :disabled="isProcessing"
        >
          {{ shareLink ? 'Закрыть' : 'Отмена' }}
        </Button>
        <Button
          v-if="!shareLink"
          variant="primary"
          size="md"
          @click="handleShare"
          :disabled="permissions.length === 0 || isProcessing"
        >
          <span v-if="!isProcessing">Создать ссылку</span>
          <span v-else>Создание...</span>
        </Button>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import { assetService } from '@/services/assetService'
import { formatApiError } from '@/utils/errors'

interface Props {
  isOpen: boolean
  selectedIds: number[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [shareLink: string]
}>()

const shareType = ref<'link' | 'users' | 'team'>('link')
const permissions = ref<string[]>(['view'])
const hasExpiration = ref(false)
const expirationDate = ref('')
const hasPassword = ref(false)
const password = ref('')
const isProcessing = ref(false)
const shareLink = ref<string | null>(null)
const error = ref<string | null>(null)

const selectedCount = computed(() => props.selectedIds.length)
const minDate = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
})

// Reset on open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      shareType.value = 'link'
      permissions.value = ['view']
      hasExpiration.value = false
      expirationDate.value = ''
      hasPassword.value = false
      password.value = ''
      isProcessing.value = false
      shareLink.value = null
      error.value = null
    }
  }
)

async function handleShare() {
  if (permissions.value.length === 0) return

  isProcessing.value = true
  error.value = null

  try {
    // In real implementation, this would call a share API endpoint
    // For now, simulate with bulkOperation
    const result = await assetService.bulkOperation({
      ids: props.selectedIds,
      action: 'export', // Placeholder - would be 'share' in real API
      data: {
        share_type: shareType.value,
        permissions: permissions.value,
        expiration_date: hasExpiration.value ? expirationDate.value : null,
        password: hasPassword.value ? password.value : null
      }
    })

    if (result.success) {
      // Generate share link (in real implementation, this would come from API)
      const baseUrl = window.location.origin
      shareLink.value = `${baseUrl}/share/${Date.now()}`
      emit('success', shareLink.value)
    } else {
      error.value = 'Не удалось создать ссылку'
    }
  } catch (err) {
    error.value = formatApiError(err)
  } finally {
    isProcessing.value = false
  }
}

function copyLink() {
  if (shareLink.value) {
    navigator.clipboard.writeText(shareLink.value)
    // Show toast notification (would use toast service in real implementation)
    alert('Ссылка скопирована в буфер обмена')
  }
}
</script>

