<template>
  <div id="app" class="min-h-screen bg-neutral-0 dark:bg-neutral-0">
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUiStore } from '@/stores/uiStore'
import Header from '@/components/Layout/Header.vue'
import Sidebar from '@/components/Layout/Sidebar.vue'
import MainContent from '@/components/Layout/MainContent.vue'

const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUiStore()

const showLayout = computed(() => {
  // Don't show layout on login/home pages
  return route.name !== 'login' && route.name !== 'home'
})

onMounted(async () => {
  // Check authentication on app mount
  await authStore.checkAuth()
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
  uiStore.openModal('upload')
}

function handleNotifications() {
  // TODO: Open notifications center
  uiStore.openModal('notifications')
}

function handleMobileMenuToggle() {
  uiStore.toggleMobileMenu()
}

function handleNavigate(path: string) {
  // Navigation handled by router-link in Sidebar
}

function handleSidebarToggle() {
  uiStore.toggleSidebar()
}

function handleNewFolder() {
  // TODO: Open create folder modal
  uiStore.openModal('create-folder')
}
</script>

<style scoped>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
}
</style>


