// @ts-nocheck
<template>
  <div class="metadata-schema-page">
    <!-- Toolbar -->
    <div class="metadata-schema-page__toolbar">
      <Button
        v-if="canCreateSchema"
        variant="primary"
        @click="handleCreateSchema"
        aria-label="Create new schema"
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
        Create Schema
      </Button>

      <div class="metadata-schema-page__search">
        <Input
          v-model="searchQuery"
          type="search"
          placeholder="Search schemas..."
          @input="handleSearchDebounced"
          aria-label="Search schemas"
        />
      </div>
    </div>

    <!-- Main Layout: 3 columns -->
    <div class="metadata-schema-page__layout">
      <!-- Left Panel: Schema List -->
      <div class="metadata-schema-page__sidebar">
        <div class="schema-list">
          <div
            v-for="schema in filteredSchemas"
            :key="schema.id"
            :class="[
              'schema-list__item',
              { 'schema-list__item--active': currentSchema?.id === schema.id }
            ]"
            @click="handleSelectSchema(schema)"
            role="button"
            tabindex="0"
            @keydown.enter="handleSelectSchema(schema)"
            @keydown.space.prevent="handleSelectSchema(schema)"
            :aria-label="`Select schema ${schema.name}`"
          >
            <div class="schema-list__header">
              <h4 class="schema-list__name">{{ schema.name }}</h4>
              <Badge
                :variant="schema.is_active ? 'success' : 'warning'"
                size="sm"
              >
                {{ schema.is_active ? 'Active' : 'Inactive' }}
              </Badge>
            </div>
            <p v-if="schema.description" class="schema-list__description">
              {{ schema.description }}
            </p>
            <div class="schema-list__meta">
              <span class="schema-list__fields-count">
                {{ schema.fields.length }} field{{ schema.fields.length !== 1 ? 's' : '' }}
              </span>
              <span class="schema-list__applies-to">
                {{ formatAppliesTo(schema.applies_to) }}
              </span>
            </div>
          </div>

          <div
            v-if="filteredSchemas.length === 0"
            class="schema-list__empty"
            role="status"
            aria-live="polite"
          >
            <p>No schemas found</p>
            <Button
              v-if="canCreateSchema"
              variant="secondary"
              size="sm"
              @click="handleCreateSchema"
            >
              Create First Schema
            </Button>
          </div>
        </div>
      </div>

      <!-- Center Panel: Schema Editor -->
      <div class="metadata-schema-page__editor">
        <div v-if="!currentSchema" class="editor-empty">
          <p>Select a schema from the list to edit</p>
        </div>

        <div v-else class="schema-editor">
          <!-- Schema Header -->
          <div class="schema-editor__header">
            <div class="schema-editor__title-group">
              <Input
                v-model="schemaFormData.name"
                label="Schema Name"
                required
                :error="schemaErrors.name"
              />
              <Textarea
                v-model="schemaFormData.description"
                label="Description"
                placeholder="Optional description for this schema"
              />
            </div>

            <div class="schema-editor__actions">
              <Button
                variant="secondary"
                size="sm"
                @click="handleSaveSchema"
                :loading="isSavingSchema"
                :disabled="!hasSchemaChanges"
              >
                Save Schema
              </Button>
              <Button
                variant="ghost"
                size="sm"
                @click="handleDeleteSchema"
                :disabled="!canDeleteSchema"
              >
                Delete
              </Button>
            </div>
          </div>

          <!-- Applies To -->
          <div class="schema-editor__section">
            <label class="form-label">Applies To</label>
            <div class="applies-to-checkboxes">
              <label
                v-for="assetType in assetTypeOptions"
                :key="assetType.value"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="assetType.value"
                  :checked="schemaFormData.applies_to.includes(assetType.value)"
                  @change="handleAppliesToChange(assetType.value, $event)"
                  class="checkbox-input"
                />
                <span>{{ assetType.label }}</span>
              </label>
            </div>
          </div>

          <!-- Fields List (Drag-drop) -->
          <div class="schema-editor__section">
            <div class="fields-header">
              <h3 class="fields-header__title">Fields</h3>
              <Button
                variant="secondary"
                size="sm"
                @click="handleAddField"
                aria-label="Add new field"
              >
                <svg
                  class="w-4 h-4"
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
                Add Field
              </Button>
            </div>

            <div class="fields-list" ref="fieldsListRef">
              <div
                v-for="(field, index) in schemaFormData.fields"
                :key="field.name || `field-${index}`"
                :draggable="true"
                @dragstart="handleDragStart($event, index)"
                @dragover.prevent="handleDragOver($event, index)"
                @drop="handleDrop($event, index)"
                @dragend="handleDragEnd"
                :class="[
                  'field-card',
                  { 'field-card--dragging': draggingIndex === index }
                ]"
                role="button"
                tabindex="0"
                :aria-label="`Field ${field.label || field.name}, drag to reorder`"
              >
                <div class="field-card__drag-handle" aria-label="Drag handle">
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
                      d="M4 8h16M4 16h16"
                    />
                  </svg>
                </div>

                <div class="field-card__content">
                  <div class="field-card__header">
                    <span class="field-card__name">{{ field.label || field.name }}</span>
                    <Badge :variant="getFieldTypeBadgeVariant(field.type)" size="sm">
                      {{ formatFieldType(field.type) }}
                    </Badge>
                    <Badge v-if="field.required" variant="warning" size="sm">
                      Required
                    </Badge>
                  </div>
                  <p v-if="field.description" class="field-card__description">
                    {{ field.description }}
                  </p>
                </div>

                <div class="field-card__actions">
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="handleEditField(field, index)"
                    aria-label="Edit field"
                  >
                    <svg
                      class="w-4 h-4"
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
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    @click="handleDeleteField(index)"
                    aria-label="Delete field"
                  >
                    <svg
                      class="w-4 h-4"
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

              <div
                v-if="schemaFormData.fields.length === 0"
                class="fields-list__empty"
                role="status"
              >
                <p>No fields yet. Click "Add Field" to get started.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Field Editor -->
      <div class="metadata-schema-page__field-editor">
        <FieldEditor
          v-if="editingField"
          :field="editingField"
          :existing-field-names="existingFieldNames"
          @save="handleSaveField"
          @cancel="editingField = null"
        />
        <div v-else class="field-editor-empty">
          <p>Select or add a field to edit</p>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <DeleteConfirmModal
      v-if="deletingSchema"
      :title="`Delete Schema: ${deletingSchema.name}`"
      :message="'This action cannot be undone. Are you sure?'"
      @confirm="confirmDeleteSchema"
      @cancel="deletingSchema = null"
    />
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useAdminStore } from '@/stores/adminStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { useDebounceFn } from '@vueuse/core'
import type {
  MetadataSchema,
  SchemaField,
  CreateMetadataSchemaRequest,
  UpdateMetadataSchemaRequest,
  AssetType
} from '@/types/admin'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'
import Badge from '@/components/Common/Badge.vue'
import FieldEditor from '@/components/admin/FieldEditor.vue'
import DeleteConfirmModal from '@/components/admin/DeleteConfirmModal.vue'

// Simple textarea component
const Textarea = {
  props: {
    modelValue: String,
    label: String,
    placeholder: String
  },
  emits: ['update:modelValue'],
  template: `
    <div>
      <label v-if="label" class="form-label">{{ label }}</label>
      <textarea
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :placeholder="placeholder"
        class="form-textarea"
        rows="3"
      />
    </div>
  `
}

// Hooks
const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()
const notificationStore = useNotificationStore()

// State
const searchQuery = ref('')
const currentSchema = ref<MetadataSchema | null>(null)
const editingField = ref<SchemaField | null>(null)
const editingFieldIndex = ref<number>(-1)
const deletingSchema = ref<MetadataSchema | null>(null)
const isSavingSchema = ref(false)
const draggingIndex = ref<number>(-1)
const fieldsListRef = ref<HTMLElement | null>(null)

const schemaFormData = reactive<{
  name: string
  description: string
  applies_to: AssetType[]
  fields: SchemaField[]
}>({
  name: '',
  description: '',
  applies_to: [],
  fields: []
})

const schemaErrors = reactive<{ name?: string }>({})

// Computed
const canCreateSchema = computed(() =>
  authStore.hasPermission.value('admin.schema_manage')
)
const canDeleteSchema = computed(() =>
  authStore.hasPermission.value('admin.schema_manage')
)

const filteredSchemas = computed(() => {
  if (!searchQuery.value) return adminStore.schemas
  const query = searchQuery.value.toLowerCase()
  return adminStore.schemas.filter(
    (schema) =>
      schema.name.toLowerCase().includes(query) ||
      schema.description?.toLowerCase().includes(query)
  )
})

const existingFieldNames = computed(() => {
  return schemaFormData.fields
    .map((f) => f.name)
    .filter((name, index) => index !== editingFieldIndex.value)
})

const hasSchemaChanges = computed(() => {
  if (!currentSchema.value) return false
  return (
    schemaFormData.name !== currentSchema.value.name ||
    schemaFormData.description !== (currentSchema.value.description || '') ||
    JSON.stringify(schemaFormData.applies_to.sort()) !==
      JSON.stringify(currentSchema.value.applies_to.sort()) ||
    JSON.stringify(schemaFormData.fields) !==
      JSON.stringify(currentSchema.value.fields)
  )
})

const assetTypeOptions = [
  { value: 'image', label: 'Images' },
  { value: 'video', label: 'Videos' },
  { value: 'document', label: 'Documents' },
  { value: 'audio', label: 'Audio' },
  { value: 'all', label: 'All Types' }
]

// Methods
const fetchSchemas = async (): Promise<void> => {
  try {
    await adminStore.fetchSchemas()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to load schemas'
    })
  }
}

const handleSearchDebounced = useDebounceFn(() => {
  // Search is handled by computed filteredSchemas
}, 300)

const handleSelectSchema = async (schema: MetadataSchema): Promise<void> => {
  try {
    const fullSchema = await adminStore.getSchema(schema.id)
    currentSchema.value = fullSchema
    editingField.value = null
    editingFieldIndex.value = -1

    // Populate form
    schemaFormData.name = fullSchema.name
    schemaFormData.description = fullSchema.description || ''
    schemaFormData.applies_to = [...fullSchema.applies_to]
    schemaFormData.fields = fullSchema.fields.map((f) => ({ ...f }))
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to load schema'
    })
  }
}

const handleCreateSchema = (): void => {
  currentSchema.value = null
  editingField.value = null
  schemaFormData.name = ''
  schemaFormData.description = ''
  schemaFormData.applies_to = []
  schemaFormData.fields = []
}

const handleAppliesToChange = (
  assetType: AssetType,
  event: Event
): void => {
  const checked = (event.target as HTMLInputElement).checked
  if (checked) {
    if (assetType === 'all') {
      schemaFormData.applies_to = ['all']
    } else {
      schemaFormData.applies_to = schemaFormData.applies_to.filter(
        (t) => t !== 'all'
      )
      if (!schemaFormData.applies_to.includes(assetType)) {
        schemaFormData.applies_to.push(assetType)
      }
    }
  } else {
    schemaFormData.applies_to = schemaFormData.applies_to.filter(
      (t) => t !== assetType
    )
  }
}

const handleAddField = (): void => {
  editingField.value = null
  editingFieldIndex.value = -1
}

const handleEditField = (field: SchemaField, index: number): void => {
  editingField.value = { ...field }
  editingFieldIndex.value = index
}

const handleSaveField = (field: SchemaField): void => {
  if (editingFieldIndex.value >= 0) {
    // Update existing field
    schemaFormData.fields[editingFieldIndex.value] = field
  } else {
    // Add new field
    schemaFormData.fields.push(field)
  }
  editingField.value = null
  editingFieldIndex.value = -1
}

const handleDeleteField = (index: number): void => {
  if (confirm('Delete this field?')) {
    schemaFormData.fields.splice(index, 1)
    if (editingFieldIndex.value === index) {
      editingField.value = null
      editingFieldIndex.value = -1
    }
  }
}

// Drag and Drop
const handleDragStart = (event: DragEvent, index: number): void => {
  draggingIndex.value = index
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(index))
  }
}

const handleDragOver = (event: DragEvent, index: number): void => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

const handleDrop = (event: DragEvent, targetIndex: number): void => {
  event.preventDefault()
  const sourceIndex = draggingIndex.value

  if (sourceIndex !== -1 && sourceIndex !== targetIndex) {
    const fields = [...schemaFormData.fields]
    const [removed] = fields.splice(sourceIndex, 1)
    fields.splice(targetIndex, 0, removed)
    schemaFormData.fields = fields
  }

  draggingIndex.value = -1
}

const handleDragEnd = (): void => {
  draggingIndex.value = -1
}

const handleSaveSchema = async (): Promise<void> => {
  // Validate
  if (!schemaFormData.name.trim()) {
    schemaErrors.name = 'Schema name is required'
    return
  }

  if (schemaFormData.fields.length === 0) {
    notificationStore.addNotification({
      type: 'warning',
      title: 'Warning',
      message: 'Schema must have at least one field'
    })
    return
  }

  isSavingSchema.value = true
  try {
    if (currentSchema.value) {
      // Update existing
      const updateData: UpdateMetadataSchemaRequest = {
        name: schemaFormData.name,
        description: schemaFormData.description || undefined,
        applies_to: schemaFormData.applies_to,
        fields: schemaFormData.fields
      }
      await adminStore.updateSchema(currentSchema.value.id, updateData)
      notificationStore.addNotification({
        type: 'success',
        title: 'Success',
        message: 'Schema updated successfully'
      })
    } else {
      // Create new
      const createData: CreateMetadataSchemaRequest = {
        name: schemaFormData.name,
        description: schemaFormData.description || undefined,
        applies_to: schemaFormData.applies_to,
        fields: schemaFormData.fields,
        is_active: true
      }
      const newSchema = await adminStore.createSchema(createData)
      currentSchema.value = newSchema
      notificationStore.addNotification({
        type: 'success',
        title: 'Success',
        message: 'Schema created successfully'
      })
    }
    await fetchSchemas()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to save schema'
    })
  } finally {
    isSavingSchema.value = false
  }
}

const handleDeleteSchema = (): void => {
  if (currentSchema.value) {
    deletingSchema.value = currentSchema.value
  }
}

const confirmDeleteSchema = async (): Promise<void> => {
  if (!deletingSchema.value) return

  try {
    await adminStore.deleteSchema(deletingSchema.value.id)
    deletingSchema.value = null
    currentSchema.value = null
    notificationStore.addNotification({
      type: 'success',
      title: 'Success',
      message: 'Schema deleted successfully'
    })
    await fetchSchemas()
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Error',
      message: 'Failed to delete schema'
    })
  }
}

const formatAppliesTo = (appliesTo: AssetType[]): string => {
  if (appliesTo.includes('all')) return 'All Types'
  return appliesTo.map((t) => t.charAt(0).toUpperCase() + t.slice(1)).join(', ')
}

const formatFieldType = (type: string): string => {
  const typeMap: Record<string, string> = {
    text: 'Text',
    textarea: 'Textarea',
    number: 'Number',
    date: 'Date',
    date_range: 'Date Range',
    select: 'Select',
    multi_select: 'Multi-select',
    checkbox: 'Checkbox',
    file_upload: 'File Upload',
    url: 'URL'
  }
  return typeMap[type] || type
}

const getFieldTypeBadgeVariant = (
  type: string
): 'success' | 'warning' | 'info' | 'neutral' => {
  const variantMap: Record<string, 'success' | 'warning' | 'info' | 'neutral'> = {
    text: 'info',
    textarea: 'info',
    number: 'success',
    date: 'warning',
    select: 'info',
    multi_select: 'info',
    checkbox: 'neutral',
    file_upload: 'warning',
    url: 'info'
  }
  return variantMap[type] || 'neutral'
}

// Lifecycle
onMounted(async () => {
  if (!authStore.hasPermission.value('admin.schema_manage')) {
    await router.push({ name: 'forbidden' })
    return
  }

  await fetchSchemas()
})
</script>

<style scoped lang="css">
.metadata-schema-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  gap: 24px;
}

.metadata-schema-page__toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.metadata-schema-page__search {
  flex: 1;
  min-width: 200px;
}

.metadata-schema-page__layout {
  display: grid;
  grid-template-columns: 280px 1fr 400px;
  gap: 24px;
  flex: 1;
  min-height: 0;
}

.metadata-schema-page__sidebar {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 8px);
  overflow-y: auto;
}

.metadata-schema-page__editor {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 8px);
  overflow-y: auto;
  padding: 24px;
}

.metadata-schema-page__field-editor {
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-lg, 8px);
  overflow-y: auto;
}

/* Schema List */
.schema-list {
  display: flex;
  flex-direction: column;
}

.schema-list__item {
  padding: 16px;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  cursor: pointer;
  transition: background-color 150ms ease;
}

.schema-list__item:hover {
  background: rgba(0, 0, 0, 0.02);
}

.schema-list__item--active {
  background: rgba(59, 130, 246, 0.05);
  border-left: 3px solid var(--color-primary, #3b82f6);
}

.schema-list__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.schema-list__name {
  font-size: var(--font-size-base, 14px);
  font-weight: 600;
  color: var(--color-text, #111827);
  flex: 1;
}

.schema-list__description {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 8px;
}

.schema-list__meta {
  display: flex;
  gap: 12px;
  font-size: var(--font-size-xs, 11px);
  color: var(--color-text-secondary, #6b7280);
}

.schema-list__empty {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
}

/* Schema Editor */
.editor-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary, #6b7280);
}

.schema-editor {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.schema-editor__header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.schema-editor__title-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schema-editor__actions {
  display: flex;
  gap: 8px;
}

.schema-editor__section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.applies-to-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

/* Fields List */
.fields-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.fields-header__title {
  font-size: var(--font-size-lg, 18px);
  font-weight: 600;
  color: var(--color-text, #111827);
}

.fields-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-base, 6px);
  background: var(--color-surface, #ffffff);
  cursor: move;
  transition: all 150ms ease;
}

.field-card:hover {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.field-card--dragging {
  opacity: 0.5;
  border-color: var(--color-primary, #3b82f6);
}

.field-card__drag-handle {
  color: var(--color-text-secondary, #6b7280);
  cursor: grab;
}

.field-card__drag-handle:active {
  cursor: grabbing;
}

.field-card__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-card__header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-card__name {
  font-weight: 500;
  color: var(--color-text, #111827);
}

.field-card__description {
  font-size: var(--font-size-sm, 12px);
  color: var(--color-text-secondary, #6b7280);
}

.field-card__actions {
  display: flex;
  gap: 4px;
}

.fields-list__empty {
  padding: 48px 24px;
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
}

.field-editor-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary, #6b7280);
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

/* Responsive */
@media (max-width: 1200px) {
  .metadata-schema-page__layout {
    grid-template-columns: 240px 1fr 350px;
  }
}

@media (max-width: 968px) {
  .metadata-schema-page__layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }

  .metadata-schema-page__sidebar {
    max-height: 200px;
  }

  .metadata-schema-page__field-editor {
    max-height: 400px;
  }
}
</style>



