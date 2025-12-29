// @ts-nocheck
<template>
  <div class="admin-sources space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Источники</h1>
        <p class="text-sm text-gray-500 mt-1">Настройка импорта документов</p>
      </div>
      <button
        type="button"
        class="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors"
        @click="showCreateModal = true"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
        </svg>
        Добавить источник
      </button>
    </div>

    <!-- Sources Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div
        v-for="source in sources"
        :key="source.id"
        class="bg-white rounded-xl border border-gray-200 p-5"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-3">
            <div
              :class="[
                'w-12 h-12 rounded-xl flex items-center justify-center',
                source.enabled ? 'bg-violet-100' : 'bg-gray-100'
              ]"
            >
              <component
                :is="sourceIcons[source.source_type]"
                :class="[
                  'w-6 h-6',
                  source.enabled ? 'text-violet-600' : 'text-gray-400'
                ]"
              />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900">{{ source.label }}</h3>
              <p class="text-sm text-gray-500">{{ sourceTypeLabels[source.source_type] }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span
              :class="[
                'px-2.5 py-1 text-xs font-medium rounded-full',
                source.enabled ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'
              ]"
            >
              {{ source.enabled ? 'Активен' : 'Отключён' }}
            </span>
          </div>
        </div>

        <div v-if="source.source_type !== 'yandex_disk'" class="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-gray-500">Последняя синхронизация</p>
            <p class="font-medium text-gray-900">{{ source.last_sync ? formatDate(source.last_sync) : 'Никогда' }}</p>
          </div>
          <div>
            <p class="text-gray-500">Импортировано файлов</p>
            <p class="font-medium text-gray-900">{{ formatNumber(source.documents_imported) }}</p>
          </div>
        </div>

        <div class="mt-4 flex items-center gap-2">
          <button
            v-if="source.enabled && source.source_type !== 'yandex_disk'"
            type="button"
            class="flex-1 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            @click="syncSource(source)"
          >
            {{ syncingId === source.id ? 'Синхронизация...' : 'Запустить синхронизацию' }}
          </button>
          <div v-else class="flex-1"></div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              @click="editSource(source)"
              title="Настроить"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              v-if="source.source_type === 'yandex_disk'"
              type="button"
              class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              @click="openDeleteConfirm(source)"
              title="Удалить источник"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="sources.length === 0" class="bg-white rounded-xl border border-gray-200 px-5 py-16 text-center">
      <svg class="mx-auto w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
      </svg>
      <h3 class="mt-4 text-lg font-semibold text-gray-900">Нет настроенных источников</h3>
      <p class="mt-2 text-sm text-gray-500">Добавьте источник для импорта документов</p>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport to="body">
      <div
        v-if="showCreateModal || editingSource"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="closeModal" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            {{ editingSource ? 'Редактировать источник' : 'Добавить источник' }}
          </h2>
          
          <form @submit.prevent="saveSource" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
              <input
                v-model="sourceForm.label"
                type="text"
                required
                placeholder="Например: Яндекс.Диск (Маркетинг)"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Тип источника</label>
              <select
                v-model="sourceForm.source_type"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              >
                <option value="web_form">Веб-форма</option>
                <option value="email">Email</option>
                <option value="staging_folder">Staging папка</option>
                <option value="watch_folder">Watch папка</option>
                <option value="yandex_disk">Яндекс.Диск</option>
              </select>
            </div>

            <!-- Yandex.Disk specific fields -->
            <template v-if="sourceForm.source_type === 'yandex_disk'">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Client ID</label>
                <input
                  v-model="sourceForm.client_id"
                  type="text"
                  required
                  placeholder="OAuth Client ID от Яндекса"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Client Secret</label>
                <input
                  v-model="sourceForm.client_secret"
                  type="password"
                  placeholder="OAuth Client Secret (оставьте пустым, чтобы не менять)"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Код авторизации (опционально)</label>
                <div class="flex gap-2">
                  <input
                    v-model="sourceForm.authorization_code"
                    type="text"
                    placeholder="Одноразовый код из https://oauth.yandex.ru/verification_code"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                  <button
                    type="button"
                    :disabled="!sourceForm.client_id"
                    class="px-4 py-2 text-sm font-medium text-violet-600 bg-violet-50 hover:bg-violet-100 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed rounded-lg transition-colors border border-violet-200 disabled:border-gray-200 flex items-center gap-2"
                    @click="getAuthorizationCode"
                    title="Откроет страницу oauth.yandex.ru в новом окне"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    Получить код
                  </button>
                </div>
                <p class="text-xs text-gray-500 mt-1">Используется для автоматического получения токена. Кнопка откроет страницу oauth.yandex.ru в новом окне.</p>
              </div>
            </template>

            <!-- Other source types -->
            <div v-if="sourceForm.source_type === 'watch_folder' || sourceForm.source_type === 'staging_folder'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Путь</label>
              <input
                v-model="sourceForm.path"
                type="text"
                placeholder="/var/incoming"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
            </div>

            <div class="flex items-center gap-2">
              <input
                v-model="sourceForm.enabled"
                type="checkbox"
                id="source-enabled"
                class="w-4 h-4 text-violet-600 border-gray-300 rounded"
              />
              <label for="source-enabled" class="text-sm text-gray-700">Включён</label>
            </div>

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                @click="closeModal"
              >
                Отмена
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700"
              >
                {{ editingSource ? 'Сохранить' : 'Создать' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirm Modal -->
    <ConfirmModal
      :is-open="showDeleteConfirm"
      title="Удалить источник Яндекс.Диск?"
      :message="deleteConfirmMessage"
      confirm-text="Удалить"
      cancel-text="Отмена"
      confirm-variant="danger"
      @close="showDeleteConfirm = false"
      @confirm="handleDeleteConfirm"
    />

    <!-- Toast -->
    <Teleport to="body">
      <Transition name="toast">
        <div
          v-if="toast.show"
          class="fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg bg-emerald-600 text-white"
        >
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, reactive, h, onMounted, computed } from 'vue'
import type { Source, SourceType } from '@/types/admin'
import { yandexDiskService } from '@/services/yandexDiskService'
import { apiService } from '@/services/apiService'
import ConfirmModal from '@/components/Common/ConfirmModal.vue'

const showCreateModal = ref(false)
const editingSource = ref<Source | null>(null)
const syncingId = ref<number | null>(null)
const showDeleteConfirm = ref(false)
const deleteTarget = ref<Source | null>(null)

const toast = reactive({
  show: false,
  message: ''
})

const sourceForm = ref({
  label: '',
  source_type: 'web_form' as SourceType,
  path: '',
  enabled: true,
  // Yandex.Disk specific fields
  client_id: '',
  client_secret: '',
  authorization_code: ''
})

// Icons
const WebFormIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
    ])
  }
}

const EmailIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' })
    ])
  }
}

const FolderIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z' })
    ])
  }
}

const CloudIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z' })
    ])
  }
}

const sourceIcons: Record<SourceType, ReturnType<typeof h>> = {
  web_form: WebFormIcon,
  email: EmailIcon,
  staging_folder: FolderIcon,
  watch_folder: FolderIcon,
  yandex_disk: CloudIcon
}

const sourceTypeLabels: Record<SourceType, string> = {
  web_form: 'Веб-форма',
  email: 'Email',
  staging_folder: 'Staging папка',
  watch_folder: 'Watch папка',
  yandex_disk: 'Яндекс.Диск'
}

// Sources data - loaded from API
const sources = ref<Source[]>([])

// Computed property for delete confirmation message
const deleteConfirmMessage = computed(() => {
  if (deleteTarget.value) {
    return `Источник "${deleteTarget.value.label}" будет удалён. Все настройки подключения будут очищены. Действие необратимо.`
  }
  return 'Удалить источник?'
})

// Load sources from API
async function loadSources() {
  try {
    // Load Yandex.Disk configuration
    const yandexConfig = await yandexDiskService.getConfig()
    
    // Build sources list
    const loadedSources: Source[] = []
    
    // Add Yandex.Disk source if configured
    if (yandexConfig.client_id || yandexConfig.has_token) {
      loadedSources.push({
        id: 1,
        label: yandexConfig.cabinet_root_label || 'Яндекс.Диск',
        enabled: yandexConfig.enabled,
        backend_path: 'mayan.apps.dam.backends.YandexDiskSource',
        backend_data: { 
          path: yandexConfig.base_path || 'disk:/',
          client_id: yandexConfig.client_id
        },
        source_type: 'yandex_disk',
        last_sync: null, // TODO: Add last sync tracking
        documents_imported: 0 // TODO: Add import count tracking
      })
    }
    
    sources.value = loadedSources
  } catch (error) {
    console.error('[AdminSources] Failed to load sources:', error)
    // On error, show empty list
    sources.value = []
  }
}

onMounted(async () => {
  await loadSources()
})

// Methods
function showToast(message: string) {
  toast.message = message
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

function formatDate(iso: string): string {
  const date = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 60) return `${diffMins} мин назад`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} ч назад`
  return date.toLocaleDateString('ru-RU')
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat('ru-RU').format(num)
}

async function editSource(source: Source) {
  editingSource.value = source
  sourceForm.value = {
    label: source.label,
    source_type: source.source_type,
    path: (source.backend_data as { path?: string }).path || '',
    enabled: source.enabled,
    client_id: '',
    client_secret: '',
    authorization_code: ''
  }
  
  // Load Yandex.Disk config if editing Yandex.Disk source
  if (source.source_type === 'yandex_disk') {
    try {
      const config = await yandexDiskService.getConfig()
      sourceForm.value.client_id = config.client_id || ''
      sourceForm.value.label = config.cabinet_root_label || 'Яндекс.Диск'
    } catch (error) {
      console.error('[AdminSources] Failed to load Yandex.Disk config:', error)
    }
  }
}

function closeModal() {
  showCreateModal.value = false
  editingSource.value = null
  sourceForm.value = { 
    label: '', 
    source_type: 'web_form', 
    path: '', 
    enabled: true,
    client_id: '',
    client_secret: '',
    authorization_code: ''
  }
}

async function saveSource() {
  try {
    // If editing Yandex.Disk source, save via API
    if (editingSource.value?.source_type === 'yandex_disk') {
      await yandexDiskService.updateConfig({
        client_id: sourceForm.value.client_id,
        client_secret: sourceForm.value.client_secret || undefined,
        cabinet_root_label: sourceForm.value.label,
        authorization_code: sourceForm.value.authorization_code || undefined
      })
      
      // Reload sources to get updated data
      await loadSources()
      showToast('Настройки Яндекс.Диска обновлены')
      closeModal()
      return
    }
    
    // For other source types, use local state (mock behavior)
    if (editingSource.value) {
      // Update existing
      const idx = sources.value.findIndex(s => s.id === editingSource.value!.id)
      if (idx > -1) {
        sources.value[idx] = {
          ...sources.value[idx],
          label: sourceForm.value.label,
          source_type: sourceForm.value.source_type,
          enabled: sourceForm.value.enabled,
          backend_data: sourceForm.value.path ? { path: sourceForm.value.path } : {}
        }
      }
      showToast('Источник обновлён')
    } else {
      // Create new (only for non-Yandex.Disk sources)
      const backendPaths: Record<SourceType, string> = {
        web_form: 'mayan.apps.sources.backends.WebFormSource',
        email: 'mayan.apps.sources.backends.EmailSource',
        staging_folder: 'mayan.apps.sources.backends.StagingFolderSource',
        watch_folder: 'mayan.apps.sources.backends.WatchFolderSource',
        yandex_disk: 'mayan.apps.dam.backends.YandexDiskSource'
      }

      const newSource: Source = {
        id: Date.now(),
        label: sourceForm.value.label,
        enabled: sourceForm.value.enabled,
        backend_path: backendPaths[sourceForm.value.source_type],
        backend_data: sourceForm.value.path ? { path: sourceForm.value.path } : {},
        source_type: sourceForm.value.source_type,
        documents_imported: 0
      }
      sources.value.push(newSource)
      showToast('Источник создан')
    }
    closeModal()
  } catch (error: any) {
    console.error('[AdminSources] Failed to save source:', error)
    showToast(error.message || 'Ошибка при сохранении')
  }
}

async function syncSource(source: Source) {
  syncingId.value = source.id
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  const idx = sources.value.findIndex(s => s.id === source.id)
  if (idx > -1) {
    sources.value[idx].last_sync = new Date().toISOString()
    sources.value[idx].documents_imported += Math.floor(Math.random() * 50) + 5
  }
  
  syncingId.value = null
  showToast('Синхронизация завершена')
}

function getAuthorizationCode() {
  if (!sourceForm.value.client_id) {
    showToast('Сначала укажите Client ID')
    return
  }
  
  const authUrl = `https://oauth.yandex.ru/authorize?response_type=code&client_id=${encodeURIComponent(sourceForm.value.client_id)}`
  window.open(authUrl, '_blank')
}

function openDeleteConfirm(source: Source) {
  deleteTarget.value = source
  showDeleteConfirm.value = true
}

async function handleDeleteConfirm() {
  if (!deleteTarget.value || deleteTarget.value.source_type !== 'yandex_disk') {
    showDeleteConfirm.value = false
    return
  }

  try {
    // Clear Yandex.Disk configuration and token
    await yandexDiskService.updateConfig({
      client_id: '',
      client_secret: '',
      base_path: 'disk:/',
      cabinet_root_label: 'Yandex Disk',
      document_type_id: null,
      max_file_size_mb: 20,
      file_limit: 0,
      clear_token: true
    })
    
    // Reload sources to reflect the deletion
    await loadSources()
    showToast('Источник Яндекс.Диск удалён')
    showDeleteConfirm.value = false
    deleteTarget.value = null
  } catch (error: any) {
    console.error('[AdminSources] Failed to delete Yandex.Disk source:', error)
    showToast(error.message || 'Ошибка при удалении источника')
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>

