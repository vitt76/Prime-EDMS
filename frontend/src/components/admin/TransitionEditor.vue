<template>
  <div class="transition-editor">
    <div class="transition-editor__header">
      <h3 class="transition-editor__title">Transition Properties</h3>
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

    <form @submit.prevent="handleSave" class="transition-editor__form">
      <!-- From Node (read-only) -->
      <div class="form-group">
        <label class="form-label">From Node</label>
        <Input
          :model-value="fromNodeName"
          disabled
          readonly
        />
      </div>

      <!-- To Node (read-only) -->
      <div class="form-group">
        <label class="form-label">To Node</label>
        <Input
          :model-value="toNodeName"
          disabled
          readonly
        />
      </div>

      <!-- Label -->
      <div class="form-group">
        <Input
          v-model="formData.label"
          label="Label"
          placeholder="e.g., Approve"
          required
          :error="errors.label"
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

      <!-- Condition Type -->
      <div class="form-group">
        <Select
          v-model="conditionType"
          :options="conditionTypeOptions"
          label="Condition Type"
          @change="handleConditionTypeChange"
        />
      </div>

      <!-- Condition Parameters -->
      <div v-if="conditionType !== 'none'" class="form-group">
        <div v-if="conditionType === 'role'" class="condition-params">
          <Select
            v-model="conditionRole"
            :options="roleOptions"
            label="Required Role"
          />
        </div>
        <div v-if="conditionType === 'action'" class="condition-params">
          <Select
            v-model="conditionAction"
            :options="actionOptions"
            label="Required Action"
          />
        </div>
        <div v-if="conditionType === 'time'" class="condition-params">
          <Input
            v-model.number="conditionDays"
            type="number"
            label="Days"
            placeholder="0"
          />
        </div>
      </div>

      <!-- Actions -->
      <div class="transition-editor__actions">
        <Button
          variant="danger"
          size="sm"
          @click="handleDelete"
          type="button"
        >
          Delete Transition
        </Button>
        <Button variant="primary" type="submit" :loading="isSaving">
          Save Transition
        </Button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import type {
  WorkflowTransition,
  WorkflowNode,
  WorkflowCondition
} from '@/types/admin'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Button from '@/components/Common/Button.vue'

interface Props {
  transition: WorkflowTransition
  workflowNodes: WorkflowNode[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  save: [transition: WorkflowTransition]
  delete: [transitionId: string]
  cancel: []
}>()

const isSaving = ref(false)
const errors = reactive<{ label?: string }>({})

const formData = reactive<{
  label: string
  description: string
  condition?: WorkflowCondition
}>({
  label: props.transition.label || '',
  description: props.transition.description || '',
  condition: props.transition.condition
})

const conditionType = ref<'none' | 'role' | 'action' | 'time'>('none')
const conditionRole = ref<string>('')
const conditionAction = ref<string>('')
const conditionDays = ref<number>(0)

const fromNodeName = computed(() => {
  const node = props.workflowNodes.find((n) => n.id === props.transition.from_node)
  return node?.name || props.transition.from_node
})

const toNodeName = computed(() => {
  const node = props.workflowNodes.find((n) => n.id === props.transition.to_node)
  return node?.name || props.transition.to_node
})

const conditionTypeOptions = [
  { value: 'none', label: 'No Condition' },
  { value: 'role', label: 'User Role' },
  { value: 'action', label: 'User Action' },
  { value: 'time', label: 'Time-based' }
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
  () => props.transition,
  (newTransition) => {
    formData.label = newTransition.label || ''
    formData.description = newTransition.description || ''
    formData.condition = newTransition.condition

    // Parse condition
    if (newTransition.condition) {
      const cond = newTransition.condition
      if (cond.field === 'role') {
        conditionType.value = 'role'
        conditionRole.value = String(cond.value)
      } else if (cond.field === 'action') {
        conditionType.value = 'action'
        conditionAction.value = String(cond.value)
      } else if (cond.field === 'days') {
        conditionType.value = 'time'
        conditionDays.value = Number(cond.value)
      }
    } else {
      conditionType.value = 'none'
    }
  },
  { immediate: true }
)

const handleConditionTypeChange = (): void => {
  formData.condition = undefined
  conditionRole.value = ''
  conditionAction.value = ''
  conditionDays.value = 0
}

const validate = (): boolean => {
  Object.keys(errors).forEach((key) => delete errors[key as keyof typeof errors])

  if (!formData.label.trim()) {
    errors.label = 'Transition label is required'
  }

  return Object.keys(errors).length === 0
}

const handleSave = (): void => {
  if (!validate()) return

  isSaving.value = true
  try {
    let condition: WorkflowCondition | undefined = undefined

    if (conditionType.value !== 'none') {
      switch (conditionType.value) {
        case 'role':
          condition = {
            field: 'role',
            operator: 'equals',
            value: conditionRole.value
          }
          break
        case 'action':
          condition = {
            field: 'action',
            operator: 'equals',
            value: conditionAction.value
          }
          break
        case 'time':
          condition = {
            field: 'days',
            operator: 'greater_than',
            value: conditionDays.value
          }
          break
      }
    }

    const updatedTransition: WorkflowTransition = {
      ...props.transition,
      label: formData.label.trim(),
      description: formData.description.trim() || undefined,
      condition
    }
    emit('save', updatedTransition)
  } finally {
    isSaving.value = false
  }
}

const handleDelete = (): void => {
  if (confirm('Delete this transition?')) {
    emit('delete', props.transition.id)
  }
}
</script>

<style scoped lang="css">
.transition-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
}

.transition-editor__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.transition-editor__title {
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.transition-editor__form {
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

.condition-params {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transition-editor__actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--color-border, #e5e7eb);
  margin-top: auto;
}
</style>



