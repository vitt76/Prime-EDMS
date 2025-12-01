<template>
  <div class="folder-tree">
    <!-- Section: Системные папки -->
    <div
      v-for="section in folderStore.allSections"
      :key="section.id"
      :class="isCollapsed ? 'mb-2' : 'mb-4'"
    >
      <!-- Section Header -->
      <button
        :class="[
          'w-full flex items-center rounded-lg transition-colors',
          isCollapsed 
            ? 'justify-center p-2' 
            : 'gap-2 px-3 py-2 text-xs font-semibold uppercase tracking-wider',
          'text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200',
          'hover:bg-neutral-100 dark:hover:bg-neutral-700/50'
        ]"
        @click="handleSectionClick(section)"
        :title="isCollapsed ? `${section.name} (${countFolders(section.folders)})` : undefined"
      >
        <!-- Chevron (только в развёрнутом режиме) -->
        <svg
          v-if="!isCollapsed"
          class="w-3 h-3 transition-transform duration-200"
          :class="{ 'rotate-90': section.expanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
        
        <!-- Section Icon -->
        <component
          :is="section.icon === 'cloud' ? CloudIcon : FolderIcon"
          :class="[
            isCollapsed ? 'w-5 h-5' : 'w-4 h-4',
            section.icon === 'cloud' ? 'text-blue-500' : 'text-amber-500'
          ]"
        />
        
        <!-- Section Name (только в развёрнутом режиме) -->
        <template v-if="!isCollapsed">
          <span class="flex-1 text-left">{{ section.name }}</span>
          
          <!-- Folder count -->
          <span class="text-[10px] text-neutral-400 font-normal">
            {{ countFolders(section.folders) }}
          </span>
        </template>
      </button>
      
      <!-- Section Content (только в развёрнутом режиме) -->
      <Transition
        v-if="!isCollapsed"
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 max-h-0"
        enter-to-class="opacity-100 max-h-[2000px]"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 max-h-[2000px]"
        leave-to-class="opacity-0 max-h-0"
      >
        <div v-if="section.expanded" class="overflow-hidden">
          <FolderTreeNode
            v-for="folder in section.folders"
            :key="folder.id"
            :folder="folder"
            :depth="0"
            :section-type="section.type"
            @select="handleFolderSelect"
            @drop="handleDrop"
          />
        </div>
      </Transition>
    </div>
    
    <!-- Create Folder Button (только в развёрнутом режиме) -->
    <div 
      v-if="!isCollapsed" 
      class="mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-700"
    >
      <button
        type="button"
        class="w-full flex items-center justify-center gap-2 px-3 py-2.5 
               text-sm font-medium text-neutral-600 dark:text-neutral-300
               bg-neutral-50 dark:bg-neutral-800
               hover:bg-neutral-100 dark:hover:bg-neutral-700
               border border-dashed border-neutral-300 dark:border-neutral-600
               hover:border-primary-400 dark:hover:border-primary-500
               hover:text-primary-600 dark:hover:text-primary-400
               rounded-lg transition-all duration-200"
        @click.stop.prevent="showCreateModal = true"
      >
        <FolderPlusIcon class="w-4 h-4" />
        <span>Создать папку</span>
      </button>
    </div>
    
    <!-- Create Folder Modal -->
    <CreateFolderModal
      :is-open="showCreateModal"
      @close="showCreateModal = false"
      @create="handleCreateFolder"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FolderIcon, CloudIcon } from '@heroicons/vue/24/solid'
import { FolderPlusIcon } from '@heroicons/vue/24/outline'
import { useFolderStore } from '@/stores/folderStore'
import { useAssetStore } from '@/stores/assetStore'
import { useNotificationStore } from '@/stores/notificationStore'
import FolderTreeNode from './FolderTreeNode.vue'
import CreateFolderModal from './CreateFolderModal.vue'
import type { FolderNode, FolderTreeSection } from '@/mocks/folders'

// Props
const props = withDefaults(defineProps<{
  isCollapsed?: boolean
}>(), {
  isCollapsed: false
})

const emit = defineEmits<{
  folderSelect: [folderId: string]
  expandSidebar: []
}>()

const folderStore = useFolderStore()
const assetStore = useAssetStore()
const notificationStore = useNotificationStore()

const showCreateModal = ref(false)

function countFolders(folders: FolderNode[]): number {
  let count = folders.length
  for (const folder of folders) {
    count += countFolders(folder.children)
  }
  return count
}

function handleSectionClick(section: FolderTreeSection) {
  if (props.isCollapsed) {
    // В свёрнутом режиме: разворачиваем sidebar и открываем секцию
    emit('expandSidebar')
    // Небольшая задержка для плавности анимации
    setTimeout(() => {
      if (!section.expanded) {
        folderStore.toggleSection(section.id)
      }
    }, 150)
  } else {
    // В развёрнутом режиме: просто toggle секции
    folderStore.toggleSection(section.id)
  }
}

function handleFolderSelect(folderId: string) {
  folderStore.selectFolder(folderId)
  emit('folderSelect', folderId)
}

async function handleDrop(payload: { folderId: string; assetIds: number[] }) {
  const { folderId, assetIds } = payload
  if (assetIds.length === 1 && assetIds[0] !== undefined) {
    await folderStore.handleAssetDrop(assetIds[0], folderId)
  } else if (assetIds.length > 1) {
    await folderStore.handleBulkAssetDrop(assetIds, folderId)
  }
  
  // Clear selection after drop
  assetStore.clearSelection()
}

async function handleCreateFolder(folderName: string) {
  // Определяем тип папки (по умолчанию 'local')
  const section = folderStore.allSections.find(s => s.expanded) || folderStore.allSections[0]
  const folderType = section?.type || 'local'
  
  // Создаем папку в корне выбранной секции
  const newFolder = await folderStore.createFolder(null, folderName, folderType)
  
  // Закрываем модальное окно
  showCreateModal.value = false
  
  if (newFolder) {
    notificationStore.addNotification({
      type: 'success',
      title: 'Папка создана',
      message: `Папка "${folderName}" успешно создана`,
    })
  }
}
</script>

