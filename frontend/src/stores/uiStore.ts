import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Breadcrumb {
  label: string
  path: string
}

export const useUIStore = defineStore(
  'ui',
  () => {
    // State
    const sidebarExpanded = ref(true)
    const theme = ref<'light' | 'dark' | 'auto'>('light')
    const activeModal = ref<string | null>(null)
    const mobileMenuOpen = ref(false)
    const breadcrumbs = ref<Breadcrumb[]>([])
    const notifications = ref<any[]>([])

    // Getters
    const isDarkMode = computed(() => {
      if (theme.value === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      return theme.value === 'dark'
    })

    // Actions
    function toggleSidebar() {
      sidebarExpanded.value = !sidebarExpanded.value
    }

    function setTheme(newTheme: 'light' | 'dark' | 'auto') {
      theme.value = newTheme
      applyTheme()
    }

    function applyTheme() {
      const isDark = isDarkMode.value
      if (isDark) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }

    function openModal(modalName: string) {
      activeModal.value = modalName
    }

    function closeModal() {
      activeModal.value = null
    }

    function toggleMobileMenu() {
      mobileMenuOpen.value = !mobileMenuOpen.value
    }

    function setBreadcrumbs(crumbs: Breadcrumb[]) {
      breadcrumbs.value = crumbs
    }

    function addNotification(notification: any) {
      notifications.value.unshift(notification)
      // Auto-remove after 5 seconds
      setTimeout(() => {
        const index = notifications.value.indexOf(notification)
        if (index !== -1) {
          notifications.value.splice(index, 1)
        }
      }, 5000)
    }

    function removeNotification(notification: any) {
      const index = notifications.value.indexOf(notification)
      if (index !== -1) {
        notifications.value.splice(index, 1)
      }
    }

    // Initialize theme on store creation
    applyTheme()

    return {
      // State
      sidebarExpanded,
      theme,
      activeModal,
      mobileMenuOpen,
      breadcrumbs,
      notifications,
      // Getters
      isDarkMode,
      // Actions
      toggleSidebar,
      setTheme,
      applyTheme,
      openModal,
      closeModal,
      toggleMobileMenu,
      setBreadcrumbs,
      addNotification,
      removeNotification
    }
  },
  {
    persist: {
      paths: ['sidebarExpanded', 'theme']
    }
  }
)


