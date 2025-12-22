<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 overflow-y-auto"
        aria-labelledby="share-modal-title"
        role="dialog"
        aria-modal="true"
      >
        <!-- Backdrop -->
        <div 
          class="fixed inset-0 bg-black/60 backdrop-blur-sm"
          @click="handleClose"
        />

        <!-- Modal Panel -->
        <div class="flex min-h-full items-center justify-center p-4">
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-4"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="isOpen"
              class="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl overflow-hidden"
            >
              <!-- Header -->
              <div class="relative bg-gradient-to-r from-primary-600 to-primary-500 px-6 py-5">
                <div class="flex items-center justify-between">
                  <div>
                    <h2 
                      id="share-modal-title"
                      class="text-xl font-semibold text-white"
                    >
                      {{ linkCreated ? 'Ссылка создана!' : 'Поделиться' }}
                    </h2>
                    <p class="mt-1 text-sm text-primary-100">
                      {{ selectedAssets.length }} {{ getAssetsWord(selectedAssets.length) }}
                    </p>
                  </div>
                  <button
                    type="button"
                    class="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    @click="handleClose"
                    aria-label="Закрыть"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Content -->
              <div class="p-6 space-y-5">
                <!-- Success State: Link Created -->
                <template v-if="linkCreated && createdLink">
                  <!-- Generated Link -->
                  <div class="p-4 bg-success-50 border border-success-200 rounded-xl">
                    <div class="flex items-center gap-3 mb-3">
                      <div class="flex-shrink-0 w-10 h-10 bg-success-100 rounded-full flex items-center justify-center">
                        <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <p class="text-sm font-medium text-success-800">Ссылка успешно создана</p>
                        <p class="text-xs text-success-600">Ссылка скопирована в буфер обмена</p>
                      </div>
                    </div>
                    
                    <div class="flex items-center gap-2">
                      <input
                        :value="createdLink.url"
                        type="text"
                        readonly
                        class="flex-1 px-3 py-2.5 bg-white border border-success-300 rounded-lg text-sm text-neutral-900 font-mono"
                      />
                      <button
                        type="button"
                        class="flex-shrink-0 p-2.5 bg-success-600 text-white rounded-lg hover:bg-success-700 transition-colors"
                        @click="copyLinkToClipboard"
                        :title="copied ? 'Скопировано!' : 'Копировать'"
                      >
                        <svg v-if="!copied" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  <!-- Link Details -->
                  <div class="grid grid-cols-2 gap-3 text-sm">
                    <div class="p-3 bg-neutral-50 rounded-lg">
                      <p class="text-neutral-500 text-xs mb-1">Срок действия</p>
                      <p class="font-medium text-neutral-900">
                        {{ createdLink.expires_date ? formatDate(createdLink.expires_date) : 'Бессрочно' }}
                      </p>
                    </div>
                    <div class="p-3 bg-neutral-50 rounded-lg">
                      <p class="text-neutral-500 text-xs mb-1">Защита</p>
                      <p class="font-medium text-neutral-900">
                        {{ createdLink.password_protected ? 'Пароль' : 'Без пароля' }}
                      </p>
                    </div>
                    <div class="p-3 bg-neutral-50 rounded-lg">
                      <p class="text-neutral-500 text-xs mb-1">Скачивание</p>
                      <p class="font-medium text-neutral-900">
                        {{ createdLink.allow_download ? 'Разрешено' : 'Запрещено' }}
                      </p>
                    </div>
                    <div class="p-3 bg-neutral-50 rounded-lg">
                      <p class="text-neutral-500 text-xs mb-1">Комментарии</p>
                      <p class="font-medium text-neutral-900">
                        {{ createdLink.allow_comment ? 'Разрешены' : 'Запрещены' }}
                      </p>
                    </div>
                  </div>
                </template>

                <!-- Create Form -->
                <template v-else>
                  <!-- Assets Preview -->
                  <div>
                    <label class="block text-sm font-medium text-neutral-700 mb-2">
                      Выбранные активы
                    </label>
                    <div class="flex flex-wrap gap-2 p-3 bg-neutral-50 rounded-xl max-h-24 overflow-y-auto">
                      <div
                        v-for="asset in selectedAssets.slice(0, 8)"
                        :key="asset.id"
                        class="relative w-14 h-14 rounded-lg overflow-hidden bg-neutral-200 flex-shrink-0"
                      >
                        <img
                          v-if="asset.thumbnail_url"
                          :src="asset.thumbnail_url"
                          :alt="asset.label"
                          class="w-full h-full object-cover"
                        />
                        <div v-else class="w-full h-full flex items-center justify-center">
                          <svg class="w-6 h-6 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                      </div>
                      <div
                        v-if="selectedAssets.length > 8"
                        class="w-14 h-14 rounded-lg bg-neutral-300 flex items-center justify-center flex-shrink-0"
                      >
                        <span class="text-sm font-medium text-neutral-600">+{{ selectedAssets.length - 8 }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Link Name -->
                  <div>
                    <label for="link-name" class="block text-sm font-medium text-neutral-700 mb-2">
                      Название ссылки
                    </label>
                    <input
                      id="link-name"
                      v-model="linkName"
                      type="text"
                      :placeholder="defaultLinkName"
                      class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    />
                  </div>

                  <!-- Public Link Toggle -->
                  <div class="flex items-center justify-between p-4 bg-neutral-50 rounded-xl">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                        </svg>
                      </div>
                      <div>
                        <p class="text-sm font-medium text-neutral-900">Публичная ссылка</p>
                        <p class="text-xs text-neutral-500">Любой с ссылкой получит доступ</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      role="switch"
                      :aria-checked="isPublic"
                      :class="[
                        'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
                        isPublic ? 'bg-primary-600' : 'bg-neutral-300'
                      ]"
                      @click="isPublic = !isPublic"
                    >
                      <span
                        :class="[
                          'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                          isPublic ? 'translate-x-5' : 'translate-x-0'
                        ]"
                      />
                    </button>
                  </div>

                  <!-- Expiration Date -->
                  <div>
                    <label class="flex items-center gap-3 cursor-pointer mb-3">
                      <input
                        v-model="hasExpiration"
                        type="checkbox"
                        class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span class="text-sm font-medium text-neutral-700">Ограничить срок действия</span>
                    </label>
                    <input
                      v-if="hasExpiration"
                      v-model="expirationDate"
                      type="date"
                      :min="minDate"
                      class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    />
                  </div>

                  <!-- Password Protection -->
                  <div>
                    <label class="flex items-center gap-3 cursor-pointer mb-3">
                      <input
                        v-model="hasPassword"
                        type="checkbox"
                        class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span class="text-sm font-medium text-neutral-700">Защитить паролем</span>
                    </label>
                    <input
                      v-if="hasPassword"
                      v-model="password"
                      type="password"
                      placeholder="Введите пароль для доступа"
                      class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    />
                  </div>

                  <!-- Permissions -->
                  <div>
                    <p class="text-sm font-medium text-neutral-700 mb-3">Разрешения</p>
                    <div class="space-y-3">
                      <label class="flex items-center gap-3 cursor-pointer">
                        <input
                          v-model="allowDownload"
                          type="checkbox"
                          class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                        />
                        <div>
                          <span class="text-sm text-neutral-700">Разрешить скачивание</span>
                          <p class="text-xs text-neutral-500">Пользователи смогут скачать файлы</p>
                        </div>
                      </label>
                      <label class="flex items-center gap-3 cursor-pointer">
                        <input
                          v-model="allowComments"
                          type="checkbox"
                          class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                        />
                        <div>
                          <span class="text-sm text-neutral-700">Разрешить комментарии</span>
                          <p class="text-xs text-neutral-500">Пользователи смогут оставлять комментарии</p>
                        </div>
                      </label>
                    </div>
                  </div>

                  <!-- Error -->
                  <div v-if="error" class="p-3 bg-error-50 border border-error-200 rounded-lg">
                    <p class="text-sm text-error-700">{{ error }}</p>
                  </div>
                </template>
              </div>

              <!-- Footer -->
              <div class="px-6 py-4 bg-neutral-50 border-t border-neutral-200 flex justify-end gap-3">
                <button
                  type="button"
                  class="px-4 py-2.5 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-lg hover:bg-neutral-50 transition-colors"
                  @click="handleClose"
                  :disabled="isCreating"
                >
                  {{ linkCreated ? 'Закрыть' : 'Отмена' }}
                </button>
                <button
                  v-if="!linkCreated"
                  type="button"
                  class="px-5 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  @click="handleCreateLink"
                  :disabled="isCreating || !isPublic"
                >
                  <svg v-if="isCreating" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  {{ isCreating ? 'Создание...' : 'Создать ссылку' }}
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useDistributionStore } from '@/stores/distributionStore'
import { useNotificationStore } from '@/stores/notificationStore'
import type { Asset } from '@/types/api'
import type { SharedLink } from '@/mocks/publications'

interface Props {
  isOpen: boolean
  assets: Asset[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [link: SharedLink]
}>()

const distributionStore = useDistributionStore()
const notificationStore = useNotificationStore()

// Form state
const linkName = ref('')
const isPublic = ref(true)
const hasExpiration = ref(false)
const expirationDate = ref('')
const hasPassword = ref(false)
const password = ref('')
const allowDownload = ref(true)
const allowComments = ref(false)

// UI state
const isCreating = ref(false)
const error = ref<string | null>(null)
const linkCreated = ref(false)
const createdLink = ref<SharedLink | null>(null)
const copied = ref(false)

// Computed
const selectedAssets = computed(() => props.assets)

const defaultLinkName = computed(() => {
  if (selectedAssets.value.length === 1) {
    return selectedAssets.value[0].label
  }
  return `Подборка из ${selectedAssets.value.length} файлов`
})

const minDate = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  return tomorrow.toISOString().split('T')[0]
})

// Reset form when modal opens/closes
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    resetForm()
  }
})

function resetForm() {
  linkName.value = ''
  isPublic.value = true
  hasExpiration.value = false
  expirationDate.value = ''
  hasPassword.value = false
  password.value = ''
  allowDownload.value = true
  allowComments.value = false
  isCreating.value = false
  error.value = null
  linkCreated.value = false
  createdLink.value = null
  copied.value = false
}

function handleClose() {
  if (isCreating.value) return
  emit('close')
}

async function handleCreateLink() {
  if (!isPublic.value || isCreating.value) return

  isCreating.value = true
  error.value = null

  try {
    const newLink = await distributionStore.createSharedLink({
      name: linkName.value || defaultLinkName.value,
      asset_ids: selectedAssets.value.map(a => a.id),
      is_public: isPublic.value,
      expires_date: hasExpiration.value ? expirationDate.value : null,
      password: hasPassword.value ? password.value : undefined,
      allow_download: allowDownload.value,
      allow_comment: allowComments.value
    })

    createdLink.value = newLink
    linkCreated.value = true

    // Auto-copy to clipboard
    await copyLinkToClipboard()

    // Show success notification
    notificationStore.addNotification({
      type: 'success',
      title: 'Ссылка создана',
      message: `Публичная ссылка "${newLink.name}" успешно создана и скопирована в буфер обмена`
    })

    emit('success', newLink)
  } catch (err: any) {
    const errorMessage = err?.message || err?.response?.data?.detail || 'Не удалось создать ссылку. Попробуйте снова.'
    error.value = errorMessage
    
    // Show detailed error notification
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка создания ссылки',
      message: errorMessage
    })
    
    console.error('Failed to create share link:', err)
  } finally {
    isCreating.value = false
  }
}

async function copyLinkToClipboard() {
  if (!createdLink.value) return

  try {
    await navigator.clipboard.writeText(createdLink.value.url)
    copied.value = true
    
    // Reset copied state after 2 seconds
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy to clipboard:', err)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка копирования',
      message: 'Не удалось скопировать ссылку в буфер обмена'
    })
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function getAssetsWord(count: number): string {
  if (count === 1) return 'актив'
  if (count >= 2 && count <= 4) return 'актива'
  return 'активов'
}
</script>

