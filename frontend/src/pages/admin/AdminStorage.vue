<template>
  <div class="admin-storage space-y-4 sm:space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-semibold text-gray-900">Хранилище S3</h1>
        <p class="text-sm text-gray-600 mt-1">Управление облачным хранилищем и бакетами</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          type="button"
          class="inline-flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 shadow-sm transition-colors"
          @click="refreshStats"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': isRefreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <span class="hidden sm:inline">Обновить</span>
        </button>
        <button
          type="button"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-medium text-sm rounded-lg shadow-sm transition-colors"
          @click="showSettingsModal = true"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span class="hidden sm:inline">Настройки</span>
        </button>
      </div>
    </div>

    <!-- Connection Status -->
    <div
      :class="[
        'flex items-center gap-4 p-4 rounded-xl border',
        s3Config.connected 
          ? 'bg-emerald-50 border-emerald-200'
          : 'bg-red-50 border-red-200'
      ]"
    >
      <div
        :class="[
          'w-10 h-10 rounded-lg flex items-center justify-center',
          s3Config.connected ? 'bg-emerald-100' : 'bg-red-100'
        ]"
      >
        <svg
          :class="[
            'w-5 h-5',
            s3Config.connected ? 'text-emerald-600' : 'text-red-600'
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path v-if="s3Config.connected" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div class="flex-1">
        <h3 :class="['font-semibold', s3Config.connected ? 'text-emerald-900' : 'text-red-900']">
          {{ s3Config.connected ? 'Подключено к S3' : 'Нет подключения к S3' }}
        </h3>
        <p :class="['text-sm', s3Config.connected ? 'text-emerald-700' : 'text-red-700']">
          {{ s3Config.connected ? s3Config.endpoint : 'Настройте подключение к хранилищу' }}
        </p>
      </div>
      <div v-if="s3Config.connected" class="text-right hidden sm:block">
        <p class="text-sm font-medium text-emerald-900">{{ s3Config.region }}</p>
        <p class="text-xs text-emerald-600">Регион</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-violet-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
            </svg>
          </div>
          <div>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ stats.buckets_count }}</p>
            <p class="text-xs sm:text-sm text-gray-500">Бакетов</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ formatNumber(stats.total_objects) }}</p>
            <p class="text-xs sm:text-sm text-gray-500">Объектов</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
          </div>
          <div>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ formatBytes(stats.total_size) }}</p>
            <p class="text-xs sm:text-sm text-gray-500">Использовано</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div>
            <p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ formatBytesOrDash(stats.monthly_transfer) }}</p>
            <p class="text-xs sm:text-sm text-gray-500">Трафик / мес</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Buckets List -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="font-semibold text-gray-900">Бакеты</h2>
        <button
          type="button"
          disabled
          title="В текущей интеграции используется один S3 bucket из docker-compose.yml. Управление бакетами будет добавлено позже."
          class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-violet-600 hover:bg-violet-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          @click="showCreateBucketModal = true"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Создать бакет
        </button>
      </div>

      <div class="divide-y divide-gray-100">
        <div
          v-for="bucket in buckets"
          :key="bucket.name"
          class="px-5 py-4 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div
                :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center',
                  getBucketTypeColor(bucket.type)
                ]"
              >
                <component :is="getBucketIcon(bucket.type)" class="w-6 h-6" />
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-gray-900">{{ bucket.name }}</h3>
                  <span
                    v-if="bucket.is_default"
                    class="px-2 py-0.5 text-[10px] font-medium bg-violet-100 text-violet-700 rounded"
                  >
                    По умолчанию
                  </span>
                </div>
                <p class="text-sm text-gray-500">{{ bucket.description }}</p>
              </div>
            </div>
            <div class="flex items-center gap-6 text-right">
              <div class="hidden sm:block">
                <p class="text-sm font-medium text-gray-900">{{ formatNumber(bucket.objects_count) }}</p>
                <p class="text-xs text-gray-500">объектов</p>
              </div>
              <div class="hidden md:block">
                <p class="text-sm font-medium text-gray-900">{{ formatBytes(bucket.size) }}</p>
                <p class="text-xs text-gray-500">размер</p>
              </div>
              <div class="flex items-center gap-1">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-lg',
                    bucket.status === 'active' 
                      ? 'bg-emerald-100 text-emerald-700'
                      : 'bg-gray-100 text-gray-600'
                  ]"
                >
                  {{ bucket.status === 'active' ? 'Активен' : 'Неактивен' }}
                </span>
                <button
                  type="button"
                  class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                  @click="editBucket(bucket)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Storage breakdown -->
          <div class="mt-4 pl-16">
            <div class="flex items-center gap-2 mb-2">
              <div class="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-violet-500 to-violet-600 rounded-full transition-all"
                  :style="{ width: `${stats.total_size ? (bucket.size / stats.total_size) * 100 : 0}%` }"
                />
              </div>
              <span class="text-xs text-gray-500 w-12 text-right">
                {{ (stats.total_size ? (bucket.size / stats.total_size) * 100 : 0).toFixed(1) }}%
              </span>
            </div>
            <div class="flex items-center gap-4 text-xs text-gray-500">
              <span>Создан: {{ formatDate(bucket.created_at) }}</span>
              <span>Регион: {{ bucket.region }}</span>
              <span v-if="bucket.versioning">Версионирование: Вкл</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Operations -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm">
      <div class="px-5 py-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-900">Последние операции</h2>
      </div>
      <div class="divide-y divide-gray-100 max-h-[300px] overflow-y-auto">
        <div
          v-for="op in recentOperations"
          :key="op.id"
          class="px-5 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <div
              :class="[
                'w-8 h-8 rounded-lg flex items-center justify-center',
                getOperationColor(op.type)
              ]"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  :d="getOperationIcon(op.type)"
                />
              </svg>
            </div>
            <div>
              <p class="text-sm text-gray-900">{{ op.description }}</p>
              <p class="text-xs text-gray-500">{{ op.bucket }} • {{ formatBytes(op.size) }}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-xs text-gray-500">{{ formatTime(op.timestamp) }}</p>
            <span
              :class="[
                'px-2 py-0.5 text-[10px] font-medium rounded',
                op.status === 'success' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
              ]"
            >
              {{ op.status === 'success' ? 'Успешно' : 'Ошибка' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <Teleport to="body">
      <div
        v-if="showSettingsModal"
        class="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div class="absolute inset-0 bg-black/50" @click="showSettingsModal = false" />
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Настройки S3</h2>
          <p class="text-xs text-gray-500 mb-4">
            Настройки берутся из <code class="px-1 py-0.5 bg-gray-100 rounded">docker-compose.yml</code> (read-only).
            Изменения через UI пока отключены, чтобы не сломать подключение к Beget S3.
          </p>
          
          <form @submit.prevent="saveSettings" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Endpoint URL</label>
              <input
                v-model="settingsForm.endpoint"
                type="text"
                disabled
                placeholder="https://s3.ru1.storage.beget.cloud"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:cursor-not-allowed"
              />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Access Key</label>
                <input
                  v-model="settingsForm.accessKey"
                  type="text"
                  disabled
                  placeholder="(masked)"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:cursor-not-allowed"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Secret Key</label>
                <input
                  v-model="settingsForm.secretKey"
                  type="password"
                  disabled
                  placeholder="(masked)"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:cursor-not-allowed"
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Регион</label>
              <select
                v-model="settingsForm.region"
                disabled
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-500 disabled:cursor-not-allowed"
              >
                <option value="ru-1">ru-1 (Beget)</option>
              </select>
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model="settingsForm.useSSL"
                type="checkbox"
                id="use-ssl"
                disabled
                class="w-4 h-4 text-violet-600 border-gray-300 rounded disabled:cursor-not-allowed"
              />
              <label for="use-ssl" class="text-sm text-gray-700">Использовать SSL</label>
            </div>

            <div class="flex gap-3 pt-4">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                @click="testConnection"
              >
                Проверить
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2.5 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700"
              >
                Сохранить
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Toast -->
    <Teleport to="body">
      <Transition name="toast">
        <div
          v-if="toast.show"
          :class="[
            'fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg',
            toast.type === 'success' ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
          ]"
        >
          <span class="text-sm font-medium">{{ toast.message }}</span>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { apiService } from '@/services/apiService'

interface S3Config {
  connected: boolean
  endpoint: string
  region: string
  accessKey: string
}

interface Bucket {
  name: string
  description: string
  type: 'documents' | 'media' | 'backups' | 'renditions'
  objects_count: number
  size: number
  status: 'active' | 'inactive'
  is_default: boolean
  region: string
  versioning: boolean
  created_at: string
}

interface Operation {
  id: number
  type: 'upload' | 'download' | 'delete' | 'sync'
  description: string
  bucket: string
  size: number
  status: 'success' | 'error'
  timestamp: string
}

interface HeadlessS3ConfigResponse {
  config: {
    enabled: boolean
    endpoint_url: string
    bucket_name: string
    region_name: string
    use_ssl: boolean
    verify: boolean
    location: string
    distribution_location: string
    access_key_masked: string
    secret_key_masked: string
  }
  connection: {
    connected: boolean
    message: string
  }
  source: string
}

interface HeadlessS3StatsResponse {
  connection: {
    connected: boolean
    message: string
  }
  stats: {
    bucket_name: string
    endpoint_url?: string
    region_name?: string
    total_objects: number
    total_size: number
    is_partial: boolean
    scanned_objects: number
    elapsed_ms: number
    breakdown: Record<string, { objects: number; size: number }>
    recent_objects: Array<{ key: string; size: number; last_modified: string }>
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const isRefreshing = ref(false)
const showSettingsModal = ref(false)
const showCreateBucketModal = ref(false)

const toast = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

const settingsForm = ref({
  endpoint: '',
  accessKey: '',
  secretKey: '',
  region: 'ru-1',
  useSSL: true,
  verify: true,
  bucketName: '',
  location: '',
  distributionLocation: ''
})

const s3Config = ref<S3Config>({
  connected: false,
  endpoint: '',
  region: 'ru-1',
  accessKey: ''
})

const stats = ref({
  buckets_count: 0,
  total_objects: 0,
  total_size: 0,
  monthly_transfer: 0,
  is_partial: false,
  scanned_objects: 0,
  elapsed_ms: 0
})

const buckets = ref<Bucket[]>([])
const recentOperations = ref<Operation[]>([])

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

function formatNumber(num: number): string {
  return new Intl.NumberFormat('ru-RU').format(num)
}

function formatBytes(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let unitIndex = 0
  let size = bytes
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

function formatBytesOrDash(bytes: number): string {
  if (!bytes) return '—'
  return formatBytes(bytes)
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU')
}

function formatTime(iso: string): string {
  const date = new Date(iso)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000)
  if (diffMins < 1) return 'только что'
  if (diffMins < 60) return `${diffMins} мин назад`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} ч назад`
  return date.toLocaleDateString('ru-RU')
}

function getBucketTypeColor(type: Bucket['type']): string {
  const colors = {
    documents: 'bg-blue-100 text-blue-600',
    media: 'bg-violet-100 text-violet-600',
    renditions: 'bg-amber-100 text-amber-600',
    backups: 'bg-emerald-100 text-emerald-600'
  }
  return colors[type]
}

function getBucketIcon(type: Bucket['type']) {
  return {
    render() {
      const paths = {
        documents: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
        media: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
        renditions: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6z',
        backups: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4'
      }
      return h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
        h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: paths[type] })
      ])
    }
  }
}

function getOperationColor(type: Operation['type']): string {
  const colors = {
    upload: 'bg-blue-100 text-blue-600',
    download: 'bg-emerald-100 text-emerald-600',
    delete: 'bg-red-100 text-red-600',
    sync: 'bg-violet-100 text-violet-600'
  }
  return colors[type]
}

function getOperationIcon(type: Operation['type']): string {
  const icons = {
    upload: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12',
    download: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4',
    delete: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16',
    sync: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
  }
  return icons[type]
}

async function refreshStats() {
  isRefreshing.value = true
  try {
    await loadS3Data()
    showToast('Статистика обновлена')
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : 'Ошибка обновления статистики'
    showToast(msg, 'error')
  }
  isRefreshing.value = false
}

function testConnection() {
  // Read-only: backend checks the connection using current settings.
  refreshStats()
}

function saveSettings() {
  // IMPORTANT: settings are controlled via docker-compose.yml / environment.
  // We intentionally do not write these settings from the SPA to avoid breaking S3.
  showSettingsModal.value = false
  showToast('Настройки берутся из docker-compose.yml (read-only)')
}

function editBucket(bucket: Bucket) {
  console.log('Edit bucket:', bucket.name)
}

async function loadS3Data(): Promise<void> {
  const [configResp, statsResp] = await Promise.all([
    apiService.get<HeadlessS3ConfigResponse>('/api/v4/headless/storage/s3/config/', undefined as any, false),
    apiService.get<HeadlessS3StatsResponse>(
      '/api/v4/headless/storage/s3/stats/',
      { params: { max_objects: 20000 } } as any,
      false
    ),
  ])

  // Connection + config (masked)
  s3Config.value.connected = Boolean(configResp.connection?.connected)
  s3Config.value.endpoint = configResp.config?.endpoint_url || ''
  s3Config.value.region = configResp.config?.region_name || 'ru-1'
  s3Config.value.accessKey = configResp.config?.access_key_masked || ''

  settingsForm.value.endpoint = configResp.config?.endpoint_url || ''
  settingsForm.value.accessKey = configResp.config?.access_key_masked || ''
  settingsForm.value.secretKey = configResp.config?.secret_key_masked || ''
  settingsForm.value.region = configResp.config?.region_name || 'ru-1'
  settingsForm.value.useSSL = Boolean(configResp.config?.use_ssl)
  settingsForm.value.verify = Boolean(configResp.config?.verify)
  settingsForm.value.bucketName = configResp.config?.bucket_name || ''
  settingsForm.value.location = configResp.config?.location || ''
  settingsForm.value.distributionLocation = configResp.config?.distribution_location || ''

  // Stats
  const s = statsResp.stats
  stats.value.total_objects = s.total_objects || 0
  stats.value.total_size = s.total_size || 0
  stats.value.is_partial = Boolean(s.is_partial)
  stats.value.scanned_objects = s.scanned_objects || 0
  stats.value.elapsed_ms = s.elapsed_ms || 0

  // Virtual buckets (prefix breakdown)
  const breakdown = s.breakdown || {}
  const region = configResp.config?.region_name || 'ru-1'
  const nowIso = new Date().toISOString()
  const bucketName = configResp.config?.bucket_name || s.bucket_name || 's3-bucket'

  const docs = breakdown.documents || { objects: 0, size: 0 }
  const pubs = breakdown.publications || { objects: 0, size: 0 }
  const other = breakdown.other || { objects: 0, size: 0 }

  buckets.value = [
    {
      name: bucketName,
      description: `Документы (prefix: ${settingsForm.value.location || '/'})`,
      type: 'documents',
      objects_count: docs.objects,
      size: docs.size,
      status: statsResp.connection?.connected ? 'active' : 'inactive',
      is_default: true,
      region,
      versioning: false,
      created_at: nowIso
    },
    {
      name: bucketName,
      description: `Публикации (prefix: ${settingsForm.value.distributionLocation || '/'})`,
      type: 'media',
      objects_count: pubs.objects,
      size: pubs.size,
      status: statsResp.connection?.connected ? 'active' : 'inactive',
      is_default: false,
      region,
      versioning: false,
      created_at: nowIso
    },
    {
      name: bucketName,
      description: 'Прочее (все остальные ключи)',
      type: 'renditions',
      objects_count: other.objects,
      size: other.size,
      status: statsResp.connection?.connected ? 'active' : 'inactive',
      is_default: false,
      region,
      versioning: false,
      created_at: nowIso
    }
  ]

  stats.value.buckets_count = buckets.value.length

  // Recent operations: map recent objects to "upload" events
  recentOperations.value = (s.recent_objects || []).map((obj, idx) => {
    return {
      id: idx + 1,
      type: 'upload',
      description: `Объект: ${obj.key}`,
      bucket: bucketName,
      size: obj.size || 0,
      status: 'success',
      timestamp: obj.last_modified
    }
  })
}

onMounted(() => {
  loadS3Data().catch((err: unknown) => {
    const msg = err instanceof Error ? err.message : 'Ошибка загрузки S3'
    showToast(msg, 'error')
  })
})
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


