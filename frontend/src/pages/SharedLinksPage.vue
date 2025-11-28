<template>
  <div class="shared-links-page min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-neutral-900">Публичные ссылки</h1>
          <p class="mt-1 text-sm text-neutral-600">Управление расшаренными активами</p>
        </div>
        <button
          type="button"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300 rounded-lg hover:bg-neutral-50"
          @click="refreshLinks"
          :disabled="distributionStore.sharedLinksLoading"
        >
          <svg :class="['w-4 h-4', distributionStore.sharedLinksLoading && 'animate-spin']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Обновить
        </button>
      </div>

      <!-- Filters -->
      <div class="flex flex-col sm:flex-row gap-4 mb-6">
        <div class="flex-1 max-w-md relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input v-model="searchQuery" type="text" placeholder="Поиск..." class="w-full pl-10 pr-4 py-2.5 border border-neutral-300 rounded-lg text-sm" @input="handleSearch" />
        </div>
        <select v-model="statusFilter" class="px-4 py-2.5 border border-neutral-300 rounded-lg text-sm bg-white" @change="handleStatusFilter">
          <option value="">Все статусы</option>
          <option value="active">Активные</option>
          <option value="expired">Истекшие</option>
          <option value="revoked">Отозванные</option>
        </select>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-10 h-10 bg-success-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
          </div>
          <div><p class="text-2xl font-bold text-neutral-900">{{ activeCount }}</p><p class="text-sm text-neutral-500">Активных</p></div>
        </div>
        <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-10 h-10 bg-warning-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <div><p class="text-2xl font-bold text-neutral-900">{{ expiredCount }}</p><p class="text-sm text-neutral-500">Истекших</p></div>
        </div>
        <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
          </div>
          <div><p class="text-2xl font-bold text-neutral-900">{{ totalViews.toLocaleString() }}</p><p class="text-sm text-neutral-500">Всего просмотров</p></div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="distributionStore.sharedLinksLoading && distributionStore.sharedLinks.length === 0" class="space-y-4">
        <div v-for="i in 5" :key="i" class="bg-white rounded-xl border p-4 animate-pulse flex gap-4">
          <div class="w-16 h-16 bg-neutral-200 rounded-lg"></div>
          <div class="flex-1"><div class="h-4 bg-neutral-200 rounded w-1/3 mb-2"></div><div class="h-3 bg-neutral-200 rounded w-1/2"></div></div>
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="distributionStore.sharedLinks.length === 0" class="bg-white rounded-xl border p-12 text-center">
        <svg class="mx-auto w-16 h-16 text-neutral-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
        <h3 class="text-lg font-medium text-neutral-900 mb-2">Нет публичных ссылок</h3>
        <p class="text-neutral-500 mb-4">Выберите активы в галерее и нажмите "Поделиться"</p>
        <router-link to="/dam" class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700">Перейти в галерею</router-link>
      </div>

      <!-- Table -->
      <div v-else class="bg-white rounded-xl border overflow-hidden">
        <table class="w-full">
          <thead>
            <tr class="bg-neutral-50 border-b">
              <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase">Название</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase">Создано</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase">Истекает</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase">Статистика</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase">Статус</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-neutral-600 uppercase">Действия</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="link in distributionStore.sharedLinks" :key="link.id" class="hover:bg-neutral-50">
              <td class="px-4 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                    <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
                  </div>
                  <div><p class="text-sm font-medium text-neutral-900">{{ link.name }}</p><p class="text-xs text-neutral-500 font-mono">{{ link.slug }}</p></div>
                </div>
              </td>
              <td class="px-4 py-4"><p class="text-sm text-neutral-900">{{ formatDate(link.created_date) }}</p><p class="text-xs text-neutral-500">{{ link.created_by }}</p></td>
              <td class="px-4 py-4"><p class="text-sm text-neutral-900">{{ link.expires_date ? formatDate(link.expires_date) : 'Бессрочно' }}</p></td>
              <td class="px-4 py-4">
                <div class="flex items-center gap-4 text-sm text-neutral-600">
                  <span class="flex items-center gap-1"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>{{ link.views }}</span>
                  <span class="flex items-center gap-1"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>{{ link.downloads }}</span>
                </div>
              </td>
              <td class="px-4 py-4"><span :class="['inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium', getStatusClasses(link.status)]">{{ getStatusLabel(link.status) }}</span></td>
              <td class="px-4 py-4">
                <div class="flex items-center justify-end gap-2">
                  <button v-if="link.status === 'active'" type="button" class="p-2 text-neutral-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg" title="Копировать" @click="copyLink(link)">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                  </button>
                  <button v-if="link.status !== 'revoked'" type="button" class="p-2 text-neutral-500 hover:text-error-600 hover:bg-error-50 rounded-lg" title="Отозвать" @click="revokeLink(link)">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Revoke Modal -->
    <Teleport to="body">
      <div v-if="showRevokeModal && revokingLink" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/60" @click="closeRevokeModal" />
        <div class="relative w-full max-w-sm bg-white rounded-xl shadow-xl p-6 text-center">
          <div class="w-12 h-12 mx-auto bg-error-100 rounded-full flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          </div>
          <h3 class="text-lg font-semibold text-neutral-900 mb-2">Отозвать ссылку?</h3>
          <p class="text-sm text-neutral-600 mb-6">Ссылка "{{ revokingLink.name }}" перестанет работать.</p>
          <div class="flex justify-center gap-3">
            <button type="button" class="px-4 py-2 text-sm font-medium text-neutral-700 bg-white border rounded-lg hover:bg-neutral-50" @click="closeRevokeModal">Отмена</button>
            <button type="button" class="px-4 py-2 text-sm font-medium text-white bg-error-600 rounded-lg hover:bg-error-700" @click="confirmRevoke">Отозвать</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDistributionStore, type SharedLink } from '@/stores/distributionStore'
import { useNotificationStore } from '@/stores/notificationStore'

const distributionStore = useDistributionStore()
const notificationStore = useNotificationStore()

const searchQuery = ref('')
const statusFilter = ref<'' | SharedLink['status']>('')
const showRevokeModal = ref(false)
const revokingLink = ref<SharedLink | null>(null)

const activeCount = computed(() => distributionStore.sharedLinks.filter(l => l.status === 'active').length)
const expiredCount = computed(() => distributionStore.sharedLinks.filter(l => l.status === 'expired').length)
const totalViews = computed(() => distributionStore.sharedLinks.reduce((sum, l) => sum + l.views, 0))

onMounted(() => { distributionStore.fetchSharedLinks() })

function handleSearch() {
  distributionStore.applySharedLinkFilters({ search: searchQuery.value || undefined, status: statusFilter.value || undefined })
}
function handleStatusFilter() {
  distributionStore.applySharedLinkFilters({ search: searchQuery.value || undefined, status: statusFilter.value || undefined })
}
function refreshLinks() { distributionStore.refreshSharedLinks() }

async function copyLink(link: SharedLink) {
  try {
    await navigator.clipboard.writeText(link.url)
    notificationStore.addNotification({ type: 'success', title: 'Скопировано', message: 'Ссылка скопирована в буфер обмена' })
  } catch { notificationStore.addNotification({ type: 'error', title: 'Ошибка', message: 'Не удалось скопировать' }) }
}

function revokeLink(link: SharedLink) { revokingLink.value = link; showRevokeModal.value = true }
function closeRevokeModal() { showRevokeModal.value = false; revokingLink.value = null }

async function confirmRevoke() {
  if (!revokingLink.value) return
  try {
    await distributionStore.revokeSharedLink(revokingLink.value.id)
    notificationStore.addNotification({ type: 'success', title: 'Отозвано', message: 'Ссылка больше не работает' })
    closeRevokeModal()
  } catch { notificationStore.addNotification({ type: 'error', title: 'Ошибка', message: 'Не удалось отозвать' }) }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
}

function getStatusClasses(status: SharedLink['status']): string {
  return status === 'active' ? 'bg-success-100 text-success-700' : status === 'expired' ? 'bg-warning-100 text-warning-700' : 'bg-neutral-100 text-neutral-600'
}
function getStatusLabel(status: SharedLink['status']): string {
  return status === 'active' ? 'Активна' : status === 'expired' ? 'Истекла' : 'Отозвана'
}
</script>

<style scoped>
.shared-links-page { padding-top: calc(var(--header-height, 64px)); }
</style>

