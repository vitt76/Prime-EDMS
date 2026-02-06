<template>
  <div id="app" class="min-h-screen bg-neutral-0 dark:bg-neutral-0">
    <ErrorBoundary
      :max-retries="3"
      :auto-retry-delay="5"
      :show-auto-retry="true"
      @error="handleGlobalError"
      @retry="handleRetry"
      @recovered="handleRecovered"
    >
      <!-- Layout for authenticated routes -->
      <template v-if="showLayout">
        <Header
          @filter-toggle="handleFilterToggle"
          @upload="handleUpload"
          @notifications="handleNotifications"
          @mobile-menu-toggle="handleMobileMenuToggle"
        />
        <Sidebar
          @navigate="handleNavigate"
          @sidebar-toggle="handleSidebarToggle"
          @new-folder="handleNewFolder"
          @open-upload="handleUpload"
        />
        <MainContent>
          <RouterView @open-upload="handleUpload" />
        </MainContent>
      </template>

      <!-- Simple layout for auth pages -->
      <template v-else>
        <RouterView />
      </template>
    </ErrorBoundary>
    
    <!-- Global Upload Wizard Modal -->
    <UploadWizard
      :is-open="showUploadWizard"
      @close="handleUploadClose"
      @success="handleUploadSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { setupGlobalErrorHandlers, logError } from '@/composables/useErrorBoundary'
import Header from '@/components/Layout/Header.vue'
import Sidebar from '@/components/Layout/Sidebar.vue'
import MainContent from '@/components/Layout/MainContent.vue'
import ErrorBoundary from '@/components/ErrorBoundary.vue'
import UploadWizard from '@/components/DAM/UploadWizard.vue'
import type { Asset } from '@/types/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const uiStore = useUIStore()

// Upload Wizard state - sync with uiStore
const showUploadWizard = ref(false)

// Sync showUploadWizard with uiStore.activeModal
watch(() => uiStore.activeModal, (modal) => {
  showUploadWizard.value = modal === 'upload'
})

// Sync uiStore when showUploadWizard changes (for close events)
watch(showUploadWizard, (isOpen) => {
  if (!isOpen && uiStore.activeModal === 'upload') {
    uiStore.closeModal()
  }
})

const showLayout = computed(() => {
  // Show layout for all authenticated pages except auth-related pages and admin pages
  const authPages = ['login', 'forgot-password', 'reset-password', 'two-factor-auth']
  
  // Admin pages use their own AdminLayout
  const isAdminRoute = route.path.startsWith('/admin')
  
  // Check if route.name exists, is not an auth page, and is not an admin route
  return route.name && !authPages.includes(route.name as string) && !isAdminRoute
})

onMounted(async () => {
  // Setup global error handlers
  const cleanup = setupGlobalErrorHandlers()

  // Check authentication on app mount
  await authStore.checkAuth()

  // Cleanup on unmount
  return cleanup
})

function handleSearch(query: string) {
  // Search is handled via useDamSearchFilters() inside Header (single source of truth).
}

function handleFilterToggle() {
  // TODO: Toggle filters panel
  console.log('Toggle filters')
}

function handleUpload() {
  showUploadWizard.value = true
}

function handleUploadClose() {
  showUploadWizard.value = false
}

function handleUploadSuccess(assets: Asset[]) {
  console.log('Upload successful:', assets)
  // Notification is already handled in UploadWizard
  showUploadWizard.value = false
}

function handleNotifications() {
  // TODO: Open notifications center
  const uiStore = useUIStore()
  uiStore.openModal('notifications')
}

function handleMobileMenuToggle() {
  const uiStore = useUIStore()
  uiStore.toggleMobileMenu()
}

function handleNavigate(path: string) {
  // Navigation handled by router-link in Sidebar
}

function handleSidebarToggle() {
  const uiStore = useUIStore()
  uiStore.toggleSidebar()
}

function handleNewFolder() {
  // TODO: Open create folder modal
  const uiStore = useUIStore()
  uiStore.openModal('create-folder')
}

// Error Boundary handlers
function handleGlobalError(error: Error, instance: any, info: string) {
  console.error('Global error caught:', { error, instance, info })

  // Log to external services
  logError(error, {
    component: instance?.$?.type?.name,
    info,
    route: route.name,
    path: route.path
  })
}

function handleRetry(attempt: number) {
  console.log(`Retrying operation (attempt ${attempt})`)

  // Refresh current route data if needed
  if (route.name) {
    // Trigger a soft reload of current route
    window.location.reload()
  }
}

function handleRecovered() {
  console.log('Application recovered from error')

  // Clear any cached error state
  // Reset loading states if needed
}
</script>

<style scoped>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
}
</style>


