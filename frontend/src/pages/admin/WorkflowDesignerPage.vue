// @ts-nocheck
<template>
  <div class="workflow-designer">
    <!-- Toolbar -->
    <div class="workflow-designer__toolbar">
      <Button
        v-if="canCreateWorkflow"
        variant="primary"
        @click="handleCreateWorkflow"
        aria-label="Create new workflow"
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
        Create Workflow
      </Button>

      <div v-if="currentWorkflow" class="workflow-designer__workflow-info">
        <Input
          v-model="workflowFormData.name"
          placeholder="Workflow name"
          class="workflow-name-input"
        />
        <Button
          variant="secondary"
          size="sm"
          @click="handleSaveWorkflow"
          :loading="isSavingWorkflow"
          :disabled="!hasWorkflowChanges"
        >
          Save
        </Button>
        <Button
          variant="ghost"
          size="sm"
          @click="handleDeleteWorkflow"
          :disabled="!canDeleteWorkflow"
        >
          Delete
        </Button>
      </div>

      <div class="workflow-designer__zoom-controls">
        <Button
          variant="ghost"
          size="sm"
          @click="handleZoomOut"
          :disabled="zoom <= 0.5"
          aria-label="Zoom out"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
          </svg>
        </Button>
        <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
        <Button
          variant="ghost"
          size="sm"
          @click="handleZoomIn"
          :disabled="zoom >= 2"
          aria-label="Zoom in"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
          </svg>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          @click="handleResetZoom"
          aria-label="Reset zoom"
        >
          Reset
        </Button>
      </div>
    </div>

    <!-- Main Layout -->
    <div class="workflow-designer__layout">
      <!-- Canvas Area -->
      <div class="workflow-designer__canvas-area">
        <WorkflowCanvas
          :nodes="workflowFormData.nodes"
          :transitions="workflowFormData.transitions"
          :zoom="zoom"
          :pan="pan"
          :selected-node-id="selectedNodeId"
          :selected-transition-id="selectedTransitionId"
          :show-grid="showGrid"
          @node-click="handleNodeClick"
          @transition-click="handleTransitionClick"
          @node-drag="handleNodeDrag"
          @pan-change="handlePanChange"
          @zoom-change="handleZoomChange"
        />
      </div>

      <!-- Right Panel: Node/Transition Editor -->
      <div class="workflow-designer__properties">
        <NodeEditor
          v-if="selectedNode"
          :node="selectedNode"
          :workflow-nodes="workflowFormData.nodes"
          @save="handleSaveNode"
          @delete="handleDeleteNode"
          @cancel="selectedNode = null"
        />
        <TransitionEditor
          v-else-if="selectedTransition"
          :transition="selectedTransition"
          :workflow-nodes="workflowFormData.nodes"
          @save="handleSaveTransition"
          @delete="handleDeleteTransition"
          @cancel="selectedTransition = null"
        />
        <div v-else class="properties-empty">
          <p>Select a node or transition to edit</p>
        </div>
      </div>
    </div>

    <!-- Node Creation Menu -->
    <div
      v-if="showNodeMenu"
      class="node-menu"
      :style="nodeMenuStyle"
      @click.stop
    >
      <Button
        variant="ghost"
        size="sm"
        @click="handleAddNode('start')"
        :disabled="hasStartNode"
      >
        Add Start Node
      </Button>
      <Button variant="ghost" size="sm" @click="handleAddNode('state')">
        Add State Node
      </Button>
      <Button variant="ghost" size="sm" @click="handleAddNode('end')">
        Add End Node
      </Button>
    </div>

    <!-- Modals -->
    <DeleteConfirmModal
      v-if="deletingWorkflow"
      :title="`Delete Workflow: ${deletingWorkflow.name}`"
      :message="'This action cannot be undone. Are you sure?'"
      @confirm="confirmDeleteWorkflow"
      @cancel="deletingWorkflow = null"
    />
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useAdminStore } from '@/stores/adminStore'
import { useNotificationStore } from '@/stores/notificationStore'
import type {
  Workflow,
  WorkflowNode,
  WorkflowTransition,
  CreateWorkflowRequest,
  UpdateWorkflowRequest
} from '@/types/admin'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'
import WorkflowCanvas from '@/components/admin/WorkflowCanvas.vue'
import NodeEditor from '@/components/admin/NodeEditor.vue'
import TransitionEditor from '@/components/admin/TransitionEditor.vue'
import DeleteConfirmModal from '@/components/admin/DeleteConfirmModal.vue'

// Hooks
const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()
const notificationStore = useNotificationStore()

// State
const currentWorkflow = ref<Workflow | null>(null)
const selectedNode = ref<WorkflowNode | null>(null)
const selectedNodeId = ref<string | null>(null)
const selectedTransition = ref<WorkflowTransition | null>(null)
const selectedTransitionId = ref<string | null>(null)
const deletingWorkflow = ref<Workflow | null>(null)
const isSavingWorkflow = ref(false)
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const showGrid = ref(true)
const showNodeMenu = ref(false)
const nodeMenuPosition = ref({ x: 0, y: 0 })

const workflowFormData = reactive<{
  name: string
  description: string
  nodes: WorkflowNode[]
  transitions: WorkflowTransition[]
}>({
  name: '',
  description: '',
  nodes: [],
  transitions: []
})

// Computed
const canCreateWorkflow = computed(() =>
  authStore.hasPermission.value('admin.workflow_manage')
)
const canDeleteWorkflow = computed(() =>
  authStore.hasPermission.value('admin.workflow_manage')
)

const hasStartNode = computed(() => {
  return workflowFormData.nodes.some((n) => n.type === 'start')
})

const hasWorkflowChanges = computed(() => {
  if (!currentWorkflow.value) return false
  return (
    workflowFormData.name !== currentWorkflow.value.name ||
    workflowFormData.description !== (currentWorkflow.value.description || '') ||
    JSON.stringify(workflowFormData.nodes) !==
      JSON.stringify(currentWorkflow.value.nodes) ||
    JSON.stringify(workflowFormData.transitions) !==
      JSON.stringify(currentWorkflow.value.transitions)
  )
})

const nodeMenuStyle = computed(() => {
  return {
    left: `${nodeMenuPosition.value.x}px`,
    top: `${nodeMenuPosition.value.y}px`
  }
})

// Methods
const fetchWorkflows = async (): Promise<void> => {
  try {
    await adminStore.fetchWorkflows()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to load workflows'
    })
  }
}

const handleCreateWorkflow = (): void => {
  currentWorkflow.value = null
  workflowFormData.name = 'New Workflow'
  workflowFormData.description = ''
  workflowFormData.nodes = []
  workflowFormData.transitions = []
  selectedNode.value = null
  selectedNodeId.value = null
  selectedTransition.value = null
  selectedTransitionId.value = null
}

const handleSaveWorkflow = async (): Promise<void> => {
  if (!workflowFormData.name.trim()) {
    notificationStore.addNotification({
      type: 'warning',
      title: 'Warning',
      message: 'Workflow name is required'
    })
    return
  }

  // Validate workflow
  if (workflowFormData.nodes.length === 0) {
    notificationStore.addNotification({
      type: 'warning',
      title: 'Warning',
      message: 'Workflow must have at least one node'
    })
    return
  }

  if (!hasStartNode.value) {
    notificationStore.addNotification({
      type: 'warning',
      title: 'Warning',
      message: 'Workflow must have at least one start node'
    })
    return
  }

  const hasEndNode = workflowFormData.nodes.some((n) => n.type === 'end')
  if (!hasEndNode) {
    notificationStore.addNotification({
      type: 'warning',
      title: 'Warning',
      message: 'Workflow must have at least one end node'
    })
    return
  }

  isSavingWorkflow.value = true
  try {
    if (currentWorkflow.value) {
      // Update existing
      const updateData: UpdateWorkflowRequest = {
        name: workflowFormData.name,
        description: workflowFormData.description || undefined,
        nodes: workflowFormData.nodes,
        transitions: workflowFormData.transitions
      }
      await adminStore.updateWorkflow(currentWorkflow.value.id, updateData)
      notificationStore.addNotification({
        type: 'success',
        title: 'Success',
        message: 'Workflow updated successfully'
      })
    } else {
      // Create new
      const createData: CreateWorkflowRequest = {
        name: workflowFormData.name,
        description: workflowFormData.description || undefined,
        nodes: workflowFormData.nodes,
        transitions: workflowFormData.transitions,
        is_active: false
      }
      const newWorkflow = await adminStore.createWorkflow(createData)
      currentWorkflow.value = newWorkflow
      notificationStore.addNotification({
        type: 'success',
        title: 'Success',
        message: 'Workflow created successfully'
      })
    }
    await fetchWorkflows()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to save workflow'
    })
  } finally {
    isSavingWorkflow.value = false
  }
}

const handleDeleteWorkflow = (): void => {
  if (currentWorkflow.value) {
    deletingWorkflow.value = currentWorkflow.value
  }
}

const confirmDeleteWorkflow = async (): Promise<void> => {
  if (!deletingWorkflow.value) return

  try {
    await adminStore.deleteWorkflow(deletingWorkflow.value.id)
    deletingWorkflow.value = null
    currentWorkflow.value = null
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Workflow deleted successfully'
    })
    await fetchWorkflows()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to delete workflow'
    })
  }
}

const handleNodeClick = (node: WorkflowNode): void => {
  selectedNode.value = node
  selectedNodeId.value = node.id
  selectedTransition.value = null
  selectedTransitionId.value = null
}

const handleTransitionClick = (transition: WorkflowTransition): void => {
  selectedTransition.value = transition
  selectedTransitionId.value = transition.id
  selectedNode.value = null
  selectedNodeId.value = null
}

const handleNodeDrag = (
  nodeId: string,
  position: { x: number; y: number }
): void => {
  const node = workflowFormData.nodes.find((n) => n.id === nodeId)
  if (node) {
    node.position = { ...position }
  }
}

const handlePanChange = (newPan: { x: number; y: number }): void => {
  pan.value = { ...newPan }
}

const handleZoomChange = (newZoom: number): void => {
  zoom.value = newZoom
}

const handleZoomIn = (): void => {
  zoom.value = Math.min(2, zoom.value + 0.1)
}

const handleZoomOut = (): void => {
  zoom.value = Math.max(0.5, zoom.value - 0.1)
}

const handleResetZoom = (): void => {
  zoom.value = 1
  pan.value = { x: 0, y: 0 }
}

const handleAddNode = (type: 'start' | 'state' | 'end'): void => {
  if (type === 'start' && hasStartNode.value) {
    notificationStore.addNotification({
      type: 'warning',
      title: 'Warning',
      message: 'Workflow can only have one start node'
    })
    return
  }

  const newNode: WorkflowNode = {
    id: `node-${Date.now()}`,
    name: type === 'start' ? 'Start' : type === 'end' ? 'End' : 'New State',
    type,
    position: {
      x: nodeMenuPosition.value.x / zoom.value - pan.value.x / zoom.value,
      y: nodeMenuPosition.value.y / zoom.value - pan.value.y / zoom.value
    },
    allowed_roles: [],
    actions: []
  }

  workflowFormData.nodes.push(newNode)
  showNodeMenu.value = false
  selectedNode.value = newNode
  selectedNodeId.value = newNode.id
}

const handleSaveNode = (node: WorkflowNode): void => {
  const index = workflowFormData.nodes.findIndex((n) => n.id === node.id)
  if (index !== -1) {
    workflowFormData.nodes[index] = { ...node }
  }
  selectedNode.value = null
  selectedNodeId.value = null
}

const handleDeleteNode = (nodeId: string): void => {
  // Remove node
  workflowFormData.nodes = workflowFormData.nodes.filter((n) => n.id !== nodeId)
  // Remove related transitions
  workflowFormData.transitions = workflowFormData.transitions.filter(
    (t) => t.from_node !== nodeId && t.to_node !== nodeId
  )
  selectedNode.value = null
  selectedNodeId.value = null
}

const handleSaveTransition = (transition: WorkflowTransition): void => {
  const index = workflowFormData.transitions.findIndex((t) => t.id === transition.id)
  if (index !== -1) {
    workflowFormData.transitions[index] = { ...transition }
  } else {
    workflowFormData.transitions.push(transition)
  }
  selectedTransition.value = null
  selectedTransitionId.value = null
}

const handleDeleteTransition = (transitionId: string): void => {
  workflowFormData.transitions = workflowFormData.transitions.filter(
    (t) => t.id !== transitionId
  )
  selectedTransition.value = null
  selectedTransitionId.value = null
}

// Lifecycle
onMounted(async () => {
  if (!authStore.hasPermission.value('admin.workflow_manage')) {
    await router.push({ name: 'forbidden' })
    return
  }

  await fetchWorkflows()

  // Handle canvas right-click for node menu
  document.addEventListener('contextmenu', (e) => {
    if ((e.target as HTMLElement).closest('.workflow-designer__canvas-area')) {
      e.preventDefault()
      nodeMenuPosition.value = { x: e.clientX, y: e.clientY }
      showNodeMenu.value = true
    } else {
      showNodeMenu.value = false
    }
  })

  document.addEventListener('click', () => {
    showNodeMenu.value = false
  })
})
</script>

<style scoped lang="css">
.workflow-designer {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  gap: 16px;
}

.workflow-designer__toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.workflow-designer__workflow-info {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
}

.workflow-name-input {
  flex: 1;
  max-width: 300px;
}

.workflow-designer__zoom-controls {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-left: auto;
}

.zoom-level {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  min-width: 50px;
  text-align: center;
}

.workflow-designer__layout {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.workflow-designer__canvas-area {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 8px);
  overflow: hidden;
  position: relative;
}

.workflow-designer__properties {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 8px);
  overflow-y: auto;
}

.properties-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary, #6b7280);
  padding: 48px 24px;
  text-align: center;
}

.node-menu {
  position: fixed;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 6px);
  box-shadow: var(--shadow-lg, 0 10px 15px rgba(0, 0, 0, 0.1));
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 1000;
}

/* Responsive */
@media (max-width: 968px) {
  .workflow-designer__layout {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr auto;
  }

  .workflow-designer__properties {
    max-height: 400px;
  }
}
</style>



