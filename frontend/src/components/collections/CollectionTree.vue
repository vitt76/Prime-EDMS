<template>
  <div class="collection-tree">
    <ul class="collection-tree__list" role="tree" aria-label="Collections tree">
      <li
        v-for="node in collections"
        :key="node.collection.id"
        class="collection-tree__item"
        role="treeitem"
        :aria-expanded="expandedNodes.includes(node.collection.id)"
        :aria-level="node.level + 1"
      >
        <div class="collection-tree__row">
          <!-- Toggle Button -->
          <button
            v-if="node.children.length > 0"
            class="collection-tree__toggle"
            @click="emit('toggle-expand', node.collection.id)"
            :aria-label="`${expandedNodes.includes(node.collection.id) ? 'Collapse' : 'Expand'} ${node.collection.name}`"
            tabindex="0"
            :data-testid="`collection-toggle-${node.collection.id}`"
          >
            <svg
              class="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                v-if="expandedNodes.includes(node.collection.id)"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 9l-7 7-7-7"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>

          <div v-else class="collection-tree__spacer" />

          <!-- Collection Button -->
          <button
            :class="[
              'collection-tree__button',
              {
                'collection-tree__button--active':
                  selectedCollectionId === node.collection.id,
                'collection-tree__button--dragging':
                  draggedCollection?.id === node.collection.id
              }
            ]"
            :draggable="true"
            @click="emit('select', node.collection)"
            @dragstart="handleDragStart($event, node.collection)"
            @dragover.prevent="handleDragOver($event, node.collection)"
            @drop="handleDrop($event, node.collection)"
            @dragend="handleDragEnd"
            @keydown.enter="emit('select', node.collection)"
            @keydown.space.prevent="emit('select', node.collection)"
            @keydown.arrow-left="handleArrowLeft(node)"
            @keydown.arrow-right="handleArrowRight(node)"
            :aria-label="`Collection ${node.collection.name} with ${node.collection.asset_count} assets`"
            :aria-selected="selectedCollectionId === node.collection.id"
            tabindex="0"
            :data-testid="`collection-node-${node.collection.id}`"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
              />
            </svg>
            <span class="collection-tree__name">{{ node.collection.name }}</span>
            <span class="collection-tree__count">{{
              node.collection.asset_count
            }}</span>
          </button>
        </div>

        <!-- Children (recursive) -->
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 max-h-0"
          enter-to-class="opacity-100 max-h-96"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 max-h-96"
          leave-to-class="opacity-0 max-h-0"
        >
          <CollectionTree
            v-if="expandedNodes.includes(node.collection.id) && node.children.length > 0"
            :collections="node.children"
            :expanded-nodes="expandedNodes"
            :selected-collection-id="selectedCollectionId"
            :dragged-collection="draggedCollection"
            class="collection-tree__children"
            @select="emit('select', $event)"
            @toggle-expand="emit('toggle-expand', $event)"
            @drag-start="emit('drag-start', $event)"
            @drop="(target: Collection, parent?: number | null) => emit('drop', target, parent)"
          />
        </Transition>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { CollectionTree as ICollectionTree, Collection } from '@/types/collections'

interface Props {
  collections: ICollectionTree[]
  expandedNodes: number[]
  selectedCollectionId: number | string | null
  draggedCollection: Collection | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  select: [collection: Collection]
  'toggle-expand': [nodeId: number]
  'drag-start': [collection: Collection]
  drop: [targetCollection: Collection, newParentId?: number | null]
}>()

const dragOverNode = ref<number | null>(null)

const handleDragStart = (e: DragEvent, collection: Collection): void => {
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(collection.id))
  }
  emit('drag-start', collection)
}

const handleDragOver = (e: DragEvent, collection: Collection): void => {
  e.preventDefault()
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move'
  }
  dragOverNode.value = collection.id
}

const handleDrop = (e: DragEvent, collection: Collection): void => {
  e.preventDefault()
  e.stopPropagation()
  
  // Determine if dropping on the collection itself (as parent) or as sibling
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const isDroppingOnCollection = e.offsetY < rect.height / 2
  
  emit('drop', collection, isDroppingOnCollection ? collection.id : collection.parent_id)
  dragOverNode.value = null
}

const handleDragEnd = (): void => {
  dragOverNode.value = null
}

const handleArrowLeft = (node: ICollectionTree): void => {
  // Collapse if expanded
  if (props.expandedNodes.includes(node.collection.id)) {
    emit('toggle-expand', node.collection.id)
  }
}

const handleArrowRight = (node: ICollectionTree): void => {
  // Expand if collapsed and has children
  if (
    !props.expandedNodes.includes(node.collection.id) &&
    node.children.length > 0
  ) {
    emit('toggle-expand', node.collection.id)
  }
}
</script>

<style scoped lang="css">
.collection-tree {
  width: 100%;
}

.collection-tree__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.collection-tree__item {
  display: flex;
  flex-direction: column;
  margin: 0;
}

.collection-tree__row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.collection-tree__toggle {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm, 4px);
  transition: all 150ms ease;
  flex-shrink: 0;
}

.collection-tree__toggle:hover {
  background: var(--color-bg-1, #f9fafb);
  color: var(--color-text, #111827);
}

.collection-tree__toggle:focus-visible {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: 2px;
}

.collection-tree__button {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-base, 14px);
  text-align: left;
  transition: all 200ms ease;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  min-width: 0;
}

.collection-tree__button:hover {
  background: var(--color-bg-1, #f9fafb);
  color: var(--color-text, #111827);
}

.collection-tree__button:focus-visible {
  outline: 2px solid var(--color-primary, #3b82f6);
  outline-offset: -2px;
}

.collection-tree__button--active {
  background: var(--color-primary, #3b82f6);
  color: white;
  font-weight: 600;
}

.collection-tree__button--active:hover {
  background: var(--color-primary-dark, #2563eb);
}

.collection-tree__button--dragging {
  opacity: 0.5;
}

.collection-tree__name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.collection-tree__count {
  margin-left: auto;
  font-size: var(--font-size-sm, 12px);
  opacity: 0.7;
  flex-shrink: 0;
}

.collection-tree__children {
  margin-left: 24px;
  border-left: 1px solid var(--color-border, #e5e7eb);
  padding-left: 8px;
  margin-top: 2px;
}

.collection-tree__spacer {
  width: 24px;
  flex-shrink: 0;
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  .collection-tree__button,
  .collection-tree__toggle {
    transition: none;
  }
}
</style>

