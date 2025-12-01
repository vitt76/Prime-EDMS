/**
 * Folder Store
 * 
 * Manages the unified folder tree state including:
 * - System Folders (Cabinets)
 * - Cloud Storage (Yandex.Disk)
 * - Expansion states
 * - Selection
 * - Drag & Drop operations
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  FOLDER_TREE_SECTIONS,
  findFolderInTree,
  findFolderById,
  getFolderPath,
  moveAssetToFolder,
  type FolderNode,
  type FolderTreeSection,
  type FolderSource,
} from '@/mocks/folders'
import { useNotificationStore } from './notificationStore'

export const useFolderStore = defineStore(
  'folder',
  () => {
    // ========================================================================
    // STATE
    // ========================================================================
    
    // Tree sections with folders
    const sections = ref<FolderTreeSection[]>(
      JSON.parse(JSON.stringify(FOLDER_TREE_SECTIONS))
    )
    
    // Currently selected folder
    const selectedFolderId = ref<string | null>(null)
    
    // Loading state
    const isLoading = ref(false)
    
    // Drag & Drop state
    const dragOverFolderId = ref<string | null>(null)
    const isDragging = ref(false)
    
    // Search/filter
    const searchQuery = ref('')
    
    // ========================================================================
    // GETTERS
    // ========================================================================
    
    /**
     * Get all sections
     */
    const allSections = computed(() => sections.value)
    
    /**
     * Get system folders section
     */
    const systemFolders = computed(() =>
      sections.value.find(s => s.type === 'local')?.folders || []
    )
    
    /**
     * Get Yandex folders section
     */
    const yandexFolders = computed(() =>
      sections.value.find(s => s.type === 'yandex')?.folders || []
    )
    
    /**
     * Get currently selected folder
     */
    const selectedFolder = computed((): FolderNode | null => {
      if (!selectedFolderId.value) return null
      return findFolderInTree(selectedFolderId.value)
    })
    
    /**
     * Get breadcrumb path for selected folder
     */
    const selectedFolderPath = computed((): FolderNode[] => {
      if (!selectedFolderId.value) return []
      return getFolderPath(selectedFolderId.value)
    })
    
    /**
     * Check if a folder is expanded
     */
    const isFolderExpanded = computed(() => (folderId: string): boolean => {
      const folder = findFolderInSections(folderId)
      return folder?.expanded ?? false
    })
    
    /**
     * Check if a folder is selected
     */
    const isFolderSelected = computed(() => (folderId: string): boolean => {
      return selectedFolderId.value === folderId
    })
    
    /**
     * Check if a folder is being dragged over
     */
    const isFolderDragOver = computed(() => (folderId: string): boolean => {
      return dragOverFolderId.value === folderId
    })
    
    // ========================================================================
    // INTERNAL HELPERS
    // ========================================================================
    
    /**
     * Find a folder in the sections state (mutable)
     */
    function findFolderInSections(folderId: string): FolderNode | null {
      for (const section of sections.value) {
        const found = findFolderById(section.folders, folderId)
        if (found) return found
      }
      return null
    }
    
    /**
     * Update folder in tree (recursive)
     */
    function updateFolderInTree(
      folders: FolderNode[],
      folderId: string,
      updates: Partial<FolderNode>
    ): boolean {
      for (const folder of folders) {
        if (folder.id === folderId) {
          Object.assign(folder, updates)
          return true
        }
        if (folder.children.length > 0) {
          if (updateFolderInTree(folder.children, folderId, updates)) {
            return true
          }
        }
      }
      return false
    }
    
    // ========================================================================
    // ACTIONS
    // ========================================================================
    
    /**
     * Toggle folder expansion
     */
    function toggleFolder(folderId: string): void {
      for (const section of sections.value) {
        if (updateFolderInTree(section.folders, folderId, { 
          expanded: !findFolderInSections(folderId)?.expanded 
        })) {
          break
        }
      }
    }
    
    /**
     * Expand folder
     */
    function expandFolder(folderId: string): void {
      for (const section of sections.value) {
        if (updateFolderInTree(section.folders, folderId, { expanded: true })) {
          break
        }
      }
    }
    
    /**
     * Collapse folder
     */
    function collapseFolder(folderId: string): void {
      for (const section of sections.value) {
        if (updateFolderInTree(section.folders, folderId, { expanded: false })) {
          break
        }
      }
    }
    
    /**
     * Select folder
     */
    function selectFolder(folderId: string | null): void {
      selectedFolderId.value = folderId
      
      // Expand parent folders to make selection visible
      if (folderId) {
        const path = getFolderPath(folderId)
        for (const folder of path.slice(0, -1)) { // Exclude the selected folder itself
          expandFolder(folder.id)
        }
      }
    }
    
    /**
     * Toggle section expansion
     */
    function toggleSection(sectionId: string): void {
      const section = sections.value.find(s => s.id === sectionId)
      if (section) {
        section.expanded = !section.expanded
      }
    }
    
    /**
     * Set drag over state
     */
    function setDragOver(folderId: string | null): void {
      dragOverFolderId.value = folderId
    }
    
    /**
     * Set dragging state
     */
    function setDragging(dragging: boolean): void {
      isDragging.value = dragging
      if (!dragging) {
        dragOverFolderId.value = null
      }
    }
    
    /**
     * Handle asset drop onto folder
     */
    async function handleAssetDrop(
      assetId: number,
      folderId: string
    ): Promise<boolean> {
      const notificationStore = useNotificationStore()
      const result = moveAssetToFolder(assetId, folderId)
      
      if (result.success) {
        notificationStore.addNotification({
          type: 'success',
          title: 'Файл перемещён',
          message: `Файл перемещён в папку "${result.folderName}"`,
        })
        
        // Update folder asset count (mock)
        const folder = findFolderInSections(folderId)
        if (folder) {
          folder.assetCount++
        }
        
        return true
      } else {
        notificationStore.addNotification({
          type: 'error',
          title: 'Ошибка перемещения',
          message: 'Не удалось переместить файл в указанную папку',
        })
        return false
      }
    }
    
    /**
     * Handle multiple assets drop
     */
    async function handleBulkAssetDrop(
      assetIds: number[],
      folderId: string
    ): Promise<{ success: number; failed: number }> {
      const notificationStore = useNotificationStore()
      let success = 0
      let failed = 0
      
      for (const assetId of assetIds) {
        const result = moveAssetToFolder(assetId, folderId)
        if (result.success) {
          success++
        } else {
          failed++
        }
      }
      
      const folder = findFolderInSections(folderId)
      if (folder) {
        folder.assetCount += success
      }
      
      if (success > 0) {
        notificationStore.addNotification({
          type: 'success',
          title: 'Файлы перемещены',
          message: `${success} файл(ов) перемещено в папку "${folder?.name || 'Неизвестно'}"`,
        })
      }
      
      if (failed > 0) {
        notificationStore.addNotification({
          type: 'warning',
          title: 'Частичная ошибка',
          message: `${failed} файл(ов) не удалось переместить`,
        })
      }
      
      return { success, failed }
    }
    
    /**
     * Create new folder
     */
    async function createFolder(
      parentId: string | null,
      name: string,
      type: FolderSource
    ): Promise<FolderNode | null> {
      const notificationStore = useNotificationStore()
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300))
      
      const newFolder: FolderNode = {
        id: `${type === 'local' ? 'sys' : 'yd'}-new-${Date.now()}`,
        name,
        type,
        parentId,
        children: [],
        expanded: false,
        assetCount: 0,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
      }
      
      if (parentId) {
        // Add to parent folder
        const parent = findFolderInSections(parentId)
        if (parent) {
          parent.children.push(newFolder)
          expandFolder(parentId)
        }
      } else {
        // Add to section root
        const section = sections.value.find(s => s.type === type)
        if (section) {
          section.folders.push(newFolder)
        }
      }
      
      notificationStore.addNotification({
        type: 'success',
        title: 'Папка создана',
        message: `Папка "${name}" успешно создана`,
      })
      
      return newFolder
    }
    
    /**
     * Rename folder
     */
    async function renameFolder(folderId: string, newName: string): Promise<boolean> {
      const notificationStore = useNotificationStore()
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300))
      
      for (const section of sections.value) {
        if (updateFolderInTree(section.folders, folderId, { 
          name: newName,
          updatedAt: new Date().toISOString(),
        })) {
          notificationStore.addNotification({
            type: 'success',
            title: 'Папка переименована',
            message: `Папка переименована в "${newName}"`,
          })
          return true
        }
      }
      
      return false
    }
    
    /**
     * Delete folder
     */
    async function deleteFolder(folderId: string): Promise<boolean> {
      const notificationStore = useNotificationStore()
      const folder = findFolderInSections(folderId)
      
      if (!folder) return false
      
      if (!folder.canDelete) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Удаление запрещено',
          message: 'Эту папку нельзя удалить',
        })
        return false
      }
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Remove from parent or section
      function removeFromTree(folders: FolderNode[]): boolean {
        const index = folders.findIndex(f => f.id === folderId)
        if (index > -1) {
          folders.splice(index, 1)
          return true
        }
        for (const f of folders) {
          if (removeFromTree(f.children)) return true
        }
        return false
      }
      
      for (const section of sections.value) {
        if (removeFromTree(section.folders)) {
          if (selectedFolderId.value === folderId) {
            selectedFolderId.value = null
          }
          
          notificationStore.addNotification({
            type: 'success',
            title: 'Папка удалена',
            message: `Папка "${folder.name}" удалена`,
          })
          return true
        }
      }
      
      return false
    }
    
    /**
     * Refresh folders from API
     */
    async function refreshFolders(): Promise<void> {
      isLoading.value = true
      
      try {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // In real implementation, fetch from API
        // For now, just reset to mock data
        sections.value = JSON.parse(JSON.stringify(FOLDER_TREE_SECTIONS))
      } finally {
        isLoading.value = false
      }
    }
    
    /**
     * Set search query
     */
    function setSearchQuery(query: string): void {
      searchQuery.value = query
    }
    
    /**
     * Clear selection
     */
    function clearSelection(): void {
      selectedFolderId.value = null
    }
    
    // ========================================================================
    // RETURN
    // ========================================================================
    
    return {
      // State
      sections,
      selectedFolderId,
      isLoading,
      dragOverFolderId,
      isDragging,
      searchQuery,
      
      // Getters
      allSections,
      systemFolders,
      yandexFolders,
      selectedFolder,
      selectedFolderPath,
      isFolderExpanded,
      isFolderSelected,
      isFolderDragOver,
      
      // Actions
      toggleFolder,
      expandFolder,
      collapseFolder,
      selectFolder,
      toggleSection,
      setDragOver,
      setDragging,
      handleAssetDrop,
      handleBulkAssetDrop,
      createFolder,
      renameFolder,
      deleteFolder,
      refreshFolders,
      setSearchQuery,
      clearSelection,
    }
  },
  {
    persist: {
      paths: ['selectedFolderId'], // Only persist selection
    },
  }
)

