<template>
  <header
    class="fixed top-0 left-0 right-0 h-16 bg-white/95 backdrop-blur-md border-b border-gray-200/80 z-50 flex items-center px-4 lg:px-6"
  >
    <!-- ═══════════════════════════════════════════════════════════════════════
         ZONE 1: LEFT — Brand + Omnibox Search
         ═══════════════════════════════════════════════════════════════════════ -->
    <div class="flex items-center gap-4 flex-1">
      <!-- Logo (Compact) -->
      <router-link
        to="/"
        class="flex items-center gap-2 text-lg font-semibold text-gray-900 hover:text-indigo-600 transition-colors flex-shrink-0"
      >
        <div class="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
          <svg
            class="w-5 h-5 text-white"
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
        </div>
        <span class="hidden lg:inline font-semibold">MADDAM</span>
      </router-link>

      <!-- Global Omnibox Search -->
      <div class="flex-1 max-w-xl">
        <div
          class="flex items-center h-10 bg-gray-100 hover:bg-gray-50 focus-within:bg-white 
                 rounded-xl px-3 border border-transparent focus-within:border-indigo-500 
                 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all duration-200"
        >
          <!-- Search Icon -->
          <svg
            class="w-4 h-4 text-gray-400 flex-shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>

          <!-- Search Input -->
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            placeholder="Поиск активов, тегов, метаданных..."
            class="flex-1 h-full bg-transparent border-none outline-none px-3 
                   text-sm text-gray-900 placeholder-gray-500"
            @keydown.enter="handleSearch"
            @focus="isSearchFocused = true"
            @blur="isSearchFocused = false"
          />

          <!-- Keyboard Shortcut Badge -->
          <kbd
            v-if="!isSearchFocused && !searchQuery"
            class="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium 
                   text-gray-400 bg-gray-200/60 rounded-md"
          >
            <span class="text-[10px]">⌘</span>K
          </kbd>

          <!-- Clear Button -->
          <button
            v-if="searchQuery"
            type="button"
            class="p-1 rounded-md hover:bg-gray-200 transition-colors"
            @click="clearSearch"
          >
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════
         ZONE 2: RIGHT — View Controls, Sort, Actions
         ═══════════════════════════════════════════════════════════════════════ -->
    <div class="flex items-center gap-3">
      <!-- View Mode Toggle (Grid/List) -->
      <div class="hidden md:flex items-center bg-gray-100 p-1 rounded-lg">
        <button
          type="button"
          :class="[
            'flex items-center justify-center w-8 h-7 rounded-md transition-all duration-200',
            viewMode === 'grid'
              ? 'bg-white shadow-sm text-gray-900'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="setViewMode('grid')"
          title="Вид сеткой"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
            />
          </svg>
        </button>
        <button
          type="button"
          :class="[
            'flex items-center justify-center w-8 h-7 rounded-md transition-all duration-200',
            viewMode === 'list'
              ? 'bg-white shadow-sm text-gray-900'
              : 'text-gray-500 hover:text-gray-700'
          ]"
          @click="setViewMode('list')"
          title="Вид списком"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
        </button>
      </div>

      <!-- Sort Dropdown -->
      <div class="relative hidden sm:block" ref="sortDropdownRef">
        <button
          type="button"
          class="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 
                 transition-colors px-2.5 py-1.5 rounded-lg hover:bg-gray-100"
          @click="toggleSortDropdown"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
          </svg>
          <span class="hidden lg:inline">{{ currentSortLabel }}</span>
          <svg
            class="w-3.5 h-3.5 transition-transform duration-200"
            :class="{ 'rotate-180': isSortDropdownOpen }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Sort Dropdown Menu -->
        <Transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div
            v-if="isSortDropdownOpen"
            class="absolute right-0 mt-2 w-44 bg-white rounded-xl shadow-lg border border-gray-200 py-1.5 z-50"
          >
            <button
              v-for="option in sortOptions"
              :key="option.value"
              type="button"
              class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors flex items-center gap-2"
              :class="sortBy === option.value ? 'text-indigo-600 bg-indigo-50 font-medium' : 'text-gray-700'"
              @click="selectSort(option.value)"
            >
              <svg v-if="sortBy === option.value" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <span :class="sortBy === option.value ? '' : 'ml-6'">{{ option.label }}</span>
            </button>
          </div>
        </Transition>
      </div>

      <!-- Divider -->
      <div class="h-6 w-px bg-gray-200 hidden sm:block" />

      <!-- Notifications -->
      <button
        type="button"
        class="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 
               rounded-lg transition-colors"
        @click="handleNotifications"
        :title="`Уведомления${unreadCount > 0 ? ` (${unreadCount})` : ''}`"
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
          class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"
        />
      </button>

      <!-- User Avatar Menu -->
      <div class="relative" ref="userMenuRef">
        <button
          type="button"
          class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          @click="toggleUserMenu"
          :aria-expanded="isUserMenuOpen"
        >
          <div class="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white text-sm font-medium ring-2 ring-white">
            {{ userInitials }}
          </div>
        </button>

        <!-- User Dropdown -->
        <Transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div
            v-if="isUserMenuOpen"
            class="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-1.5 z-50"
          >
            <!-- User Info -->
            <div class="px-4 py-3 border-b border-gray-100">
              <p class="text-sm font-medium text-gray-900">{{ userName }}</p>
              <p class="text-xs text-gray-500 truncate">{{ userEmail }}</p>
            </div>

            <router-link
              to="/settings/profile"
              class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              @click="closeUserMenu"
            >
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Профиль
            </router-link>
          <a
            v-if="isAdmin"
            href="http://localhost:5173/admin"
            class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            @click="closeUserMenu"
          >
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h18M3 12h18M3 17h18" />
            </svg>
            Админ-панель
          </a>
            <router-link
              to="/settings"
              class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              @click="closeUserMenu"
            >
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Настройки
            </router-link>
            
            <div class="border-t border-gray-100 mt-1.5 pt-1.5">
              <button
                type="button"
                class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                @click="handleLogout"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Выйти
              </button>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Primary Action: Upload (THE STAR) -->
      <button
        type="button"
        class="inline-flex items-center gap-2 px-4 py-2 
               bg-indigo-600 hover:bg-indigo-700 
               text-white font-medium text-sm rounded-xl
               shadow-md hover:shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40
               transition-all duration-200
               focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        @click="handleUpload"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <span class="hidden sm:inline">Загрузить</span>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { useAssetStore } from '@/stores/assetStore'

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const assetStore = useAssetStore()

// ═══════════════════════════════════════════════════════════════════════════════
// Refs
// ═══════════════════════════════════════════════════════════════════════════════
const searchInputRef = ref<HTMLInputElement | null>(null)
const sortDropdownRef = ref<HTMLElement | null>(null)
const userMenuRef = ref<HTMLElement | null>(null)

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const searchQuery = ref('')
const isSearchFocused = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')
const sortBy = ref('newest')
const isSortDropdownOpen = ref(false)
const isUserMenuOpen = ref(false)

const sortOptions = [
  { value: 'newest', label: 'Сначала новые' },
  { value: 'oldest', label: 'Сначала старые' },
  { value: 'name_asc', label: 'Имя А → Я' },
  { value: 'name_desc', label: 'Имя Я → А' },
  { value: 'size_desc', label: 'Сначала большие' },
  { value: 'size_asc', label: 'Сначала маленькие' }
]

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const unreadCount = computed(() => notificationStore.unreadCount)

const userInitials = computed(() => {
  const user = authStore.user
  if (!user) return 'U'
  const name = user.first_name || user.username || ''
  return name.charAt(0).toUpperCase() || 'U'
})

const userName = computed(() => {
  const user = authStore.user
  if (!user) return 'Пользователь'
  return user.first_name && user.last_name 
    ? `${user.first_name} ${user.last_name}` 
    : user.username || 'Пользователь'
})

const userEmail = computed(() => {
  return authStore.user?.email || 'user@example.com'
})
const isAdmin = computed(() => {
  const user = authStore.user as any
  if (!user) return false
  const perms: string[] = user.permissions || []
  return Boolean(
    user.is_superuser ||
    user.role === 'admin' ||
    user.username === 'admin' ||
    perms.includes('admin.access') ||
    perms.includes('mayan.add_user')
  )
})

const currentSortLabel = computed(() => {
  const option = sortOptions.find(o => o.value === sortBy.value)
  return option?.label ?? 'Сначала новые'
})

// ═══════════════════════════════════════════════════════════════════════════════
// Handlers
// ═══════════════════════════════════════════════════════════════════════════════
function handleSearch() {
  if (searchQuery.value.trim()) {
    assetStore.setSearchQuery(searchQuery.value)
    emit('search', searchQuery.value)
  }
}

function clearSearch() {
  searchQuery.value = ''
  assetStore.setSearchQuery('')
}

function setViewMode(mode: 'grid' | 'list') {
  viewMode.value = mode
  emit('view-mode-change', mode)
}

function toggleSortDropdown() {
  isSortDropdownOpen.value = !isSortDropdownOpen.value
}

function selectSort(value: string) {
  sortBy.value = value
  isSortDropdownOpen.value = false
  emit('sort-change', value)
}

function handleUpload() {
  emit('upload')
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

// ═══════════════════════════════════════════════════════════════════════════════
// Keyboard Shortcut: Cmd/Ctrl + K
// ═══════════════════════════════════════════════════════════════════════════════
function handleKeydown(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
    event.preventDefault()
    searchInputRef.value?.focus()
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Click Outside
// ═══════════════════════════════════════════════════════════════════════════════
function handleClickOutside(event: MouseEvent) {
  const target = event.target as Node
  
  if (sortDropdownRef.value && !sortDropdownRef.value.contains(target)) {
    isSortDropdownOpen.value = false
  }
  
  if (userMenuRef.value && !userMenuRef.value.contains(target)) {
    isUserMenuOpen.value = false
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Lifecycle
// ═══════════════════════════════════════════════════════════════════════════════
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})

// ═══════════════════════════════════════════════════════════════════════════════
// Emits
// ═══════════════════════════════════════════════════════════════════════════════
const emit = defineEmits<{
  search: [query: string]
  'view-mode-change': [mode: 'grid' | 'list']
  'sort-change': [value: string]
  upload: []
  notifications: []
}>()
</script>
