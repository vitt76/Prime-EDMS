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
          @search="handleSearch"
          @filter-toggle="handleFilterToggle"
          @upload="handleUpload"
          @notifications="handleNotifications"
          @mobile-menu-toggle="handleMobileMenuToggle"
        />
        <Sidebar
          @navigate="handleNavigate"
          @sidebar-toggle="handleSidebarToggle"
          @new-folder="handleNewFolder"
        />
        <MainContent>
          <RouterView />
        </MainContent>
      </template>

      <!-- Simple layout for auth pages -->
      <template v-else>
        <RouterView />
      </template>
    </ErrorBoundary>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import { setupGlobalErrorHandlers, logError } from '@/composables/useErrorBoundary'
import Header from '@/components/Layout/Header.vue'
import Sidebar from '@/components/Layout/Sidebar.vue'
import MainContent from '@/components/Layout/MainContent.vue'
import ErrorBoundary from '@/components/ErrorBoundary.vue'

const route = useRoute()
const authStore = useAuthStore()

const showLayout = computed(() => {
  // Don't show layout on login/home pages
  return route.name !== 'login' && route.name !== 'home'
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
  // TODO: Implement search
  console.log('Search:', query)
}

function handleFilterToggle() {
  // TODO: Toggle filters panel
  console.log('Toggle filters')
}

function handleUpload() {
  // TODO: Open upload modal
  const uiStore = useUIStore()
  uiStore.openModal('upload')
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


