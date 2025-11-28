<template>
  <div class="folder-tree">
    <!-- Section: Системные папки -->
    <div
      v-for="section in folderStore.allSections"
      :key="section.id"
      class="mb-4"
    >
      <!-- Section Header -->
      <button
        class="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold uppercase tracking-wider
               text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200
               hover:bg-neutral-100 dark:hover:bg-neutral-700/50 rounded-lg transition-colors"
        @click="folderStore.toggleSection(section.id)"
      >
        <svg
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
          class="w-4 h-4"
          :class="section.icon === 'cloud' ? 'text-blue-500' : 'text-amber-500'"
        />
        
        <span class="flex-1 text-left">{{ section.name }}</span>
        
        <!-- Folder count -->
        <span class="text-[10px] text-neutral-400 font-normal">
          {{ countFolders(section.folders) }}
        </span>
      </button>
      
      <!-- Section Content -->
      <Transition
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
    
    <!-- Quick Actions -->
    <div class="mt-4 pt-4 border-t border-neutral-200 dark:border-neutral-700">
      <button
        class="w-full flex items-center gap-2 px-3 py-2 text-sm text-neutral-600 dark:text-neutral-400
               hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-700
               rounded-lg transition-colors"
        @click="handleCreateFolder"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>Создать папку</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FolderIcon, CloudIcon } from '@heroicons/vue/24/solid'
import { useFolderStore } from '@/stores/folderStore'
import { useAssetStore } from '@/stores/assetStore'
import FolderTreeNode from './FolderTreeNode.vue'
import type { FolderNode } from '@/mocks/folders'

const emit = defineEmits<{
  folderSelect: [folderId: string]
  createFolder: []
}>()

const folderStore = useFolderStore()
const assetStore = useAssetStore()

function countFolders(folders: FolderNode[]): number {
  let count = folders.length
  for (const folder of folders) {
    count += countFolders(folder.children)
  }
  return count
}

function handleFolderSelect(folderId: string) {
  folderStore.selectFolder(folderId)
  emit('folderSelect', folderId)
}

async function handleDrop(folderId: string, assetIds: number[]) {
  if (assetIds.length === 1) {
    await folderStore.handleAssetDrop(assetIds[0], folderId)
  } else {
    await folderStore.handleBulkAssetDrop(assetIds, folderId)
  }
  
  // Clear selection after drop
  assetStore.clearSelection()
}

function handleCreateFolder() {
  emit('createFolder')
}
</script>

