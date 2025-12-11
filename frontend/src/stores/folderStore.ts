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
  findFolderById,
  type FolderNode,
  type FolderTreeSection,
  type FolderSource,
} from '@/mocks/folders'
import {
  cabinetService,
} from '@/services/cabinetService'
import { useNotificationStore } from './notificationStore'

export const useFolderStore = defineStore(
  'folder',
  () => {
    // ========================================================================
    // STATE
    // ========================================================================
    
    // Helpers to keep Yandex data intact
    const yandexSectionTemplate = FOLDER_TREE_SECTIONS.find(
      section => section.type === 'yandex'
    )

    // Tree sections with folders (system from API, Yandex from mocks)
    const sections = ref<FolderTreeSection[]>([
      {
        id: 'section-system',
        name: 'Системные папки',
        type: 'local',
        icon: 'folder',
        color: 'amber',
        folders: [],
        expanded: true,
      },
      yandexSectionTemplate
        ? JSON.parse(JSON.stringify(yandexSectionTemplate))
        : {
            id: 'section-yandex',
            name: 'Яндекс.Диск',
            type: 'yandex' as FolderSource,
            icon: 'cloud' as const,
            color: 'blue',
            folders: [],
            expanded: true,
          },
    ])
    
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
      return findFolderInSections(selectedFolderId.value)
    })
    
    /**
     * Get breadcrumb path for selected folder
     */
    const selectedFolderPath = computed((): FolderNode[] => {
      if (!selectedFolderId.value) return []
      return getFolderPathFromSections(selectedFolderId.value)
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

    function getSystemSection(): FolderTreeSection {
      return (
        sections.value.find(section => section.type === 'local') ||
        sections.value[0]
      )
    }

    /**
     * Build breadcrumb path using current sections state
     */
    function getFolderPathFromSections(folderId: string): FolderNode[] {
      const path: FolderNode[] = []
      let current = findFolderInSections(folderId)

      while (current) {
        path.unshift(current)
        current = current.parentId
          ? findFolderInSections(current.parentId)
          : null
      }

      return path
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
        const path = getFolderPathFromSections(folderId)
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
      const targetFolder = findFolderInSections(folderId)

      if (!targetFolder || targetFolder.type !== 'local') {
        notificationStore.addNotification({
          type: 'error',
          title: 'Недоступно',
          message: 'Перемещение в эту папку недоступно',
        })
        return false
      }

      try {
        await cabinetService.addDocumentsToCabinet(
          Number(folderId),
          [assetId]
        )

        notificationStore.addNotification({
          type: 'success',
          title: 'Файл перемещён',
          message: `Файл перемещён в папку "${targetFolder.name}"`,
        })

        targetFolder.assetCount += 1
        return true
      } catch (error) {
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
      const targetFolder = findFolderInSections(folderId)

      if (!targetFolder || targetFolder.type !== 'local') {
        notificationStore.addNotification({
          type: 'error',
          title: 'Недоступно',
          message: 'Перемещение в эту папку недоступно',
        })
        return { success: 0, failed: assetIds.length }
      }

      try {
        await cabinetService.addDocumentsToCabinet(
          Number(folderId),
          assetIds
        )

        targetFolder.assetCount += assetIds.length

        notificationStore.addNotification({
          type: 'success',
          title: 'Файлы перемещены',
          message: `${assetIds.length} файл(ов) перемещено в папку "${targetFolder.name}"`,
        })

        return { success: assetIds.length, failed: 0 }
      } catch (error) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Ошибка перемещения',
          message: 'Не удалось переместить файлы в указанную папку',
        })
        return { success: 0, failed: assetIds.length }
      }
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

      if (type !== 'local') {
        notificationStore.addNotification({
          type: 'error',
          title: 'Создание недоступно',
          message: 'Создавать можно только системные папки',
        })
        return null
      }

      try {
        const newFolder = await cabinetService.createCabinet({
          label: name,
          parent: parentId ? Number(parentId) : null,
        })

        if (parentId) {
          const parent = findFolderInSections(parentId)
          if (parent) {
            parent.children.push(newFolder)
            expandFolder(parentId)
          }
        } else {
          const systemSection = getSystemSection()
          systemSection.folders.push(newFolder)
        }
        
        notificationStore.addNotification({
          type: 'success',
          title: 'Папка создана',
          message: `Папка "${name}" успешно создана`,
        })

        return newFolder
      } catch (error) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Ошибка создания',
          message: 'Не удалось создать папку',
        })
        return null
      }
    }
    
    /**
     * Rename folder
     */
    async function renameFolder(folderId: string, newName: string): Promise<boolean> {
      const notificationStore = useNotificationStore()

      const folder = findFolderInSections(folderId)

      if (!folder || folder.type !== 'local' || !folder.canEdit) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Переименование недоступно',
          message: 'Недостаточно прав для изменения этой папки',
        })
        return false
      }

      try {
        const updated = await cabinetService.updateCabinet(Number(folderId), {
          label: newName,
        })

        for (const section of sections.value) {
          if (
            updateFolderInTree(section.folders, folderId, { 
              name: updated.name,
              updatedAt: updated.updatedAt,
              canEdit: updated.canEdit,
              canDelete: updated.canDelete,
              canAddChildren: updated.canAddChildren,
            })
          ) {
            notificationStore.addNotification({
              type: 'success',
              title: 'Папка переименована',
              message: `Папка переименована в "${newName}"`,
            })
            return true
          }
        }
      } catch (error) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Ошибка сохранения',
          message: 'Не удалось переименовать папку',
        })
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
      
      if (folder.type !== 'local' || !folder.canDelete) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Удаление запрещено',
          message: 'Эту папку нельзя удалить',
        })
        return false
      }
      
      try {
        await cabinetService.deleteCabinet(Number(folderId))
        
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
      } catch (error) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Ошибка удаления',
          message: 'Не удалось удалить папку',
        })
      }
      
      return false
    }
    
    /**
     * Refresh folders from API
     */
    async function refreshFolders(): Promise<void> {
      isLoading.value = true
      
      const notificationStore = useNotificationStore()
      try {
        const systemTree = await cabinetService.getCabinetTree()
        const systemSection = getSystemSection()
        systemSection.folders = systemTree
      } catch (error) {
        notificationStore.addNotification({
          type: 'error',
          title: 'Ошибка загрузки',
          message: 'Не удалось загрузить системные папки',
        })
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

