<template>
  <div class="node-editor">
    <div class="node-editor__header">
      <h3 class="node-editor__title">Node Properties</h3>
      <Button
        variant="ghost"
        size="sm"
        @click="$emit('cancel')"
        aria-label="Close editor"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </Button>
    </div>

    <form @submit.prevent="handleSave" class="node-editor__form">
      <!-- Node Name -->
      <div class="form-group">
        <Input
          v-model="formData.name"
          label="Node Name"
          required
          :error="errors.name"
        />
      </div>

      <!-- Node Type -->
      <div class="form-group">
        <Select
          v-model="formData.type"
          :options="nodeTypeOptions"
          label="Node Type"
          required
          :error="errors.type"
          :disabled="formData.type === 'start'"
        />
      </div>

      <!-- Description -->
      <div class="form-group">
        <label class="form-label">Description</label>
        <textarea
          v-model="formData.description"
          class="form-textarea"
          rows="3"
          placeholder="Optional description"
        />
      </div>

      <!-- Allowed Roles -->
      <div class="form-group">
        <label class="form-label">Allowed Roles</label>
        <div class="role-checkboxes">
          <label
            v-for="role in roleOptions"
            :key="role.value"
            class="checkbox-label"
          >
            <input
              type="checkbox"
              :value="role.value"
              :checked="formData.allowed_roles.includes(role.value)"
              @change="handleRoleChange(role.value, $event)"
              class="checkbox-input"
            />
            <span>{{ role.label }}</span>
          </label>
        </div>
      </div>

      <!-- Actions -->
      <div class="form-group">
        <label class="form-label">Available Actions</label>
        <div class="action-checkboxes">
          <label
            v-for="action in actionOptions"
            :key="action.value"
            class="checkbox-label"
          >
            <input
              type="checkbox"
              :value="action.value"
              :checked="formData.actions.some((a) => a.action_type === action.value)"
              @change="handleActionChange(action.value, $event)"
              class="checkbox-input"
            />
            <span>{{ action.label }}</span>
          </label>
        </div>
      </div>

      <!-- Actions -->
      <div class="node-editor__actions">
        <Button
          variant="danger"
          size="sm"
          @click="handleDelete"
          type="button"
        >
          Delete Node
        </Button>
        <Button variant="primary" type="submit" :loading="isSaving">
          Save Node
        </Button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { WorkflowNode, UserRole, WorkflowAction } from '@/types/admin'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Button from '@/components/Common/Button.vue'

interface Props {
  node: WorkflowNode
  workflowNodes: WorkflowNode[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [node: WorkflowNode]
  delete: [nodeId: string]
  cancel: []
}>()

const isSaving = ref(false)
const errors = reactive<{ name?: string; type?: string }>({})

const formData = reactive<{
  name: string
  type: 'start' | 'state' | 'end'
  description: string
  allowed_roles: UserRole[]
  actions: WorkflowAction[]
}>({
  name: props.node.name,
  type: props.node.type,
  description: props.node.description || '',
  allowed_roles: [...props.node.allowed_roles],
  actions: [...props.node.actions]
})

const nodeTypeOptions = [
  { value: 'start', label: 'Start' },
  { value: 'state', label: 'State' },
  { value: 'end', label: 'End' }
]

const roleOptions = [
  { value: 'admin', label: 'Administrator' },
  { value: 'editor', label: 'Editor' },
  { value: 'viewer', label: 'Viewer' }
]

const actionOptions = [
  { value: 'approve', label: 'Approve' },
  { value: 'reject', label: 'Reject' },
  { value: 'request_changes', label: 'Request Changes' },
  { value: 'publish', label: 'Publish' },
  { value: 'archive', label: 'Archive' }
]

watch(
  () => props.node,
  (newNode) => {
    formData.name = newNode.name
    formData.type = newNode.type
    formData.description = newNode.description || ''
    formData.allowed_roles = [...newNode.allowed_roles]
    formData.actions = [...newNode.actions]
  },
  { immediate: true }
)

const handleRoleChange = (role: UserRole, event: Event): void => {
  const checked = (event.target as HTMLInputElement).checked
  if (checked) {
    if (!formData.allowed_roles.includes(role)) {
      formData.allowed_roles.push(role)
    }
  } else {
    formData.allowed_roles = formData.allowed_roles.filter((r) => r !== role)
  }
}

const handleActionChange = (actionType: string, event: Event): void => {
  const checked = (event.target as HTMLInputElement).checked
  if (checked) {
    const action: WorkflowAction = {
      id: `action-${Date.now()}`,
      label: actionOptions.find((a) => a.value === actionType)?.label || actionType,
      action_type: actionType as WorkflowAction['action_type'],
      target_node_id: ''
    }
    formData.actions.push(action)
  } else {
    formData.actions = formData.actions.filter(
      (a) => a.action_type !== actionType
    )
  }
}

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])

  if (!formData.name.trim()) {
    errors.name = 'Node name is required'
  }

  return Object.keys(errors).length === 0
}

const handleSave = (): void => {
  if (!validate()) return

  isSaving.value = true
  try {
    const updatedNode: WorkflowNode = {
      ...props.node,
      name: formData.name.trim(),
      type: formData.type,
      description: formData.description.trim() || undefined,
      allowed_roles: formData.allowed_roles,
      actions: formData.actions
    }
    emit('save', updatedNode)
  } finally {
    isSaving.value = false
  }
}

const handleDelete = (): void => {
  if (confirm('Delete this node? All connected transitions will also be removed.')) {
    emit('delete', props.node.id)
  }
}
</script>

<style scoped lang="css">
.node-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
}

.node-editor__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.node-editor__title {
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.node-editor__form {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: var(--font-size-sm, 12px);
  font-weight: 500;
  color: var(--color-text, #111827);
}

.form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 6px);
  font-size: var(--font-size-base, 14px);
  font-family: inherit;
  resize: vertical;
}

.role-checkboxes,
.action-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: var(--font-size-base, 14px);
  color: var(--color-text, #111827);
}

.checkbox-input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.node-editor__actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--color-border, #e5e7eb);
  margin-top: auto;
}
</style>



