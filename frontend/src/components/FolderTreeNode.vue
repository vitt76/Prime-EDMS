<template>
  <div class="folder-tree-node">
    <!-- Folder Item -->
    <div
      ref="folderRef"
      class="group relative flex items-center gap-1 py-1 pr-2 rounded-lg cursor-pointer
             transition-all duration-150"
      :class="[
        // Indentation based on depth
        indentClass,
        // Selection state
        isSelected
          ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
          : 'hover:bg-neutral-100 dark:hover:bg-neutral-700/50 text-neutral-700 dark:text-neutral-300',
        // Drag over state
        isDragOver && 'ring-2 ring-primary-500 bg-blue-100 dark:bg-blue-900/30',
      ]"
      :draggable="false"
      @click="handleClick"
      @dragenter.prevent="handleDragEnter"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @drop.prevent="handleDropEvent"
    >
      <!-- Expand/Collapse Arrow -->
      <button
        v-if="folder.children.length > 0"
        class="p-1 rounded hover:bg-neutral-200 dark:hover:bg-neutral-600 transition-colors shrink-0"
        @click.stop="toggleExpand"
      >
        <svg
          class="w-3 h-3 transition-transform duration-200"
          :class="{ 'rotate-90': folder.expanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
      <span v-else class="w-5 shrink-0"></span>
      
      <!-- Folder Icon -->
      <component
        :is="folderIcon"
        class="w-4 h-4 shrink-0"
        :class="iconColorClass"
      />
      
      <!-- Folder Name -->
      <span class="flex-1 text-sm truncate" :title="folder.name">
        {{ folder.name }}
      </span>
      
      <!-- Asset Count Badge -->
      <span
        v-if="folder.assetCount > 0"
        class="text-[10px] px-1.5 py-0.5 rounded-full bg-neutral-200 dark:bg-neutral-600 
               text-neutral-600 dark:text-neutral-300 shrink-0"
      >
        {{ formatCount(folder.assetCount) }}
      </span>
      
      <!-- Options Button (on hover) -->
      <div ref="menuRef" class="relative shrink-0">
        <button
          class="p-1 rounded opacity-0 group-hover:opacity-100 
                 hover:bg-neutral-300 dark:hover:bg-neutral-500 transition-all"
          @click.stop="toggleContextMenu"
          title="Действия"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
          </svg>
        </button>
        
        <!-- Context Menu -->
        <Teleport to="body">
          <Transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="showMenu && sectionType === 'local' && folder.canDelete"
              ref="contextMenuRef"
              class="fixed bg-white dark:bg-neutral-800 rounded-lg shadow-lg border border-neutral-200 dark:border-neutral-700 py-1 z-[60] min-w-[160px]"
              :style="contextMenuStyle"
              @click.stop
            >
              <button
                class="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
                @click="handleDelete"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Удалить
              </button>
            </div>
          </Transition>
        </Teleport>
      </div>
      
      <!-- Drop Indicator Line -->
      <div
        v-if="isDragOver"
        class="absolute inset-0 border-2 border-primary-500 border-dashed rounded-lg pointer-events-none"
      />
    </div>
    
    <!-- Children (Recursive) -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 max-h-0"
      enter-to-class="opacity-100 max-h-[2000px]"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 max-h-[2000px]"
      leave-to-class="opacity-0 max-h-0"
    >
      <div v-if="folder.expanded && folder.children.length > 0" class="overflow-hidden">
        <FolderTreeNode
          v-for="child in folder.children"
          :key="child.id"
          :folder="child"
          :depth="depth + 1"
          :section-type="sectionType"
          @select="$emit('select', $event)"
          @drop="handleChildDrop"
        />
      </div>
    </Transition>
    
    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/60" @click="showDeleteModal = false" />
          <div class="relative w-full max-w-md bg-white dark:bg-neutral-800 rounded-2xl shadow-xl p-6">
            <h3 class="text-lg font-semibold text-neutral-900 dark:text-white mb-4">Удалить папку?</h3>
            <p class="text-sm text-neutral-600 dark:text-neutral-400 mb-6">
              Папка "<strong>{{ folder.name }}</strong>" будет удалена. 
              <span v-if="folder.assetCount > 0">
                Все документы из этой папки ({{ folder.assetCount }}) будут перемещены на корневой уровень.
              </span>
            </p>
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-neutral-700 dark:text-neutral-300 bg-neutral-100 dark:bg-neutral-700 rounded-xl hover:bg-neutral-200 dark:hover:bg-neutral-600 transition-colors"
                @click="showDeleteModal = false"
              >
                Отмена
              </button>
              <button
                type="button"
                class="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-red-600 rounded-xl hover:bg-red-700 transition-colors"
                @click="confirmDelete"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { FolderIcon, CloudIcon, FolderOpenIcon } from '@heroicons/vue/24/solid'
import { useFolderStore } from '@/stores/folderStore'
import { useAssetStore } from '@/stores/assetStore'
import { useNotificationStore } from '@/stores/notificationStore'
import type { FolderNode, FolderSource } from '@/mocks/folders'

interface Props {
  folder: FolderNode
  depth: number
  sectionType: FolderSource
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [folderId: string]
  drop: [payload: { folderId: string; assetIds: number[] }]
}>()

const folderStore = useFolderStore()
const assetStore = useAssetStore()
const notificationStore = useNotificationStore()
const folderRef = ref<HTMLElement | null>(null)
const showMenu = ref(false)
const showDeleteModal = ref(false)
const menuRef = ref<HTMLElement | null>(null)
const contextMenuRef = ref<HTMLElement | null>(null)
const contextMenuStyle = ref<{ top: string; left: string }>({ top: '0px', left: '0px' })

// ============================================================================
// COMPUTED
// ============================================================================

const isSelected = computed(() => folderStore.isFolderSelected(props.folder.id))

const isDragOver = computed(() => folderStore.isFolderDragOver(props.folder.id))

const indentClass = computed(() => {
  const indents = [
    'pl-2',    // depth 0
    'pl-6',    // depth 1
    'pl-10',   // depth 2
    'pl-14',   // depth 3
    'pl-18',   // depth 4
    'pl-22',   // depth 5
  ]
  return indents[Math.min(props.depth, indents.length - 1)]
})

const folderIcon = computed(() => {
  if (props.sectionType === 'yandex') {
    return CloudIcon
  }
  return props.folder.expanded ? FolderOpenIcon : FolderIcon
})

const iconColorClass = computed(() => {
  if (props.sectionType === 'yandex') {
    return 'text-blue-500'
  }
  return props.folder.expanded ? 'text-amber-400' : 'text-amber-500'
})

// ============================================================================
// METHODS
// ============================================================================

function formatCount(count: number): string {
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'K'
  }
  return count.toString()
}

function handleClick() {
  emit('select', props.folder.id)
}

function toggleExpand() {
  folderStore.toggleFolder(props.folder.id)
}

function toggleContextMenu(event: MouseEvent) {
  event.stopPropagation()
  
  if (!showMenu.value) {
    // Calculate position for context menu
    const button = event.currentTarget as HTMLElement
    const rect = button.getBoundingClientRect()
    
    // Position menu below the button, aligned to the right
    const menuWidth = 160 // min-w-[160px]
    const menuHeight = 40 // approximate height
    const spacing = 4 // mt-1
    
    let left = rect.right - menuWidth
    let top = rect.bottom + spacing
    
    // Check if menu would go off screen to the right
    if (left < 0) {
      left = rect.left
    }
    
    // Check if menu would go off screen to the bottom
    if (top + menuHeight > window.innerHeight) {
      top = rect.top - menuHeight - spacing
    }
    
    contextMenuStyle.value = {
      top: `${top}px`,
      left: `${left}px`
    }
  }
  
  showMenu.value = !showMenu.value
}

function handleDelete() {
  showMenu.value = false
  if (props.sectionType !== 'local' || !props.folder.canDelete) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Удаление запрещено',
      message: 'Эту папку нельзя удалить'
    })
    return
  }
  showDeleteModal.value = true
}

async function confirmDelete() {
  showDeleteModal.value = false
  
  try {
    const success = await folderStore.deleteFolder(props.folder.id)
    if (success) {
      notificationStore.addNotification({
        type: 'success',
        title: 'Папка удалена',
        message: `Папка "${props.folder.name}" удалена. Документы перемещены на корневой уровень.`
      })
    }
  } catch (error: any) {
    console.error('Failed to delete folder:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось удалить папку'
    })
  }
}

// Close menu when clicking outside
function handleClickOutside(event: MouseEvent) {
  const target = event.target as Node
  if (
    menuRef.value && 
    !menuRef.value.contains(target) &&
    contextMenuRef.value &&
    !contextMenuRef.value.contains(target)
  ) {
    showMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

// ============================================================================
// DRAG & DROP HANDLERS
// ============================================================================

function handleDragEnter(event: DragEvent) {
  if (!event.dataTransfer) return
  if (props.sectionType !== 'local' || !props.folder.canAddChildren) return
  
  // Check if dragging assets
  if (event.dataTransfer.types.includes('application/json')) {
    folderStore.setDragOver(props.folder.id)
  }
}

function handleDragOver(event: DragEvent) {
  if (!event.dataTransfer) return
  if (props.sectionType !== 'local' || !props.folder.canAddChildren) return
  
  // Indicate this is a valid drop target
  if (event.dataTransfer.types.includes('application/json')) {
    event.dataTransfer.dropEffect = 'move'
    folderStore.setDragOver(props.folder.id)
  }
}

function handleDragLeave(event: DragEvent) {
  // Only clear if leaving the folder element completely
  const related = event.relatedTarget as HTMLElement | null
  if (!folderRef.value?.contains(related)) {
    folderStore.setDragOver(null)
  }
}

function handleDropEvent(event: DragEvent) {
  folderStore.setDragOver(null)
  
  if (!event.dataTransfer) return
  if (props.sectionType !== 'local' || !props.folder.canAddChildren) return
  
  try {
    const data = event.dataTransfer.getData('application/json')
    if (!data) return
    
    const payload = JSON.parse(data)
    
    if (payload.type === 'asset' && payload.assetIds) {
      // Убеждаемся, что assetIds является массивом
      // Обрабатываем случаи, когда assetIds может быть числом или массивом
      let assetIds: number[] = []
      
      if (Array.isArray(payload.assetIds)) {
        assetIds = payload.assetIds
      } else if (typeof payload.assetIds === 'number') {
        // Если передан один ID как число, преобразуем в массив
        assetIds = [payload.assetIds]
      } else if (payload.assetIds !== null && payload.assetIds !== undefined) {
        // Попытка преобразовать в массив, если это возможно
        assetIds = [Number(payload.assetIds)].filter(id => !isNaN(id))
      }
      
      if (assetIds.length > 0) {
        emit('drop', {
          folderId: props.folder.id,
          assetIds: assetIds,
        })
      }
    }
  } catch (e) {
    console.error('Failed to parse drop data:', e)
  }
}

function handleChildDrop(event: { folderId: string; assetIds: number[] }) {
  // Проксируем событие drop от дочернего компонента
  emit('drop', event)
}
</script>

<style scoped>
/* Custom indentation classes for deeper nesting */
.pl-18 {
  padding-left: 4.5rem;
}
.pl-22 {
  padding-left: 5.5rem;
}
</style>

