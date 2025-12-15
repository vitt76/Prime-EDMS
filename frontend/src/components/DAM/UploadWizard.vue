<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 overflow-y-auto"
        aria-labelledby="upload-wizard-title"
        role="dialog"
        aria-modal="true"
      >
        <!-- Backdrop -->
        <div 
          class="fixed inset-0 bg-black/60 backdrop-blur-sm"
          @click="handleClose"
        />

        <!-- Modal Panel -->
        <div class="flex min-h-full items-center justify-center p-4">
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-4"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 scale-100"
            leave-to-class="opacity-0 scale-95"
          >
            <div
              v-if="isOpen"
              class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden"
            >
              <!-- Header -->
              <div class="relative bg-gradient-to-r from-primary-600 to-primary-500 px-6 py-5">
                <div class="flex items-center justify-between">
                  <div>
                    <h2 
                      id="upload-wizard-title"
                      class="text-xl font-semibold text-white"
                    >
                      Загрузка файлов
                    </h2>
                    <p class="mt-1 text-sm text-primary-100">
                      {{ stepDescriptions[currentStep] }}
                    </p>
                  </div>
                  <button
                    type="button"
                    class="p-2 text-white/80 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    @click="handleClose"
                    aria-label="Закрыть"
                  >
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <!-- Progress Steps -->
                <div class="flex items-center gap-2 mt-5">
                  <template v-for="(step, index) in steps" :key="step.id">
                    <div class="flex items-center">
                      <div
                        :class="[
                          'flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-all duration-300',
                          index < currentStep
                            ? 'bg-white text-primary-600'
                            : index === currentStep
                              ? 'bg-white text-primary-600 ring-4 ring-white/30'
                              : 'bg-primary-400/50 text-primary-200'
                        ]"
                      >
                        <svg 
                          v-if="index < currentStep" 
                          class="w-5 h-5" 
                          fill="currentColor" 
                          viewBox="0 0 20 20"
                        >
                          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                        <span v-else>{{ index + 1 }}</span>
                      </div>
                      <span 
                        :class="[
                          'ml-2 text-sm font-medium hidden sm:block',
                          index <= currentStep ? 'text-white' : 'text-primary-200'
                        ]"
                      >
                        {{ step.label }}
                      </span>
                    </div>
                    <div
                      v-if="index < steps.length - 1"
                      :class="[
                        'flex-1 h-0.5 mx-3 rounded',
                        index < currentStep ? 'bg-white' : 'bg-primary-400/50'
                      ]"
                    />
                  </template>
                </div>
              </div>

              <!-- Content -->
              <div class="p-6 min-h-[400px]">
                <!-- Step 1: Drop Zone -->
                <div v-if="currentStep === 0" class="space-y-6">
                  <div
                    :class="[
                      'relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200',
                      isDragging
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-neutral-300 hover:border-primary-400 hover:bg-neutral-50'
                    ]"
                    @dragover.prevent="isDragging = true"
                    @dragleave.prevent="isDragging = false"
                    @drop.prevent="handleDrop"
                  >
                    <input
                      type="file"
                      multiple
                      accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx"
                      class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                      @change="handleFileSelect"
                    />
                    
                    <div class="space-y-4">
                      <div 
                        :class="[
                          'mx-auto w-16 h-16 rounded-full flex items-center justify-center transition-colors',
                          isDragging ? 'bg-primary-100' : 'bg-neutral-100'
                        ]"
                      >
                        <svg 
                          :class="[
                            'w-8 h-8 transition-colors',
                            isDragging ? 'text-primary-600' : 'text-neutral-400'
                          ]" 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                      </div>
                      <div>
                        <p class="text-lg font-medium text-neutral-700">
                          Перетащите файлы сюда
                        </p>
                        <p class="mt-1 text-sm text-neutral-500">
                          или <span class="text-primary-600 font-medium">выберите файлы</span> с компьютера
                        </p>
                      </div>
                      <p class="text-xs text-neutral-400">
                        Поддерживаются: изображения, видео, аудио, документы (до 500MB каждый)
                      </p>
                    </div>
                  </div>

                  <!-- File List -->
                  <div v-if="files.length > 0" class="space-y-3">
                    <div class="flex items-center justify-between">
                      <h3 class="text-sm font-medium text-neutral-700">
                        Выбрано файлов: {{ files.length }}
                      </h3>
                      <button
                        type="button"
                        class="text-sm text-red-600 hover:text-red-700"
                        @click="clearFiles"
                      >
                        Очистить все
                      </button>
                    </div>
                    
                    <div class="max-h-60 overflow-y-auto space-y-2">
                    <div
                      v-for="(file, idx) in files"
                      :key="getFileKey(file)"
                        class="flex items-center gap-3 p-3 bg-neutral-50 rounded-lg group"
                      >
                        <!-- File Icon -->
                        <div 
                          :class="[
                            'w-10 h-10 rounded-lg flex items-center justify-center',
                            getFileTypeColor(file.type)
                          ]"
                        >
                          <component :is="getFileTypeIcon(file.type)" class="w-5 h-5 text-white" />
                        </div>
                        
                        <!-- File Info -->
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-neutral-700 truncate">
                            {{ file.name }}
                          </p>
                          <p class="text-xs text-neutral-500">
                            {{ formatFileSize(file.size) }}
                          </p>
                        </div>
                        
                        <!-- Progress Bar (during upload simulation) -->
                        <div v-if="uploadProgress[idx] !== undefined" class="w-24">
                          <div class="h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                            <div
                              class="h-full bg-primary-500 rounded-full transition-all duration-300"
                              :style="{ width: `${uploadProgress[idx]}%` }"
                            />
                          </div>
                          <p class="mt-0.5 text-[10px] text-neutral-500 text-right">
                            {{ uploadProgress[idx] }}%
                          </p>
                        </div>
                        
                        <!-- Remove Button -->
                        <button
                          v-else
                          type="button"
                          class="p-1.5 text-neutral-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
                          @click="removeFile(idx)"
                          aria-label="Удалить файл"
                        >
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Step 2: Metadata -->
                <div v-else-if="currentStep === 1" class="space-y-4">
                  <div class="flex items-center justify-between">
                    <h3 class="text-sm font-medium text-neutral-700">Метаданные по каждому файлу</h3>
                    <p class="text-xs text-neutral-500">Название обязательно для каждого файла</p>
                  </div>
                  <div class="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                    <div
                      v-for="file in files"
                      :key="getFileKey(file)"
                      class="border border-neutral-200 rounded-lg p-4 space-y-3 shadow-sm"
                    >
                      <div class="flex items-center justify-between gap-3">
                        <div class="min-w-0">
                          <p class="text-sm font-medium text-neutral-800 truncate">{{ file.name }}</p>
                          <p class="text-xs text-neutral-500">{{ formatFileSize(file.size) }}</p>
                        </div>
                        <div class="flex items-center gap-2">
                          <span class="text-xs text-neutral-500">AI</span>
                          <button
                            type="button"
                            :class="[
                              'relative inline-flex h-6 w-11 items-center rounded-full transition-colors',
                              ensureFileMeta(file).enableAI ? 'bg-purple-600' : 'bg-neutral-200'
                            ]"
                            @click="ensureFileMeta(file).enableAI = !ensureFileMeta(file).enableAI"
                          >
                            <span class="sr-only">Toggle AI</span>
                            <span
                              :class="[
                                'inline-block h-4 w-4 transform rounded-full bg-white transition-transform',
                                ensureFileMeta(file).enableAI ? 'translate-x-6' : 'translate-x-1'
                              ]"
                            />
                          </button>
                        </div>
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-1">
                          Название <span class="text-red-500">*</span>
                        </label>
                        <input
                          v-model="ensureFileMeta(file).title"
                          type="text"
                          class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg 
                                 focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                                 transition-colors"
                          :placeholder="file.name"
                        />
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-1">
                          Описание
                        </label>
                        <textarea
                          v-model="ensureFileMeta(file).description"
                          rows="2"
                          class="w-full px-4 py-2.5 border border-neutral-300 rounded-lg 
                                 focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                                 transition-colors resize-none"
                          placeholder="Добавьте описание..."
                        />
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-1">
                          Теги
                        </label>
                        <div class="flex flex-wrap gap-2 p-3 border border-neutral-300 rounded-lg min-h-[48px]">
                          <span
                            v-for="tag in ensureFileMeta(file).tags"
                            :key="tag"
                            class="inline-flex items-center gap-1 px-2.5 py-1 bg-primary-100 text-primary-700 
                                   text-sm rounded-full"
                          >
                            {{ tag }}
                            <button
                              type="button"
                              class="hover:text-primary-900"
                              @click="removeTagForFile(getFileKey(file), tag)"
                            >
                              <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                              </svg>
                            </button>
                          </span>
                          <input
                            v-model="newTagMap[getFileKey(file)]"
                            type="text"
                            class="flex-1 min-w-[120px] border-0 p-0 text-sm focus:ring-0 placeholder-neutral-400"
                            placeholder="Добавить тег..."
                            @keydown.enter.prevent="addTagForFile(getFileKey(file))"
                            @keydown.comma.prevent="addTagForFile(getFileKey(file))"
                          />
                        </div>
                        <p class="mt-1 text-xs text-neutral-500">
                          Нажмите Enter или запятую для добавления тега
                        </p>
                        <div v-if="suggestedTags.length > 0" class="mt-2 flex flex-wrap gap-1.5">
                          <button
                            v-for="tag in suggestedTags"
                            :key="tag"
                            type="button"
                            :class="[
                              'px-2.5 py-1 text-xs rounded-full transition-colors',
                              ensureFileMeta(file).tags.includes(tag)
                                ? 'bg-primary-100 text-primary-700'
                                : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                            ]"
                            @click="toggleTagForFile(getFileKey(file), tag)"
                          >
                            {{ tag }}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Step 3: Review -->
                <div v-else-if="currentStep === 2" class="space-y-6">
                  <div class="bg-neutral-50 rounded-xl p-5">
                    <h3 class="font-medium text-neutral-800 mb-4">Сводка загрузки</h3>
                    
                    <dl class="space-y-3">
                      <div class="flex justify-between">
                        <dt class="text-sm text-neutral-600">Файлов:</dt>
                        <dd class="text-sm font-medium text-neutral-800">{{ files.length }}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-sm text-neutral-600">Общий размер:</dt>
                        <dd class="text-sm font-medium text-neutral-800">{{ formatFileSize(totalSize) }}</dd>
                      </div>
                      <div class="flex justify-between">
                        <dt class="text-sm text-neutral-600">AI Анализ:</dt>
                        <dd class="text-sm font-medium text-neutral-800">
                          {{ files.filter(f => ensureFileMeta(f).enableAI).length }} из {{ files.length }} включены
                        </dd>
                      </div>
                    </dl>
                  </div>

                  <!-- File Preview List -->
                  <div>
                    <h3 class="font-medium text-neutral-800 mb-3">Файлы для загрузки</h3>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                      <div
                        v-for="(file, index) in files"
                        :key="index"
                        class="aspect-square rounded-lg overflow-hidden bg-neutral-100 relative group"
                      >
                        <!-- Image Preview -->
                        <img
                          v-if="file.type.startsWith('image/')"
                          :src="getFilePreview(file)"
                          :alt="file.name"
                          class="w-full h-full object-cover"
                        />
                        <!-- Other File Types -->
                        <div v-else class="w-full h-full flex flex-col items-center justify-center">
                          <component 
                            :is="getFileTypeIcon(file.type)" 
                            :class="['w-8 h-8', getFileTypeTextColor(file.type)]" 
                          />
                          <span class="mt-2 text-xs text-neutral-500 truncate max-w-full px-2">
                            {{ file.name.split('.').pop()?.toUpperCase() }}
                          </span>
                        </div>
                        <!-- Overlay with filename -->
                        <div class="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                          <p class="text-xs text-white truncate">{{ ensureFileMeta(file).title || file.name }}</p>
                          <p class="text-[10px] text-white/80 truncate">
                            {{ ensureFileMeta(file).tags.join(', ') || '—' }} • AI: {{ ensureFileMeta(file).enableAI ? 'On' : 'Off' }}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Footer -->
              <div class="flex items-center justify-between px-6 py-4 bg-neutral-50 border-t border-neutral-200">
                <button
                  v-if="currentStep > 0"
                  type="button"
                  class="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-neutral-800 
                         hover:bg-neutral-100 rounded-lg transition-colors"
                  @click="prevStep"
                  :disabled="isUploading"
                >
                  ← Назад
                </button>
                <div v-else />

                <div class="flex items-center gap-3">
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-neutral-800 
                           hover:bg-neutral-100 rounded-lg transition-colors"
                    @click="handleClose"
                    :disabled="isUploading"
                  >
                    Отмена
                  </button>
                  
                  <button
                    v-if="currentStep < steps.length - 1"
                    type="button"
                    class="px-5 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-lg
                           hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                           disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    :disabled="!canProceed"
                    @click="nextStep"
                  >
                    Далее →
                  </button>
                  
                  <button
                    v-else
                    type="button"
                    class="px-5 py-2.5 bg-primary-600 text-white text-sm font-medium rounded-lg
                           hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                           disabled:opacity-50 disabled:cursor-not-allowed transition-colors
                           inline-flex items-center gap-2"
                    :disabled="isUploading || !canProceed"
                    @click="handleUpload"
                  >
                    <svg v-if="isUploading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>{{ isUploading ? 'Загрузка...' : 'Загрузить' }}</span>
                  </button>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, h } from 'vue'
import { useAssetStore } from '@/stores/assetStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { uploadService, type UploadResult } from '@/services/uploadService'
import type { Asset } from '@/types/api'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [assets: Asset[]]
}>()

const assetStore = useAssetStore()
const notificationStore = useNotificationStore()

// Steps configuration
const steps = [
  { id: 'upload', label: 'Файлы' },
  { id: 'metadata', label: 'Метаданные' },
  { id: 'review', label: 'Проверка' }
]

const stepDescriptions = [
  'Выберите или перетащите файлы для загрузки',
  'Добавьте название, описание и теги',
  'Проверьте и подтвердите загрузку'
]

// State
const currentStep = ref(0)
const isDragging = ref(false)
const isUploading = ref(false)
const files = ref<File[]>([])
const uploadProgress = ref<Record<number, number>>({})
const filePreviews = ref<Map<File, string>>(new Map())

type FileMeta = {
  title: string
  description: string
  tags: string[]
  enableAI: boolean
}

const fileMetadata = ref<Record<string, FileMeta>>({})
const newTagMap = ref<Record<string, string>>({})

// Suggested tags from existing assets
const suggestedTags = computed(() => assetStore.availableTags.slice(0, 10))

// Computed
const totalSize = computed(() => files.value.reduce((sum, f) => sum + f.size, 0))

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return files.value.length > 0
    case 1:
      return files.value.length > 0 && files.value.every(f => ensureFileMeta(f).title.trim().length > 0)
    case 2:
      return files.value.length > 0 && files.value.every(f => ensureFileMeta(f).title.trim().length > 0)
    default:
      return false
  }
})

// Methods
function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

function getFileKey(file: File): string {
  return `${file.name}-${file.size}-${file.lastModified}`
}

function ensureFileMeta(file: File): FileMeta {
  const key = getFileKey(file)
  if (!fileMetadata.value[key]) {
    const basename = file.name.replace(/\.[^/.]+$/, '')
    fileMetadata.value[key] = {
      title: basename || file.name,
      description: '',
      tags: [],
      enableAI: true
    }
  }
  if (!newTagMap.value[key]) newTagMap.value[key] = ''
  return fileMetadata.value[key]
}

function addFiles(newFiles: File[]) {
  const validFiles = newFiles.filter(file => {
    // Check file size (500MB max)
    if (file.size > 500 * 1024 * 1024) {
      notificationStore.addNotification({
        type: 'warning',
        title: 'Файл слишком большой',
        message: `${file.name} превышает лимит 500MB`
      })
      return false
    }
    return true
  })
  
  files.value = [...files.value, ...validFiles]
  validFiles.forEach(file => ensureFileMeta(file))
  // (debug ingest removed)
  
  // Generate previews for images
  validFiles.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        filePreviews.value.set(file, e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  })
}

function removeFile(index: number) {
  const file = files.value[index]
  if (!file) return
  if (filePreviews.value.has(file)) {
    filePreviews.value.delete(file)
  }
  files.value.splice(index, 1)
}

function clearFiles() {
  files.value = []
  filePreviews.value.clear()
  uploadProgress.value = {}
  fileMetadata.value = {}
  newTagMap.value = {}
}

function getFilePreview(file: File): string {
  return filePreviews.value.get(file) || ''
}

function addTagForFile(key: string) {
  const tag = (newTagMap.value[key] || '').trim().replace(/,/g, '')
  const meta = fileMetadata.value[key]
  if (!meta) return
  if (tag && !meta.tags.includes(tag)) {
    meta.tags.push(tag)
  }
  newTagMap.value[key] = ''
}

function removeTagForFile(key: string, tag: string) {
  const meta = fileMetadata.value[key]
  if (!meta) return
  const index = meta.tags.indexOf(tag)
  if (index > -1) {
    meta.tags.splice(index, 1)
  }
}

function toggleTagForFile(key: string, tag: string) {
  const meta = fileMetadata.value[key]
  if (!meta) return
  if (meta.tags.includes(tag)) {
    removeTagForFile(key, tag)
  } else {
    meta.tags.push(tag)
  }
}

function nextStep() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function handleUpload() {
  if (!canProceed.value || isUploading.value) return
  if (files.value.length === 0) return

  isUploading.value = true

  try {
    const uploadedAssets: Asset[] = []

    for (let i = 0; i < files.value.length; i++) {
      const file = files.value[i] as File
      uploadProgress.value[i] = 0
      const meta = ensureFileMeta(file)
      // (debug ingest removed)

      const result: UploadResult = await uploadService.uploadFile(file, {
        documentTypeId: 1,
        label: meta.title || file.name,
        description: meta.description,
        tags: meta.tags,
        metadata: {
          tags: meta.tags.join(','),
          description: meta.description
        },
        onProgress: (progress) => {
          uploadProgress.value[i] = Math.round(progress.percent)
        }
      })

      const effectiveLabel = meta.title || file.name
      uploadedAssets.push({
        id: result.documentId,
        label: effectiveLabel,
        filename: file.name,
        size: file.size,
        mime_type: file.type,
        date_added: new Date().toISOString(),
        download_url: result.downloadUrl,
        thumbnail_url: file.type.startsWith('image/') ? filePreviews.value.get(file) : undefined,
        tags: [...meta.tags],
        metadata: { description: meta.description, enableAI: meta.enableAI }
      } as Asset)
    }

    notificationStore.addNotification({
      type: 'success',
      title: 'Загрузка завершена',
      message: `Успешно загружено ${uploadedAssets.length} файл(ов)`
    })

    emit('success', uploadedAssets)
    closeAndReset()
  } catch (error) {
    console.error('Upload failed:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка загрузки',
      message: 'Не удалось загрузить файлы. Попробуйте снова.'
    })
  } finally {
    isUploading.value = false
  }
}

/**
 * Close modal after successful upload (unconditional)
 */
function closeAndReset() {
  // Reset state
  currentStep.value = 0
  files.value = []
  filePreviews.value.clear()
  uploadProgress.value = {}
  fileMetadata.value = {}
  newTagMap.value = {}
  
  emit('close')
}

/**
 * Handle close button / backdrop click (prevents closing during upload)
 */
function handleClose() {
  if (isUploading.value) return
  closeAndReset()
}

// File type helpers
function getFileTypeColor(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'bg-blue-500'
  if (mimeType.startsWith('video/')) return 'bg-purple-500'
  if (mimeType.startsWith('audio/')) return 'bg-pink-500'
  if (mimeType.includes('pdf')) return 'bg-red-500'
  if (mimeType.includes('word') || mimeType.includes('document')) return 'bg-blue-600'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'bg-green-600'
  if (mimeType.includes('powerpoint') || mimeType.includes('presentation')) return 'bg-orange-500'
  return 'bg-neutral-500'
}

function getFileTypeTextColor(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'text-blue-500'
  if (mimeType.startsWith('video/')) return 'text-purple-500'
  if (mimeType.startsWith('audio/')) return 'text-pink-500'
  if (mimeType.includes('pdf')) return 'text-red-500'
  return 'text-neutral-500'
}

// Icon components
const ImageIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' 
      })
    ])
  }
}

const VideoIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' 
      })
    ])
  }
}

const AudioIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3' 
      })
    ])
  }
}

const DocumentIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 
        'stroke-linecap': 'round', 
        'stroke-linejoin': 'round', 
        'stroke-width': '2', 
        d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' 
      })
    ])
  }
}

function getFileTypeIcon(mimeType: string) {
  if (mimeType.startsWith('image/')) return ImageIcon
  if (mimeType.startsWith('video/')) return VideoIcon
  if (mimeType.startsWith('audio/')) return AudioIcon
  return DocumentIcon
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// Watch for modal open to reset state
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    // Fetch tags when modal opens
    if (assetStore.availableTags.length === 0) {
      assetStore.fetchAssets()
    }
  }
})
</script>

