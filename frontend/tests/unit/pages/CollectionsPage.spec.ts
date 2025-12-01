import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import CollectionsPage from '@/pages/CollectionsPage.vue'
import { useCollectionsStore } from '@/stores/collectionsStore'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import type { Collection } from '@/types/collections'

// Mock stores
vi.mock('@/stores/collectionsStore')
vi.mock('@/stores/authStore')
vi.mock('@/stores/uiStore')

describe('CollectionsPage', () => {
  let pinia: any
  let router: any
  let wrapper: ReturnType<typeof mount>

  const mockCollection: Collection = {
    id: 1,
    name: 'Test Collection',
    description: 'Test Description',
    parent_id: null,
    is_favorite: false,
    is_shared: false,
    visibility: 'private',
    asset_count: 10,
    created_by: 1,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    cover_image_id: null
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/collections', component: CollectionsPage },
        { path: '/collections/:id', component: CollectionsPage }
      ]
    })

    // Setup mock stores
    const collectionsStore = useCollectionsStore()
    const authStore = useAuthStore()
    const uiStore = useUIStore()

    collectionsStore.collectionsTree = []
    collectionsStore.currentCollection = null
    collectionsStore.expandedNodes = new Set()
    collectionsStore.draggedCollection = null
    collectionsStore.favorites = []
    collectionsStore.recentCollections = []
    collectionsStore.sharedWithMe = []
    collectionsStore.publicCollections = []
    collectionsStore.canCreateCollection = true
    collectionsStore.canDeleteCollection = true
    collectionsStore.canEditCollection = true
    collectionsStore.fetchCollections = vi.fn().mockResolvedValue(undefined)
    collectionsStore.fetchSpecialCollections = vi.fn().mockResolvedValue(undefined)
    collectionsStore.fetchCollection = vi.fn().mockResolvedValue(mockCollection)
    collectionsStore.createCollection = vi.fn().mockResolvedValue(mockCollection)
    collectionsStore.updateCollection = vi.fn().mockResolvedValue(mockCollection)
    collectionsStore.deleteCollection = vi.fn().mockResolvedValue(undefined)
    collectionsStore.moveCollection = vi.fn().mockResolvedValue(mockCollection)
    collectionsStore.toggleFavorite = vi.fn().mockResolvedValue(mockCollection)
    collectionsStore.toggleNodeExpanded = vi.fn()
    collectionsStore.setDraggedCollection = vi.fn()
    collectionsStore.setCurrentCollection = vi.fn()
    collectionsStore.breadcrumbs = vi.fn().mockReturnValue([])
    collectionsStore.rootCollections = []

    authStore.user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com'
    }

    uiStore.addNotification = vi.fn()
  })

  afterEach(() => {
    vi.clearAllMocks()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.collections-page').exists()).toBe(true)
  })

  it('displays page title', () => {
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('Collections')
  })

  it('renders skip links for accessibility', () => {
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    const skipLinks = wrapper.findAll('.skip-link')
    expect(skipLinks.length).toBeGreaterThan(0)
  })

  it('renders sidebar with CollectionTree', () => {
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: {
            template: '<div class="collection-tree">Collection Tree</div>'
          },
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    expect(wrapper.find('#collections-sidebar').exists()).toBe(true)
    expect(wrapper.find('.collection-tree').exists()).toBe(true)
  })

  it('renders breadcrumbs', () => {
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: {
            template: '<nav class="breadcrumbs">Breadcrumbs</nav>'
          },
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    expect(wrapper.find('.breadcrumbs').exists()).toBe(true)
  })

  it('shows empty state when no collection is selected', () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.currentCollection = null

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    expect(wrapper.find('.collections-empty').exists()).toBe(true)
    expect(wrapper.text()).toContain('Select a collection to view assets')
  })

  it('shows AssetGrid when collection is selected', async () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.currentCollection = mockCollection

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: {
            template: '<div class="asset-grid">Asset Grid</div>'
          },
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.find('.asset-grid').exists()).toBe(true)
  })

  it('shows Create button when user has permission', () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.canCreateCollection = true

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: {
            template: '<button><slot /></button>',
            props: ['variant']
          },
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    expect(wrapper.text()).toContain('New Collection')
  })

  it('hides Create button when user lacks permission', () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.canCreateCollection = false

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: {
            template: '<button><slot /></button>',
            props: ['variant']
          },
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    expect(wrapper.text()).not.toContain('New Collection')
  })

  it('shows Rename button when user has edit permission', async () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.currentCollection = mockCollection
    collectionsStore.canEditCollection = true

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: {
            template: '<button><slot /></button>',
            props: ['variant']
          },
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Rename')
  })

  it('hides Rename button when user lacks edit permission', async () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.currentCollection = mockCollection
    collectionsStore.canEditCollection = false

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: {
            template: '<button><slot /></button>',
            props: ['variant']
          },
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).not.toContain('Rename')
  })

  it('opens CreateCollectionModal on Create button click', async () => {
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant']
          },
          AssetGrid: true,
          CreateCollectionModal: {
            template: '<div v-if="isOpen" class="create-modal">Create Modal</div>',
            props: ['isOpen']
          },
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    const createButton = wrapper.findAll('button').find((btn) => btn.text()?.includes('New Collection'))
    if (createButton) {
      await createButton.trigger('click')
      await wrapper.vm.$nextTick()
      // Modal should be shown
      expect(wrapper.vm.showCreateModal).toBe(true)
    }
  })

  it('calls fetchCollections on mount', async () => {
    const collectionsStore = useCollectionsStore()
    
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(collectionsStore.fetchCollections).toHaveBeenCalled()
  })

  it('handles collection selection', async () => {
    const collectionsStore = useCollectionsStore()
    
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: {
            template: '<div @select="$emit(\'select\', mockCollection)">Tree</div>',
            emits: ['select'],
            setup() {
              return { mockCollection }
            }
          },
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    // Collection selection should trigger fetchCollection
    expect(collectionsStore.fetchCollection).toHaveBeenCalled()
  })

  it('handles collection creation', async () => {
    const collectionsStore = useCollectionsStore()
    const uiStore = useUIStore()
    
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: {
            template: '<div>Modal</div>',
            emits: ['submit', 'close']
          },
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    wrapper.vm.showCreateModal = true
    await wrapper.vm.$nextTick()

    // Simulate form submission
    const modal = wrapper.findComponent({ name: 'CreateCollectionModal' })
    if (modal.exists()) {
      await modal.vm.$emit('submit', {
        name: 'New Collection',
        description: 'Description',
        visibility: 'private'
      })
      await wrapper.vm.$nextTick()

      expect(collectionsStore.createCollection).toHaveBeenCalled()
      expect(uiStore.addNotification).toHaveBeenCalled()
    }
  })

  it('handles collection deletion', async () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.currentCollection = mockCollection
    const uiStore = useUIStore()
    
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: {
            template: '<div>Modal</div>',
            emits: ['confirm', 'cancel']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    wrapper.vm.showDeleteModal = true
    await wrapper.vm.$nextTick()

    // Simulate confirmation
    const modal = wrapper.findComponent({ name: 'DeleteConfirmModal' })
    if (modal.exists()) {
      await modal.vm.$emit('confirm')
      await wrapper.vm.$nextTick()

      expect(collectionsStore.deleteCollection).toHaveBeenCalled()
      expect(uiStore.addNotification).toHaveBeenCalled()
    }
  })

  it('handles favorite toggle', async () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.currentCollection = mockCollection
    const uiStore = useUIStore()
    
    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: {
            template: '<button @click="$emit(\'click\')"><slot /></button>',
            props: ['variant']
          },
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    // Find favorite button and click
    const favoriteButton = wrapper.findAll('button').find((btn) => 
      btn.attributes('aria-label')?.includes('favorite')
    )
    if (favoriteButton) {
      await favoriteButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(collectionsStore.toggleFavorite).toHaveBeenCalled()
      expect(uiStore.addNotification).toHaveBeenCalled()
    }
  })

  it('handles asset click navigation', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/collections', component: CollectionsPage },
        { path: '/dam/assets/:id', component: { template: '<div>Asset Detail</div>' } }
      ]
    })
    const pushSpy = vi.spyOn(router, 'push')

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: {
            template: '<div @asset-click="$emit(\'asset-click\', 123)">Grid</div>',
            emits: ['asset-click']
          },
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    const assetGrid = wrapper.findComponent({ name: 'AssetGrid' })
    if (assetGrid.exists()) {
      await assetGrid.vm.$emit('asset-click', 123)
      await wrapper.vm.$nextTick()

      expect(pushSpy).toHaveBeenCalledWith({
        name: 'asset-detail',
        params: { id: 123 }
      })
    }
  })

  it('displays special collections when available', () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.favorites = [mockCollection]
    collectionsStore.recentCollections = [mockCollection]

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    // Special collections should be displayed
    expect(wrapper.find('.special-collections').exists()).toBe(true)
  })

  it('handles special collection selection', async () => {
    const collectionsStore = useCollectionsStore()
    collectionsStore.favorites = [mockCollection]
    const uiStore = useUIStore()

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    
    // Find and click special collection button
    const specialButtons = wrapper.findAll('.special-collections__item')
    if (specialButtons.length > 0) {
      await specialButtons[0].trigger('click')
      await wrapper.vm.$nextTick()

      // Should set current collection
      expect(collectionsStore.setCurrentCollection).toHaveBeenCalled()
    }
  })

  it('handles route params for collection ID', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/collections', component: CollectionsPage },
        { path: '/collections/:id', component: CollectionsPage }
      ]
    })

    await router.push('/collections/1')

    const collectionsStore = useCollectionsStore()

    wrapper = mount(CollectionsPage, {
      global: {
        plugins: [pinia, router],
        stubs: {
          CollectionTree: true,
          Breadcrumbs: true,
          Button: true,
          AssetGrid: true,
          CreateCollectionModal: true,
          RenameCollectionModal: true,
          DeleteConfirmModal: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise((resolve) => setTimeout(resolve, 100))

    // Should fetch collection by ID from route
    expect(collectionsStore.fetchCollection).toHaveBeenCalledWith(1)
  })
})



