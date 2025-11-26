<template>
  <div class="collection-step">
    <div class="collection-step__header">
      <h2 class="collection-step__title">Choose Collection</h2>
      <p class="collection-step__description">
        Organize your files by assigning them to a collection or creating a new one.
      </p>
    </div>

    <!-- Search and Actions -->
    <div class="collection-step__toolbar">
      <div class="collection-step__search">
        <input
          type="text"
          placeholder="Search collections..."
          class="collection-step__search-input"
          v-model="searchQuery"
          @input="debouncedSearch"
        />
        <svg class="collection-step__search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <Button
        variant="outline"
        size="sm"
        @click="showCreateModal = true"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Collection
      </Button>
    </div>

    <!-- Collection Tree -->
    <div class="collection-step__tree-container">
      <div
        v-if="isLoading"
        class="collection-step__loading"
      >
        <Spinner size="lg" />
        <p>Loading collections...</p>
      </div>

      <div
        v-else-if="filteredCollections.length === 0 && !searchQuery"
        class="collection-step__empty"
      >
        <svg class="w-16 h-16 text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <h3 class="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
          No collections yet
        </h3>
        <p class="text-neutral-600 dark:text-neutral-400 mb-4">
          Create your first collection to organize your files.
        </p>
        <Button @click="showCreateModal = true">
          Create Collection
        </Button>
      </div>

      <div
        v-else-if="filteredCollections.length === 0 && searchQuery"
        class="collection-step__empty"
      >
        <svg class="w-16 h-16 text-neutral-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <h3 class="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
          No collections found
        </h3>
        <p class="text-neutral-600 dark:text-neutral-400">
          Try a different search term or create a new collection.
        </p>
      </div>

      <div
        v-else
        class="collection-step__tree"
        role="tree"
        aria-label="Collections"
      >
        <CollectionTreeNode
          v-for="collection in filteredCollections"
          :key="collection.id"
          :collection="collection"
          :selected-id="selectedCollection?.id"
          :expanded-nodes="expandedNodes"
          :search-query="searchQuery"
          @select="handleSelect"
          @toggle-expand="handleToggleExpand"
          @drag-over="handleDragOver"
          @drop="handleDrop"
        />
      </div>
    </div>

    <!-- Selected Collection Info -->
    <div
      v-if="selectedCollection"
      class="collection-step__selected-info"
    >
      <div class="collection-step__selected-header">
        <svg class="w-5 h-5 text-primary-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <span class="font-medium">Selected: {{ selectedCollection.name }}</span>
      </div>

      <div class="collection-step__selected-path">
        <span class="text-sm text-neutral-600 dark:text-neutral-400">
          Path: {{ getCollectionPath(selectedCollection) }}
        </span>
      </div>
    </div>

    <!-- Step Controls -->
    <div class="collection-step__controls">
      <Button
        variant="outline"
        @click="$emit('back')"
      >
        Back
      </Button>

      <Button
        variant="primary"
        @click="handleContinue"
        :disabled="!selectedCollection"
      >
        Continue to Share
      </Button>
    </div>

    <!-- Create Collection Modal -->
    <Modal
      :is-open="showCreateModal"
      title="Create New Collection"
      @close="showCreateModal = false"
    >
      <form @submit.prevent="handleCreateCollection" class="space-y-4">
        <div>
          <label for="collection-name" class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
            Collection Name
          </label>
          <input
            id="collection-name"
            type="text"
            required
            class="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:placeholder-neutral-400"
            placeholder="Enter collection name"
            v-model="newCollectionName"
          />
        </div>

        <div>
          <label for="parent-collection" class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
            Parent Collection (Optional)
          </label>
          <select
            id="parent-collection"
            class="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600"
            v-model="newCollectionParent"
          >
            <option value="">Root Level</option>
            <option
              v-for="collection in collections"
              :key="collection.id"
              :value="collection.id"
            >
              {{ collection.name }}
            </option>
          </select>
        </div>

        <div class="flex justify-end space-x-3">
          <Button
            type="button"
            variant="outline"
            @click="showCreateModal = false"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            :loading="isCreating"
          >
            Create Collection
          </Button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup lang="ts">
/**
 * Collection Step Component
 *
 * Allows users to select an existing collection or create a new one.
 * Features efficient tree rendering, search, and drag-and-drop support.
 */

import { ref, computed, onMounted, watch } from 'vue'
import { debounce } from 'lodash-es'
import Button from '@/components/Common/Button.vue'
import Spinner from '@/components/Common/Spinner.vue'
import Modal from '@/components/Common/Modal.vue'
import CollectionTreeNode from '@/components/workflow/CollectionTreeNode.vue'
import { useUploadWorkflowStore, type Collection } from '@/stores/uploadWorkflowStore'
import { collectionService } from '@/services/collectionsService'

// Props
const props = defineProps<{
  selectedCollection: Collection | null
}>()

// Emits
const emit = defineEmits<{
  'update:selected-collection': [collection: Collection | null]
  complete: []
  back: []
  error: [error: string]
}>()

// Composables
const workflowStore = useUploadWorkflowStore()

// Reactive state
const collections = ref<Collection[]>([])
const expandedNodes = ref<Set<string>>(new Set())
const searchQuery = ref('')
const filteredCollections = ref<Collection[]>([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const newCollectionName = ref('')
const newCollectionParent = ref('')
const isCreating = ref(false)

// Computed properties
const selectedCollection = computed({
  get: () => props.selectedCollection,
  set: (value) => emit('update:selected-collection', value)
})

// Debounced search function
const debouncedSearch = debounce(() => {
  filterCollections()
}, 300)

// Methods
async function loadCollections() {
  isLoading.value = true
  try {
    const data = await collectionService.getCollections({ include_tree: true })
    collections.value = flattenCollections(data)
    filteredCollections.value = [...collections.value]

    // Auto-expand root level collections
    collections.value.forEach(collection => {
      if (!collection.parentId) {
        expandedNodes.value.add(collection.id)
      }
    })
  } catch (error: any) {
    emit('error', error.message || 'Failed to load collections')
  } finally {
    isLoading.value = false
  }
}

function flattenCollections(treeData: any[]): Collection[] {
  const result: Collection[] = []

  function traverse(nodes: any[], path: string[] = []) {
    nodes.forEach(node => {
      const collection: Collection = {
        id: node.id,
        name: node.name,
        path: [...path],
        type: node.type || 'folder',
        parentId: node.parent_id
      }

      result.push(collection)

      if (node.children && node.children.length > 0) {
        traverse(node.children, [...path, node.name])
      }
    })
  }

  traverse(treeData)
  return result
}

function filterCollections() {
  if (!searchQuery.value.trim()) {
    filteredCollections.value = [...collections.value]
    return
  }

  const query = searchQuery.value.toLowerCase()
  filteredCollections.value = collections.value.filter(collection =>
    collection.name.toLowerCase().includes(query) ||
    collection.path.some(pathPart => pathPart.toLowerCase().includes(query))
  )

  // Auto-expand nodes that match search
  const matchingIds = new Set(filteredCollections.value.map(c => c.id))
  expandedNodes.value.clear()

  filteredCollections.value.forEach(collection => {
    // Expand all ancestors of matching nodes
    let currentId = collection.parentId
    while (currentId) {
      expandedNodes.value.add(currentId)
      const parent = collections.value.find(c => c.id === currentId)
      currentId = parent?.parentId
    }
  })
}

function handleSelect(collection: Collection) {
  selectedCollection.value = collection
}

function handleToggleExpand(collectionId: string) {
  if (expandedNodes.value.has(collectionId)) {
    expandedNodes.value.delete(collectionId)
  } else {
    expandedNodes.value.add(collectionId)
  }
}

function handleDragOver(event: DragEvent, collection: Collection) {
  // Allow drop if it's a valid target
  if (collection.type === 'folder' || collection.type === 'collection') {
    event.preventDefault()
  }
}

function handleDrop(event: DragEvent, collection: Collection) {
  // Handle drag and drop of files to collections
  // This would integrate with the file upload workflow
  event.preventDefault()
  console.log('Dropped files on collection:', collection.name)
}

async function handleCreateCollection() {
  if (!newCollectionName.value.trim()) return

  isCreating.value = true
  try {
    const newCollection = await collectionService.createCollection({
      name: newCollectionName.value.trim(),
      parent_id: newCollectionParent.value || null
    })

    // Add to collections list
    const collection: Collection = {
      id: newCollection.id,
      name: newCollection.name,
      path: newCollectionParent.value ?
        collections.value.find(c => c.id === newCollectionParent.value)?.path || [] : [],
      type: 'folder',
      parentId: newCollectionParent.value || undefined
    }

    collections.value.push(collection)
    filterCollections()

    // Reset form
    newCollectionName.value = ''
    newCollectionParent.value = ''
    showCreateModal.value = false

  } catch (error: any) {
    emit('error', error.message || 'Failed to create collection')
  } finally {
    isCreating.value = false
  }
}

function getCollectionPath(collection: Collection): string {
  if (collection.path.length === 0) return collection.name
  return [...collection.path, collection.name].join(' / ')
}

function handleContinue() {
  if (selectedCollection.value) {
    emit('complete')
  }
}

// Watch for search query changes
watch(searchQuery, () => {
  debouncedSearch()
})

// Load collections on mount
onMounted(() => {
  loadCollections()
})
</script>

<style scoped>
.collection-step {
  @apply space-y-6;
}

.collection-step__header {
  @apply text-center mb-8;
}

.collection-step__title {
  @apply text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2;
}

.collection-step__description {
  @apply text-neutral-600 dark:text-neutral-400;
}

.collection-step__toolbar {
  @apply flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between;
}

.collection-step__search {
  @apply relative flex-1 max-w-md;
}

.collection-step__search-input {
  @apply w-full pl-10 pr-4 py-2 border border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:border-neutral-600 dark:placeholder-neutral-400 dark:focus:ring-primary-600 dark:focus:border-primary-600;
}

.collection-step__search-icon {
  @apply absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-neutral-400;
}

.collection-step__tree-container {
  @apply min-h-96 border border-neutral-200 dark:border-neutral-700 rounded-lg;
}

.collection-step__loading {
  @apply flex flex-col items-center justify-center h-96 text-neutral-600 dark:text-neutral-400;
}

.collection-step__empty {
  @apply flex flex-col items-center justify-center h-96 text-center p-8;
}

.collection-step__tree {
  @apply p-4 max-h-96 overflow-y-auto;
}

.collection-step__selected-info {
  @apply bg-primary-50 dark:bg-primary-900/10 border border-primary-200 dark:border-primary-800 rounded-lg p-4;
}

.collection-step__selected-header {
  @apply flex items-center text-primary-900 dark:text-primary-100 font-medium mb-1;
}

.collection-step__selected-path {
  @apply text-sm;
}

.collection-step__controls {
  @apply flex justify-between pt-6 border-t border-neutral-200 dark:border-neutral-700;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .collection-step__toolbar {
    @apply flex-col items-stretch;
  }

  .collection-step__search {
    @apply max-w-none;
  }

  .collection-step__controls {
    @apply flex-col space-y-4;
  }

  .collection-step__tree-container {
    @apply min-h-64;
  }

  .collection-step__tree {
    @apply max-h-64;
  }
}
</style>
