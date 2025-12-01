import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { collectionsService } from '@/services/collectionsService'
import { formatApiError } from '@/utils/errors'
import { extractErrorCode } from '@/utils/errorHandling'
import { useAuthStore } from './authStore'
import { useUIStore } from './uiStore'
import type {
  Collection,
  CollectionTree,
  CollectionBreadcrumb,
  CreateCollectionRequest,
  UpdateCollectionRequest,
  MoveCollectionRequest,
  BulkCollectionOperation,
  BulkOperationResponse,
  GetCollectionsParams,
  PaginatedCollections,
  SpecialCollectionsResponse,
  SpecialCollectionType
} from '@/types/collections'

const CACHE_TTL = 5 * 60 * 1000 // 5 minutes in milliseconds
const MAX_BULK_OPERATION_SIZE = 50

export const useCollectionsStore = defineStore(
  'collections',
  () => {
    const authStore = useAuthStore()
    const uiStore = useUIStore()

    const collectionRequestIds = ref({
      collections: 0,
      collection: 0
    })

    const startCollectionRequest = (
      key: keyof typeof collectionRequestIds.value
    ): number => {
      const nextId = (collectionRequestIds.value[key] ?? 0) + 1
      collectionRequestIds.value = {
        ...collectionRequestIds.value,
        [key]: nextId
      }
      return nextId
    }

    const isLatestCollectionRequest = (
      key: keyof typeof collectionRequestIds.value,
      id: number
    ): boolean => collectionRequestIds.value[key] === id

    const logCollectionError = (context: string, error: unknown): string => {
      const message = formatApiError(error)
      const code = extractErrorCode(error)
      console.warn(`${context} failed`, { code, error })
      uiStore.addNotification({
        type: 'error',
        title: `${context} Error`,
        message,
        meta: code ? { code } : undefined
      })
      return message
    }

    // Collections state
    const collections = ref<Collection[]>([])
    const currentCollection = ref<Collection | null>(null)
    const collectionsTree = ref<CollectionTree[]>([])
    const selectedCollections = ref<number[]>([])
    const totalCollectionsCount = ref(0)

    // Special collections state
    const favorites = ref<Collection[]>([])
    const recentCollections = ref<Collection[]>([])
    const sharedWithMe = ref<Collection[]>([])
    const myUploads = ref<Collection[]>([])
    const publicCollections = ref<Collection[]>([])

    // UI state
    const expandedNodes = ref<Set<number>>(new Set())
    const draggedCollection = ref<Collection | null>(null)

    // Global state
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const lastFetchTime = ref<number | null>(null)

    // Computed properties - Permissions
    const canCreateCollection = computed(() => {
      return authStore.hasPermission.value('collections.create')
    })

    const canDeleteCollection = computed(() => {
      return authStore.hasPermission.value('collections.delete')
    })

    const canEditCollection = computed(() => {
      return authStore.hasPermission.value('collections.edit')
    })

    const canShareCollection = computed(() => {
      return authStore.hasPermission.value('collections.share')
    })

    // Computed properties - Tree structure
    const rootCollections = computed(() => {
      return collections.value.filter((c) => c.parent_id === null)
    })

    const flattenedTree = computed(() => {
      const result: Collection[] = []
      const flatten = (nodes: CollectionTree[]): void => {
        for (const node of nodes) {
          result.push(node.collection)
          if (node.children.length > 0) {
            flatten(node.children)
          }
        }
      }
      flatten(collectionsTree.value)
      return result
    })

    // Computed - Breadcrumbs
    const breadcrumbs = computed(() => {
      return (collectionId: number): CollectionBreadcrumb[] => {
        const result: CollectionBreadcrumb[] = []
        const collection = collections.value.find((c) => c.id === collectionId)

        if (!collection) return result

        const buildPath = (id: number, level: number): void => {
          const coll = collections.value.find((c) => c.id === id)
          if (coll) {
            if (coll.parent_id) {
              buildPath(coll.parent_id, level - 1)
            }
            result.push({
              id: coll.id,
              name: coll.name,
              level
            })
          }
        }

        buildPath(collectionId, 0)
        return result
      }
    })

    // Actions - Fetch collections
    async function fetchCollections(
      params?: GetCollectionsParams
    ): Promise<void> {
      const now = Date.now()
      if (
        lastFetchTime.value &&
        now - lastFetchTime.value < CACHE_TTL &&
        collections.value.length > 0
      ) {
        return
      }

      const key: keyof typeof collectionRequestIds.value = 'collections'
      const requestId = startCollectionRequest(key)
      isLoading.value = true
      error.value = null

      try {
        const response: PaginatedCollections =
          await collectionsService.getCollections(params)

        if (!isLatestCollectionRequest(key, requestId)) {
          return
        }

        collections.value = response.results
        totalCollectionsCount.value = response.count
        lastFetchTime.value = Date.now()

        collectionsTree.value = buildCollectionTree(collections.value)
      } catch (err) {
        if (!isLatestCollectionRequest(key, requestId)) {
          return
        }
        const message = logCollectionError('Collections list fetch', err)
        error.value = message
        collections.value = []
        totalCollectionsCount.value = 0
        collectionsTree.value = []
        throw err
      } finally {
        if (isLatestCollectionRequest(key, requestId)) {
          isLoading.value = false
        }
      }
    }

    // Actions - Fetch single collection
    async function fetchCollection(id: number): Promise<Collection> {
      const key: keyof typeof collectionRequestIds.value = 'collection'
      const requestId = startCollectionRequest(key)
      isLoading.value = true
      error.value = null

      try {
        const collection = await collectionsService.getCollection(id)

        if (!isLatestCollectionRequest(key, requestId)) {
          return collection
        }

        currentCollection.value = collection

        const index = collections.value.findIndex((c) => c.id === id)
        if (index !== -1) {
          collections.value[index] = collection
        } else {
          collections.value.push(collection)
        }

        collectionsTree.value = buildCollectionTree(collections.value)

        return collection
      } catch (err) {
        if (!isLatestCollectionRequest(key, requestId)) {
          throw err
        }
        const message = logCollectionError('Collection fetch', err)
        error.value = message
        currentCollection.value = null
        throw err
      } finally {
        if (isLatestCollectionRequest(key, requestId)) {
          isLoading.value = false
        }
      }
    }

    // Actions - Create collection
    async function createCollection(
      data: CreateCollectionRequest
    ): Promise<Collection> {
      isLoading.value = true
      error.value = null

      try {
        const newCollection = await collectionsService.createCollection(data)
        collections.value.push(newCollection)
        totalCollectionsCount.value++

        collectionsTree.value = buildCollectionTree(collections.value)
        invalidateCache()

        return newCollection
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Update collection
    async function updateCollection(
      id: number,
      data: UpdateCollectionRequest
    ): Promise<Collection> {
      isLoading.value = true
      error.value = null

      try {
        const updatedCollection = await collectionsService.updateCollection(
          id,
          data
        )

        // Update in collections array
        const index = collections.value.findIndex((c) => c.id === id)
        if (index !== -1) {
          collections.value[index] = updatedCollection
        }

        // Update current collection if it's the one being updated
        if (currentCollection.value?.id === id) {
          currentCollection.value = updatedCollection
        }

        collectionsTree.value = buildCollectionTree(collections.value)

        invalidateCache()

        if (data.is_favorite !== undefined) {
          if (data.is_favorite) {
            if (!favorites.value.find((f) => f.id === id)) {
              favorites.value.push(updatedCollection)
            }
          } else {
            favorites.value = favorites.value.filter((f) => f.id !== id)
          }
        }

        invalidateCache()

        return updatedCollection
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Delete collection
    async function deleteCollection(id: number): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        await collectionsService.deleteCollection(id)

        // Remove from collections array (and children)
        const removeCollectionAndChildren = (collectionId: number): void => {
          collections.value = collections.value.filter(
            (c) => c.id !== collectionId
          )
          const children = collections.value.filter(
            (c) => c.parent_id === collectionId
          )
          children.forEach((child) => removeCollectionAndChildren(child.id))
        }

        removeCollectionAndChildren(id)
        totalCollectionsCount.value = collections.value.length

        // Clear current collection if deleted
        if (currentCollection.value?.id === id) {
          currentCollection.value = null
        }

        // Remove from selected
        selectedCollections.value = selectedCollections.value.filter(
          (sid) => sid !== id
        )

        // Remove from favorites
        favorites.value = favorites.value.filter((f) => f.id !== id)

        // Rebuild tree
        collectionsTree.value = buildCollectionTree(collections.value)
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Move collection
    async function moveCollection(
      fromId: number,
      toId: number | null,
      newParentId?: number | null
    ): Promise<Collection> {
      isLoading.value = true
      error.value = null

      try {
        const targetParentId = newParentId !== undefined ? newParentId : toId
        const movedCollection = await collectionsService.moveCollection(fromId, {
          collection_id: fromId,
          new_parent_id: targetParentId
        })

        // Update in collections array
        const index = collections.value.findIndex((c) => c.id === fromId)
        if (index !== -1) {
          collections.value[index] = movedCollection
        }

        collectionsTree.value = buildCollectionTree(collections.value)

        invalidateCache()

        return movedCollection
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Bulk operation
    async function bulkCollectionOperation(
      operation: BulkCollectionOperation
    ): Promise<BulkOperationResponse> {
      // Validate max size
      if (operation.ids.length > MAX_BULK_OPERATION_SIZE) {
        throw new Error(
          `Maximum ${MAX_BULK_OPERATION_SIZE} collections allowed per bulk operation`
        )
      }

      isLoading.value = true
      error.value = null

      try {
        const response = await collectionsService.bulkOperation(operation)

        invalidateCache()
        await fetchCollections()

        return response
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Toggle favorite
    async function toggleFavorite(id: number): Promise<Collection> {
      isLoading.value = true
      error.value = null

      try {
        const updatedCollection = await collectionsService.toggleFavorite(id)

        // Update in collections array
        const index = collections.value.findIndex((c) => c.id === id)
        if (index !== -1) {
          collections.value[index] = updatedCollection
        }

        // Update current collection if it's the one being toggled
        if (currentCollection.value?.id === id) {
          currentCollection.value = updatedCollection
        }

        if (updatedCollection.is_favorite) {
          if (!favorites.value.find((f) => f.id === id)) {
            favorites.value.push(updatedCollection)
          }
        } else {
          favorites.value = favorites.value.filter((f) => f.id !== id)
        }

        invalidateCache()

        return updatedCollection
      } catch (err) {
        error.value = formatApiError(err)
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Fetch special collections
    async function fetchSpecialCollections(): Promise<void> {
      isLoading.value = true
      error.value = null

      try {
        const response: SpecialCollectionsResponse =
          await collectionsService.getSpecialCollections()

        favorites.value = response.favorites
        recentCollections.value = response.recent
        sharedWithMe.value = response.shared_with_me
        myUploads.value = response.my_uploads
        publicCollections.value = response.public_collections
      } catch (err) {
        const message = logCollectionError('Special collections fetch', err)
        error.value = message
        favorites.value = []
        recentCollections.value = []
        sharedWithMe.value = []
        myUploads.value = []
        publicCollections.value = []
        throw err
      } finally {
        isLoading.value = false
      }
    }

    // Actions - Tree node expansion
    function expandNode(nodeId: number): void {
      expandedNodes.value.add(nodeId)
    }

    function collapseNode(nodeId: number): void {
      expandedNodes.value.delete(nodeId)
    }

    function toggleNodeExpanded(nodeId: number): void {
      if (expandedNodes.value.has(nodeId)) {
        expandedNodes.value.delete(nodeId)
      } else {
        expandedNodes.value.add(nodeId)
      }
    }

    function isNodeExpanded(nodeId: number): boolean {
      return expandedNodes.value.has(nodeId)
    }

    // Actions - Drag-drop
    function setDraggedCollection(collection: Collection | null): void {
      draggedCollection.value = collection
    }

    // Actions - Selection
    function selectCollections(ids: number[]): void {
      selectedCollections.value = ids
    }

    function clearSelection(): void {
      selectedCollections.value = []
    }

    function toggleSelection(id: number): void {
      const index = selectedCollections.value.indexOf(id)
      if (index === -1) {
        selectedCollections.value.push(id)
      } else {
        selectedCollections.value.splice(index, 1)
      }
    }

    // Actions - Current collection
    function setCurrentCollection(collection: Collection | null): void {
      currentCollection.value = collection
    }

    // Helper - Build collection tree
    function buildCollectionTree(
      collectionsList: Collection[]
    ): CollectionTree[] {
      // Sort collections by name alphabetically
      const sorted = [...collectionsList].sort((a, b) =>
        a.name.localeCompare(b.name)
      )

      // Build a map for quick lookup
      const collectionMap = new Map<number, Collection>()
      sorted.forEach((c) => collectionMap.set(c.id, c))

      // Build tree structure
      const buildTree = (
        parentId: number | null,
        level: number
      ): CollectionTree[] => {
        const children = sorted.filter((c) => c.parent_id === parentId)
        return children.map((collection) => ({
          collection,
          children: buildTree(collection.id, level + 1),
          level
        }))
      }

      return buildTree(null, 0)
    }

    // Actions - Utility
    function clearError(): void {
      error.value = null
    }

    function invalidateCache(): void {
      // Reset the cache TTL so the next fetch hits the API after mutations.
      lastFetchTime.value = null
    }

    return {
      // State - Collections
      collections,
      currentCollection,
      collectionsTree,
      selectedCollections,
      totalCollectionsCount,

      // State - Special collections
      favorites,
      recentCollections,
      sharedWithMe,
      myUploads,
      publicCollections,

      // State - UI
      expandedNodes,
      draggedCollection,

      // Global state
      isLoading,
      error,
      lastFetchTime,

      // Computed - Permissions
      canCreateCollection,
      canDeleteCollection,
      canEditCollection,
      canShareCollection,

      // Computed - Tree structure
      rootCollections,
      flattenedTree,
      breadcrumbs,

      // Actions - Collections
      fetchCollections,
      fetchCollection,
      createCollection,
      updateCollection,
      deleteCollection,
      moveCollection,
      bulkCollectionOperation,
      toggleFavorite,

      // Actions - Special collections
      fetchSpecialCollections,

      // Actions - Tree nodes
      expandNode,
      collapseNode,
      toggleNodeExpanded,
      isNodeExpanded,

      // Actions - Drag-drop
      setDraggedCollection,

      // Actions - Selection
      selectCollections,
      clearSelection,
      toggleSelection,

      // Actions - Current collection
      setCurrentCollection,

      // Helper - Tree building
      buildCollectionTree,

      // Actions - Utility
      clearError,
      invalidateCache
    }
  },
  {
    persist: {
      paths: ['expandedNodes'] // Only persist expanded nodes, not data
    }
  }
)



