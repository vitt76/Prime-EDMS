/**
 * Mock Folders Data Layer
 * 
 * Unified folder tree combining:
 * - System Folders (Backend "Cabinets")
 * - Cloud Storage (Yandex.Disk integration)
 * 
 * Backend Mapping:
 * - type: 'local' → mayan.apps.cabinets.Cabinet model
 * - type: 'yandex' → mayan.apps.dam.services.yandex_disk
 */

export type FolderSource = 'local' | 'yandex'

export interface FolderNode {
  id: string
  name: string
  type: FolderSource
  parentId: string | null
  children: FolderNode[]
  expanded: boolean
  // Metadata
  assetCount: number
  createdAt: string
  updatedAt: string
  // Permissions
  canEdit: boolean
  canDelete: boolean
  canAddChildren: boolean
  // Visual
  icon?: string
  color?: string
}

export interface FolderTreeSection {
  id: string
  name: string
  type: FolderSource
  icon: 'folder' | 'cloud'
  color: string
  folders: FolderNode[]
  expanded: boolean
}

// ============================================================================
// MOCK DATA - SYSTEM FOLDERS (CABINETS)
// ============================================================================

const SYSTEM_FOLDERS: FolderNode[] = [
  {
    id: 'sys-1',
    name: 'Маркетинг',
    type: 'local',
    parentId: null,
    expanded: true,
    assetCount: 156,
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2025-11-20T14:30:00Z',
    canEdit: true,
    canDelete: false,
    canAddChildren: true,
    children: [
      {
        id: 'sys-1-1',
        name: 'Баннеры',
        type: 'local',
        parentId: 'sys-1',
        expanded: false,
        assetCount: 45,
        createdAt: '2024-02-01T09:00:00Z',
        updatedAt: '2025-11-18T11:20:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [
          {
            id: 'sys-1-1-1',
            name: 'Веб-баннеры',
            type: 'local',
            parentId: 'sys-1-1',
            expanded: false,
            assetCount: 23,
            createdAt: '2024-03-10T12:00:00Z',
            updatedAt: '2025-11-15T09:00:00Z',
            canEdit: true,
            canDelete: true,
            canAddChildren: true,
            children: [],
          },
          {
            id: 'sys-1-1-2',
            name: 'Социальные сети',
            type: 'local',
            parentId: 'sys-1-1',
            expanded: false,
            assetCount: 22,
            createdAt: '2024-03-10T12:00:00Z',
            updatedAt: '2025-11-10T16:45:00Z',
            canEdit: true,
            canDelete: true,
            canAddChildren: true,
            children: [],
          },
        ],
      },
      {
        id: 'sys-1-2',
        name: 'Презентации',
        type: 'local',
        parentId: 'sys-1',
        expanded: false,
        assetCount: 28,
        createdAt: '2024-02-15T14:00:00Z',
        updatedAt: '2025-11-22T10:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'sys-1-3',
        name: 'Брендбук',
        type: 'local',
        parentId: 'sys-1',
        expanded: false,
        assetCount: 12,
        createdAt: '2024-01-20T08:00:00Z',
        updatedAt: '2025-10-05T13:30:00Z',
        canEdit: true,
        canDelete: false,
        canAddChildren: false,
        children: [],
      },
    ],
  },
  {
    id: 'sys-2',
    name: 'Документы',
    type: 'local',
    parentId: null,
    expanded: false,
    assetCount: 89,
    createdAt: '2024-01-10T08:00:00Z',
    updatedAt: '2025-11-25T09:15:00Z',
    canEdit: true,
    canDelete: false,
    canAddChildren: true,
    children: [
      {
        id: 'sys-2-1',
        name: 'Контракты',
        type: 'local',
        parentId: 'sys-2',
        expanded: false,
        assetCount: 34,
        createdAt: '2024-01-12T10:00:00Z',
        updatedAt: '2025-11-24T16:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'sys-2-2',
        name: 'Отчёты',
        type: 'local',
        parentId: 'sys-2',
        expanded: false,
        assetCount: 55,
        createdAt: '2024-01-12T10:00:00Z',
        updatedAt: '2025-11-23T11:30:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
    ],
  },
  {
    id: 'sys-3',
    name: 'Фотосессии 2025',
    type: 'local',
    parentId: null,
    expanded: false,
    assetCount: 342,
    createdAt: '2025-01-05T09:00:00Z',
    updatedAt: '2025-11-26T08:00:00Z',
    canEdit: true,
    canDelete: true,
    canAddChildren: true,
    children: [
      {
        id: 'sys-3-1',
        name: 'Январь — Зимняя коллекция',
        type: 'local',
        parentId: 'sys-3',
        expanded: false,
        assetCount: 128,
        createdAt: '2025-01-10T10:00:00Z',
        updatedAt: '2025-02-01T14:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'sys-3-2',
        name: 'Март — Весенняя коллекция',
        type: 'local',
        parentId: 'sys-3',
        expanded: false,
        assetCount: 95,
        createdAt: '2025-03-15T09:00:00Z',
        updatedAt: '2025-04-10T11:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'sys-3-3',
        name: 'Ноябрь — Новогодняя',
        type: 'local',
        parentId: 'sys-3',
        expanded: false,
        assetCount: 119,
        createdAt: '2025-11-01T08:00:00Z',
        updatedAt: '2025-11-26T08:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
    ],
  },
  {
    id: 'sys-4',
    name: 'HR',
    type: 'local',
    parentId: null,
    expanded: false,
    assetCount: 23,
    createdAt: '2024-06-01T10:00:00Z',
    updatedAt: '2025-11-20T15:00:00Z',
    canEdit: true,
    canDelete: true,
    canAddChildren: true,
    children: [],
  },
]

// ============================================================================
// MOCK DATA - YANDEX.DISK FOLDERS
// ============================================================================

const YANDEX_FOLDERS: FolderNode[] = [
  {
    id: 'yd-1',
    name: 'Архив',
    type: 'yandex',
    parentId: null,
    expanded: false,
    assetCount: 1250,
    createdAt: '2023-01-01T00:00:00Z',
    updatedAt: '2025-11-15T12:00:00Z',
    canEdit: true,
    canDelete: false,
    canAddChildren: true,
    children: [
      {
        id: 'yd-1-1',
        name: '2024',
        type: 'yandex',
        parentId: 'yd-1',
        expanded: false,
        assetCount: 450,
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-12-31T23:59:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'yd-1-2',
        name: '2023',
        type: 'yandex',
        parentId: 'yd-1',
        expanded: false,
        assetCount: 380,
        createdAt: '2023-01-01T00:00:00Z',
        updatedAt: '2023-12-31T23:59:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'yd-1-3',
        name: 'Старые проекты',
        type: 'yandex',
        parentId: 'yd-1',
        expanded: false,
        assetCount: 420,
        createdAt: '2022-01-01T00:00:00Z',
        updatedAt: '2022-12-31T23:59:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
    ],
  },
  {
    id: 'yd-2',
    name: 'Исходники',
    type: 'yandex',
    parentId: null,
    expanded: true,
    assetCount: 89,
    createdAt: '2024-06-01T10:00:00Z',
    updatedAt: '2025-11-25T14:30:00Z',
    canEdit: true,
    canDelete: true,
    canAddChildren: true,
    children: [
      {
        id: 'yd-2-1',
        name: 'RAW файлы',
        type: 'yandex',
        parentId: 'yd-2',
        expanded: false,
        assetCount: 56,
        createdAt: '2024-06-05T12:00:00Z',
        updatedAt: '2025-11-24T10:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'yd-2-2',
        name: 'PSD проекты',
        type: 'yandex',
        parentId: 'yd-2',
        expanded: false,
        assetCount: 33,
        createdAt: '2024-06-10T09:00:00Z',
        updatedAt: '2025-11-20T16:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
    ],
  },
  {
    id: 'yd-3',
    name: 'Общий доступ',
    type: 'yandex',
    parentId: null,
    expanded: false,
    assetCount: 45,
    createdAt: '2025-01-15T08:00:00Z',
    updatedAt: '2025-11-26T09:00:00Z',
    canEdit: true,
    canDelete: true,
    canAddChildren: true,
    children: [
      {
        id: 'yd-3-1',
        name: 'Для клиентов',
        type: 'yandex',
        parentId: 'yd-3',
        expanded: false,
        assetCount: 28,
        createdAt: '2025-02-01T10:00:00Z',
        updatedAt: '2025-11-25T11:00:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
      {
        id: 'yd-3-2',
        name: 'Для партнёров',
        type: 'yandex',
        parentId: 'yd-3',
        expanded: false,
        assetCount: 17,
        createdAt: '2025-03-01T14:00:00Z',
        updatedAt: '2025-11-22T15:30:00Z',
        canEdit: true,
        canDelete: true,
        canAddChildren: true,
        children: [],
      },
    ],
  },
]

// ============================================================================
// TREE SECTIONS
// ============================================================================

export const FOLDER_TREE_SECTIONS: FolderTreeSection[] = [
  {
    id: 'section-system',
    name: 'Системные папки',
    type: 'local',
    icon: 'folder',
    color: 'amber',
    folders: SYSTEM_FOLDERS,
    expanded: true,
  },
  {
    id: 'section-yandex',
    name: 'Яндекс.Диск',
    type: 'yandex',
    icon: 'cloud',
    color: 'blue',
    folders: YANDEX_FOLDERS,
    expanded: true,
  },
]

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Find a folder by ID in the tree (recursive)
 */
export function findFolderById(
  folders: FolderNode[],
  id: string
): FolderNode | null {
  for (const folder of folders) {
    if (folder.id === id) return folder
    if (folder.children.length > 0) {
      const found = findFolderById(folder.children, id)
      if (found) return found
    }
  }
  return null
}

/**
 * Find a folder in all sections
 */
export function findFolderInTree(id: string): FolderNode | null {
  for (const section of FOLDER_TREE_SECTIONS) {
    const found = findFolderById(section.folders, id)
    if (found) return found
  }
  return null
}

/**
 * Get folder path (breadcrumb)
 */
export function getFolderPath(id: string): FolderNode[] {
  const path: FolderNode[] = []
  let current = findFolderInTree(id)
  
  while (current) {
    path.unshift(current)
    current = current.parentId ? findFolderInTree(current.parentId) : null
  }
  
  return path
}

/**
 * Get total asset count including children
 */
export function getTotalAssetCount(folder: FolderNode): number {
  let total = folder.assetCount
  for (const child of folder.children) {
    total += getTotalAssetCount(child)
  }
  return total
}

/**
 * Flatten tree to array
 */
export function flattenTree(folders: FolderNode[]): FolderNode[] {
  const result: FolderNode[] = []
  
  function traverse(nodes: FolderNode[]) {
    for (const node of nodes) {
      result.push(node)
      if (node.children.length > 0) {
        traverse(node.children)
      }
    }
  }
  
  traverse(folders)
  return result
}

/**
 * Get all folders as flat list (all sections)
 */
export function getAllFolders(): FolderNode[] {
  const all: FolderNode[] = []
  for (const section of FOLDER_TREE_SECTIONS) {
    all.push(...flattenTree(section.folders))
  }
  return all
}

/**
 * Move asset to folder (mock)
 */
export function moveAssetToFolder(
  assetId: number,
  folderId: string
): { success: boolean; folderName: string } {
  const folder = findFolderInTree(folderId)
  if (!folder) {
    return { success: false, folderName: '' }
  }
  
  // In real implementation, this would call the backend API
  // For mock, just return success
  return { success: true, folderName: folder.name }
}

