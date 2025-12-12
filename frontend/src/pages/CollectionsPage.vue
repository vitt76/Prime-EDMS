// @ts-nocheck
<template>
  <div class="collections-page">
    <!-- Skip Links for Accessibility -->
    <a href="#collections-main" class="skip-link">Skip to main content</a>
    <a href="#collections-sidebar" class="skip-link">Skip to sidebar</a>
    
    <!-- Header -->
    <div class="collections-page__header">
      <h1 class="collections-page__title">Collections</h1>
    </div>

    <div class="collections-page__layout">
      <!-- Sidebar -->
      <aside id="collections-sidebar" class="collections-page__sidebar" aria-label="Collections navigation">
        <!-- Special Collections -->
        <div class="special-collections">
          <button
            v-for="special in specialCollections"
            :key="special.id"
            :class="[
              'special-collections__item',
              {
                'special-collections__item--active':
                  currentCollectionId === special.id
              }
            ]"
            @click="selectSpecialCollection(special)"
            :aria-label="`Select ${special.name} collection`"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                v-if="special.type === 'favorites'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
              />
              <path
                v-else-if="special.type === 'recent'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
              <path
                v-else-if="special.type === 'my_uploads'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
              <path
                v-else-if="special.type === 'shared_with_me'"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8.684 13.342C8.885 12.938 9 12.482 9 12c0-.482-.115-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 002 2h2.945M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span class="special-collections__label">{{ special.name }}</span>
            <span class="special-collections__count">{{
              special.asset_count
            }}</span>
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
      </aside>

      <!-- Main Content -->
      <main id="collections-main" class="collections-page__content" aria-label="Collections content">
        <!-- Toolbar -->
        <div class="collections-toolbar">
          <!-- Breadcrumbs -->
          <Breadcrumbs :items="breadcrumbs" />

          <!-- Actions -->
          <div class="collections-toolbar__actions">
            <Button
              v-if="canCreateCollection"
              variant="primary"
              @click="showCreateModal = true"
              aria-label="Create new collection"
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
                  d="M12 4v16m8-8H4"
                />
              </svg>
              New Collection
            </Button>

            <Button
              v-if="currentCollection && !isSpecialCollection && canEditCollection"
              variant="secondary"
              @click="showRenameModal = true"
              aria-label="Rename collection"
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
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Rename
            </Button>

            <Button
              v-if="currentCollection"
              variant="secondary"
              @click="toggleFavorite"
              :aria-label="
                currentCollection.is_favorite
                  ? 'Remove from favorites'
                  : 'Add to favorites'
              "
            >
              <svg
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                :class="{
                  'fill-current': currentCollection.is_favorite
                }"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                />
              </svg>
            </Button>

            <Button
              v-if="currentCollection && !isSpecialCollection && canDeleteCollection"
              variant="secondary"
              @click="showDeleteModal = true"
              aria-label="Delete collection"
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
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete
            </Button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!currentCollection" class="collections-empty">
          <svg
            class="w-16 h-16 text-neutral-400"
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
          <p class="collections-empty__text">
            Select a collection to view assets
          </p>
        </div>

        <!-- Assets Grid (if collection selected) -->
        <div v-else class="collections-content">
          <!-- Header -->
          <div class="collections-header">
            <h2 class="collections-header__title">
              {{ currentCollection.name }}
            </h2>
            <p
              v-if="currentCollection.description"
              class="collections-header__description"
            >
              {{ currentCollection.description }}
            </p>
            <span class="collections-header__count">
              {{ currentCollection.asset_count }} asset{{
                currentCollection.asset_count !== 1 ? 's' : ''
              }}
            </span>
          </div>

          <!-- Assets Grid -->
          <AssetGrid
            :collection-id="isSpecialCollection ? currentCollection.id : currentCollection.id"
            @asset-click="handleAssetClick"
          />
        </div>
      </main>
    </div>

    <!-- Modals -->
    <CreateCollectionModal
      v-if="showCreateModal"
      :parent-id="currentCollection?.id || null"
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
      :message="'This will also delete all child collections. Are you sure?'"
      @confirm="handleDeleteCollection"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useCollectionsStore } from '@/stores/collectionsStore'
import { useUIStore } from '@/stores/uiStore'
import type { Collection, SpecialCollectionType } from '@/types/collections'
import CollectionTree from '@/components/collections/CollectionTree.vue'
import Breadcrumbs from '@/components/Common/Breadcrumbs.vue'
import Button from '@/components/Common/Button.vue'
import AssetGrid from '@/components/collections/AssetGrid.vue'
import CreateCollectionModal from '@/components/collections/CreateCollectionModal.vue'
import RenameCollectionModal from '@/components/collections/RenameCollectionModal.vue'
import DeleteConfirmModal from '@/components/admin/DeleteConfirmModal.vue'

// Hooks
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collectionsStore = useCollectionsStore()
const uiStore = useUIStore()

// State
const currentCollectionId = ref<number | string | null>(null)
const showCreateModal = ref(false)
const showRenameModal = ref(false)
const showDeleteModal = ref(false)
const isLoading = ref(false)
const fetchCollectionsRequestId = ref(0)
const selectionRequestId = ref(0)

// Computed
const collectionsTree = computed(() => collectionsStore.collectionsTree)
const currentCollection = computed(() => collectionsStore.currentCollection)
const expandedNodes = computed(() =>
  Array.from(collectionsStore.expandedNodes)
)
const draggedCollection = computed(() => collectionsStore.draggedCollection)
const canCreateCollection = computed(() =>
  collectionsStore.canCreateCollection
)
const canDeleteCollection = computed(() =>
  collectionsStore.canDeleteCollection
)
const canEditCollection = computed(() =>
  collectionsStore.canEditCollection
)

const specialCollections = computed(() => {
  const collections: Array<
    Collection & { type: SpecialCollectionType; id: string | number }
  > = []

  if (collectionsStore.favorites.length > 0) {
    collections.push({
      id: 'favorites',
      name: 'Favorites',
      description: '',
      parent_id: null,
      is_favorite: false,
      is_shared: false,
      visibility: 'private',
      asset_count: collectionsStore.favorites.reduce(
        (sum, c) => sum + c.asset_count,
        0
      ),
      created_by: authStore.user?.id || 0,
      created_at: '',
      updated_at: '',
      cover_image_id: null,
      type: 'favorites'
    })
  }

  if (collectionsStore.recentCollections.length > 0) {
    collections.push({
      id: 'recent',
      name: 'Recent',
      description: '',
      parent_id: null,
      is_favorite: false,
      is_shared: false,
      visibility: 'private',
      asset_count: collectionsStore.recentCollections.reduce(
        (sum, c) => sum + c.asset_count,
        0
      ),
      created_by: authStore.user?.id || 0,
      created_at: '',
      updated_at: '',
      cover_image_id: null,
      type: 'recent'
    })
  }

  if (collectionsStore.sharedWithMe.length > 0) {
    collections.push({
      id: 'shared_with_me',
      name: 'Shared with Me',
      description: '',
      parent_id: null,
      is_favorite: false,
      is_shared: true,
      visibility: 'shared',
      asset_count: collectionsStore.sharedWithMe.reduce(
        (sum, c) => sum + c.asset_count,
        0
      ),
      created_by: authStore.user?.id || 0,
      created_at: '',
      updated_at: '',
      cover_image_id: null,
      type: 'shared_with_me'
    })
  }

  if (collectionsStore.publicCollections.length > 0) {
    collections.push({
      id: 'public_collections',
      name: 'Public Collections',
      description: '',
      parent_id: null,
      is_favorite: false,
      is_shared: false,
      visibility: 'public',
      asset_count: collectionsStore.publicCollections.reduce(
        (sum, c) => sum + c.asset_count,
        0
      ),
      created_by: authStore.user?.id || 0,
      created_at: '',
      updated_at: '',
      cover_image_id: null,
      type: 'public_collections'
    })
  }

  return collections
})

const isSpecialCollection = computed(() => {
  if (!currentCollectionId.value) return false
  return typeof currentCollectionId.value === 'string'
})

const breadcrumbs = computed(() => {
  const items: Array<{ label: string; to: string | null }> = [
    { label: 'Collections', to: '/collections' }
  ]

  if (currentCollectionId.value && typeof currentCollectionId.value === 'number') {
    const breadcrumbPath = collectionsStore.breadcrumbs(currentCollectionId.value)
    breadcrumbPath.forEach((crumb) => {
      items.push({
        label: crumb.name,
        to: `/collections/${crumb.id}`
      })
    })
  } else if (currentCollectionId.value) {
    const special = specialCollections.value.find(
      (s) => s.id === currentCollectionId.value
    )
    if (special) {
      items.push({ label: special.name, to: null })
    }
  }

  return items
})

// Methods
const fetchCollections = async (): Promise<void> => {
  const requestId = ++fetchCollectionsRequestId.value
  isLoading.value = true
  try {
    await collectionsStore.fetchCollections()
    await collectionsStore.fetchSpecialCollections()

    if (requestId !== fetchCollectionsRequestId.value) {
      return
    }

    if (!currentCollectionId.value) {
      const firstRoot = collectionsStore.rootCollections[0]
      if (firstRoot) {
        await selectCollection(firstRoot)
      }
    }
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to load collections'
    })
  } finally {
    isLoading.value = false
  }
}

const handleSelectCollection = async (collection: Collection): Promise<void> => {
  const requestId = ++selectionRequestId.value
  currentCollectionId.value = collection.id
  await collectionsStore.fetchCollection(collection.id)
  if (requestId !== selectionRequestId.value) {
    return
  }
}

const selectSpecialCollection = async (
  special: Collection & { type: SpecialCollectionType }
): Promise<void> => {
  try {
    currentCollectionId.value = special.id
    
    // Load assets for special collections
    let assets: any[] = []
    switch (special.type) {
      case 'favorites':
        assets = collectionsStore.favorites.flatMap(c => {
          // Get assets from favorite collections
          return c.asset_count > 0 ? [] : [] // Placeholder - would fetch from API
        })
        break
      case 'recent':
        assets = collectionsStore.recentCollections.flatMap(c => {
          return c.asset_count > 0 ? [] : [] // Placeholder - would fetch from API
        })
        break
      case 'shared_with_me':
        assets = collectionsStore.sharedWithMe.flatMap(c => {
          return c.asset_count > 0 ? [] : [] // Placeholder - would fetch from API
        })
        break
      case 'public_collections':
        assets = collectionsStore.publicCollections.flatMap(c => {
          return c.asset_count > 0 ? [] : [] // Placeholder - would fetch from API
        })
        break
    }
    
    // Set a virtual collection for special collections
    collectionsStore.setCurrentCollection({
      id: special.id,
      name: special.name,
      description: special.description || '',
      parent_id: null,
      is_favorite: special.type === 'favorites',
      is_shared: special.type === 'shared_with_me' || special.type === 'public_collections',
      visibility: special.visibility,
      asset_count: special.asset_count,
      created_by: authStore.user?.id || 0,
      created_at: '',
      updated_at: '',
      cover_image_id: null
    } as Collection)
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to load special collection'
    })
  }
}

const selectCollection = (collection: Collection): void => {
  handleSelectCollection(collection)
}

const handleToggleExpand = (nodeId: number): void => {
  collectionsStore.toggleNodeExpanded(nodeId)
}

const handleDragStart = (collection: Collection): void => {
  collectionsStore.setDraggedCollection(collection)
}

const handleDrop = async (
  targetCollection: Collection,
  newParentId?: number | null
): Promise<void> => {
  const draggedId = collectionsStore.draggedCollection?.id
  if (!draggedId || typeof draggedId !== 'number') return

  // Prevent dropping on itself or its children
  if (draggedId === targetCollection.id) {
    collectionsStore.setDraggedCollection(null)
    return
  }

  try {
    await collectionsStore.moveCollection(
      draggedId,
      targetCollection.id,
      newParentId !== undefined ? newParentId : targetCollection.id
    )
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Collection moved successfully'
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to move collection'
    })
  } finally {
    collectionsStore.setDraggedCollection(null)
  }
}

const toggleFavorite = async (): Promise<void> => {
  if (!currentCollection.value || typeof currentCollection.value.id !== 'number')
    return
  try {
    await collectionsStore.toggleFavorite(currentCollection.value.id)
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: currentCollection.value.is_favorite
        ? 'Removed from favorites'
        : 'Added to favorites'
    })
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to toggle favorite'
    })
  }
}

const handleCreateCollection = async (data: {
  name: string
  description?: string
  visibility?: string
}): Promise<void> => {
  try {
    await collectionsStore.createCollection({
      ...data,
      parent_id: currentCollection.value?.id || null,
      visibility: (data.visibility as 'private' | 'shared' | 'public') || 'private'
    })
    showCreateModal.value = false
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Collection created successfully'
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to create collection'
    })
  }
}

const handleRenameCollection = async (data: {
  name: string
  description?: string
}): Promise<void> => {
  if (!currentCollection.value) return
  try {
    await collectionsStore.updateCollection(currentCollection.value.id, data)
    showRenameModal.value = false
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Collection renamed successfully'
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to rename collection'
    })
  }
}

const handleDeleteCollection = async (): Promise<void> => {
  if (!currentCollection.value || typeof currentCollection.value.id !== 'number')
    return
  try {
    await collectionsStore.deleteCollection(currentCollection.value.id)
    showDeleteModal.value = false
    currentCollectionId.value = null
    uiStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Collection deleted successfully'
    })
    await fetchCollections()
  } catch (error) {
    uiStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to delete collection'
    })
  }
}

const handleAssetClick = (assetId: number): void => {
  router.push({ name: 'asset-detail', params: { id: assetId } })
}

// Lifecycle
onMounted(async () => {
  // Check if route has collection ID
  if (route.params.id) {
    const collectionId = typeof route.params.id === 'string' 
      ? parseInt(route.params.id) 
      : parseInt(route.params.id[0])
    if (!isNaN(collectionId)) {
      await collectionsStore.fetchCollection(collectionId)
      currentCollectionId.value = collectionId
    }
  } else {
    await fetchCollections()
  }
})
</script>

<style scoped lang="css">
.collections-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--color-background, #f9fafb);
}

.collections-page__header {
  padding: 24px;
  background: var(--color-surface, #ffffff);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.collections-page__title {
  font-size: var(--font-size-3xl, 30px);
  font-weight: 600;
  color: var(--color-text, #111827);
  margin: 0;
}

.collections-page__layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  flex: 1;
  min-height: 0;
}

.collections-page__sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--color-surface, #ffffff);
  border-right: 1px solid var(--color-border, #e5e7eb);
  overflow-y: auto;
  max-height: calc(100vh - 100px);
}

.collections-page__content {
  display: flex;
  flex-direction: column;
  min-height: 0;
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
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-base, 14px);
  transition: all 200ms ease;
  text-align: left;
  width: 100%;
}

.special-collections__item:hover {
  background: var(--color-bg-1, #f9fafb);
  color: var(--color-text, #111827);
}

.special-collections__item--active {
  background: var(--color-primary, #3b82f6);
  color: white;
  font-weight: 600;
}

.special-collections__label {
  flex: 1;
}

.special-collections__count {
  font-size: var(--font-size-sm, 12px);
  opacity: 0.7;
}

.collections-sidebar__divider {
  height: 1px;
  background: var(--color-border, #e5e7eb);
  margin: 8px 0;
}

.collections-toolbar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  background: var(--color-surface, #ffffff);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.collections-toolbar__actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.collections-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--color-text-secondary, #6b7280);
  gap: 16px;
}

.collections-empty__text {
  font-size: var(--font-size-lg, 18px);
  margin: 0;
}

.collections-content {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.collections-header {
  margin-bottom: 32px;
}

.collections-header__title {
  margin: 0 0 8px 0;
  font-size: var(--font-size-3xl, 30px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.collections-header__description {
  margin: 0 0 12px 0;
  color: var(--color-text-secondary, #6b7280);
  font-size: var(--font-size-base, 14px);
  line-height: 1.5;
}

.collections-header__count {
  display: inline-block;
  padding: 4px 12px;
  background: var(--color-bg-1, #f9fafb);
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  font-weight: 500;
}

/* Skip Links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-primary, #3b82f6);
  color: white;
  padding: 8px 16px;
  text-decoration: none;
  z-index: 1000;
  border-radius: 0 0 4px 0;
  font-weight: 600;
}

.skip-link:focus {
  top: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .collections-page__layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }

  .collections-page__sidebar {
    max-height: 300px;
    border-right: none;
    border-bottom: 1px solid var(--color-border, #e5e7eb);
  }
}

@media (max-width: 768px) {
  .collections-toolbar {
    padding: 16px;
  }

  .collections-toolbar__actions {
    flex-direction: column;
  }

  .collections-toolbar__actions button {
    width: 100%;
  }

  .collections-content {
    padding: 16px;
  }
}
</style>

