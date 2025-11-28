<template>
  <aside
    :class="[
      'fixed left-0 top-16 bottom-0 bg-neutral-0 dark:bg-neutral-0 border-r border-neutral-300 dark:border-neutral-300 transition-all duration-300 ease-in-out z-40 overflow-y-auto',
      isExpanded ? 'w-70' : 'w-16'
    ]"
  >
    <!-- Toggle Button -->
    <button
      class="absolute top-4 right-2 p-2 text-neutral-600 dark:text-neutral-600 hover:bg-neutral-100 dark:hover:bg-neutral-100 rounded-md transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
      @click="toggleSidebar"
      :aria-label="isExpanded ? 'Свернуть боковую панель' : 'Развернуть боковую панель'"
      :aria-expanded="isExpanded"
      type="button"
    >
      <svg
        class="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          v-if="isExpanded"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
        />
        <path
          v-else
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M13 5l7 7-7 7M5 5l7 7-7 7"
        />
      </svg>
    </button>

    <!-- Navigation -->
    <nav class="pt-16 px-2">
      <ul class="space-y-1">
        <li v-for="item in navigationItems" :key="item.path">
          <router-link
            :to="item.path"
            :class="[
              'flex items-center gap-3 px-3 py-2 rounded-md transition-colors',
              isActive(item.path)
                ? 'bg-primary-50 dark:bg-primary-50 text-primary-600 dark:text-primary-600'
                : 'text-neutral-600 dark:text-neutral-600 hover:bg-neutral-100 dark:hover:bg-neutral-100'
            ]"
            @click="handleNavigate(item.path)"
          >
            <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
            <span v-if="isExpanded" class="text-sm font-medium">
              {{ item.label }}
            </span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Collections Section (Quick Links) -->
    <div v-if="isExpanded" class="mt-6 px-2">
      <div class="flex items-center justify-between px-3 mb-2">
        <h3 class="text-xs font-semibold text-neutral-500 dark:text-neutral-500 uppercase tracking-wider">
          Коллекции
        </h3>
      </div>
      <ul class="space-y-0.5">
        <li v-for="collection in collections" :key="collection.id">
          <router-link
            :to="collection.path"
            :class="[
              'flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors text-sm',
              isActive(collection.path)
                ? 'bg-primary-50 dark:bg-primary-50 text-primary-600 dark:text-primary-600'
                : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700/50'
            ]"
          >
            <component :is="collection.icon" class="w-4 h-4 flex-shrink-0" />
            <span>{{ collection.label }}</span>
          </router-link>
        </li>
      </ul>
    </div>

    <!-- File Structure Section with FolderTree -->
    <div v-if="isExpanded" class="mt-6 px-2">
      <FolderTree 
        @folder-select="handleFolderSelect"
        @create-folder="handleNewFolder"
      />
    </div>

    <!-- Quick Actions -->
    <div class="mt-auto px-2 pb-4 space-y-2">
      <!-- Upload Button - Primary Action -->
      <button
        class="w-full flex items-center justify-center gap-3 px-3 py-3 
               bg-gradient-to-r from-primary-600 to-primary-500 text-white rounded-xl 
               hover:from-primary-700 hover:to-primary-600 
               transition-all duration-200 min-h-[48px]
               shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30"
        @click="handleUpload"
        type="button"
        aria-label="Загрузить файлы"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        <span v-if="isExpanded" class="text-sm font-semibold">Загрузить</span>
      </button>
      
      <!-- New Folder Button - Secondary Action -->
      <button
        class="w-full flex items-center justify-center gap-3 px-3 py-2.5 
               bg-neutral-100 text-neutral-700 rounded-lg 
               hover:bg-neutral-200 transition-colors min-h-[44px]"
        @click="handleNewFolder"
        type="button"
        aria-label="Создать новую папку"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"
          />
        </svg>
        <span v-if="isExpanded" class="text-sm font-medium">Новая папка</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIStore } from '@/stores/uiStore'
import { useFolderStore } from '@/stores/folderStore'
import FolderTree from '@/components/FolderTree.vue'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()
const folderStore = useFolderStore()

// Initialize folder store on mount
onMounted(() => {
  // Folders are already loaded from mock data, no need to refresh
  // folderStore.refreshFolders()
})

const isExpanded = computed(() => uiStore.sidebarExpanded)

// Icon components (можно заменить на @heroicons/vue)
const DashboardIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  `
}

const DAMIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  `
}

const DistributionIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
    </svg>
  `
}

const SettingsIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  `
}

const UploadIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
  `
}

const HeartIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  `
}

const ClockIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `
}

const ShareIcon = {
  template: `
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
    </svg>
  `
}

const navigationItems = [
  { path: '/', label: 'Dashboard', icon: DashboardIcon },
  { path: '/dam', label: 'DAM Gallery', icon: DAMIcon },
  { path: '/sharing', label: 'Распространение', icon: DistributionIcon },
  { path: '/settings', label: 'Настройки', icon: SettingsIcon }
]

const collections = [
  { id: 1, path: '/dam/my-uploads', label: 'Мои загрузки', icon: UploadIcon },
  { id: 2, path: '/dam/favorites', label: 'Избранное', icon: HeartIcon },
  { id: 3, path: '/dam/recent', label: 'Недавние', icon: ClockIcon },
  { id: 4, path: '/dam/shared', label: 'Доступные мне', icon: ShareIcon }
]

function toggleSidebar() {
  uiStore.toggleSidebar()
}

function isActive(path: string): boolean {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleNavigate(path: string) {
  emit('navigate', path)
}

function handleNewFolder() {
  emit('new-folder')
}

function handleUpload() {
  emit('open-upload')
}

function handleFolderSelect(folderId: string) {
  // Navigate to DAM gallery with folder filter
  router.push({
    path: '/dam',
    query: { folder: folderId }
  })
}

const emit = defineEmits<{
  navigate: [path: string]
  'sidebar-toggle': []
  'new-folder': []
  'open-upload': []
}>()
</script>

<style scoped>
.w-70 {
  width: 280px;
}
</style>

