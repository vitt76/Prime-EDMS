/**
 * Mock Workflow States, Transitions, and History
 * Maps to Backend: /api/v4/workflows/
 * 
 * Workflows define the lifecycle of assets through various states.
 * Each state can have allowed transitions to other states.
 */

export type WorkflowStateType = 'initial' | 'intermediate' | 'final'

export interface WorkflowState {
  id: string
  name: string
  label: string
  description: string
  type: WorkflowStateType
  color: string // Tailwind color class
  icon: string // Heroicon name
  order: number
  allowedActions: string[] // Actions available in this state
}

export interface WorkflowTransition {
  id: string
  name: string
  label: string
  description: string
  fromState: string // State ID
  toState: string // State ID
  icon: string
  color: string
  requiresComment: boolean
  requiresPermission?: string
  confirmationMessage?: string
}

export interface Workflow {
  id: number
  name: string
  label: string
  description: string
  documentTypes: string[] // Which document types this workflow applies to
  states: WorkflowState[]
  transitions: WorkflowTransition[]
  initialState: string // State ID
  isDefault: boolean
  createdAt: string
  updatedAt: string
}

export interface WorkflowHistoryEntry {
  id: number
  assetId: number
  workflowId: number
  fromState: string | null
  toState: string
  transitionId: string | null
  comment: string | null
  performedBy: {
    id: number
    name: string
    avatar?: string
  }
  performedAt: string
  metadata?: Record<string, unknown>
}

export interface AssetWorkflowState {
  assetId: number
  workflowId: number
  currentState: string
  enteredAt: string
  history: WorkflowHistoryEntry[]
}

// ============================================================
// MOCK WORKFLOW DEFINITIONS
// ============================================================

export const WORKFLOWS: Workflow[] = [
  {
    id: 1,
    name: 'asset_approval',
    label: 'Согласование активов',
    description: 'Стандартный процесс согласования медиа-активов',
    documentTypes: ['image', 'video', 'document', 'audio'],
    isDefault: true,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2025-10-15T12:00:00Z',
    initialState: 'draft',
    states: [
      {
        id: 'draft',
        name: 'draft',
        label: 'Черновик',
        description: 'Актив загружен, но ещё не отправлен на проверку',
        type: 'initial',
        color: 'gray',
        icon: 'PencilSquareIcon',
        order: 1,
        allowedActions: ['edit', 'delete', 'tag', 'metadata']
      },
      {
        id: 'pending_review',
        name: 'pending_review',
        label: 'На проверке',
        description: 'Актив отправлен на проверку ответственному',
        type: 'intermediate',
        color: 'amber',
        icon: 'ClockIcon',
        order: 2,
        allowedActions: ['view', 'comment', 'metadata']
      },
      {
        id: 'in_revision',
        name: 'in_revision',
        label: 'На доработке',
        description: 'Актив возвращён на доработку автору',
        type: 'intermediate',
        color: 'orange',
        icon: 'ArrowPathIcon',
        order: 3,
        allowedActions: ['edit', 'upload_version', 'tag', 'metadata']
      },
      {
        id: 'approved',
        name: 'approved',
        label: 'Согласовано',
        description: 'Актив прошёл проверку и одобрен к использованию',
        type: 'intermediate',
        color: 'green',
        icon: 'CheckCircleIcon',
        order: 4,
        allowedActions: ['view', 'download', 'share', 'distribute']
      },
      {
        id: 'published',
        name: 'published',
        label: 'Опубликовано',
        description: 'Актив опубликован и доступен внешним пользователям',
        type: 'final',
        color: 'blue',
        icon: 'GlobeAltIcon',
        order: 5,
        allowedActions: ['view', 'download', 'share', 'analytics']
      },
      {
        id: 'archived',
        name: 'archived',
        label: 'В архиве',
        description: 'Актив перемещён в архив',
        type: 'final',
        color: 'slate',
        icon: 'ArchiveBoxIcon',
        order: 6,
        allowedActions: ['view', 'restore']
      },
      {
        id: 'rejected',
        name: 'rejected',
        label: 'Отклонено',
        description: 'Актив отклонён и не может быть использован',
        type: 'final',
        color: 'red',
        icon: 'XCircleIcon',
        order: 7,
        allowedActions: ['view', 'delete']
      }
    ],
    transitions: [
      {
        id: 'submit_for_review',
        name: 'submit_for_review',
        label: 'Отправить на проверку',
        description: 'Отправить актив на проверку ответственному лицу',
        fromState: 'draft',
        toState: 'pending_review',
        icon: 'PaperAirplaneIcon',
        color: 'primary',
        requiresComment: false,
        confirmationMessage: 'Отправить актив на проверку?'
      },
      {
        id: 'approve',
        name: 'approve',
        label: 'Согласовать',
        description: 'Одобрить актив к использованию',
        fromState: 'pending_review',
        toState: 'approved',
        icon: 'CheckIcon',
        color: 'success',
        requiresComment: false,
        requiresPermission: 'asset.approve',
        confirmationMessage: 'Согласовать актив?'
      },
      {
        id: 'request_revision',
        name: 'request_revision',
        label: 'На доработку',
        description: 'Вернуть актив автору для доработки',
        fromState: 'pending_review',
        toState: 'in_revision',
        icon: 'ArrowUturnLeftIcon',
        color: 'warning',
        requiresComment: true,
        requiresPermission: 'asset.review',
        confirmationMessage: 'Вернуть актив на доработку? Укажите причину.'
      },
      {
        id: 'reject',
        name: 'reject',
        label: 'Отклонить',
        description: 'Отклонить актив без возможности доработки',
        fromState: 'pending_review',
        toState: 'rejected',
        icon: 'XMarkIcon',
        color: 'danger',
        requiresComment: true,
        requiresPermission: 'asset.reject',
        confirmationMessage: 'Отклонить актив? Это действие нельзя отменить. Укажите причину.'
      },
      {
        id: 'resubmit',
        name: 'resubmit',
        label: 'Повторно отправить',
        description: 'Отправить доработанный актив на повторную проверку',
        fromState: 'in_revision',
        toState: 'pending_review',
        icon: 'ArrowPathIcon',
        color: 'primary',
        requiresComment: false,
        confirmationMessage: 'Отправить на повторную проверку?'
      },
      {
        id: 'publish',
        name: 'publish',
        label: 'Опубликовать',
        description: 'Опубликовать актив для внешнего доступа',
        fromState: 'approved',
        toState: 'published',
        icon: 'GlobeAltIcon',
        color: 'success',
        requiresComment: false,
        requiresPermission: 'asset.publish',
        confirmationMessage: 'Опубликовать актив?'
      },
      {
        id: 'unpublish',
        name: 'unpublish',
        label: 'Снять с публикации',
        description: 'Снять актив с публикации',
        fromState: 'published',
        toState: 'approved',
        icon: 'EyeSlashIcon',
        color: 'warning',
        requiresComment: true,
        requiresPermission: 'asset.unpublish',
        confirmationMessage: 'Снять актив с публикации? Укажите причину.'
      },
      {
        id: 'archive',
        name: 'archive',
        label: 'В архив',
        description: 'Переместить актив в архив',
        fromState: 'approved',
        toState: 'archived',
        icon: 'ArchiveBoxIcon',
        color: 'neutral',
        requiresComment: false,
        confirmationMessage: 'Переместить актив в архив?'
      },
      {
        id: 'archive_published',
        name: 'archive_published',
        label: 'В архив',
        description: 'Переместить опубликованный актив в архив',
        fromState: 'published',
        toState: 'archived',
        icon: 'ArchiveBoxIcon',
        color: 'neutral',
        requiresComment: true,
        confirmationMessage: 'Актив будет снят с публикации и перемещён в архив. Укажите причину.'
      },
      {
        id: 'restore',
        name: 'restore',
        label: 'Восстановить',
        description: 'Восстановить актив из архива',
        fromState: 'archived',
        toState: 'approved',
        icon: 'ArrowUpTrayIcon',
        color: 'primary',
        requiresComment: false,
        confirmationMessage: 'Восстановить актив из архива?'
      }
    ]
  }
]

// ============================================================
// MOCK ASSET WORKFLOW STATES
// ============================================================

const MOCK_USERS = [
  { id: 1, name: 'Иванов А.А.', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face' },
  { id: 2, name: 'Петров Б.В.', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=32&h=32&fit=crop&crop=face' },
  { id: 3, name: 'Сидорова В.Г.', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=32&h=32&fit=crop&crop=face' },
  { id: 4, name: 'Козлов Д.Е.', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=32&h=32&fit=crop&crop=face' }
]

export const ASSET_WORKFLOW_STATES: Map<number, AssetWorkflowState> = new Map()

// Initialize with some mock data
function initializeAssetWorkflowStates() {
  // Asset 1 - In Review
  ASSET_WORKFLOW_STATES.set(1, {
    assetId: 1,
    workflowId: 1,
    currentState: 'pending_review',
    enteredAt: '2025-11-27T14:30:00Z',
    history: [
      {
        id: 1,
        assetId: 1,
        workflowId: 1,
        fromState: null,
        toState: 'draft',
        transitionId: null,
        comment: null,
        performedBy: MOCK_USERS[0],
        performedAt: '2025-11-25T10:00:00Z'
      },
      {
        id: 2,
        assetId: 1,
        workflowId: 1,
        fromState: 'draft',
        toState: 'pending_review',
        transitionId: 'submit_for_review',
        comment: null,
        performedBy: MOCK_USERS[0],
        performedAt: '2025-11-27T14:30:00Z'
      }
    ]
  })

  // Asset 2 - Approved
  ASSET_WORKFLOW_STATES.set(2, {
    assetId: 2,
    workflowId: 1,
    currentState: 'approved',
    enteredAt: '2025-11-26T16:45:00Z',
    history: [
      {
        id: 3,
        assetId: 2,
        workflowId: 1,
        fromState: null,
        toState: 'draft',
        transitionId: null,
        comment: null,
        performedBy: MOCK_USERS[1],
        performedAt: '2025-11-20T09:00:00Z'
      },
      {
        id: 4,
        assetId: 2,
        workflowId: 1,
        fromState: 'draft',
        toState: 'pending_review',
        transitionId: 'submit_for_review',
        comment: null,
        performedBy: MOCK_USERS[1],
        performedAt: '2025-11-22T11:30:00Z'
      },
      {
        id: 5,
        assetId: 2,
        workflowId: 1,
        fromState: 'pending_review',
        toState: 'approved',
        transitionId: 'approve',
        comment: 'Отлично! Качество соответствует требованиям.',
        performedBy: MOCK_USERS[2],
        performedAt: '2025-11-26T16:45:00Z'
      }
    ]
  })

  // Asset 3 - Published
  ASSET_WORKFLOW_STATES.set(3, {
    assetId: 3,
    workflowId: 1,
    currentState: 'published',
    enteredAt: '2025-11-15T10:00:00Z',
    history: [
      {
        id: 6,
        assetId: 3,
        workflowId: 1,
        fromState: null,
        toState: 'draft',
        transitionId: null,
        comment: null,
        performedBy: MOCK_USERS[0],
        performedAt: '2025-11-01T08:00:00Z'
      },
      {
        id: 7,
        assetId: 3,
        workflowId: 1,
        fromState: 'draft',
        toState: 'pending_review',
        transitionId: 'submit_for_review',
        comment: null,
        performedBy: MOCK_USERS[0],
        performedAt: '2025-11-05T14:00:00Z'
      },
      {
        id: 8,
        assetId: 3,
        workflowId: 1,
        fromState: 'pending_review',
        toState: 'approved',
        transitionId: 'approve',
        comment: null,
        performedBy: MOCK_USERS[3],
        performedAt: '2025-11-10T09:30:00Z'
      },
      {
        id: 9,
        assetId: 3,
        workflowId: 1,
        fromState: 'approved',
        toState: 'published',
        transitionId: 'publish',
        comment: 'Готово к публикации на сайте',
        performedBy: MOCK_USERS[2],
        performedAt: '2025-11-15T10:00:00Z'
      }
    ]
  })

  // Asset 5 - In Revision
  ASSET_WORKFLOW_STATES.set(5, {
    assetId: 5,
    workflowId: 1,
    currentState: 'in_revision',
    enteredAt: '2025-11-28T09:00:00Z',
    history: [
      {
        id: 10,
        assetId: 5,
        workflowId: 1,
        fromState: null,
        toState: 'draft',
        transitionId: null,
        comment: null,
        performedBy: MOCK_USERS[1],
        performedAt: '2025-11-24T15:00:00Z'
      },
      {
        id: 11,
        assetId: 5,
        workflowId: 1,
        fromState: 'draft',
        toState: 'pending_review',
        transitionId: 'submit_for_review',
        comment: null,
        performedBy: MOCK_USERS[1],
        performedAt: '2025-11-26T10:00:00Z'
      },
      {
        id: 12,
        assetId: 5,
        workflowId: 1,
        fromState: 'pending_review',
        toState: 'in_revision',
        transitionId: 'request_revision',
        comment: 'Необходимо улучшить качество изображения. Слишком много шума в тенях.',
        performedBy: MOCK_USERS[2],
        performedAt: '2025-11-28T09:00:00Z'
      }
    ]
  })

  // Initialize remaining assets as drafts
  for (let i = 4; i <= 75; i++) {
    if (!ASSET_WORKFLOW_STATES.has(i)) {
      const randomUser = MOCK_USERS[Math.floor(Math.random() * MOCK_USERS.length)]
      const states = ['draft', 'pending_review', 'approved', 'published', 'archived']
      const weights = [30, 20, 25, 15, 10] // Probability weights
      
      let randomState = 'draft'
      const rand = Math.random() * 100
      let cumulative = 0
      for (let j = 0; j < states.length; j++) {
        cumulative += weights[j]
        if (rand < cumulative) {
          randomState = states[j]
          break
        }
      }
      
      const createdDate = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
      
      ASSET_WORKFLOW_STATES.set(i, {
        assetId: i,
        workflowId: 1,
        currentState: randomState,
        enteredAt: createdDate.toISOString(),
        history: [
          {
            id: 100 + i,
            assetId: i,
            workflowId: 1,
            fromState: null,
            toState: 'draft',
            transitionId: null,
            comment: null,
            performedBy: randomUser,
            performedAt: createdDate.toISOString()
          }
        ]
      })
    }
  }
}

// Initialize on module load
initializeAssetWorkflowStates()

// ============================================================
// HELPER FUNCTIONS
// ============================================================

let historyIdCounter = 1000

/**
 * Get default workflow
 */
export function getDefaultWorkflow(): Workflow {
  return WORKFLOWS.find(w => w.isDefault) || WORKFLOWS[0]
}

/**
 * Get workflow by ID
 */
export function getWorkflowById(id: number): Workflow | undefined {
  return WORKFLOWS.find(w => w.id === id)
}

/**
 * Get asset workflow state
 */
export function getAssetWorkflowState(assetId: number): AssetWorkflowState | undefined {
  // Initialize if not exists
  if (!ASSET_WORKFLOW_STATES.has(assetId)) {
    const workflow = getDefaultWorkflow()
    ASSET_WORKFLOW_STATES.set(assetId, {
      assetId,
      workflowId: workflow.id,
      currentState: workflow.initialState,
      enteredAt: new Date().toISOString(),
      history: [{
        id: historyIdCounter++,
        assetId,
        workflowId: workflow.id,
        fromState: null,
        toState: workflow.initialState,
        transitionId: null,
        comment: null,
        performedBy: { id: 1, name: 'Система' },
        performedAt: new Date().toISOString()
      }]
    })
  }
  return ASSET_WORKFLOW_STATES.get(assetId)
}

/**
 * Get current workflow state details
 */
export function getCurrentState(assetId: number): WorkflowState | undefined {
  const assetState = getAssetWorkflowState(assetId)
  if (!assetState) return undefined
  
  const workflow = getWorkflowById(assetState.workflowId)
  if (!workflow) return undefined
  
  return workflow.states.find(s => s.id === assetState.currentState)
}

/**
 * Get available transitions for an asset
 */
export function getAvailableTransitions(assetId: number): WorkflowTransition[] {
  const assetState = getAssetWorkflowState(assetId)
  if (!assetState) return []
  
  const workflow = getWorkflowById(assetState.workflowId)
  if (!workflow) return []
  
  return workflow.transitions.filter(t => t.fromState === assetState.currentState)
}

/**
 * Execute a workflow transition
 */
export function executeTransition(
  assetId: number,
  transitionId: string,
  comment: string | null = null,
  performedBy: { id: number; name: string; avatar?: string } = { id: 1, name: 'Текущий пользователь' }
): { success: boolean; error?: string; newState?: WorkflowState } {
  const assetState = getAssetWorkflowState(assetId)
  if (!assetState) {
    return { success: false, error: 'Asset not found' }
  }
  
  const workflow = getWorkflowById(assetState.workflowId)
  if (!workflow) {
    return { success: false, error: 'Workflow not found' }
  }
  
  const transition = workflow.transitions.find(t => t.id === transitionId)
  if (!transition) {
    return { success: false, error: 'Transition not found' }
  }
  
  if (transition.fromState !== assetState.currentState) {
    return { success: false, error: 'Transition not available from current state' }
  }
  
  if (transition.requiresComment && !comment) {
    return { success: false, error: 'Comment is required for this transition' }
  }
  
  const now = new Date().toISOString()
  
  // Add history entry
  assetState.history.push({
    id: historyIdCounter++,
    assetId,
    workflowId: assetState.workflowId,
    fromState: assetState.currentState,
    toState: transition.toState,
    transitionId,
    comment,
    performedBy,
    performedAt: now
  })
  
  // Update current state
  assetState.currentState = transition.toState
  assetState.enteredAt = now
  
  const newState = workflow.states.find(s => s.id === transition.toState)
  
  return { success: true, newState }
}

/**
 * Get workflow history for an asset
 */
export function getWorkflowHistory(assetId: number): WorkflowHistoryEntry[] {
  const assetState = getAssetWorkflowState(assetId)
  return assetState?.history || []
}

/**
 * Get state label by state ID
 */
export function getStateLabel(stateId: string, workflowId: number = 1): string {
  const workflow = getWorkflowById(workflowId)
  const state = workflow?.states.find(s => s.id === stateId)
  return state?.label || stateId
}

/**
 * Get transition label by transition ID
 */
export function getTransitionLabel(transitionId: string, workflowId: number = 1): string {
  const workflow = getWorkflowById(workflowId)
  const transition = workflow?.transitions.find(t => t.id === transitionId)
  return transition?.label || transitionId
}

