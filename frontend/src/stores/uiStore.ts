import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUIStore = defineStore(
  'ui',
  () => {
    // State
    const sidebarExpanded = ref(true)
    const theme = ref<'light' | 'dark' | 'auto'>('light')
    const activeModal = ref<string | null>(null)
    const mobileMenuOpen = ref(false)

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

    // Initialize theme on store creation
    applyTheme()

    return {
      // State
      sidebarExpanded,
      theme,
      activeModal,
      mobileMenuOpen,
      // Getters
      isDarkMode,
      // Actions
      toggleSidebar,
      setTheme,
      applyTheme,
      openModal,
      closeModal,
      toggleMobileMenu
    }
  },
  {
    persist: {
      paths: ['sidebarExpanded', 'theme']
    }
  }
)


