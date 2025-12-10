<template>
  <div class="admin-layout min-h-screen bg-gray-50">
    <!-- ═══════════════════════════════════════════════════════════════════════
         MOBILE OVERLAY
         ═══════════════════════════════════════════════════════════════════════ -->
    <Transition name="fade">
      <div
        v-if="isMobileMenuOpen"
        class="fixed inset-0 bg-black/50 z-40 lg:hidden"
        @click="isMobileMenuOpen = false"
      />
    </Transition>

    <!-- ═══════════════════════════════════════════════════════════════════════
         SIDEBAR — Dark Theme Navigation
         ═══════════════════════════════════════════════════════════════════════ -->
    <aside
      :class="[
        'fixed top-0 left-0 bottom-0 z-50 flex flex-col bg-gray-900 border-r border-gray-800 transition-all duration-300 ease-in-out',
        // Desktop behavior
        'lg:translate-x-0',
        isSidebarCollapsed ? 'lg:w-16' : 'lg:w-64',
        // Mobile behavior
        isMobileMenuOpen ? 'translate-x-0 w-64' : '-translate-x-full w-64'
      ]"
    >
      <!-- Brand Header -->
      <div class="h-16 flex items-center justify-between px-4 border-b border-gray-800">
        <router-link
          to="/admin"
          class="flex items-center gap-3 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 focus:ring-offset-gray-900 rounded-lg"
          @click="isMobileMenuOpen = false"
        >
          <div class="w-8 h-8 bg-gradient-to-br from-violet-500 to-fuchsia-600 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg shadow-violet-500/25">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <span
            v-if="!isSidebarCollapsed || isMobileMenuOpen"
            class="font-semibold text-white tracking-tight"
          >
            MADDAM Admin
          </span>
        </router-link>

        <!-- Collapse Toggle (Desktop) -->
        <button
          v-if="(!isSidebarCollapsed || isMobileMenuOpen)"
          type="button"
          class="hidden lg:flex p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500"
          @click="toggleSidebar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>

        <!-- Close Button (Mobile) -->
        <button
          type="button"
          class="lg:hidden p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500"
          @click="isMobileMenuOpen = false"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <template v-for="item in navigationItems" :key="item.path || item.label">
          <!-- Section Divider -->
          <div
            v-if="item.divider"
            class="pt-4 pb-2"
          >
            <span
              v-if="!isSidebarCollapsed || isMobileMenuOpen"
              class="px-3 text-[10px] font-semibold text-gray-500 uppercase tracking-wider"
            >
              {{ item.label }}
            </span>
            <div v-else class="h-px bg-gray-800 mx-2" />
          </div>

          <!-- Nav Item -->
          <router-link
            v-else
            :to="item.path"
            :class="[
              'group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
              'focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-1 focus:ring-offset-gray-900',
              isActive(item.path)
                ? 'bg-gray-800 text-white shadow-sm'
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
            ]"
            :title="(isSidebarCollapsed && !isMobileMenuOpen) ? item.label : undefined"
            @click="isMobileMenuOpen = false"
          >
            <component
              :is="item.icon"
              :class="[
                'w-5 h-5 flex-shrink-0 transition-colors',
                isActive(item.path) ? 'text-violet-400' : 'text-gray-500 group-hover:text-gray-300'
              ]"
            />
            <span v-if="!isSidebarCollapsed || isMobileMenuOpen">{{ item.label }}</span>
            
            <!-- Badge -->
            <span
              v-if="item.badge && (!isSidebarCollapsed || isMobileMenuOpen)"
              :class="[
                'ml-auto px-2 py-0.5 text-xs font-medium rounded-full',
                item.badgeType === 'error'
                  ? 'bg-red-500/20 text-red-400'
                  : item.badgeType === 'warning'
                  ? 'bg-amber-500/20 text-amber-400'
                  : 'bg-violet-500/20 text-violet-400'
              ]"
            >
              {{ item.badge }}
            </span>
          </router-link>
        </template>
      </nav>

      <!-- Bottom Section -->
      <div class="border-t border-gray-800 p-3 space-y-2">
        <!-- Expand Button (Desktop, when collapsed) -->
        <button
          v-if="isSidebarCollapsed && !isMobileMenuOpen"
          type="button"
          class="hidden lg:flex w-full p-2.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors items-center justify-center focus:outline-none focus:ring-2 focus:ring-violet-500"
          @click="toggleSidebar"
          title="Развернуть панель"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
          </svg>
        </button>

        <!-- Back to App Button -->
        <router-link
          to="/dam"
          :class="[
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
            'text-gray-400 hover:text-white bg-gray-800/50 hover:bg-gray-800',
            'focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-1 focus:ring-offset-gray-900',
            (isSidebarCollapsed && !isMobileMenuOpen) ? 'justify-center' : ''
          ]"
          :title="(isSidebarCollapsed && !isMobileMenuOpen) ? 'Вернуться в приложение' : undefined"
          @click="isMobileMenuOpen = false"
        >
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 15l-3-3m0 0l3-3m-3 3h8M3 12a9 9 0 1118 0 9 9 0 01-18 0z" />
          </svg>
          <span v-if="!isSidebarCollapsed || isMobileMenuOpen">Вернуться в приложение</span>
        </router-link>
      </div>
    </aside>

    <!-- ═══════════════════════════════════════════════════════════════════════
         MAIN CONTENT AREA
         ═══════════════════════════════════════════════════════════════════════ -->
    <main
      :class="[
        'min-h-screen transition-all duration-300',
        // Desktop margin
        isSidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64',
        // Mobile: no margin (sidebar is overlay)
        'ml-0'
      ]"
    >
      <!-- Top Header Bar -->
      <header class="sticky top-0 z-30 h-14 sm:h-16 bg-white/95 backdrop-blur-sm border-b border-gray-200 flex items-center justify-between px-4 sm:px-6 shadow-sm">
        <!-- Left: Hamburger + Breadcrumb -->
        <div class="flex items-center gap-3">
          <!-- Mobile Menu Toggle -->
          <button
            type="button"
            class="lg:hidden p-2 -ml-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500"
            @click="isMobileMenuOpen = true"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Breadcrumb -->
          <div class="flex items-center gap-2 text-sm">
            <span class="hidden sm:inline text-gray-400">Admin</span>
            <svg class="hidden sm:block w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="font-medium text-gray-900">{{ currentPageTitle }}</span>
          </div>
        </div>

        <!-- Right Actions -->
        <div class="flex items-center gap-2 sm:gap-3">
          <!-- System Status Indicator (hidden on mobile) -->
          <div class="hidden md:flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
            <span
              :class="[
                'w-2 h-2 rounded-full animate-pulse',
                systemHealthy ? 'bg-emerald-500' : 'bg-red-500'
              ]"
            />
            <span class="text-xs font-medium text-gray-600">
              {{ systemHealthy ? 'Системы OK' : 'Проблемы' }}
            </span>
          </div>

          <!-- Quick Actions -->
          <button
            type="button"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-violet-500"
            title="Уведомления"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>

          <!-- Admin User Menu -->
          <div class="relative" ref="userMenuRef">
            <button
              type="button"
              class="flex items-center gap-2 pl-2 sm:pl-3 border-l border-gray-200 hover:bg-gray-50 rounded-lg transition-colors"
              @click="toggleUserMenu"
              :aria-expanded="isUserMenuOpen"
            >
              <div class="w-8 h-8 bg-gradient-to-br from-violet-500 to-fuchsia-600 rounded-full flex items-center justify-center text-white text-sm font-medium shadow-md shadow-violet-500/20">
                {{ userInitials }}
              </div>
              <div class="hidden xl:block text-left">
                <p class="text-sm font-medium text-gray-900">{{ userName }}</p>
                <p class="text-xs text-gray-500">{{ userEmail }}</p>
              </div>
            </button>

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
                <div class="px-4 py-3 border-b border-gray-100">
                  <p class="text-sm font-medium text-gray-900">{{ userName }}</p>
                  <p class="text-xs text-gray-500 truncate">{{ userEmail }}</p>
                </div>
                <button
                  type="button"
                  class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  @click="goTo('/settings/profile')"
                >
                  <span class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-xs font-semibold">P</span>
                  <span>Профиль</span>
                </button>
                <button
                  type="button"
                  class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  @click="goTo('/settings')"
                >
                  <span class="w-8 h-8 rounded-lg bg-gray-100 text-gray-700 flex items-center justify-center text-xs font-semibold">S</span>
                  <span>Настройки</span>
                </button>
                <div class="border-t border-gray-100 my-1" />
                <button
                  type="button"
                  class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  @click="handleLogout"
                >
                  <span class="w-8 h-8 rounded-lg bg-red-50 text-red-600 flex items-center justify-center text-xs font-semibold">Выйти</span>
                  <span>Выйти</span>
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="p-4 sm:p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const isSidebarCollapsed = ref(false)
const isMobileMenuOpen = ref(false)
const systemHealthy = ref(true)

// Close mobile menu on resize to desktop
function handleResize() {
  if (window.innerWidth >= 1024) {
    isMobileMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// ═══════════════════════════════════════════════════════════════════════════════
// Icons (Inline SVG Components)
// ═══════════════════════════════════════════════════════════════════════════════
const DashboardIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z' })
    ])
  }
}

const UsersIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' })
    ])
  }
}

const MetadataIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4' })
    ])
  }
}

const WorkflowIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' })
    ])
  }
}

const AIIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' })
    ])
  }
}

const SourcesIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' })
    ])
  }
}

const HealthIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' })
    ])
  }
}

const LogsIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
    ])
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Navigation Config
// ═══════════════════════════════════════════════════════════════════════════════
interface NavItem {
  path?: string
  label: string
  icon?: ReturnType<typeof h>
  badge?: string | number
  badgeType?: 'default' | 'warning' | 'error'
  divider?: boolean
}

const StorageIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4' })
    ])
  }
}

const navigationItems: NavItem[] = [
  { path: '/admin', label: 'Обзор', icon: DashboardIcon },
  { divider: true, label: 'Управление' },
  { path: '/admin/users', label: 'Пользователи', icon: UsersIcon },
  { path: '/admin/metadata', label: 'Метаданные', icon: MetadataIcon },
  { path: '/admin/workflows', label: 'Рабочие процессы', icon: WorkflowIcon },
  { divider: true, label: 'Система' },
  { path: '/admin/sources', label: 'Источники', icon: SourcesIcon },
  { path: '/admin/storage', label: 'Хранилище S3', icon: StorageIcon },
  { path: '/admin/ai-logs', label: 'AI-обработка', icon: AIIcon, badge: 3, badgeType: 'error' },
  { path: '/admin/health', label: 'Мониторинг', icon: HealthIcon },
  { path: '/admin/logs', label: 'Логи', icon: LogsIcon },
]

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const currentPageTitle = computed(() => {
  const item = navigationItems.find(i => i.path === route.path)
  return item?.label ?? 'Панель управления'
})

const userInitials = computed(() => {
  const user = authStore.user
  if (!user) return 'A'
  return (user.first_name || user.username || 'A').charAt(0).toUpperCase()
})

const userName = computed(() => {
  const user = authStore.user
  if (!user) return 'Admin'
  return user.first_name && user.last_name
    ? `${user.first_name} ${user.last_name}`
    : user.username || 'Admin'
})
const userEmail = computed(() => authStore.user?.email || 'user@example.com')

const isUserMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function isActive(path: string): boolean {
  return route.path === path || (path !== '/admin' && route.path.startsWith(path))
}

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

function toggleUserMenu() {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

function closeUserMenu() {
  isUserMenuOpen.value = false
}

function goTo(path: string) {
  closeUserMenu()
  router.push(path)
}

async function handleLogout() {
  await authStore.logout()
  closeUserMenu()
}
</script>

<style scoped>
.admin-layout {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Fade transition for overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
