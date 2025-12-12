<template>
  <div
    class="collection-tree-node"
    :class="{
      'collection-tree-node--selected': isSelected,
      'collection-tree-node--expanded': isExpanded,
      'collection-tree-node--has-children': hasChildren,
      'collection-tree-node--matches-search': matchesSearch
    }"
  >
    <!-- Node Content -->
    <div
      class="collection-tree-node__content"
      :class="{ 'collection-tree-node__content--selected': isSelected }"
      @click="handleSelect"
      @keydown.enter="handleSelect"
      @keydown.space="handleSelect"
      role="treeitem"
      :aria-expanded="hasChildren ? isExpanded : undefined"
      :aria-selected="isSelected"
      tabindex="0"
    >
      <!-- Expand/Collapse Icon -->
      <button
        v-if="hasChildren"
        class="collection-tree-node__expand-btn"
        @click.stop="handleToggleExpand"
        @keydown.enter.stop="handleToggleExpand"
        @keydown.space.stop="handleToggleExpand"
        :aria-label="isExpanded ? 'Collapse' : 'Expand'"
        type="button"
      >
        <svg
          class="w-4 h-4 transition-transform"
          :class="{ 'rotate-90': isExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>

      <!-- Indentation Spacer -->
      <div v-else class="collection-tree-node__spacer"></div>

      <!-- Icon -->
      <div class="collection-tree-node__icon">
        <svg
          v-if="collection.type === 'folder'"
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z" />
        </svg>
        <svg
          v-else
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>

      <!-- Name -->
      <span class="collection-tree-node__name">
        {{ collection.name }}
      </span>

      <!-- Item Count (if available) -->
      <span
        v-if="itemCount !== undefined"
        class="collection-tree-node__count"
      >
        ({{ itemCount }})
      </span>
    </div>

    <!-- Children -->
    <div
      v-if="hasChildren && isExpanded"
      class="collection-tree-node__children"
      role="group"
    >
      <slot />
    </div>

    <!-- Drag Overlay -->
    <div
      v-if="isDragOver"
      class="collection-tree-node__drag-overlay"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
    >
      Drop files here
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Collection Tree Node Component
 *
 * Individual node in the collection tree with expand/collapse,
 * selection, and drag-and-drop support.
 */

import { computed, ref } from 'vue'
import type { Collection } from '@/stores/uploadWorkflowStore'

// Props
const props = defineProps<{
  collection: Collection
  selectedId?: string
  expandedNodes: Set<string>
  searchQuery?: string
  itemCount?: number
  level?: number
}>()

// Emits
const emit = defineEmits<{
  select: [collection: Collection]
  'toggle-expand': [collectionId: string]
  'drag-over': [event: DragEvent, collection: Collection]
  'drag-leave': [event: DragEvent, collection: Collection]
  drop: [event: DragEvent, collection: Collection]
}>()

// Reactive state
const isDragOver = ref(false)

// Computed properties
const isSelected = computed(() => props.selectedId === props.collection.id)

const isExpanded = computed(() => props.expandedNodes.has(props.collection.id))

const hasChildren = computed(() => {
  // This would be determined by checking if there are child collections
  // For now, we'll assume folders have children
  return props.collection.type === 'folder'
})

const matchesSearch = computed(() => {
  if (!props.searchQuery) return false

  const query = props.searchQuery.toLowerCase()
  return props.collection.name.toLowerCase().includes(query) ||
         props.collection.path.some(pathPart => pathPart.toLowerCase().includes(query))
})

const indentLevel = computed(() => props.level || 0)

// Methods
function handleSelect() {
  emit('select', props.collection)
}

function handleToggleExpand() {
  emit('toggle-expand', props.collection.id)
}

function handleDragOver(event: DragEvent) {
  if (canAcceptDrop(event)) {
    event.preventDefault()
    isDragOver.value = true
    emit('drag-over', event, props.collection)
  }
}

function handleDragLeave(event: DragEvent) {
  // Only hide overlay if we're actually leaving the element
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const x = event.clientX
  const y = event.clientY

  if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
    isDragOver.value = false
    emit('drag-leave', event, props.collection)
  }
}

function handleDrop(event: DragEvent) {
  if (canAcceptDrop(event)) {
    event.preventDefault()
    isDragOver.value = false
    emit('drop', event, props.collection)
  }
}

function canAcceptDrop(event: DragEvent): boolean {
  // Check if the dragged items can be dropped on this collection
  // For now, allow drops on folders and collections
  return props.collection.type === 'folder' || props.collection.type === 'collection'
}
</script>

<style scoped>
.collection-tree-node {
  @apply select-none;
}

.collection-tree-node__content {
  @apply flex items-center px-2 py-1 rounded-md cursor-pointer transition-colors;
  @apply hover:bg-neutral-100 dark:hover:bg-neutral-700;
  padding-left: calc(1rem + var(--indent-level, 0) * 1.5rem);
}

.collection-tree-node__content--selected {
  @apply bg-primary-100 dark:bg-primary-900/20 text-primary-900 dark:text-primary-100;
}

.collection-tree-node__expand-btn {
  @apply w-6 h-6 flex items-center justify-center rounded hover:bg-neutral-200 dark:hover:bg-neutral-600 mr-1;
  @apply focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1;
}

.collection-tree-node__spacer {
  @apply w-6 mr-1;
}

.collection-tree-node__icon {
  @apply w-5 h-5 mr-2 text-neutral-500 dark:text-neutral-400 flex-shrink-0;
}

.collection-tree-node__name {
  @apply flex-1 text-sm font-medium text-neutral-900 dark:text-neutral-100 truncate;
}

.collection-tree-node__count {
  @apply text-xs text-neutral-500 dark:text-neutral-400 ml-2 flex-shrink-0;
}

.collection-tree-node__children {
  @apply ml-4;
}

.collection-tree-node__drag-overlay {
  @apply absolute inset-0 bg-primary-500 bg-opacity-20 border-2 border-primary-500 border-dashed rounded-md;
  @apply flex items-center justify-center text-primary-700 dark:text-primary-300 font-medium;
  pointer-events: none;
  z-index: 10;
}

/* Highlight search matches */
.collection-tree-node--matches-search .collection-tree-node__name {
  @apply bg-yellow-200 dark:bg-yellow-900/30;
}

/* Focus styles */
.collection-tree-node__content:focus {
  @apply outline-none ring-2 ring-primary-500 ring-offset-1;
}

/* Drag styles */
.collection-tree-node--has-children {
  position: relative;
}

.collection-tree-node--has-children .collection-tree-node__content {
  @apply relative;
}

/* Animation for expand/collapse */
.collection-tree-node__children {
  animation: slide-down 0.2s ease-out;
}

@keyframes slide-down {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Mobile adjustments */
@media (max-width: 640px) {
  .collection-tree-node__content {
    @apply py-2;
    padding-left: calc(0.75rem + var(--indent-level, 0) * 1.25rem);
  }

  .collection-tree-node__name {
    @apply text-base;
  }
}
</style>


















