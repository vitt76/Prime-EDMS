<template>
  <div class="metadata-editor space-y-6">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Empty State -->
    <div 
      v-else-if="availableTypes.length === 0" 
      class="text-center py-8 text-neutral-500"
    >
      <DocumentTextIcon class="w-12 h-12 mx-auto mb-3 text-neutral-300" />
      <p>Нет доступных типов метаданных</p>
    </div>

    <!-- Metadata Types -->
    <template v-else>
      <!-- Type Selector (if not all attached) -->
      <div v-if="unattachedTypes.length > 0" class="mb-6">
        <Menu as="div" class="relative inline-block text-left">
          <MenuButton
            class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium 
                   text-primary-600 hover:text-primary-700 hover:bg-primary-50 
                   rounded-lg transition-colors"
          >
            <PlusIcon class="w-4 h-4" />
            Добавить метаданные
            <ChevronDownIcon class="w-4 h-4" />
          </MenuButton>

          <transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <MenuItems
              class="absolute left-0 mt-2 w-64 origin-top-left rounded-lg bg-white 
                     shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
            >
              <div class="py-1">
                <MenuItem
                  v-for="type in unattachedTypes"
                  :key="type.id"
                  v-slot="{ active }"
                >
                  <button
                    :class="[
                      active ? 'bg-neutral-100' : '',
                      'w-full text-left px-4 py-2 text-sm flex items-center gap-3'
                    ]"
                    @click="attachMetadataType(type.id)"
                  >
                    <span 
                      :class="[
                        'w-8 h-8 rounded-lg flex items-center justify-center',
                        `bg-${type.color}-100 text-${type.color}-600`
                      ]"
                    >
                      <component :is="getIcon(type.icon)" class="w-4 h-4" />
                    </span>
                    <div>
                      <div class="font-medium text-neutral-900">{{ type.label }}</div>
                      <div class="text-xs text-neutral-500">{{ type.description }}</div>
                    </div>
                  </button>
                </MenuItem>
              </div>
            </MenuItems>
          </transition>
        </Menu>
      </div>

      <!-- Metadata Forms by Type -->
      <div class="space-y-6">
        <Disclosure
          v-for="(typeData, index) in attachedTypesWithData"
          :key="typeData.type.id"
          v-slot="{ open }"
          :default-open="index === 0"
        >
          <div 
            :class="[
              'border rounded-lg overflow-hidden transition-colors',
              open ? 'border-neutral-300 bg-white' : 'border-neutral-200 bg-neutral-50'
            ]"
          >
            <!-- Type Header -->
            <DisclosureButton
              class="w-full flex items-center justify-between px-4 py-3 text-left 
                     hover:bg-neutral-100 transition-colors"
            >
              <div class="flex items-center gap-3">
                <span 
                  :class="[
                    'w-8 h-8 rounded-lg flex items-center justify-center',
                    `bg-${typeData.type.color}-100 text-${typeData.type.color}-600`
                  ]"
                >
                  <component :is="getIcon(typeData.type.icon)" class="w-4 h-4" />
                </span>
                <div>
                  <div class="font-medium text-neutral-900">{{ typeData.type.label }}</div>
                  <div class="text-xs text-neutral-500">
                    {{ typeData.metadata?.completeness || 0 }}% заполнено
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <!-- Completeness indicator -->
                <div class="w-16 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-primary-500 transition-all duration-300"
                    :style="{ width: `${typeData.metadata?.completeness || 0}%` }"
                  ></div>
                </div>
                <ChevronDownIcon 
                  :class="[
                    'w-5 h-5 text-neutral-500 transition-transform duration-200',
                    open ? 'rotate-180' : ''
                  ]" 
                />
              </div>
            </DisclosureButton>

            <!-- Type Fields -->
            <transition
              enter-active-class="transition duration-100 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-out"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
            >
              <DisclosurePanel class="px-4 pb-4 pt-2">
                <div class="space-y-4">
                  <div
                    v-for="field in typeData.type.fields"
                    :key="field.id"
                    class="field-group"
                  >
                    <!-- Field Label -->
                    <label 
                      :for="`field-${typeData.type.id}-${field.id}`"
                      class="block text-sm font-medium text-neutral-700 mb-1"
                    >
                      {{ field.label }}
                      <span v-if="field.required" class="text-red-500">*</span>
                    </label>

                    <!-- Text Input -->
                    <input
                      v-if="field.type === 'text' || field.type === 'email' || field.type === 'url'"
                      :id="`field-${typeData.type.id}-${field.id}`"
                      :type="field.type"
                      :value="getFieldValue(typeData.type.id, field.id)"
                      :placeholder="field.placeholder"
                      :required="field.required"
                      :pattern="field.pattern"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             placeholder:text-neutral-400 transition-colors"
                      @input="updateFieldValue(typeData.type.id, field.id, ($event.target as HTMLInputElement).value)"
                    />

                    <!-- Textarea -->
                    <textarea
                      v-else-if="field.type === 'textarea'"
                      :id="`field-${typeData.type.id}-${field.id}`"
                      :value="getFieldValue(typeData.type.id, field.id)"
                      :placeholder="field.placeholder"
                      :required="field.required"
                      rows="3"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             placeholder:text-neutral-400 transition-colors resize-none"
                      @input="updateFieldValue(typeData.type.id, field.id, ($event.target as HTMLTextAreaElement).value)"
                    />

                    <!-- Number Input -->
                    <input
                      v-else-if="field.type === 'number'"
                      :id="`field-${typeData.type.id}-${field.id}`"
                      type="number"
                      :value="getFieldValue(typeData.type.id, field.id)"
                      :placeholder="field.placeholder"
                      :required="field.required"
                      :min="field.min"
                      :max="field.max"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             placeholder:text-neutral-400 transition-colors"
                      @input="updateFieldValue(typeData.type.id, field.id, Number(($event.target as HTMLInputElement).value))"
                    />

                    <!-- Date Input -->
                    <input
                      v-else-if="field.type === 'date'"
                      :id="`field-${typeData.type.id}-${field.id}`"
                      type="date"
                      :value="getFieldValue(typeData.type.id, field.id)"
                      :required="field.required"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             transition-colors"
                      @input="updateFieldValue(typeData.type.id, field.id, ($event.target as HTMLInputElement).value)"
                    />

                    <!-- DateTime Input -->
                    <input
                      v-else-if="field.type === 'datetime'"
                      :id="`field-${typeData.type.id}-${field.id}`"
                      type="datetime-local"
                      :value="getFieldValue(typeData.type.id, field.id)"
                      :required="field.required"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             transition-colors"
                      @input="updateFieldValue(typeData.type.id, field.id, ($event.target as HTMLInputElement).value)"
                    />

                    <!-- Select -->
                    <select
                      v-else-if="field.type === 'select'"
                      :id="`field-${typeData.type.id}-${field.id}`"
                      :value="getFieldValue(typeData.type.id, field.id) || ''"
                      :required="field.required"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             bg-white transition-colors"
                      @change="updateFieldValue(typeData.type.id, field.id, ($event.target as HTMLSelectElement).value)"
                    >
                      <option value="" disabled>Выберите...</option>
                      <option 
                        v-for="option in field.options" 
                        :key="option.value" 
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>

                    <!-- Boolean (Checkbox) -->
                    <div 
                      v-else-if="field.type === 'boolean'"
                      class="flex items-center gap-2"
                    >
                      <Switch
                        :model-value="!!getFieldValue(typeData.type.id, field.id)"
                        @update:model-value="updateFieldValue(typeData.type.id, field.id, $event)"
                        :class="[
                          getFieldValue(typeData.type.id, field.id) ? 'bg-primary-600' : 'bg-neutral-200',
                          'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full',
                          'border-2 border-transparent transition-colors duration-200 ease-in-out',
                          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
                        ]"
                      >
                        <span
                          :class="[
                            getFieldValue(typeData.type.id, field.id) ? 'translate-x-5' : 'translate-x-0',
                            'pointer-events-none inline-block h-5 w-5 transform rounded-full',
                            'bg-white shadow ring-0 transition duration-200 ease-in-out'
                          ]"
                        />
                      </Switch>
                      <span class="text-sm text-neutral-600">
                        {{ getFieldValue(typeData.type.id, field.id) ? 'Да' : 'Нет' }}
                      </span>
                    </div>

                    <!-- Help Text -->
                    <p v-if="field.helpText" class="mt-1 text-xs text-neutral-500">
                      {{ field.helpText }}
                    </p>
                  </div>
                </div>

                <!-- Actions -->
                <div class="mt-4 pt-4 border-t border-neutral-200 flex items-center justify-between">
                  <button
                    type="button"
                    class="text-sm text-red-600 hover:text-red-700 transition-colors"
                    @click="detachMetadataType(typeData.type.id)"
                  >
                    Удалить тип метаданных
                  </button>
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-white bg-primary-600 
                           rounded-lg hover:bg-primary-700 transition-colors
                           disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="isSaving"
                    @click="saveMetadata(typeData.type.id)"
                  >
                    <span v-if="isSaving && savingTypeId === typeData.type.id" class="flex items-center gap-2">
                      <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Сохранение...
                    </span>
                    <span v-else>Сохранить</span>
                  </button>
                </div>
              </DisclosurePanel>
            </transition>
          </div>
        </Disclosure>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, markRaw, type Component } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel, Menu, MenuButton, MenuItem, MenuItems, Switch } from '@headlessui/vue'
import { 
  PlusIcon, 
  ChevronDownIcon,
  DocumentTextIcon,
  MegaphoneIcon,
  ScaleIcon,
  CpuChipIcon,
  ClipboardDocumentCheckIcon,
  SwatchIcon
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notificationStore'
import {
  getAllMetadataTypes,
  getMetadataTypesForDocumentType,
  getAssetMetadata,
  bulkSaveAssetMetadata,
  type MetadataType,
  type AssetMetadata
} from '@/mocks/metadata'

interface Props {
  assetId: number
  documentType?: string
}

const props = withDefaults(defineProps<Props>(), {
  documentType: 'image'
})

const emit = defineEmits<{
  save: [typeId: number]
  change: []
}>()

const notificationStore = useNotificationStore()

// State
const isLoading = ref(true)
const isSaving = ref(false)
const savingTypeId = ref<number | null>(null)
const availableTypes = ref<MetadataType[]>([])
const assetMetadata = ref<AssetMetadata[]>([])
const attachedTypeIds = ref<Set<number>>(new Set())
const localValues = ref<Map<string, string | number | boolean | null>>(new Map())

// Icon mapping
const iconComponents: Record<string, Component> = {
  MegaphoneIcon: markRaw(MegaphoneIcon),
  ScaleIcon: markRaw(ScaleIcon),
  CpuChipIcon: markRaw(CpuChipIcon),
  ClipboardDocumentCheckIcon: markRaw(ClipboardDocumentCheckIcon),
  SwatchIcon: markRaw(SwatchIcon),
  DocumentTextIcon: markRaw(DocumentTextIcon)
}

function getIcon(iconName: string): Component {
  return iconComponents[iconName] || iconComponents.DocumentTextIcon
}

// Computed
const unattachedTypes = computed(() => {
  return availableTypes.value.filter(t => !attachedTypeIds.value.has(t.id))
})

const attachedTypesWithData = computed(() => {
  return availableTypes.value
    .filter(t => attachedTypeIds.value.has(t.id))
    .map(type => ({
      type,
      metadata: assetMetadata.value.find(m => m.typeId === type.id)
    }))
})

// Methods
function loadData() {
  isLoading.value = true
  
  // Simulate API delay
  setTimeout(() => {
    // Get available types for this document type
    availableTypes.value = props.documentType 
      ? getMetadataTypesForDocumentType(props.documentType)
      : getAllMetadataTypes()
    
    // Get existing metadata for this asset
    assetMetadata.value = getAssetMetadata(props.assetId)
    
    // Mark types with existing data as attached
    attachedTypeIds.value = new Set(assetMetadata.value.map(m => m.typeId))
    
    // Initialize local values from existing metadata
    for (const metadata of assetMetadata.value) {
      for (const value of metadata.values) {
        const key = `${metadata.typeId}-${value.fieldId}`
        localValues.value.set(key, value.value)
      }
    }
    
    isLoading.value = false
  }, 300)
}

function attachMetadataType(typeId: number) {
  attachedTypeIds.value.add(typeId)
  emit('change')
}

function detachMetadataType(typeId: number) {
  attachedTypeIds.value.delete(typeId)
  
  // Clear local values for this type
  const keysToDelete: string[] = []
  localValues.value.forEach((_, key) => {
    if (key.startsWith(`${typeId}-`)) {
      keysToDelete.push(key)
    }
  })
  keysToDelete.forEach(key => localValues.value.delete(key))
  
  // Remove from assetMetadata
  assetMetadata.value = assetMetadata.value.filter(m => m.typeId !== typeId)
  
  emit('change')
}

function getFieldValue(typeId: number, fieldId: string): string | number | boolean | null {
  const key = `${typeId}-${fieldId}`
  if (localValues.value.has(key)) {
    return localValues.value.get(key) ?? null
  }
  
  // Try to get from existing metadata
  const metadata = assetMetadata.value.find(m => m.typeId === typeId)
  const fieldValue = metadata?.values.find(v => v.fieldId === fieldId)
  return fieldValue?.value ?? null
}

function updateFieldValue(typeId: number, fieldId: string, value: string | number | boolean | null) {
  const key = `${typeId}-${fieldId}`
  localValues.value.set(key, value)
  emit('change')
}

async function saveMetadata(typeId: number) {
  isSaving.value = true
  savingTypeId.value = typeId
  
  try {
    // Collect all values for this type
    const type = availableTypes.value.find(t => t.id === typeId)
    if (!type) return
    
    const values: { fieldId: string; value: string | number | boolean | null }[] = []
    
    for (const field of type.fields) {
      const key = `${typeId}-${field.id}`
      const value = localValues.value.get(key) ?? null
      values.push({ fieldId: field.id, value })
    }
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Save to mock store
    const updatedMetadata = bulkSaveAssetMetadata(
      props.assetId,
      typeId,
      values,
      'Текущий пользователь'
    )
    
    // Update local state
    const existingIndex = assetMetadata.value.findIndex(m => m.typeId === typeId)
    if (existingIndex >= 0) {
      assetMetadata.value[existingIndex] = updatedMetadata
    } else {
      assetMetadata.value.push(updatedMetadata)
    }
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Метаданные сохранены',
      message: `Данные "${type.label}" успешно обновлены`
    })
    
    emit('save', typeId)
    
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка сохранения',
      message: 'Не удалось сохранить метаданные'
    })
  } finally {
    isSaving.value = false
    savingTypeId.value = null
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})

// Watch for asset changes
watch(() => props.assetId, () => {
  localValues.value.clear()
  loadData()
})
</script>

<style scoped>
/* Custom styles for color variants */
.bg-purple-100 { background-color: rgb(243 232 255); }
.text-purple-600 { color: rgb(147 51 234); }
.bg-amber-100 { background-color: rgb(254 243 199); }
.text-amber-600 { color: rgb(217 119 6); }
.bg-slate-100 { background-color: rgb(241 245 249); }
.text-slate-600 { color: rgb(71 85 105); }
.bg-green-100 { background-color: rgb(220 252 231); }
.text-green-600 { color: rgb(22 163 74); }
.bg-pink-100 { background-color: rgb(252 231 243); }
.text-pink-600 { color: rgb(219 39 119); }
</style>

