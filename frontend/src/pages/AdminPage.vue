<template>
  <div class="admin-page">
    <!-- Breadcrumbs -->
    <Breadcrumbs :items="breadcrumbs" />

    <!-- Admin Navigation Tabs -->
    <AdminNavigationTabs
      :current-tab="currentTab"
      @tab-change="handleTabChange"
    />

    <!-- Content Area -->
    <div class="admin-content">
      <RouterView />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import AdminNavigationTabs from '@/components/admin/AdminNavigationTabs.vue'
import Breadcrumbs from '@/components/Common/Breadcrumbs.vue'

// Hooks
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State
const currentTab = ref<string>('users')

// Computed
const breadcrumbs = computed(() => {
  const items = [
    { label: 'Home', to: '/' },
    { label: 'Administration', to: '/admin' }
  ]

  const tabName = formatTabName(currentTab.value)
  if (tabName) {
    items.push({ label: tabName, to: null })
  }

  return items
})

// Methods
const handleTabChange = async (tabName: string): Promise<void> => {
  currentTab.value = tabName
  await router.push(`/admin/${tabName}`)
}

const formatTabName = (tab: string): string => {
  const names: Record<string, string> = {
    users: 'User Management',
    schemas: 'Metadata Schemas',
    workflows: 'Workflow Designer',
    integrations: 'Integrations',
    reports: 'Reports'
  }
  return names[tab] || tab
}

// Sync tab from route
const syncTabFromRoute = (): void => {
  const pathParts = route.path.split('/').filter(Boolean)
  const tabIndex = pathParts.indexOf('admin')
  if (tabIndex !== -1 && pathParts[tabIndex + 1]) {
    currentTab.value = pathParts[tabIndex + 1]
  } else {
    currentTab.value = 'users'
  }
}

// Watch route changes
watch(
  () => route.path,
  () => {
    syncTabFromRoute()
  },
  { immediate: true }
)

// Lifecycle
onMounted(async () => {
  // Permission check
  if (!authStore.hasPermission.value('admin.access')) {
    await router.push({ name: 'forbidden' })
    return
  }

  // Sync current tab from route
  syncTabFromRoute()
})
</script>

<style scoped>
.admin-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

.admin-content {
  flex: 1;
  padding: 1.5rem;
  background: var(--color-background, #ffffff);
  animation: fadeIn 300ms ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0.95;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .admin-content {
    padding: 1rem;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .admin-content {
    animation: none;
  }
}
</style>



