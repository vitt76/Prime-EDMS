<template>
  <header
    class="fixed top-0 left-0 right-0 h-16 bg-neutral-0 dark:bg-neutral-0 border-b border-neutral-300 dark:border-neutral-300 z-50 flex items-center px-4"
  >
    <!-- Left: Logo -->
    <div class="flex-shrink-0 w-48">
      <router-link
        to="/"
        class="flex items-center gap-2 text-lg font-semibold text-neutral-900 dark:text-neutral-900 hover:text-primary-500 transition-colors"
      >
        <svg
          class="w-8 h-8 text-primary-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <span class="hidden sm:inline">DAM System</span>
      </router-link>
    </div>

    <!-- Center: Smart Search -->
    <div class="flex-1 max-w-2xl mx-4">
      <SmartSearch
        @search="handleSearch"
        @result-selected="handleResultSelected"
      />
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-2 flex-shrink-0">
      <!-- Upload Button -->
      <button
        class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors text-sm font-medium hidden sm:flex items-center gap-2 min-h-[44px] min-w-[44px]"
        @click="handleUpload"
        aria-label="Загрузить файл"
        type="button"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          />
        </svg>
        <span class="hidden md:inline">Загрузить</span>
      </button>

      <!-- Filters Toggle -->
      <button
        class="p-2 text-neutral-600 dark:text-neutral-600 hover:bg-neutral-100 dark:hover:bg-neutral-100 rounded-md transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
        @click="handleFilterToggle"
        aria-label="Фильтры"
        type="button"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
      </button>

      <!-- Notifications -->
      <button
        class="relative p-2 text-neutral-600 dark:text-neutral-600 hover:bg-neutral-100 dark:hover:bg-neutral-100 rounded-md transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
        @click="handleNotifications"
        :aria-label="`Уведомления${unreadCount > 0 ? ` (${unreadCount} непрочитанных)` : ''}`"
        type="button"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
          />
        </svg>
        <span
          v-if="unreadCount > 0"
          class="absolute top-0 right-0 w-2 h-2 bg-error rounded-full"
          aria-label="Непрочитанных: {{ unreadCount }}"
        ></span>
      </button>

      <!-- User Menu -->
      <div class="relative" ref="userMenuRef">
        <button
          class="flex items-center gap-2 p-2 text-neutral-600 dark:text-neutral-600 hover:bg-neutral-100 dark:hover:bg-neutral-100 rounded-md transition-colors min-w-[44px] min-h-[44px]"
          @click="toggleUserMenu"
          aria-label="Меню пользователя"
          :aria-expanded="isUserMenuOpen"
          type="button"
        >
          <div class="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
            {{ userInitials }}
          </div>
          <svg
            class="w-4 h-4 hidden sm:inline"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>

        <!-- User Menu Dropdown -->
        <div
          v-if="isUserMenuOpen"
          class="absolute right-0 mt-2 w-48 bg-neutral-0 dark:bg-neutral-0 border border-neutral-300 dark:border-neutral-300 rounded-md shadow-lg py-1 z-50"
          @click.stop
        >
          <router-link
            to="/settings/profile"
            class="block px-4 py-2 text-sm text-neutral-700 dark:text-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-100"
            @click="closeUserMenu"
          >
            Профиль
          </router-link>
          <router-link
            to="/settings"
            class="block px-4 py-2 text-sm text-neutral-700 dark:text-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-100"
            @click="closeUserMenu"
          >
            Настройки
          </router-link>
          <hr class="my-1 border-neutral-300 dark:border-neutral-300" />
          <button
            class="block w-full text-left px-4 py-2 text-sm text-error hover:bg-neutral-100 dark:hover:bg-neutral-100 min-h-[44px]"
            @click="handleLogout"
            type="button"
            aria-label="Выйти из системы"
          >
            Выйти
          </button>
        </div>
      </div>

      <!-- Mobile Menu Toggle -->
      <button
        class="p-2 text-neutral-600 dark:text-neutral-600 hover:bg-neutral-100 dark:hover:bg-neutral-100 rounded-md transition-colors sm:hidden min-w-[44px] min-h-[44px] flex items-center justify-center"
        @click="handleMobileMenuToggle"
        aria-label="Меню"
        :aria-expanded="false"
        type="button"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useNotificationStore } from '@/stores/notificationStore'
import SmartSearch from '@/components/SmartSearch.vue'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const isUserMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

const unreadCount = computed(() => notificationStore.unreadCount)
const userInitials = computed(() => {
  const user = authStore.user
  if (!user) return 'U'
  const name = user.first_name || user.username || ''
  return name.charAt(0).toUpperCase() || 'U'
})

function handleSearch(query: string) {
  emit('search', query)
}

function handleResultSelected(assetId: number) {
  emit('result-selected', assetId)
}

function handleUpload() {
  emit('upload')
}

function handleFilterToggle() {
  emit('filter-toggle')
}

function handleNotifications() {
  emit('notifications')
}

function toggleUserMenu() {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

function closeUserMenu() {
  isUserMenuOpen.value = false
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
  closeUserMenu()
}

function handleMobileMenuToggle() {
  emit('mobile-menu-toggle')
}

// Keyboard shortcut: Ctrl+K is handled by SearchBar component

// Click outside to close user menu
function handleClickOutside(event: MouseEvent) {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    isUserMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const emit = defineEmits<{
  search: [query: string]
  'result-selected': [assetId: number]
  'filter-toggle': []
  upload: []
  notifications: []
  'mobile-menu-toggle': []
}>()
</script>

