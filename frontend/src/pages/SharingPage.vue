<template>
  <div class="sharing-page min-h-screen bg-neutral-50">
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-bold text-neutral-900">Распространение</h1>
          <p class="mt-1 text-sm text-neutral-600">Управление публичными ссылками и кампаниями</p>
        </div>
        
        <!-- Create Dropdown -->
        <Menu as="div" class="relative">
          <MenuButton
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white text-sm font-semibold rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/25"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Создать
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </MenuButton>
          
          <Transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <MenuItems class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-neutral-200 py-2 z-10">
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="openShareModal"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Быстрая ссылка</p>
                      <p class="text-xs text-neutral-500">Поделиться активами по URL</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
              <MenuItem v-slot="{ active }">
                <button
                  :class="[
                    'w-full px-4 py-3 text-left',
                    active ? 'bg-neutral-50' : ''
                  ]"
                  @click="openCampaignModal"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-semibold text-neutral-900">Кампания</p>
                      <p class="text-xs text-neutral-500">Многоканальное распространение</p>
                    </div>
                  </div>
                </button>
              </MenuItem>
            </MenuItems>
          </Transition>
        </Menu>
      </div>
      
      <!-- Stats -->
      <div class="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.totalLinks }}</p>
            <p class="text-sm text-neutral-500">Всего ссылок</p>
          </div>
        </div>
        <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-12 h-12 bg-success-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.activeLinks }}</p>
            <p class="text-sm text-neutral-500">Активных</p>
          </div>
        </div>
        <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-12 h-12 bg-warning-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.expiredLinks }}</p>
            <p class="text-sm text-neutral-500">Истекших</p>
          </div>
        </div>
        <div class="bg-white rounded-xl border border-neutral-200 p-4 flex items-center gap-3">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-900">{{ stats.totalViews.toLocaleString() }}</p>
            <p class="text-sm text-neutral-500">Просмотров</p>
          </div>
        </div>
      </div>
      
      <!-- Tabs -->
      <div class="bg-white rounded-xl border border-neutral-200 overflow-hidden">
        <!-- Tab Headers -->
        <div class="flex items-center border-b border-neutral-200">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            :class="[
              'relative flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'text-primary-600'
                : 'text-neutral-500 hover:text-neutral-700'
            ]"
            @click="setActiveTab(tab.id)"
          >
            <span>{{ tab.label }}</span>
            <span
              v-if="tab.count !== undefined"
              :class="[
                'px-2 py-0.5 text-xs rounded-full',
                activeTab === tab.id
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-neutral-100 text-neutral-600'
              ]"
            >
              {{ tab.count }}
            </span>
            <!-- Active indicator -->
            <div
              v-if="activeTab === tab.id"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
            />
          </button>
          
          <!-- Search in Table -->
          <div class="ml-auto mr-4 flex items-center gap-3">
            <div class="relative">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="tableSearch"
                type="text"
                placeholder="Поиск..."
                class="w-48 pl-9 pr-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            <button
              type="button"
              class="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
              @click="refreshData"
              :disabled="isLoading"
            >
              <svg :class="['w-5 h-5', isLoading && 'animate-spin']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Tab Content -->
        <div class="p-0">
          <!-- Loading -->
          <div v-if="isLoading && filteredLinks.length === 0" class="p-12 text-center">
            <div class="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p class="text-sm text-neutral-500">Загрузка...</p>
          </div>
          
          <!-- Empty State -->
          <div v-else-if="filteredLinks.length === 0" class="p-12 text-center">
            <svg class="mx-auto w-16 h-16 text-neutral-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 class="text-lg font-medium text-neutral-900 mb-2">
              {{ activeTab === 'all' ? 'Нет публичных ссылок' : `Нет ${tabs.find(t => t.id === activeTab)?.label.toLowerCase()} ссылок` }}
            </h3>
            <p class="text-sm text-neutral-500 mb-4">
              Выберите активы в галерее и создайте ссылку для распространения
            </p>
            <router-link
              to="/dam"
              class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
            >
              Перейти в галерею
            </router-link>
          </div>
          
          <!-- Table -->
          <table v-else class="w-full">
            <thead>
              <tr class="bg-neutral-50 border-b border-neutral-200">
                <th class="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Ссылка
                </th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Создано
                </th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Истекает
                </th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Статистика
                </th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Статус
                </th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-neutral-600 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neutral-100">
              <tr
                v-for="link in filteredLinks"
                :key="link.id"
                class="hover:bg-neutral-50 transition-colors"
              >
                <!-- Link Info with Thumbnail Stack -->
                <td class="px-6 py-4">
                  <div class="flex items-center gap-4">
                    <!-- Stacked Thumbnails -->
                    <div class="relative flex-shrink-0" style="width: 68px; height: 44px;">
                      <template v-if="link.assets && link.assets.length > 0">
                        <div
                          v-for="(asset, idx) in link.assets.slice(0, 3)"
                          :key="idx"
                          :class="[
                            'absolute rounded-lg overflow-hidden border-2 border-white shadow-sm',
                          ]"
                          :style="{
                            width: '44px',
                            height: '44px',
                            left: `${idx * 12}px`,
                            zIndex: 3 - idx,
                          }"
                        >
                          <img
                            :src="asset.thumbnail_url || 'https://via.placeholder.com/44'"
                            :alt="asset.label"
                            class="w-full h-full object-cover"
                          />
                        </div>
                        <!-- More indicator -->
                        <div
                          v-if="link.assets.length > 3"
                          class="absolute rounded-lg bg-neutral-800 text-white text-[10px] font-bold flex items-center justify-center border-2 border-white"
                          style="width: 44px; height: 44px; left: 36px; z-index: 0;"
                        >
                          +{{ link.assets.length - 3 }}
                        </div>
                      </template>
                      <!-- No assets placeholder -->
                      <div
                        v-else
                        class="w-11 h-11 rounded-lg bg-neutral-100 flex items-center justify-center"
                      >
                        <svg class="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                    </div>
                    
                    <!-- Link Details -->
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-neutral-900 truncate max-w-[200px]">
                        {{ link.name }}
                      </p>
                      <p class="text-xs text-neutral-500 font-mono truncate max-w-[200px]">
                        {{ link.slug }}
                      </p>
                    </div>
                  </div>
                </td>
                
                <!-- Created -->
                <td class="px-6 py-4">
                  <p class="text-sm text-neutral-900">{{ formatDate(link.created_date) }}</p>
                  <p class="text-xs text-neutral-500">{{ link.created_by }}</p>
                </td>
                
                <!-- Expires -->
                <td class="px-6 py-4">
                  <p class="text-sm text-neutral-900">
                    {{ link.expires_date ? formatDate(link.expires_date) : 'Бессрочно' }}
                  </p>
                  <p
                    v-if="link.expires_date && getDaysUntilExpiry(link.expires_date) <= 7 && getDaysUntilExpiry(link.expires_date) > 0"
                    class="text-xs text-warning-600"
                  >
                    Истекает через {{ getDaysUntilExpiry(link.expires_date) }} дн.
                  </p>
                </td>
                
                <!-- Stats -->
                <td class="px-6 py-4">
                  <div class="flex items-center gap-4 text-sm text-neutral-600">
                    <span class="flex items-center gap-1.5">
                      <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      {{ link.views || 0 }}
                    </span>
                    <span class="flex items-center gap-1.5">
                      <svg class="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      {{ link.downloads || 0 }}
                    </span>
                  </div>
                </td>
                
                <!-- Status (Clickable) -->
                <td class="px-6 py-4">
                  <button
                    type="button"
                    :class="[
                      'inline-flex px-2.5 py-1 rounded-full text-xs font-semibold cursor-pointer transition-all hover:ring-2 hover:ring-offset-1',
                      getStatusClasses(link.status)
                    ]"
                    @click="filterByStatus(link.status)"
                    :title="`Показать все ${getStatusLabel(link.status).toLowerCase()} ссылки`"
                  >
                    {{ getStatusLabel(link.status) }}
                  </button>
                </td>
                
                <!-- Actions -->
                <td class="px-6 py-4 text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button
                      v-if="link.status === 'active'"
                      type="button"
                      class="p-2 text-neutral-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      title="Копировать ссылку"
                      @click="copyLink(link)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button
                      v-if="link.status !== 'revoked'"
                      type="button"
                      class="p-2 text-neutral-500 hover:text-error-600 hover:bg-error-50 rounded-lg transition-colors"
                      title="Отозвать ссылку"
                      @click="revokeLink(link)"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Revoke Confirmation Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showRevokeModal && revokingLink" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="closeRevokeModal" />
          <div class="relative w-full max-w-sm bg-white rounded-2xl shadow-xl p-6 text-center">
            <div class="w-14 h-14 mx-auto bg-error-100 rounded-full flex items-center justify-center mb-4">
              <svg class="w-7 h-7 text-error-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-neutral-900 mb-2">Отозвать ссылку?</h3>
            <p class="text-sm text-neutral-600 mb-6">
              Ссылка <span class="font-medium">"{{ revokingLink.name }}"</span> перестанет работать. Это действие нельзя отменить.
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 bg-neutral-100 rounded-xl hover:bg-neutral-200 transition-colors"
                @click="closeRevokeModal"
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
    
    <!-- Share Modal -->
    <ShareModal
      :is-open="showShareModal"
      :assets="[]"
      @close="showShareModal = false"
      @success="handleShareSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { useDistributionStore, type SharedLink } from '@/stores/distributionStore'
import { useNotificationStore } from '@/stores/notificationStore'
import ShareModal from '@/components/DAM/ShareModal.vue'

// ============================================================================
// STORES & ROUTER
// ============================================================================

const router = useRouter()
const route = useRoute()
const distributionStore = useDistributionStore()
const notificationStore = useNotificationStore()

// ============================================================================
// STATE
// ============================================================================

type TabId = 'all' | 'active' | 'expired'

const activeTab = ref<TabId>('all')
const tableSearch = ref('')
const showRevokeModal = ref(false)
const revokingLink = ref<SharedLink | null>(null)
const showShareModal = ref(false)
const isLoading = ref(false)

// ============================================================================
// COMPUTED
// ============================================================================

const tabs = computed(() => [
  { id: 'all' as const, label: 'Все ссылки', count: distributionStore.sharedLinks.length },
  { id: 'active' as const, label: 'Активные', count: distributionStore.sharedLinks.filter(l => l.status === 'active').length },
  { id: 'expired' as const, label: 'Истекшие', count: distributionStore.sharedLinks.filter(l => l.status === 'expired').length },
])

const stats = computed(() => ({
  totalLinks: distributionStore.sharedLinks.length,
  activeLinks: distributionStore.sharedLinks.filter(l => l.status === 'active').length,
  expiredLinks: distributionStore.sharedLinks.filter(l => l.status === 'expired').length,
  totalViews: distributionStore.sharedLinks.reduce((sum, l) => sum + (l.views || 0), 0),
}))

const filteredLinks = computed(() => {
  let links = distributionStore.sharedLinks
  
  // Filter by tab
  if (activeTab.value === 'active') {
    links = links.filter(l => l.status === 'active')
  } else if (activeTab.value === 'expired') {
    links = links.filter(l => l.status === 'expired' || l.status === 'revoked')
  }
  
  // Filter by search
  if (tableSearch.value) {
    const query = tableSearch.value.toLowerCase()
    links = links.filter(l => 
      l.name.toLowerCase().includes(query) ||
      l.slug.toLowerCase().includes(query)
    )
  }
  
  return links
})

// ============================================================================
// METHODS
// ============================================================================

function setActiveTab(tab: TabId) {
  activeTab.value = tab
  // Update URL query
  router.replace({ query: { ...route.query, tab } })
}

function filterByStatus(status: SharedLink['status']) {
  if (status === 'active') {
    setActiveTab('active')
  } else {
    setActiveTab('expired')
  }
}

async function refreshData() {
  isLoading.value = true
  try {
    await distributionStore.fetchSharedLinks()
  } finally {
    isLoading.value = false
  }
}

function openShareModal() {
  showShareModal.value = true
}

function openCampaignModal() {
  // TODO: Implement campaign creation modal
  notificationStore.addNotification({
    type: 'info',
    title: 'Скоро',
    message: 'Функционал создания кампаний будет доступен в следующем обновлении'
  })
}

function handleShareSuccess(url: string) {
  showShareModal.value = false
  refreshData()
}

async function copyLink(link: SharedLink) {
  try {
    await navigator.clipboard.writeText(link.url)
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

function revokeLink(link: SharedLink) {
  revokingLink.value = link
  showRevokeModal.value = true
}

function closeRevokeModal() {
  showRevokeModal.value = false
  revokingLink.value = null
}

async function confirmRevoke() {
  if (!revokingLink.value) return
  
  try {
    await distributionStore.revokeSharedLink(revokingLink.value.id)
    notificationStore.addNotification({
      type: 'success',
      title: 'Отозвано',
      message: 'Публичная ссылка больше недоступна'
    })
    closeRevokeModal()
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось отозвать ссылку'
    })
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
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
    active: 'bg-success-100 text-success-700 hover:ring-success-300',
    expired: 'bg-warning-100 text-warning-700 hover:ring-warning-300',
    revoked: 'bg-neutral-100 text-neutral-600 hover:ring-neutral-300'
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

onMounted(async () => {
  // Check URL for tab parameter
  const tabParam = route.query.tab as TabId
  if (tabParam && ['all', 'active', 'expired'].includes(tabParam)) {
    activeTab.value = tabParam
  }
  
  await refreshData()
})

// Watch for route changes
watch(() => route.query.tab, (newTab) => {
  if (newTab && ['all', 'active', 'expired'].includes(newTab as string)) {
    activeTab.value = newTab as TabId
  }
})
</script>

<style scoped>
.sharing-page {
  padding-top: calc(var(--header-height, 64px));
}
</style>

