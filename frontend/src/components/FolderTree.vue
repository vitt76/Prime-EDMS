<template>
  <div class="folder-tree">
    <div
      v-if="folderStore.isLoading"
      class="px-3 py-2 text-xs text-neutral-400"
    >
      Загрузка системных папок...
    </div>

    <!-- Create Folder Button (только для системных папок, в развёрнутом режиме) -->
    <button
      v-if="!isCollapsed && currentSection?.type === 'local'"
      type="button"
      class="w-full flex items-center justify-center gap-2 px-3 py-2.5 
             text-sm font-medium text-neutral-600 dark:text-neutral-300
             bg-neutral-50 dark:bg-neutral-800
             hover:bg-neutral-100 dark:hover:bg-neutral-700
             border border-dashed border-neutral-300 dark:border-neutral-600
             hover:border-primary-400 dark:hover:border-primary-500
             hover:text-primary-600 dark:hover:text-primary-400
             rounded-lg transition-all duration-200"
      :disabled="folderStore.isLoading"
      :class="{
        'opacity-60 cursor-not-allowed': folderStore.isLoading
      }"
      @click.stop.prevent="showCreateModal = true"
    >
      <FolderPlusIcon class="w-4 h-4" />
      <span>Создать папку</span>
    </button>

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
    
    <!-- Create Folder Modal -->
    <CreateFolderModal
      :is-open="showCreateModal"
      :parent-options="parentOptions"
      :selected-parent-id="folderStore.selectedFolder?.type === 'local' ? folderStore.selectedFolder.id : null"
      @close="showCreateModal = false"
      @create="handleCreateFolder"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
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
const currentSection = ref<FolderTreeSection | null>(null)
const parentOptions = ref<{ id: string; label: string }[]>([])

onMounted(async () => {
  await folderStore.refreshFolders()
  currentSection.value = folderStore.allSections[0] || null
  parentOptions.value = buildParentOptions(folderStore.systemFolders)
})

watch(
  () => folderStore.systemFolders,
  (val) => {
    parentOptions.value = buildParentOptions(val)
  },
  { deep: true }
)

function countFolders(folders: FolderNode[]): number {
  let count = folders.length
  for (const folder of folders) {
    count += countFolders(folder.children)
  }
  return count
}

function handleSectionClick(section: FolderTreeSection) {
  currentSection.value = section
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

function buildParentOptions(folders: FolderNode[], prefix = ''): { id: string; label: string }[] {
  const result: { id: string; label: string }[] = []
  folders.forEach(folder => {
    const label = prefix ? `${prefix} / ${folder.name}` : folder.name
    result.push({ id: folder.id, label })
    if (folder.children?.length) {
      result.push(...buildParentOptions(folder.children, label))
    }
  })
  return result
}

async function handleCreateFolder(folderName: string, parentId: string | null) {

  // Создаем папку (только системные папки)
  const newFolder = await folderStore.createFolder(parentId, folderName, 'local')
  
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

