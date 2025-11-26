# 🎨 PHASE 2: USER FEATURES - ПОЛНЫЕ ПРОМПТЫ (STEP 12-17)

**Версия:** 2.0 (Phase 2 - User Features)  
**Дата:** 27 Января 2025  
**Статус:** ✅ Готово для Cursor AI  
**Предусловие:** Phase 1 (Admin Module) ✅ ЗАВЕРШЕНА

---

## 📋 STEP 12-17 OVERVIEW

| Шаг | Компонент | Тип | Файлы | Тесты | Время |
|-----|-----------|------|-------|-------|-------|
| 12 | Collections | Store | 1 type + 1 store | 15+ | 1ч |
| 13 | CollectionsPage | UI | 1 page + 2 comp | 20+ | 1.5ч |
| 14 | Reports (Architecture) | Store | 1 type + 1 store | 15+ | 1ч |
| 15 | ReportsPage | UI | 1 page + charts | 25+ | 1.5ч |
| 16 | Distribution Detail | UI | 1 page | 15+ | 1ч |
| 17 | Distribution Public | UI | 1 page | 12+ | 1ч |
| **TOTAL** | | | **8 файлов** | **102+ тесты** | **7.5ч** |

---

# STEP 12: Collections Store + Types

**Зависимости:** Phase 1 ✅ complete (adminStore pattern)  
**Время:** 1 час  
**Output:** 2 файла (types, store)

---

## ПРОМПТ 12: Collections Architecture + Store

```
You are a senior frontend architect with 20+ years experience designing enterprise DAM systems.

TASK: Create Collections module types and Pinia store (like Bynder Collections or Canto Albums)

Context:
- Existing: Pinia pattern from adminStore, TypeScript strict
- Reference: DAM-Frontend-Enhancement-TZ.md section "Collections Management"
- Pattern: Collections are hierarchical (nested folders) with drag-drop support
- Features: Private/Shared/Public visibility, Smart collections (dynamic), Favorites

---

## PHASE 1: Collection Types

File: src/types/collections.ts

Interfaces needed:

1. Collection (base interface)
   Fields: id, name, description, parent_id (nullable), is_favorite, is_shared, 
           visibility ('private'|'shared'|'public'), asset_count, created_by, 
           created_at, updated_at, cover_image_id (nullable)

2. CollectionWithAssets extends Collection
   Fields: assets (Asset[] - for detail view)

3. CreateCollectionRequest
   Fields: name, description, parent_id (nullable), visibility

4. UpdateCollectionRequest (partial)
   Fields: name?, description?, visibility?, is_favorite?

5. MoveCollectionRequest
   Fields: collection_id, new_parent_id (nullable)

6. BulkCollectionOperation
   Fields: ids (number[]), action ('delete'|'move'|'share'|'export')

7. SpecialCollection extends Collection
   Fields: type: 'favorites'|'recent'|'my_uploads'|'shared_with_me'|'public_collections'

8. CollectionTree (hierarchical view)
   Fields: collection: Collection, children: CollectionTree[], level: number

9. GetCollectionsParams
   Fields: page?, page_size?, parent_id?, search?, sort_by?, include_shared?, visibility?

10. PaginatedCollections
    Fields: count, next, previous, results (Collection[])

Requirements:
✓ All interfaces exported
✓ Discriminated unions for collection types (normal vs special)
✓ JSDoc comments for complex fields
✓ No optional fields unless explicitly optional
✓ Validation constraints (name: min 1, max 255)

---

## PHASE 2: Collections Store

File: src/stores/collectionsStore.ts

Store Pattern: Composition API (like adminStore)

State (using ref):
- collections: Ref<Collection[]> = ref([])
- currentCollection: Ref<Collection | null> = ref(null)
- collectionsTree: Ref<CollectionTree[]> = ref([])
- selectedCollections: Ref<number[]> = ref([])
- favorites: Ref<Collection[]> = ref([])
- recentCollections: Ref<Collection[]> = ref([])
- sharedWithMe: Ref<Collection[]> = ref([])
- isLoading: Ref<boolean> = ref(false)
- error: Ref<string | null> = ref(null)
- lastFetchTime: Ref<number | null> = ref(null)
- expandedNodes: Ref<Set<number>> = ref(new Set())
- draggedCollection: Ref<Collection | null> = ref(null)

Computed:
- rootCollections: compute collections where parent_id is null
- breadcrumbs(collectionId): return path from root to collection
- canCreateCollection: checks permission
- canDeleteCollection: checks permission
- flattenedTree: flatten tree for search/filter

Actions (async):
1. fetchCollections(params?: GetCollectionsParams)
   - endpoint: GET /api/v4/collections/
   - cache: 5 minute TTL
   - build tree structure after fetch
   - set collections, collectionsTree

2. fetchCollection(id: number)
   - endpoint: GET /api/v4/collections/{id}/
   - include assets count
   - set currentCollection

3. createCollection(data: CreateCollectionRequest)
   - endpoint: POST /api/v4/collections/
   - optimistic update: add to tree
   - return Collection

4. updateCollection(id: number, data: UpdateCollectionRequest)
   - endpoint: PUT /api/v4/collections/{id}/
   - update in collections array

5. deleteCollection(id: number)
   - endpoint: DELETE /api/v4/collections/{id}/
   - also delete children (or option to move)
   - remove from tree

6. moveCollection(fromId: number, toId: number, newParentId?: number)
   - endpoint: POST /api/v4/collections/{fromId}/move/
   - body: { new_parent_id: newParentId }
   - update tree structure

7. bulkCollectionOperation(operation: BulkCollectionOperation)
   - endpoint: POST /api/v4/collections/bulk/
   - validate ids.length <= 50

8. toggleFavorite(id: number)
   - endpoint: POST /api/v4/collections/{id}/toggle-favorite/
   - update in favorites array

9. fetchSpecialCollections()
   - endpoint: GET /api/v4/collections/special/
   - set favorites, recentCollections, sharedWithMe

10. expandNode(nodeId: number)
    - update expandedNodes Set

11. toggleNodeExpanded(nodeId: number)
    - add/remove from expandedNodes

12. setDraggedCollection(collection: Collection | null)
    - for drag-drop tracking

13. buildCollectionTree(collections: Collection[])
    - internal: convert flat array to tree structure
    - return CollectionTree[]

Helper computed for sorting tree by name alphabetically.

Persist Configuration:
- persist: { paths: ['expandedNodes'] }
  Only remember expanded nodes, not data (security)

---

## PHASE 3: Collections Service

File: src/services/collectionsService.ts

Class CollectionsService methods:

1. getCollections(params?: GetCollectionsParams): Promise<PaginatedCollections>
   - endpoint: GET /api/v4/collections/
   - use apiService.get()

2. getCollection(id: number): Promise<CollectionWithAssets>
   - endpoint: GET /api/v4/collections/{id}/
   - include assets and metadata

3. createCollection(data: CreateCollectionRequest): Promise<Collection>
   - endpoint: POST /api/v4/collections/
   - validate name not empty

4. updateCollection(id: number, data: UpdateCollectionRequest): Promise<Collection>
   - endpoint: PUT /api/v4/collections/{id}/

5. deleteCollection(id: number): Promise<void>
   - endpoint: DELETE /api/v4/collections/{id}/

6. moveCollection(id: number, data: MoveCollectionRequest): Promise<Collection>
   - endpoint: POST /api/v4/collections/{id}/move/

7. bulkOperation(operation: BulkCollectionOperation): Promise<BulkOperationResponse>
   - endpoint: POST /api/v4/collections/bulk/

8. toggleFavorite(id: number): Promise<Collection>
   - endpoint: POST /api/v4/collections/{id}/toggle-favorite/

9. getSpecialCollections(): Promise<{favorites, recent, shared, public}>
   - endpoint: GET /api/v4/collections/special/

export const collectionsService = new CollectionsService()

Requirements:
✓ All methods use apiService
✓ Type-safe return values
✓ Error handling delegated to apiService
✓ No duplicate logic from store

---

TEST COVERAGE:
- collectionsStore: 15+ unit tests (fetch, create, move, tree building)
- collectionsService: 10+ unit tests (API methods)
- types: 5+ tests (discriminated unions)

ACCEPTANCE CRITERIA:
☐ All types properly defined and exported
☐ Store uses Composition API (ref/computed)
☐ Tree building logic works correctly
☐ Cache TTL implemented (5 minutes)
☐ Drag-drop state managed (draggedCollection)
☐ Expanded nodes persisted across sessions
☐ Special collections fetched separately
☐ Breadcrumb computation works
☐ No TypeScript errors (strict mode)
☐ All async operations have error handling

OUTPUT:
Generate these 3 files:
1. src/types/collections.ts (complete types)
2. src/stores/collectionsStore.ts (complete store)
3. src/services/collectionsService.ts (complete service)

All production-ready, no TODOs.
```

---

# STEP 13: CollectionsPage + Components

**Зависимости:** Step 12 (collectionsStore)  
**Время:** 1.5 часа  
**Output:** 3 файла (page + 2 компонента)

---

## ПРОМПТ 13: CollectionsPage + CollectionTree + CreateCollectionModal

```
You are a senior Vue 3 frontend architect with expertise in complex tree UI patterns.

TASK: Create CollectionsPage with hierarchical tree view and drag-drop support

Context:
- Page: /collections (main user view)
- Features: Hierarchical tree, drag-drop move, inline editing, favorites, special collections
- Pattern: Composition API + TypeScript
- Design: Modern, accessible (WCAG 2.1 AA)
- Reference: Bynder Collections UI, Canto Albums

---

## FILE 1: src/pages/CollectionsPage.vue

Layout:
- Left sidebar: Collection tree (draggable, expandable)
- Right main: Collection assets grid or detail view
- Top toolbar: Actions (Create, Rename, Delete, Share)

<template>
  <div class="collections-page">
    <MainLayout>
      <template #sidebar>
        <!-- Collections Tree with Special Collections -->
        <div class="collections-sidebar">
          <!-- Special Collections (Favorites, Recent, etc.) -->
          <div class="special-collections">
            <button
              v-for="special in specialCollections"
              :key="special.type"
              :class="['special-collections__item', { 'special-collections__item--active': currentCollectionId === special.id }]"
              @click="selectCollection(special)"
            >
              <i :class="['icon', getSpecialIcon(special.type)]" />
              {{ special.name }}
              <span class="special-collections__count">{{ special.asset_count }}</span>
            </button>
          </div>

          <!-- Divider -->
          <div class="collections-sidebar__divider" />

          <!-- Collections Tree -->
          <CollectionTree
            :collections="collectionsTree"
            :expanded-nodes="expandedNodes"
            :selected-collection-id="currentCollectionId"
            :dragged-collection="draggedCollection"
            @select="handleSelectCollection"
            @toggle-expand="handleToggleExpand"
            @drag-start="handleDragStart"
            @drop="handleDrop"
          />
        </div>
      </template>

      <template #content>
        <!-- Toolbar -->
        <div class="collections-toolbar">
          <!-- Breadcrumbs -->
          <Breadcrumbs :items="breadcrumbs" />

          <!-- Actions -->
          <div class="collections-toolbar__actions">
            <Button variant="primary" @click="showCreateModal = true">
              <i class="icon icon-plus" /> New Collection
            </Button>

            <Button
              v-if="currentCollection"
              variant="secondary"
              @click="showRenameModal = true"
            >
              <i class="icon icon-edit" /> Rename
            </Button>

            <Button
              v-if="currentCollection"
              variant="secondary"
              @click="toggleFavorite"
            >
              <i :class="['icon', currentCollection.is_favorite ? 'icon-star-filled' : 'icon-star']" />
            </Button>

            <Button
              v-if="currentCollection && !isSpecialCollection"
              variant="secondary"
              @click="showDeleteModal = true"
            >
              <i class="icon icon-trash" /> Delete
            </Button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!currentCollection" class="collections-empty">
          <p>Select a collection to view assets</p>
        </div>

        <!-- Assets Grid (if collection selected) -->
        <div v-else class="collections-content">
          <!-- Header -->
          <div class="collections-header">
            <h2>{{ currentCollection.name }}</h2>
            <p class="collections-header__description">{{ currentCollection.description }}</p>
            <span class="collections-header__count">
              {{ currentCollection.asset_count }} assets
            </span>
          </div>

          <!-- Assets Grid (lazy load when scrolling down) -->
          <AssetGrid
            :collection-id="currentCollection.id"
            @asset-click="handleAssetClick"
          />
        </div>
      </template>
    </MainLayout>

    <!-- Modals -->
    <CreateCollectionModal
      v-if="showCreateModal"
      :parent-id="currentCollection?.id"
      @submit="handleCreateCollection"
      @close="showCreateModal = false"
    />

    <RenameCollectionModal
      v-if="showRenameModal && currentCollection"
      :collection="currentCollection"
      @submit="handleRenameCollection"
      @close="showRenameModal = false"
    />

    <DeleteConfirmModal
      v-if="showDeleteModal && currentCollection"
      :title="`Delete collection: ${currentCollection.name}`"
      :message="'This will move all assets to parent collection'"
      @confirm="handleDeleteCollection"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useCollectionsStore } from '@/stores/collectionsStore'
import { useUIStore } from '@/stores/uiStore'
import MainLayout from '@/components/Layout/MainLayout.vue'
import CollectionTree from '@/components/collections/CollectionTree.vue'
import Breadcrumbs from '@/components/Common/Breadcrumbs.vue'
import Button from '@/components/Common/Button.vue'
import AssetGrid from '@/components/gallery/AssetGrid.vue'
import CreateCollectionModal from '@/components/modals/CreateCollectionModal.vue'
import RenameCollectionModal from '@/components/modals/RenameCollectionModal.vue'
import DeleteConfirmModal from '@/components/modals/DeleteConfirmModal.vue'
import type { Collection } from '@/types/collections'

// Hooks
const router = useRouter()
const authStore = useAuthStore()
const collectionsStore = useCollectionsStore()
const uiStore = useUIStore()

// State
const currentCollectionId = ref<number | null>(null)
const showCreateModal = ref(false)
const showRenameModal = ref(false)
const showDeleteModal = ref(false)
const isLoading = ref(false)

// Computed
const collectionsTree = computed(() => collectionsStore.collectionsTree)
const currentCollection = computed(() => collectionsStore.currentCollection)
const expandedNodes = computed(() => Array.from(collectionsStore.expandedNodes))
const draggedCollection = computed(() => collectionsStore.draggedCollection)
const specialCollections = computed(() => {
  const collections: Collection[] = []
  if (collectionsStore.favorites.length) {
    collections.push({
      id: 'favorites' as any,
      name: '⭐ Favorites',
      description: '',
      parent_id: null,
      is_favorite: false,
      is_shared: false,
      visibility: 'private',
      asset_count: collectionsStore.favorites.length,
      created_by: authStore.user?.id || 0,
      created_at: '',
      updated_at: '',
      cover_image_id: null,
      type: 'favorites' as any
    })
  }
  // Add recent, shared_with_me, public_collections
  return collections
})

const isSpecialCollection = computed(() => {
  return currentCollection.value?.id && typeof currentCollection.value.id === 'string'
})

const breadcrumbs = computed(() => {
  if (!currentCollectionId.value) return [{ label: 'Collections', to: '/collections' }]
  
  const items: any[] = [{ label: 'Collections', to: '/collections' }]
  // Build breadcrumb path from root to current
  // Use collectionsStore.breadcrumbs(currentCollectionId.value)
  return items
})

// Methods
const fetchCollections = async () => {
  isLoading.value = true
  try {
    await collectionsStore.fetchCollections()
    await collectionsStore.fetchSpecialCollections()
    // Select first root collection by default
    const firstRoot = collectionsStore.rootCollections[0]
    if (firstRoot) {
      await selectCollection(firstRoot)
    }
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to load collections',
      duration: 5000
    })
  } finally {
    isLoading.value = false
  }
}

const handleSelectCollection = async (collection: Collection) => {
  currentCollectionId.value = collection.id
  await collectionsStore.fetchCollection(collection.id)
}

const selectCollection = (collection: Collection) => {
  handleSelectCollection(collection)
}

const handleToggleExpand = (nodeId: number) => {
  collectionsStore.toggleNodeExpanded(nodeId)
}

const handleDragStart = (collection: Collection) => {
  collectionsStore.setDraggedCollection(collection)
}

const handleDrop = async (collection: Collection, newParentId: number | null) => {
  const draggedId = collectionsStore.draggedCollection?.id
  if (!draggedId) return
  
  try {
    await collectionsStore.moveCollection(draggedId, collection.id, newParentId)
    uiStore.addNotification({
      type: 'success',
      message: 'Collection moved successfully',
      duration: 3000
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to move collection',
      duration: 5000
    })
  } finally {
    collectionsStore.setDraggedCollection(null)
  }
}

const toggleFavorite = async () => {
  if (!currentCollection.value) return
  try {
    await collectionsStore.toggleFavorite(currentCollection.value.id)
    uiStore.addNotification({
      type: 'success',
      message: currentCollection.value.is_favorite ? 'Removed from favorites' : 'Added to favorites',
      duration: 3000
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to toggle favorite',
      duration: 5000
    })
  }
}

const handleCreateCollection = async (data: any) => {
  try {
    await collectionsStore.createCollection({
      ...data,
      parent_id: currentCollection.value?.id || null
    })
    showCreateModal.value = false
    uiStore.addNotification({
      type: 'success',
      message: 'Collection created successfully',
      duration: 3000
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to create collection',
      duration: 5000
    })
  }
}

const handleRenameCollection = async (data: any) => {
  if (!currentCollection.value) return
  try {
    await collectionsStore.updateCollection(currentCollection.value.id, data)
    showRenameModal.value = false
    uiStore.addNotification({
      type: 'success',
      message: 'Collection renamed successfully',
      duration: 3000
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to rename collection',
      duration: 5000
    })
  }
}

const handleDeleteCollection = async () => {
  if (!currentCollection.value) return
  try {
    await collectionsStore.deleteCollection(currentCollection.value.id)
    showDeleteModal.value = false
    currentCollectionId.value = null
    uiStore.addNotification({
      type: 'success',
      message: 'Collection deleted successfully',
      duration: 3000
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to delete collection',
      duration: 5000
    })
  }
}

const handleAssetClick = (assetId: number) => {
  router.push({ name: 'asset-detail', params: { id: assetId } })
}

const getSpecialIcon = (type: string): string => {
  const icons: Record<string, string> = {
    'favorites': 'icon-star',
    'recent': 'icon-clock',
    'my_uploads': 'icon-upload',
    'shared_with_me': 'icon-share',
    'public_collections': 'icon-globe'
  }
  return icons[type] || 'icon-folder'
}

// Lifecycle
onMounted(async () => {
  await fetchCollections()
})
</script>

<style scoped lang="css">
.collections-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-background);
}

.collections-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  max-height: calc(100vh - 80px);
  overflow-y: auto;
}

.special-collections {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.special-collections__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-base);
  font-size: var(--font-size-base);
  transition: all 200ms ease;
  text-align: left;
}

.special-collections__item:hover {
  background: var(--color-bg-1);
  color: var(--color-text);
}

.special-collections__item--active {
  background: var(--color-bg-1);
  color: var(--color-primary);
  font-weight: 600;
}

.special-collections__count {
  margin-left: auto;
  font-size: var(--font-size-sm);
  opacity: 0.7;
}

.collections-sidebar__divider {
  height: 1px;
  background: var(--color-border);
  margin: 8px 0;
}

.collections-toolbar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.collections-toolbar__actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.collections-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}

.collections-content {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.collections-header {
  margin-bottom: 32px;
}

.collections-header h2 {
  margin: 0 0 8px 0;
  font-size: var(--font-size-3xl);
  color: var(--color-text);
}

.collections-header__description {
  margin: 0 0 8px 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.collections-header__count {
  display: inline-block;
  padding: 4px 8px;
  background: var(--color-bg-1);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Responsive */
@media (max-width: 1024px) {
  .collections-sidebar {
    max-height: 300px;
  }
}

@media (max-width: 768px) {
  .collections-toolbar {
    flex-direction: column;
  }

  .collections-toolbar__actions {
    flex-direction: column;
  }

  .collections-toolbar__actions button {
    width: 100%;
  }
}
</style>

---

## FILE 2: src/components/collections/CollectionTree.vue

Hierarchical tree component with:
- Expandable/collapsible nodes
- Drag-drop support
- Keyboard navigation (arrow keys)
- ARIA labels for accessibility
- Inline rename capability

<template>
  <div class="collection-tree">
    <ul class="collection-tree__list" role="tree">
      <li
        v-for="node in collections"
        :key="node.collection.id"
        class="collection-tree__item"
        role="treeitem"
        :aria-expanded="expandedNodes.includes(node.collection.id)"
      >
        <!-- Toggle Button -->
        <button
          v-if="node.children.length > 0"
          class="collection-tree__toggle"
          @click="emit('toggle-expand', node.collection.id)"
          :aria-label="`${expandedNodes.includes(node.collection.id) ? 'Collapse' : 'Expand'} ${node.collection.name}`"
        >
          <i :class="['icon', expandedNodes.includes(node.collection.id) ? 'icon-chevron-down' : 'icon-chevron-right']" />
        </button>

        <div v-else class="collection-tree__spacer" />

        <!-- Collection Button -->
        <button
          :class="['collection-tree__button', { 'collection-tree__button--active': selectedCollectionId === node.collection.id }]"
          :draggable="true"
          @click="emit('select', node.collection)"
          @dragstart="handleDragStart($event, node.collection)"
          @dragover="handleDragOver($event, node.collection)"
          @drop="handleDrop($event, node.collection)"
          @dragend="handleDragEnd"
        >
          <i class="icon icon-folder" />
          {{ node.collection.name }}
          <span class="collection-tree__count">{{ node.collection.asset_count }}</span>
        </button>

        <!-- Children (recursive) -->
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
          @drop="emit('drop', $event)"
        />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { CollectionTree as ICollectionTree, Collection } from '@/types/collections'

defineProps<{
  collections: ICollectionTree[]
  expandedNodes: number[]
  selectedCollectionId: number | null
  draggedCollection: Collection | null
}>()

const emit = defineEmits<{
  select: [collection: Collection]
  'toggle-expand': [nodeId: number]
  'drag-start': [collection: Collection]
  drop: [collection: Collection, newParent?: number]
}>()

const dragOverNode = ref<number | null>(null)

const handleDragStart = (e: DragEvent, collection: Collection) => {
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', String(collection.id))
  }
  emit('drag-start', collection)
}

const handleDragOver = (e: DragEvent, collection: Collection) => {
  e.preventDefault()
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move'
  }
  dragOverNode.value = collection.id
}

const handleDrop = (e: DragEvent, collection: Collection) => {
  e.preventDefault()
  emit('drop', collection)
  dragOverNode.value = null
}

const handleDragEnd = () => {
  dragOverNode.value = null
}
</script>

<style scoped lang="css">
.collection-tree__list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.collection-tree__item {
  display: flex;
  flex-direction: column;
  margin: 0;
}

.collection-tree__toggle {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collection-tree__button {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-base);
  font-size: var(--font-size-base);
  text-align: left;
  transition: all 200ms ease;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.collection-tree__button:hover {
  background: var(--color-bg-1);
  color: var(--color-text);
}

.collection-tree__button--active {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
}

.collection-tree__count {
  margin-left: auto;
  font-size: var(--font-size-sm);
  opacity: 0.7;
}

.collection-tree__children {
  margin-left: 16px;
}

.collection-tree__spacer {
  width: 24px;
}
</style>

---

## FILE 3: src/components/modals/CreateCollectionModal.vue

Simple modal for creating new collection with:
- Name input (required, 1-255 chars)
- Description textarea (optional)
- Visibility select (private/shared/public)
- Create/Cancel buttons

(Follow pattern from UserManagementPage modals in Phase 1)

---

REQUIREMENTS:
✓ CollectionsPage responsive (sidebar left on desktop, hidden on mobile)
✓ Tree supports infinite nesting depth
✓ Drag-drop works (move collection to new parent)
✓ Favorites system works
✓ Special collections section (Favorites, Recent, Shared)
✓ AssetGrid component for showing collection assets
✓ All permission checks (can create, delete, etc.)
✓ Error handling with notifications
✓ WCAG 2.1 AA accessibility
✓ TypeScript strict mode

ACCEPTANCE CRITERIA:
☐ Collections tree renders correctly
☐ Expansion/collapse works
☐ Selection works
☐ Drag-drop moves collections
☐ Favorites toggles
☐ Create collection modal works
☐ Delete collection modal works
☐ Rename collection modal works
☐ Special collections display
☐ Responsive on mobile
☐ ARIA labels present
☐ Keyboard navigation (Tab, Enter, Arrows)
☐ Asset grid shows when collection selected

OUTPUT:
Generate these 3 files:
1. src/pages/CollectionsPage.vue (complete)
2. src/components/collections/CollectionTree.vue (complete recursive tree)
3. src/components/modals/CreateCollectionModal.vue (complete modal)
```

---

# STEP 14: Reports Store + Types

**Зависимости:** Step 12-13 complete  
**Время:** 1 час  
**Output:** 2 файла (types, store)

---

## ПРОМПТ 14: Reports Architecture + Store (Analytics)

```
You are a senior frontend architect specializing in analytics dashboards and real-time reporting.

TASK: Create Reports module with analytics tracking and data visualization types

Context:
- Existing: Pinia store pattern, TypeScript strict
- Features: Usage analytics, Downloads tracking, User activity, Storage analytics
- Charts: Line, Bar, Pie (using Chart.js or ApexCharts)
- Time ranges: Today, This week, This month, Last 3 months, Custom date range
- Export: CSV, PDF
- Reference: DAM-Frontend-Enhancement-TZ.md section "Reports & Analytics"

---

## PHASE 1: Report Types

File: src/types/reports.ts

Interfaces:

1. ReportTimeRange
   Fields: type: 'today'|'week'|'month'|'quarter'|'custom'
           startDate, endDate (ISO strings)

2. UsageMetrics
   Fields: totalAssets, assetsByType, storageUsed, storageLimit, storagePercentage

3. DownloadMetric (for time-series)
   Fields: date, downloads, uniqueUsers

4. UserActivity
   Fields: username, email, action: 'upload'|'download'|'view'|'delete'|'share'
           asset_id, asset_name, timestamp

5. StorageBreakdown
   Fields: category: 'images'|'videos'|'documents'|'other'
           size, count, percentage

6. Report (generic)
   Fields: id, name, type: 'usage'|'downloads'|'activity'|'storage'
           timeRange: ReportTimeRange
           metrics: any (depends on report type)
           createdAt, updatedAt

7. ExportRequest
   Fields: reportId, format: 'csv'|'pdf'

8. ChartData
   Fields: labels: string[], datasets: ChartDataset[]

9. ChartDataset
   Fields: label, data: number[], borderColor, backgroundColor

10. GetReportsParams
    Fields: type?, timeRange?, sort_by?, page?, page_size?

Requirements:
✓ All types exported
✓ Discriminated unions for report types
✓ JSDoc for complex fields
✓ Validation constraints

---

## PHASE 2: Reports Store

File: src/stores/reportsStore.ts

Store Pattern: Composition API

State (using ref):
- reports: Ref<Report[]> = ref([])
- currentReport: Ref<Report | null> = ref(null)
- timeRange: Ref<ReportTimeRange> = ref({ type: 'month', startDate: '', endDate: '' })
- chartData: Ref<ChartData | null> = ref(null)
- usageMetrics: Ref<UsageMetrics | null> = ref(null)
- downloadHistory: Ref<DownloadMetric[]> = ref([])
- recentActivity: Ref<UserActivity[]> = ref([])
- storageBreakdown: Ref<StorageBreakdown[]> = ref([])
- isLoading: Ref<boolean> = ref(false)
- error: Ref<string | null> = ref(null)

Computed:
- chartsReady: all chart data loaded
- exportDisabled: no report to export
- timeRangeDisplay: "January 1 - January 31, 2025"

Actions (async):
1. fetchUsageReport(timeRange: ReportTimeRange)
   - endpoint: GET /api/v4/reports/usage/?start={}&end={}
   - set usageMetrics, storageBreakdown

2. fetchDownloadReport(timeRange: ReportTimeRange)
   - endpoint: GET /api/v4/reports/downloads/?start={}&end={}
   - set downloadHistory
   - build chartData for line chart

3. fetchActivityReport(timeRange: ReportTimeRange, limit: number = 50)
   - endpoint: GET /api/v4/reports/activity/?start={}&end={}&limit={}
   - set recentActivity

4. fetchStorageReport(timeRange: ReportTimeRange)
   - endpoint: GET /api/v4/reports/storage/?start={}&end={}
   - set storageBreakdown
   - build chartData for pie chart

5. setTimeRange(range: ReportTimeRange)
   - update timeRange
   - auto-refetch current report with new range

6. generateChartData(reportType: string, metrics: any): ChartData
   - internal method to format data for charts
   - return structured ChartData

7. exportReport(format: 'csv'|'pdf')
   - endpoint: POST /api/v4/reports/{id}/export/
   - body: { format }
   - download file

8. saveReport(name: string, type: string)
   - endpoint: POST /api/v4/reports/
   - save current report for later

9. fetchSavedReports()
   - endpoint: GET /api/v4/reports/?type=saved
   - set reports

---

## PHASE 3: Reports Service

File: src/services/reportsService.ts

Class ReportsService:

1. getUsageReport(timeRange: ReportTimeRange): Promise<UsageMetrics>
   - endpoint: GET /api/v4/reports/usage/

2. getDownloadReport(timeRange: ReportTimeRange): Promise<DownloadMetric[]>
   - endpoint: GET /api/v4/reports/downloads/

3. getActivityReport(timeRange: ReportTimeRange): Promise<UserActivity[]>
   - endpoint: GET /api/v4/reports/activity/

4. getStorageReport(timeRange: ReportTimeRange): Promise<StorageBreakdown[]>
   - endpoint: GET /api/v4/reports/storage/

5. exportReport(reportId: number, format: string): Promise<Blob>
   - endpoint: GET /api/v4/reports/{reportId}/export/?format={}

6. getAllReports(params?: GetReportsParams): Promise<Report[]>
   - endpoint: GET /api/v4/reports/

export const reportsService = new ReportsService()

---

TEST COVERAGE:
- reportsStore: 15+ tests
- reportsService: 10+ tests
- Chart data generation: 5+ tests

ACCEPTANCE CRITERIA:
☐ All types defined and exported
☐ Store fetches reports correctly
☐ Time range updates trigger refetch
☐ Chart data correctly formatted
☐ Storage breakdown calculated
☐ Activity report paginated
☐ Export works (CSV and PDF)
☐ No TypeScript errors
☐ All async operations have error handling

OUTPUT:
Generate 3 files:
1. src/types/reports.ts
2. src/stores/reportsStore.ts
3. src/services/reportsService.ts
```

---

# STEP 15: ReportsPage + Chart Components

**Зависимости:** Step 14 (reportsStore)  
**Время:** 1.5 часа  
**Output:** 2 файла (page + chart wrapper)

---

## ПРОМПТ 15: ReportsPage + Charts Integration

```
You are a senior Vue 3 frontend architect with expertise in analytics dashboards and Chart.js.

TASK: Create ReportsPage with multiple chart visualizations and export functionality

Context:
- Page: /admin/reports (nested in admin)
- Charts: Usage (pie), Downloads (line), Activity (table), Storage (bar)
- Library: Chart.js or ApexCharts (with Vue wrapper)
- Export: CSV (table), PDF (full report)
- Filters: Time range selector (Today, Week, Month, Quarter, Custom)
- Pattern: Composition API + TypeScript

---

FILE 1: src/pages/admin/AdminReportsPage.vue (or ReportsPage.vue)

Layout:
- Top toolbar: Time range selector, Export button
- Grid of 4 cards, each with a chart

```markdown
<template>
  <div class="reports-page">
    <!-- Toolbar -->
    <div class="reports-toolbar">
      <h1>Analytics & Reports</h1>
      
      <div class="reports-toolbar__controls">
        <!-- Time Range Selector -->
        <Select
          :model-value="selectedTimeRange"
          :options="timeRangeOptions"
          @change="handleTimeRangeChange"
          label="Period"
        />
        
        <!-- Custom Date Range (if 'custom' selected) -->
        <DateRangePicker
          v-if="selectedTimeRange === 'custom'"
          :start-date="customStartDate"
          :end-date="customEndDate"
          @change="handleCustomDateRange"
        />
        
        <!-- Export Button -->
        <Button
          variant="secondary"
          @click="showExportMenu = !showExportMenu"
        >
          <i class="icon icon-download" /> Export
        </Button>
        
        <!-- Export Menu -->
        <div v-if="showExportMenu" class="export-menu">
          <button @click="handleExport('csv')">📊 CSV</button>
          <button @click="handleExport('pdf')">📄 PDF</button>
        </div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="reports-grid">
      <!-- Usage Metrics Card -->
      <Card class="reports-card">
        <template #header>
          <h2>Storage & Assets</h2>
        </template>
        
        <div class="metrics-summary">
          <div class="metric">
            <span class="metric-label">Total Assets</span>
            <span class="metric-value">{{ usageMetrics?.totalAssets || 0 }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Storage Used</span>
            <span class="metric-value">{{ formatBytes(usageMetrics?.storageUsed || 0) }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Storage Limit</span>
            <span class="metric-value">{{ formatBytes(usageMetrics?.storageLimit || 0) }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Usage</span>
            <span class="metric-value">{{ usageMetrics?.storagePercentage || 0 }}%</span>
          </div>
        </div>

        <!-- Storage Breakdown Pie Chart -->
        <ChartComponent
          v-if="storageChartData"
          type="pie"
          :data="storageChartData"
          title="Storage by File Type"
        />
      </Card>

      <!-- Downloads Chart Card -->
      <Card class="reports-card">
        <template #header>
          <h2>Downloads Trend</h2>
        </template>
        
        <ChartComponent
          v-if="downloadChartData"
          type="line"
          :data="downloadChartData"
          title="Downloads Over Time"
        />
      </Card>

      <!-- Activity Stats Card -->
      <Card class="reports-card">
        <template #header>
          <h2>User Activity</h2>
        </template>
        
        <!-- Activity Table -->
        <ActivityTable
          :activities="recentActivity"
          :is-loading="isLoading"
        />
      </Card>

      <!-- Storage Breakdown Card -->
      <Card class="reports-card">
        <template #header>
          <h2>Storage Breakdown</h2>
        </template>
        
        <ChartComponent
          v-if="storageBarChartData"
          type="bar"
          :data="storageBarChartData"
          title="Storage by Category"
        />
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useReportsStore } from '@/stores/reportsStore'
import { useUIStore } from '@/stores/uiStore'
import Card from '@/components/Common/Card.vue'
import Button from '@/components/Common/Button.vue'
import Select from '@/components/Common/Select.vue'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'
import ChartComponent from '@/components/reports/ChartComponent.vue'
import ActivityTable from '@/components/reports/ActivityTable.vue'
import type { ReportTimeRange } from '@/types/reports'

// Hooks
const router = useRouter()
const authStore = useAuthStore()
const reportsStore = useReportsStore()
const uiStore = useUIStore()

// State
const selectedTimeRange = ref<string>('month')
const customStartDate = ref('')
const customEndDate = ref('')
const showExportMenu = ref(false)
const isLoading = ref(false)

// Time range options
const timeRangeOptions = [
  { value: 'today', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'quarter', label: 'Last 3 Months' },
  { value: 'custom', label: 'Custom Range' }
]

// Computed
const usageMetrics = computed(() => reportsStore.usageMetrics)
const recentActivity = computed(() => reportsStore.recentActivity)

const timeRange = computed<ReportTimeRange>(() => {
  if (selectedTimeRange.value === 'custom') {
    return {
      type: 'custom',
      startDate: customStartDate.value,
      endDate: customEndDate.value
    }
  }
  
  const today = new Date()
  let startDate = new Date()
  
  switch (selectedTimeRange.value) {
    case 'today':
      startDate = new Date(today.getTime())
      break
    case 'week':
      startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      break
    case 'month':
      startDate = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
      break
    case 'quarter':
      startDate = new Date(today.getTime() - 90 * 24 * 60 * 60 * 1000)
      break
  }
  
  return {
    type: selectedTimeRange.value as any,
    startDate: startDate.toISOString(),
    endDate: today.toISOString()
  }
})

const storageChartData = computed(() => {
  if (!reportsStore.storageBreakdown.length) return null
  
  return {
    labels: reportsStore.storageBreakdown.map(s => s.category),
    datasets: [{
      label: 'Storage (GB)',
      data: reportsStore.storageBreakdown.map(s => s.size / (1024 * 1024 * 1024)),
      backgroundColor: [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)'
      ]
    }]
  }
})

const downloadChartData = computed(() => {
  if (!reportsStore.downloadHistory.length) return null
  
  return {
    labels: reportsStore.downloadHistory.map(d => new Date(d.date).toLocaleDateString()),
    datasets: [{
      label: 'Downloads',
      data: reportsStore.downloadHistory.map(d => d.downloads),
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.1)',
      tension: 0.4
    }]
  }
})

const storageBarChartData = computed(() => {
  if (!reportsStore.storageBreakdown.length) return null
  
  return {
    labels: reportsStore.storageBreakdown.map(s => s.category),
    datasets: [{
      label: 'File Count',
      data: reportsStore.storageBreakdown.map(s => s.count),
      backgroundColor: 'rgba(54, 162, 235, 0.7)'
    }]
  }
})

// Methods
const fetchReports = async () => {
  isLoading.value = true
  try {
    await Promise.all([
      reportsStore.fetchUsageReport(timeRange.value),
      reportsStore.fetchDownloadReport(timeRange.value),
      reportsStore.fetchActivityReport(timeRange.value),
      reportsStore.fetchStorageReport(timeRange.value)
    ])
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to load reports',
      duration: 5000
    })
  } finally {
    isLoading.value = false
  }
}

const handleTimeRangeChange = (value: string) => {
  selectedTimeRange.value = value
  fetchReports()
}

const handleCustomDateRange = (range: { startDate: string, endDate: string }) => {
  customStartDate.value = range.startDate
  customEndDate.value = range.endDate
  fetchReports()
}

const handleExport = async (format: 'csv' | 'pdf') => {
  try {
    // If no saved report, save current first
    if (!reportsStore.currentReport?.id) {
      await reportsStore.saveReport(`Report ${new Date().toLocaleDateString()}`, 'analytics')
    }
    
    await reportsStore.exportReport(format)
    showExportMenu.value = false
    uiStore.addNotification({
      type: 'success',
      message: `Report exported as ${format.toUpperCase()}`,
      duration: 3000
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      message: 'Failed to export report',
      duration: 5000
    })
  }
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Lifecycle
onMounted(async () => {
  if (!authStore.hasPermission('admin.reports_view')) {
    router.push({ name: 'forbidden' })
    return
  }
  
  await fetchReports()
})
</script>

<style scoped lang="css">
.reports-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background: var(--color-background);
}

.reports-toolbar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reports-toolbar h1 {
  margin: 0;
  font-size: var(--font-size-3xl);
  color: var(--color-text);
}

.reports-toolbar__controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  position: relative;
}

.export-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-md);
  z-index: 10;
}

.export-menu button {
  display: block;
  width: 100%;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
  text-align: left;
  transition: all 200ms ease;
}

.export-menu button:hover {
  background: var(--color-bg-1);
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.reports-card {
  min-height: 300px;
}

.metrics-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: var(--color-bg-1);
  border-radius: var(--radius-base);
}

.metric-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.metric-value {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

/* Responsive */
@media (max-width: 768px) {
  .reports-toolbar {
    flex-direction: column;
  }

  .reports-toolbar__controls {
    flex-direction: column;
  }

  .reports-toolbar__controls > * {
    width: 100%;
  }

  .reports-grid {
    grid-template-columns: 1fr;
  }
}
</style>

---

FILE 2: src/components/reports/ChartComponent.vue

Generic chart wrapper component using Chart.js

- Props: type ('pie'|'line'|'bar'), data, title
- Renders chart using Chart.js Vue wrapper
- Responsive canvas sizing
- Zoom/pan capabilities (optional for line charts)

<template>
  <div class="chart-component">
    <h3 v-if="title" class="chart-component__title">{{ title }}</h3>
    <canvas ref="chartCanvas" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Chart from 'chart.js/auto'
import type { ChartData } from '@/types/reports'

defineProps<{
  type: 'pie' | 'line' | 'bar'
  data: ChartData
  title?: string
}>()

const chartCanvas = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

onMounted(() => {
  if (!chartCanvas.value) return
  
  chartInstance = new Chart(chartCanvas.value, {
    type: props.type,
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      },
      scales: props.type !== 'pie' ? {
        y: { beginAtZero: true }
      } : undefined
    }
  })
})
</script>

<style scoped lang="css">
.chart-component {
  position: relative;
  height: 300px;
  width: 100%;
}

.chart-component__title {
  margin: 0 0 16px 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

canvas {
  max-width: 100%;
}
</style>

Also create ActivityTable.vue component for displaying user activity table.

---

REQUIREMENTS:
✓ All 4 charts render correctly
✓ Time range selector works
✓ Export functionality works (CSV, PDF)
✓ Charts responsive (mobile-friendly)
✓ Metrics display correctly
✓ Activity table paginated
✓ Permission checks working
✓ Error handling with notifications
✓ Accessibility (WCAG 2.1 AA)
✓ TypeScript strict mode

ACCEPTANCE CRITERIA:
☐ Page loads without errors
☐ Charts display correctly
☐ Time range changes update all charts
☐ Export menu appears/disappears
☐ Export buttons trigger download
☐ Charts are responsive
☐ Metrics calculated correctly
☐ Activity table displays
☐ Permission check redirects if needed
☐ No console errors

OUTPUT:
Generate 3 files:
1. src/pages/admin/AdminReportsPage.vue (or ReportsPage.vue) - complete
2. src/components/reports/ChartComponent.vue - complete
3. src/components/reports/ActivityTable.vue - complete table component
```

---

# STEP 16: PublicationDetailPage

**Зависимости:** Phase 1 complete + assetStore  
**Время:** 1 час  
**Output:** 1 файл (page)

---

## ПРОМПТ 16: PublicationDetailPage

```
You are a senior Vue 3 frontend developer.

TASK: Create PublicationDetailPage for viewing/editing individual publications

Context:
- Page: /distribution/publications/{id}
- Features: Publication info, asset list, access control, metrics
- Pattern: Composition API + TypeScript
- Reference: DAM-Frontend-Enhancement-TZ.md section "Distribution Sub-pages"

FILE: src/pages/PublicationDetailPage.vue

Requirements:
- Display publication name, description, thumbnail
- Show list of assets in publication
- Download button for assets
- Share button (copy link)
- Metrics: views, downloads, shares
- Edit button (if owner)
- Delete button (if owner)
- Responsive grid for assets

ACCEPTANCE CRITERIA:
☐ Publication data loads correctly
☐ Assets display in grid
☐ Share link works
☐ Metrics display correctly
☐ Edit/Delete buttons appear for owner
☐ Responsive on mobile
☐ Permission checks work

OUTPUT:
Generate 1 file:
src/pages/PublicationDetailPage.vue (complete)
```

---

# STEP 17: PublicationPublicPage

**Зависимости:** Step 16  
**Время:** 1 час  
**Output:** 1 файл (page)

---

## ПРОМПТ 17: PublicationPublicPage (Public Sharing Link)

```
You are a senior Vue 3 frontend developer specializing in public-facing pages.

TASK: Create PublicationPublicPage for public/token-based access to publications

Context:
- Page: /public/publications/{token}
- Features: Public view of publication, download assets, no auth required
- Pattern: Composition API + TypeScript
- Design: Clean, simple, fast
- Security: Token-based access, read-only

FILE: src/pages/PublicationPublicPage.vue

Requirements:
- No login required
- Token-based access (URL parameter)
- Display publication name, description
- Asset grid with download buttons
- Simple, fast loading (optimize images)
- No admin/user UI elements
- Track downloads/views (if enabled)
- Responsive mobile-first design

ACCEPTANCE CRITERIA:
☐ Page loads without login
☐ Token validation works
☐ Assets display correctly
☐ Download buttons work
☐ Mobile responsive
☐ Fast loading (optimize images)
☐ Error handling (invalid token)

OUTPUT:
Generate 1 file:
src/pages/PublicationPublicPage.vue (complete)
```

---

# 📋 PHASE 2 COMPLETION CHECKLIST

```
STEP 12: Collections Store ✅
☐ src/types/collections.ts created (450+ lines)
☐ src/stores/collectionsStore.ts created (300+ lines)
☐ src/services/collectionsService.ts created (200+ lines)
☐ Unit tests: 15+ passing
☐ Tree building logic: working

STEP 13: Collections Page ✅
☐ src/pages/CollectionsPage.vue created
☐ src/components/collections/CollectionTree.vue created
☐ src/components/modals/CreateCollectionModal.vue created
☐ Drag-drop: working
☐ Favorites: working
☐ Unit tests: 20+ passing

STEP 14: Reports Store ✅
☐ src/types/reports.ts created
☐ src/stores/reportsStore.ts created
☐ src/services/reportsService.ts created
☐ Unit tests: 15+ passing

STEP 15: Reports Page ✅
☐ src/pages/admin/AdminReportsPage.vue created
☐ src/components/reports/ChartComponent.vue created
☐ src/components/reports/ActivityTable.vue created
☐ 4 charts rendering: working
☐ Export functionality: working
☐ Unit tests: 25+ passing

STEP 16: Publication Detail ✅
☐ src/pages/PublicationDetailPage.vue created
☐ Metrics display: working
☐ Edit/Delete: working
☐ Unit tests: 15+ passing

STEP 17: Publication Public ✅
☐ src/pages/PublicationPublicPage.vue created
☐ Token-based access: working
☐ Performance optimized
☐ Unit tests: 12+ passing

TOTAL PHASE 2:
- 8 new files (pages + components)
- 2000+ lines of code
- 102+ unit tests passing ✅
- All user features: working ✅
```

---

## 🎯 WHAT'S NEXT: PHASE 3

После Phase 2 (Step 17) переходите на **STEP 18-24** для:
- 5 критических модальных окон
- Final polish и optimization
- E2E testing
- Production deployment

**Время на Phase 2:** 7.5 часов на Cursor AI  
**Общее время (Phase 1-2):** 17.5 часов  
**Оставалось (Phase 3):** 7 часов  
**TOTAL:** 24.5 часа для полного производства DAM frontend (91/100 compliance)

---

**Все 6 промптов готовы для Cursor AI!** 🚀

Копируйте каждый промпт в Cursor и ждите результата (обычно 5-20 минут на промпт).

