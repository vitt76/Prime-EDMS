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
      <button
        class="p-1 rounded opacity-0 group-hover:opacity-100 
               hover:bg-neutral-300 dark:hover:bg-neutral-500 transition-all shrink-0"
        @click.stop="showContextMenu"
        title="Действия"
      >
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
        </svg>
      </button>
      
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
          @drop="$emit('drop', $event.folderId, $event.assetIds)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { FolderIcon, CloudIcon, FolderOpenIcon } from '@heroicons/vue/24/solid'
import { useFolderStore } from '@/stores/folderStore'
import { useAssetStore } from '@/stores/assetStore'
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
const folderRef = ref<HTMLElement | null>(null)

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

function showContextMenu(event: MouseEvent) {
  // TODO: Implement context menu
  console.log('Context menu for:', props.folder.name)
}

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
      emit('drop', {
        folderId: props.folder.id,
        assetIds: payload.assetIds,
      })
    }
  } catch (e) {
    console.error('Failed to parse drop data:', e)
  }
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

