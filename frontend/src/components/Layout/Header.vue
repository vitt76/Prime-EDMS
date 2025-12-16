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
        <div class="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center overflow-hidden">
          <svg
            class="w-full h-full text-white p-1"
            viewBox="0 0 1287.000000 1214.000000"
            xmlns="http://www.w3.org/2000/svg"
            preserveAspectRatio="xMidYMid meet"
          >
            <g transform="translate(0.000000,1214.000000) scale(0.100000,-0.100000)" fill="currentColor" stroke="none">
              <path d="M2075 9581 c-229 -65 -388 -224 -445 -445 -17 -69 -18 -191 -22
-2927 -3 -2744 -2 -2857 15 -2919 61 -216 235 -385 447 -434 131 -31 272 -12
405 54 143 71 243 189 303 359 15 42 17 219 22 1930 l5 1884 64 -104 c35 -57
103 -167 151 -244 48 -77 106 -171 129 -210 23 -38 127 -207 232 -375 104
-168 201 -325 216 -350 14 -25 65 -107 112 -182 47 -76 128 -206 179 -290 52
-86 115 -176 145 -206 212 -218 576 -229 797 -25 51 47 99 110 155 204 11 19
29 48 40 66 11 17 73 118 138 225 152 247 235 381 272 438 42 64 45 69 93 151
24 41 65 108 92 149 27 41 49 81 49 88 1 6 6 12 11 12 6 0 10 4 10 10 0 9 69
123 90 147 5 7 10 14 10 17 0 2 23 42 52 88 28 46 62 101 75 123 36 61 46 76
76 122 15 23 27 44 27 47 0 2 15 28 33 57 l32 52 5 -1879 c4 -1317 9 -1889 17
-1914 70 -225 162 -327 383 -423 85 -37 129 -38 1200 -34 1133 4 1106 3 1397
62 424 86 791 238 1168 483 93 60 262 185 311 228 172 153 326 305 391 384 15
19 39 48 53 63 22 25 69 88 188 252 80 110 262 446 327 605 29 71 88 245 130
382 31 104 77 335 101 508 25 183 26 637 1 815 -75 529 -221 951 -476 1373
-370 612 -940 1095 -1601 1356 -80 32 -159 64 -177 71 -47 21 -314 92 -429
115 -240 48 -315 52 -997 57 -356 3 -654 2 -662 -1 -12 -4 -6 -17 25 -58 95
-123 162 -314 180 -513 6 -61 9 -218 8 -350 l-3 -240 505 -6 c549 -7 600 -11
828 -70 300 -78 569 -211 791 -392 130 -106 327 -309 394 -407 200 -291 290
-478 367 -766 93 -344 100 -753 18 -1079 -80 -323 -201 -581 -388 -830 -126
-167 -218 -266 -344 -369 -310 -255 -641 -408 -1036 -478 -121 -21 -148 -22
-800 -23 l-675 0 -5 2535 c-5 2370 -6 2539 -22 2592 -53 175 -176 323 -328
396 -68 33 -195 62 -267 62 -88 0 -194 -25 -282 -67 -92 -44 -219 -166 -274
-263 -21 -36 -83 -139 -139 -230 -55 -91 -127 -208 -158 -260 -54 -89 -81
-134 -258 -420 -39 -63 -89 -144 -110 -180 -40 -67 -159 -260 -248 -403 -68
-111 -193 -315 -214 -352 -22 -38 -176 -289 -205 -335 -42 -65 -125 -202 -125
-205 0 -3 -24 -42 -53 -88 -28 -45 -58 -92 -64 -102 -7 -11 -29 -48 -49 -82
l-36 -63 -82 133 c-46 72 -145 233 -221 357 -76 124 -163 266 -195 315 -31 50
-67 108 -80 130 -35 60 -175 288 -240 390 -60 95 -200 322 -240 390 -13 22
-62 103 -110 180 -48 77 -107 174 -132 215 -25 41 -96 158 -158 260 -62 102
-141 233 -174 291 -101 176 -175 253 -310 322 -125 64 -304 84 -431 48z"/>
              <path d="M8270 7151 c-76 -25 -136 -78 -169 -151 -20 -44 -21 -62 -21 -780 l0
-735 24 -50 c43 -94 127 -147 236 -148 75 -1 119 19 310 138 19 12 114 68 210
125 96 56 195 115 220 130 25 15 77 45 115 67 39 22 133 78 210 124 77 46 151
89 165 95 85 39 142 114 160 208 13 70 8 110 -22 171 -29 58 -64 91 -143 137
-38 23 -144 85 -235 138 -91 53 -214 125 -275 160 -60 35 -153 89 -205 120
-213 127 -338 199 -386 223 -54 28 -152 42 -194 28z"/>
            </g>
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
          <router-link
            v-if="isAdmin"
            to="/admin"
            class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
            @click="closeUserMenu"
          >
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h18M3 12h18M3 17h18" />
            </svg>
            Админ-панель
          </router-link>
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
  const perms: string[] = (authStore.permissions as any) || user.permissions || []
  const hasAdminPerm =
    Array.isArray(perms) &&
    perms.some((p) =>
      String(p).startsWith('user_management.user_') ||
      String(p).startsWith('user_management.group_') ||
      String(p).startsWith('permissions.role_')
    )
  return Boolean(
    user.is_staff === true ||
    user.is_superuser === true ||
    user.can_access_admin_panel === true ||
    hasAdminPerm
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
