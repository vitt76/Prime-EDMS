// @ts-nocheck
<template>
  <div class="sharing-detail-page min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-6 max-w-5xl">
      <!-- Back Button -->
      <button
        type="button"
        class="inline-flex items-center gap-2 text-sm text-neutral-600 hover:text-primary-600 mb-6 transition-colors"
        @click="goBack"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Назад к списку
      </button>
      
      <!-- Loading State -->
      <div v-if="isLoading" class="bg-white rounded-2xl border border-neutral-200 p-12 text-center">
        <div class="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p class="text-neutral-500">Загрузка данных...</p>
      </div>
      
      <!-- Not Found -->
      <div v-else-if="!link" class="bg-white rounded-2xl border border-neutral-200 p-12 text-center">
        <svg class="w-16 h-16 text-neutral-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h2 class="text-lg font-semibold text-neutral-900 mb-2">Ссылка не найдена</h2>
        <p class="text-sm text-neutral-500 mb-4">Возможно, она была удалена или срок действия истёк</p>
        <router-link
          to="/sharing"
          class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-xl hover:bg-primary-700 transition-colors"
        >
          Вернуться к списку
        </router-link>
      </div>
      
      <!-- Link Details -->
      <template v-else>
        <!-- Header Card -->
        <div class="bg-white rounded-2xl border border-neutral-200 p-6 mb-6">
          <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-3 mb-2">
                <h1 class="text-2xl font-bold text-neutral-900 truncate">{{ link.name }}</h1>
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold',
                    getStatusClasses(link.status)
                  ]"
                >
                  <span :class="getStatusDotClass(link.status)" />
                  {{ getStatusLabel(link.status) }}
                </span>
              </div>
              
              <div class="flex items-center gap-2 mt-3 text-sm text-neutral-600">
                <code class="px-2 py-1 bg-neutral-100 rounded font-mono text-xs">
                  {{ link.url }}
                </code>
                <button
                  type="button"
                  class="p-1.5 text-neutral-400 hover:text-primary-600 hover:bg-primary-50 rounded-md transition-colors"
                  title="Копировать ссылку"
                  @click="copyLink"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
              
              <p class="mt-3 text-sm text-neutral-500">
                UUID: <code class="font-mono text-xs">{{ link.slug || link.uuid }}</code>
              </p>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center gap-2">
              <button
                v-if="link.status === 'active'"
                type="button"
                class="px-4 py-2 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="showEditModal = true"
              >
                Редактировать
              </button>
              <button
                v-if="link.status !== 'revoked'"
                type="button"
                class="px-4 py-2 text-sm font-medium text-error-600 bg-error-50 rounded-xl hover:bg-error-100 transition-colors"
                @click="showRevokeModal = true"
              >
                Отозвать
              </button>
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Main Info -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Stats -->
            <div class="bg-white rounded-2xl border border-neutral-200 p-6">
              <h3 class="text-sm font-semibold text-neutral-900 mb-4">Статистика</h3>
              <div class="grid grid-cols-3 gap-4">
                <div class="text-center p-4 bg-neutral-50 rounded-xl">
                  <p class="text-3xl font-bold text-neutral-900">{{ formatNumber(link.views) }}</p>
                  <p class="text-sm text-neutral-500 mt-1">Просмотров</p>
                </div>
                <div class="text-center p-4 bg-neutral-50 rounded-xl">
                  <p class="text-3xl font-bold text-neutral-900">{{ formatNumber(link.downloads) }}</p>
                  <p class="text-sm text-neutral-500 mt-1">Скачиваний</p>
                </div>
                <div class="text-center p-4 bg-neutral-50 rounded-xl">
                  <p class="text-3xl font-bold text-neutral-900">{{ formatNumber(link.unique_visitors) }}</p>
                  <p class="text-sm text-neutral-500 mt-1">Уникальных</p>
                </div>
              </div>
            </div>
            
            <!-- Assets -->
            <div class="bg-white rounded-2xl border border-neutral-200 p-6">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-sm font-semibold text-neutral-900">
                  Активы ({{ link.assets?.length || 0 }})
                </h3>
              </div>
              
              <div v-if="link.assets && link.assets.length > 0" class="grid grid-cols-4 sm:grid-cols-6 gap-3">
                <div
                  v-for="asset in link.assets"
                  :key="asset.id"
                  class="relative aspect-square rounded-lg overflow-hidden group cursor-pointer"
                >
                  <img
                    :src="asset.thumbnail_url || 'https://via.placeholder.com/100'"
                    :alt="asset.label"
                    class="w-full h-full object-cover transition-transform group-hover:scale-110"
                    loading="lazy"
                  />
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <span class="text-xs text-white font-medium truncate px-2">{{ asset.label }}</span>
                  </div>
                </div>
              </div>
              
              <div v-else class="p-8 text-center text-neutral-500">
                <svg class="w-12 h-12 mx-auto text-neutral-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-sm">Нет прикреплённых активов</p>
              </div>
            </div>
          </div>
          
          <!-- Sidebar -->
          <div class="space-y-6">
            <!-- Settings -->
            <div class="bg-white rounded-2xl border border-neutral-200 p-6">
              <h3 class="text-sm font-semibold text-neutral-900 mb-4">Настройки</h3>
              
              <dl class="space-y-4">
                <div class="flex items-center justify-between">
                  <dt class="text-sm text-neutral-600">Публичная</dt>
                  <dd>
                    <span
                      :class="[
                        'px-2 py-0.5 text-xs rounded-full',
                        link.is_public ? 'bg-success-100 text-success-700' : 'bg-neutral-100 text-neutral-600'
                      ]"
                    >
                      {{ link.is_public ? 'Да' : 'Нет' }}
                    </span>
                  </dd>
                </div>
                
                <div class="flex items-center justify-between">
                  <dt class="text-sm text-neutral-600">Пароль</dt>
                  <dd>
                    <span
                      :class="[
                        'px-2 py-0.5 text-xs rounded-full',
                        link.password_protected ? 'bg-warning-100 text-warning-700' : 'bg-neutral-100 text-neutral-600'
                      ]"
                    >
                      {{ link.password_protected ? 'Защищено' : 'Нет' }}
                    </span>
                  </dd>
                </div>
                
                <div class="flex items-center justify-between">
                  <dt class="text-sm text-neutral-600">Скачивание</dt>
                  <dd>
                    <span
                      :class="[
                        'px-2 py-0.5 text-xs rounded-full',
                        link.allow_download ? 'bg-success-100 text-success-700' : 'bg-neutral-100 text-neutral-600'
                      ]"
                    >
                      {{ link.allow_download ? 'Разрешено' : 'Запрещено' }}
                    </span>
                  </dd>
                </div>
                
                <div class="flex items-center justify-between">
                  <dt class="text-sm text-neutral-600">Комментарии</dt>
                  <dd>
                    <span
                      :class="[
                        'px-2 py-0.5 text-xs rounded-full',
                        link.allow_comment ? 'bg-success-100 text-success-700' : 'bg-neutral-100 text-neutral-600'
                      ]"
                    >
                      {{ link.allow_comment ? 'Разрешены' : 'Запрещены' }}
                    </span>
                  </dd>
                </div>
              </dl>
            </div>
            
            <!-- Dates -->
            <div class="bg-white rounded-2xl border border-neutral-200 p-6">
              <h3 class="text-sm font-semibold text-neutral-900 mb-4">Даты</h3>
              
              <dl class="space-y-3">
                <div>
                  <dt class="text-xs text-neutral-500">Создано</dt>
                  <dd class="text-sm text-neutral-900">{{ formatFullDate(link.created_date) }}</dd>
                  <dd class="text-xs text-neutral-500">{{ link.created_by }}</dd>
                </div>
                
                <div v-if="link.expires_date">
                  <dt class="text-xs text-neutral-500">Истекает</dt>
                  <dd class="text-sm text-neutral-900">{{ formatFullDate(link.expires_date) }}</dd>
                  <dd
                    v-if="getDaysUntilExpiry(link.expires_date) <= 7 && getDaysUntilExpiry(link.expires_date) > 0"
                    class="text-xs text-warning-600 font-medium"
                  >
                    ⏰ Через {{ getDaysUntilExpiry(link.expires_date) }} дней
                  </dd>
                </div>
                
                <div v-else>
                  <dt class="text-xs text-neutral-500">Истекает</dt>
                  <dd class="text-sm text-neutral-900">∞ Бессрочно</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <!-- Revoke Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showRevokeModal && link" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="showRevokeModal = false" />
          <div class="relative w-full max-w-sm bg-white rounded-2xl shadow-xl p-6 text-center">
            <div class="w-14 h-14 mx-auto bg-error-100 rounded-full flex items-center justify-center mb-4">
              <svg class="w-7 h-7 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-neutral-900 mb-2">Отозвать ссылку?</h3>
            <p class="text-sm text-neutral-600 mb-6">
              Эта ссылка перестанет работать. Действие нельзя отменить.
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="showRevokeModal = false"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-error-600 rounded-xl hover:bg-error-700 transition-colors"
                @click="confirmRevoke"
              >
                Отозвать
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
    
    <!-- Edit Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showEditModal && link" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="showEditModal = false" />
          <div class="relative w-full max-w-md bg-white rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-semibold text-neutral-900 mb-4">Редактировать ссылку</h3>
            
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-neutral-700 mb-2">Название ссылки</label>
                <input
                  v-model="editForm.name"
                  type="text"
                  class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
              </div>
              
              <!-- Expiration Date -->
              <div>
                <label class="flex items-center gap-3 cursor-pointer mb-3">
                  <input
                    v-model="editForm.has_expiration"
                    type="checkbox"
                    class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="text-sm font-medium text-neutral-700">Ограничить срок действия</span>
                </label>
                <input
                  v-if="editForm.has_expiration"
                  v-model="editForm.expires_date"
                  type="date"
                  :min="new Date().toISOString().split('T')[0]"
                  class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
              </div>
              
              <!-- Password Protection -->
              <div>
                <label class="flex items-center gap-3 cursor-pointer mb-3">
                  <input
                    v-model="editForm.has_password"
                    type="checkbox"
                    class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="text-sm font-medium text-neutral-700">Защитить паролем</span>
                </label>
                <input
                  v-if="editForm.has_password"
                  v-model="editForm.password"
                  type="password"
                  placeholder="Введите новый пароль (оставьте пустым, чтобы убрать пароль)"
                  class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
              </div>
              
              <!-- Limits -->
              <div class="space-y-4">
                <div>
                  <label class="flex items-center gap-3 cursor-pointer mb-3">
                    <input
                      v-model="editForm.has_max_views"
                      type="checkbox"
                      class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span class="text-sm font-medium text-neutral-700">Ограничить просмотры</span>
                  </label>
                  <input
                    v-if="editForm.has_max_views"
                    v-model.number="editForm.max_views"
                    type="number"
                    min="1"
                    placeholder="Максимальное количество просмотров"
                    class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                  />
                </div>
                
                <div>
                  <label class="flex items-center gap-3 cursor-pointer mb-3">
                    <input
                      v-model="editForm.has_max_downloads"
                      type="checkbox"
                      class="w-4 h-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span class="text-sm font-medium text-neutral-700">Ограничить скачивания</span>
                  </label>
                  <input
                    v-if="editForm.has_max_downloads"
                    v-model.number="editForm.max_downloads"
                    type="number"
                    min="1"
                    placeholder="Максимальное количество скачиваний"
                    class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                  />
                </div>
              </div>
              
              <!-- Permissions -->
              <div>
                <p class="text-sm font-medium text-neutral-700 mb-3">Разрешения</p>
                <div class="space-y-3">
                  <label class="flex items-center gap-3 cursor-pointer">
                    <input
                      v-model="editForm.allow_download"
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
                      v-model="editForm.allow_comment"
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
            </div>
            
            <div class="flex gap-3 mt-6">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="showEditModal = false"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-colors"
                @click="saveEdit"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDistributionStore, type SharedLink } from '@/stores/distributionStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { distributionService } from '@/services/distributionService'
import { adaptShareLink } from '@/utils/shareLinkAdapter'
import { apiService } from '@/services/apiService'
import { resolveAssetImageUrl } from '@/utils/imageUtils'

// ============================================================================
// PROPS & ROUTE
// ============================================================================

const props = defineProps<{
  id: string
}>()

const route = useRoute()
const router = useRouter()
const distributionStore = useDistributionStore()
const notificationStore = useNotificationStore()

// ============================================================================
// STATE
// ============================================================================

const isLoading = ref(true)
const link = ref<SharedLink | null>(null)
const showRevokeModal = ref(false)
const showEditModal = ref(false)
const assetPreviews = ref<Record<string, string>>({})

const editForm = reactive({
  name: '',
  has_expiration: false,
  expires_date: '',
  has_password: false,
  password: '',
  has_max_views: false,
  max_views: null as number | null,
  has_max_downloads: false,
  max_downloads: null as number | null,
  allow_download: true,
  allow_comment: false
})

// ============================================================================
// METHODS
// ============================================================================

async function loadLink() {
  isLoading.value = true
  
  try {
    const id = parseInt(props.id || route.params.id as string, 10)
    
    // Загружаем детали ссылки напрямую из API
    const apiLink = await distributionService.getShareLinkById(id)
    
    // Адаптируем данные из API в формат SharedLink
    const baseUrl = window.location.origin
    link.value = adaptShareLink(apiLink, baseUrl)
    
    if (link.value) {
      editForm.name = link.value.name
      editForm.has_expiration = !!link.value.expires_date
      editForm.expires_date = link.value.expires_date ? link.value.expires_date.split('T')[0] : ''
      editForm.has_password = link.value.password_protected
      editForm.password = '' // Не показываем существующий пароль
      editForm.has_max_views = !!link.value.max_views
      editForm.max_views = link.value.max_views || null
      editForm.has_max_downloads = !!link.value.max_downloads
      editForm.max_downloads = link.value.max_downloads || null
      editForm.allow_download = link.value.allow_download
      editForm.allow_comment = link.value.allow_comment
      
      // Загружаем детали активов и их превью
      await loadAssetDetails()
    }
  } catch (error) {
    console.error('Failed to load share link:', error)
    link.value = null
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось загрузить данные ссылки'
    })
  } finally {
    isLoading.value = false
  }
}

async function loadAssetDetails() {
  if (!link.value || !link.value.assets || link.value.assets.length === 0) {
    return
  }
  
  const previews: Record<string, string> = {}
  
  for (const asset of link.value.assets) {
    if (!asset.document_id) continue
    
    try {
      // Загружаем детали документа для получения правильного названия
      const docResponse: any = await apiService.get(
        `/api/v4/documents/${asset.document_id}/`,
        undefined,
        false
      )
      
      // Обновляем название актива
      asset.label = docResponse.label || `Document #${asset.document_id}`
      
      // Получаем активную версию файла
      const fileId = docResponse.version_active_file_id || asset.document_file_id || asset.file_id
      
      if (fileId) {
        // Загружаем превью
        try {
          const blob = await apiService.get<Blob>(
            `/api/v4/documents/${asset.document_id}/files/${fileId}/download/`,
            { responseType: 'blob' } as any,
            false
          )
          const objectUrl = window.URL.createObjectURL(blob)
          previews[`${asset.document_id}-${fileId}`] = objectUrl
          asset.thumbnail_url = objectUrl
        } catch (e) {
          // Fallback: используем resolveAssetImageUrl
          const pseudoAsset: any = {
            id: asset.document_id,
            version_active_file_id: fileId,
            file_latest_id: fileId
          }
          const imageUrl = resolveAssetImageUrl(pseudoAsset)
          if (imageUrl && imageUrl !== '/placeholder-document.svg') {
            previews[`${asset.document_id}-${fileId}`] = imageUrl
            asset.thumbnail_url = imageUrl
          }
        }
      }
    } catch (e) {
      console.warn(`Failed to load asset details for document ${asset.document_id}:`, e)
    }
  }
  
  assetPreviews.value = previews
}

function goBack() {
  router.push('/sharing')
}

async function copyLink() {
  if (!link.value) return
  
  try {
    await navigator.clipboard.writeText(link.value.url)
    notificationStore.addNotification({
      type: 'success',
      title: 'Скопировано',
      message: 'Ссылка скопирована в буфер обмена'
    })
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось скопировать ссылку'
    })
  }
}

async function confirmRevoke() {
  if (!link.value) return
  
  try {
    await distributionStore.revokeSharedLink(link.value.id)
    notificationStore.addNotification({
      type: 'success',
      title: 'Отозвано',
      message: 'Публичная ссылка больше недоступна'
    })
    showRevokeModal.value = false
    await loadLink() // Refresh
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось отозвать ссылку'
    })
  }
}

async function saveEdit() {
  if (!link.value) return
  
  try {
    const updates: any = {
      // Note: 'name' is not a field in ShareLink model - it's derived from publication title
      // 'allow_comment' is also not supported by the backend
      allow_download: editForm.allow_download,
      max_views: editForm.has_max_views ? (editForm.max_views || null) : null,
      max_downloads: editForm.has_max_downloads ? (editForm.max_downloads || null) : null
    }
    
    // Handle expires_date: convert date string to ISO datetime format
    if (editForm.has_expiration && editForm.expires_date) {
      // Convert date string (YYYY-MM-DD) to ISO datetime (YYYY-MM-DDTHH:mm:ssZ)
      const date = new Date(editForm.expires_date + 'T23:59:59Z')
      updates.expires_date = date.toISOString()
    } else if (!editForm.has_expiration) {
      updates.expires_date = null
    }
    
    // Handle password: if checkbox is off, clear password; if on and password provided, set it
    if (!editForm.has_password) {
      updates.password = '' // Clear password
    } else if (editForm.password) {
      updates.password = editForm.password // Set new password
    }
    // If checkbox is on but password is empty, don't change it (don't include in updates)
    
    await distributionStore.updateSharedLink(link.value.id, updates)
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Сохранено',
      message: 'Настройки ссылки обновлены'
    })
    
    showEditModal.value = false
    await loadLink() // Refresh
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось сохранить изменения'
    })
  }
}

// ============================================================================
// FORMATTERS
// ============================================================================

function formatNumber(value: number | null | undefined): string {
  const num = typeof value === 'number' ? value : Number(value ?? 0)

  if (!Number.isFinite(num) || num <= 0) {
    return '0'
  }

  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

function formatFullDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getDaysUntilExpiry(dateStr: string): number {
  const now = new Date()
  const expiry = new Date(dateStr)
  const diffTime = expiry.getTime() - now.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

function getStatusClasses(status: SharedLink['status']): string {
  const classes = {
    active: 'bg-success-100 text-success-700',
    expired: 'bg-warning-100 text-warning-700',
    revoked: 'bg-neutral-100 text-neutral-600'
  }
  return classes[status] || classes.revoked
}

function getStatusDotClass(status: SharedLink['status']): string {
  const classes = {
    active: 'w-1.5 h-1.5 rounded-full bg-success-500',
    expired: 'w-1.5 h-1.5 rounded-full bg-warning-500',
    revoked: 'w-1.5 h-1.5 rounded-full bg-neutral-400'
  }
  return classes[status] || classes.revoked
}

function getStatusLabel(status: SharedLink['status']): string {
  const labels = {
    active: 'Активна',
    expired: 'Истекла',
    revoked: 'Отозвана'
  }
  return labels[status] || 'Неизвестно'
}

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  loadLink()
})

watch(
  () => props.id,
  () => loadLink()
)

onBeforeUnmount(() => {
  // Очищаем blob URLs для превью активов
  Object.values(assetPreviews.value).forEach(url => {
    if (url.startsWith('blob:')) {
      try {
        URL.revokeObjectURL(url)
      } catch {
        // ignore
      }
    }
  })
  assetPreviews.value = {}
})
</script>

<style scoped>
.sharing-detail-page {
  padding-top: calc(var(--header-height, 64px));
}
</style>

