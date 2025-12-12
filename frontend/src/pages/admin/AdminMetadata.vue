// @ts-nocheck
<template>
  <div class="admin-metadata flex gap-6 h-[calc(100vh-180px)]">
    <!-- Left Panel: Schema List -->
    <div class="w-72 flex-shrink-0 bg-white rounded-xl border border-gray-200 flex flex-col">
      <div class="p-4 border-b border-gray-100">
        <div class="flex items-center justify-between mb-3">
          <h2 class="font-semibold text-gray-900">Схемы метаданных</h2>
          <button
            type="button"
            class="p-1.5 text-gray-400 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
            @click="createSchema"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </button>
        </div>
        <input
          v-model="schemaSearch"
          type="text"
          placeholder="Поиск схем..."
          class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
        />
      </div>

      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <button
          v-for="schema in filteredSchemas"
          :key="schema.id"
          type="button"
          :class="[
            'w-full text-left px-3 py-3 rounded-lg transition-colors',
            selectedSchema?.id === schema.id
              ? 'bg-violet-50 text-violet-700 border border-violet-200'
              : 'hover:bg-gray-50 text-gray-700'
          ]"
          @click="selectSchema(schema)"
        >
          <div class="flex items-center gap-3">
            <div
              :class="[
                'w-8 h-8 rounded-lg flex items-center justify-center',
                selectedSchema?.id === schema.id ? 'bg-violet-100' : 'bg-gray-100'
              ]"
            >
              <svg class="w-4 h-4" :class="selectedSchema?.id === schema.id ? 'text-violet-600' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate">{{ schema.name }}</p>
              <p class="text-xs text-gray-500">{{ schema.fields.length }} полей</p>
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- Center: Field Editor -->
    <div class="flex-1 bg-white rounded-xl border border-gray-200 flex flex-col">
      <template v-if="selectedSchema">
        <!-- Header -->
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <h2 class="font-semibold text-gray-900">{{ selectedSchema.name }}</h2>
            <p class="text-sm text-gray-500">{{ selectedSchema.description }}</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Предпросмотр
            </button>
            <button
              type="button"
              class="px-4 py-1.5 text-sm font-medium text-white bg-violet-600 hover:bg-violet-700 rounded-lg transition-colors"
            >
              Сохранить
            </button>
          </div>
        </div>

        <!-- Fields List (Drag & Drop) -->
        <div class="flex-1 overflow-y-auto p-5">
          <div class="space-y-3">
            <div
              v-for="(field, index) in selectedSchema.fields"
              :key="field.id"
              class="group flex items-start gap-3 p-4 bg-gray-50 rounded-xl border border-gray-200 hover:border-violet-300 transition-colors cursor-pointer"
              :class="{ 'border-violet-400 bg-violet-50': selectedField?.id === field.id }"
              @click="selectField(field)"
            >
              <!-- Drag Handle -->
              <div class="pt-1 cursor-grab text-gray-400 hover:text-gray-600">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM8 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM8 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM14 6a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM14 12a2 2 0 1 1-4 0 2 2 0 0 1 4 0zM14 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0z" />
                </svg>
              </div>

              <!-- Field Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900">{{ field.label }}</span>
                  <span
                    v-if="field.required"
                    class="px-1.5 py-0.5 text-[10px] font-medium bg-red-100 text-red-600 rounded"
                  >
                    Обязательное
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-0.5">{{ field.name }}</p>
              </div>

              <!-- Field Type Badge -->
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded-lg',
                  fieldTypeStyles[field.field_type] || 'bg-gray-100 text-gray-600'
                ]"
              >
                {{ fieldTypeLabels[field.field_type] || field.field_type }}
              </span>

              <!-- Actions -->
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  type="button"
                  class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
                  @click.stop="duplicateField(index)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
                <button
                  type="button"
                  class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  @click.stop="deleteField(index)"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Add Field Button -->
          <button
            type="button"
            class="w-full mt-4 py-3 border-2 border-dashed border-gray-300 rounded-xl text-sm font-medium text-gray-500 hover:text-violet-600 hover:border-violet-400 hover:bg-violet-50 transition-colors"
            @click="addField"
          >
            <span class="flex items-center justify-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Добавить поле
            </span>
          </button>
        </div>
      </template>

      <!-- Empty State -->
      <div v-else class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <svg class="mx-auto w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
          </svg>
          <p class="mt-4 text-sm text-gray-500">Выберите схему для редактирования</p>
        </div>
      </div>
    </div>

    <!-- Right Panel: Field Properties -->
    <div
      v-if="selectedField"
      class="w-80 flex-shrink-0 bg-white rounded-xl border border-gray-200 flex flex-col"
    >
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-semibold text-gray-900">Свойства поля</h3>
        <button
          type="button"
          class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          @click="selectedField = null"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-5 space-y-5">
        <!-- Field Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Тип поля</label>
          <select
            v-model="selectedField.field_type"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          >
            <option value="text">Текст</option>
            <option value="textarea">Многострочный текст</option>
            <option value="number">Число</option>
            <option value="date">Дата</option>
            <option value="datetime">Дата и время</option>
            <option value="select">Выпадающий список</option>
            <option value="multiselect">Множественный выбор</option>
            <option value="boolean">Да/Нет</option>
            <option value="url">URL</option>
            <option value="email">Email</option>
          </select>
        </div>

        <!-- Label -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Название</label>
          <input
            v-model="selectedField.label"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <!-- Internal Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Системное имя</label>
          <input
            v-model="selectedField.name"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
          <p class="mt-1 text-xs text-gray-500">Используется в API</p>
        </div>

        <!-- Placeholder -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Placeholder</label>
          <input
            v-model="selectedField.placeholder"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <!-- Helper Text -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Подсказка</label>
          <textarea
            v-model="selectedField.helper_text"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <!-- Default Value -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Значение по умолчанию</label>
          <input
            v-model="selectedField.default"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <!-- Required Toggle -->
        <div class="flex items-center justify-between py-2">
          <span class="text-sm font-medium text-gray-700">Обязательное поле</span>
          <button
            type="button"
            :class="[
              'relative w-11 h-6 rounded-full transition-colors',
              selectedField.required ? 'bg-violet-600' : 'bg-gray-200'
            ]"
            @click="selectedField.required = !selectedField.required"
          >
            <span
              :class="[
                'absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform',
                selectedField.required ? 'translate-x-6' : 'translate-x-1'
              ]"
            />
          </button>
        </div>

        <!-- Options (for Select/Multiselect) -->
        <div v-if="selectedField.field_type === 'select' || selectedField.field_type === 'multiselect'">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Варианты</label>
          <div class="space-y-2">
            <div
              v-for="(option, idx) in selectedField.options || []"
              :key="idx"
              class="flex items-center gap-2"
            >
              <input
                v-model="option.label"
                type="text"
                placeholder="Название"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
              <button
                type="button"
                class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                @click="removeOption(idx)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <button
            type="button"
            class="mt-2 text-sm text-violet-600 hover:text-violet-700"
            @click="addOption"
          >
            + Добавить вариант
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, computed, onMounted } from 'vue'
import type { MetadataSchema, MetadataType, MetadataFieldType } from '@/types/admin'
import { adminService } from '@/services/adminService'

// ═══════════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════════
const schemaSearch = ref('')
const selectedSchema = ref<MetadataSchema | null>(null)
const selectedField = ref<MetadataType | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const fieldTypeStyles: Record<MetadataFieldType, string> = {
  text: 'bg-blue-100 text-blue-700',
  textarea: 'bg-blue-100 text-blue-700',
  number: 'bg-emerald-100 text-emerald-700',
  date: 'bg-amber-100 text-amber-700',
  datetime: 'bg-amber-100 text-amber-700',
  select: 'bg-violet-100 text-violet-700',
  multiselect: 'bg-violet-100 text-violet-700',
  boolean: 'bg-gray-100 text-gray-700',
  url: 'bg-cyan-100 text-cyan-700',
  email: 'bg-pink-100 text-pink-700'
}

const fieldTypeLabels: Record<MetadataFieldType, string> = {
  text: 'Текст',
  textarea: 'Текст',
  number: 'Число',
  date: 'Дата',
  datetime: 'Дата/Время',
  select: 'Выбор',
  multiselect: 'Множ. выбор',
  boolean: 'Да/Нет',
  url: 'URL',
  email: 'Email'
}

// Schemas from real API
const schemas = ref<MetadataSchema[]>([])

// ═══════════════════════════════════════════════════════════════════════════════
// Data Loading
// ═══════════════════════════════════════════════════════════════════════════════
async function loadMetadataTypes() {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await adminService.getSchemas({ page_size: 100 })
    
    // Map Mayan metadata types to MetadataSchema interface
    schemas.value = response.results.map(mt => ({
      id: String(mt.id),
      name: mt.name,
      description: mt.default || '',
      document_types: [],
      fields: [{
        id: mt.id,
        name: mt.name.toLowerCase().replace(/\s+/g, '_'),
        label: mt.label || mt.name,
        default: mt.default || '',
        lookup: mt.lookup || '',
        validation: mt.validation || '',
        parser: mt.parser || '',
        field_type: 'text' as MetadataFieldType,
        required: false
      }],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }))
    
    console.log('[AdminMetadata] Loaded metadata types:', schemas.value.length)
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Ошибка загрузки типов метаданных'
    console.error('[AdminMetadata] Failed to load metadata types:', err)
  } finally {
    isLoading.value = false
  }
}

// Initial load
onMounted(() => {
  loadMetadataTypes()
})

// ═══════════════════════════════════════════════════════════════════════════════
// Computed
// ═══════════════════════════════════════════════════════════════════════════════
const filteredSchemas = computed(() => {
  if (!schemaSearch.value) return schemas.value
  const query = schemaSearch.value.toLowerCase()
  return schemas.value.filter(s => s.name.toLowerCase().includes(query))
})

// ═══════════════════════════════════════════════════════════════════════════════
// Methods
// ═══════════════════════════════════════════════════════════════════════════════
function selectSchema(schema: MetadataSchema) {
  selectedSchema.value = schema
  selectedField.value = null
}

function selectField(field: MetadataType) {
  selectedField.value = { ...field }
}

async function createSchema() {
  try {
    // Create new metadata type in Mayan
    const response = await adminService.createSchema({
      name: 'Новый тип',
      label: 'Новый тип метаданных'
    })
    
    // Reload list
    await loadMetadataTypes()
    
    // Select the new schema
    const newSchema = schemas.value.find(s => s.id === String(response.id))
    if (newSchema) {
      selectedSchema.value = newSchema
    }
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Ошибка создания типа метаданных'
    console.error('[AdminMetadata] Failed to create metadata type:', err)
  }
}

function addField() {
  if (!selectedSchema.value) return
  
  const newField: MetadataType = {
    id: Date.now(),
    name: `field_${selectedSchema.value.fields.length + 1}`,
    label: 'Новое поле',
    default: '',
    lookup: '',
    validation: '',
    parser: '',
    field_type: 'text',
    required: false
  }
  selectedSchema.value.fields.push(newField)
  selectedField.value = newField
}

function duplicateField(index: number) {
  if (!selectedSchema.value) return
  const field = selectedSchema.value.fields[index]
  const duplicate: MetadataType = {
    ...field,
    id: Date.now(),
    name: `${field.name}_copy`,
    label: `${field.label} (копия)`
  }
  selectedSchema.value.fields.splice(index + 1, 0, duplicate)
}

function deleteField(index: number) {
  if (!selectedSchema.value) return
  selectedSchema.value.fields.splice(index, 1)
  selectedField.value = null
}

function addOption() {
  if (!selectedField.value) return
  if (!selectedField.value.options) {
    selectedField.value.options = []
  }
  selectedField.value.options.push({ value: '', label: '' })
}

function removeOption(index: number) {
  if (!selectedField.value?.options) return
  selectedField.value.options.splice(index, 1)
}
</script>

