<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/70 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel 
              class="w-full max-w-5xl transform overflow-hidden rounded-2xl 
                     bg-neutral-900 text-white shadow-2xl flex flex-col"
              style="height: 85vh;"
            >
              <!-- Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-neutral-700 shrink-0">
                <div class="flex items-center gap-4">
                  <DialogTitle class="text-lg font-semibold">
                    Редактор изображений
                  </DialogTitle>
                  <span class="text-sm text-neutral-400">{{ asset?.label }}</span>
                </div>
                <button
                  class="p-2 text-neutral-400 hover:text-white hover:bg-neutral-700 rounded-lg transition-colors"
                  @click="handleClose"
                >
                  <XMarkIcon class="w-5 h-5" />
                </button>
              </div>

              <!-- Main Content -->
              <div class="flex flex-1 overflow-hidden">
                <!-- Canvas Area -->
                <div class="flex-1 flex items-center justify-center bg-neutral-950 relative overflow-hidden p-8">
                  <!-- Image Preview with Crop Overlay -->
                  <div class="relative max-w-full max-h-full">
                    <img
                      ref="imageRef"
                      :src="asset?.preview_url || asset?.thumbnail_url"
                      :alt="asset?.label"
                      class="max-w-full max-h-[60vh] object-contain rounded-lg"
                      :style="imageStyle"
                      @load="handleImageLoad"
                    />
                    
                    <!-- Crop Overlay (simplified visual) -->
                    <div 
                      v-if="activeToolId === 'crop' && cropPreview"
                      class="absolute border-2 border-blue-500 bg-blue-500/10 pointer-events-none"
                      :style="cropOverlayStyle"
                    />
                  </div>

                  <!-- Processing Overlay -->
                  <div 
                    v-if="isProcessing"
                    class="absolute inset-0 bg-black/60 flex flex-col items-center justify-center"
                  >
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                    <p class="text-white font-medium">Обрабатываем изображение...</p>
                    <p class="text-neutral-400 text-sm mt-1">{{ processingMessage }}</p>
                  </div>
                </div>

                <!-- Tools Sidebar -->
                <div class="w-80 bg-neutral-800 border-l border-neutral-700 flex flex-col shrink-0">
                  <!-- Tool Tabs -->
                  <div class="flex border-b border-neutral-700 shrink-0">
                    <button
                      v-for="tool in tools"
                      :key="tool.id"
                      :class="[
                        'flex-1 flex flex-col items-center gap-1 px-4 py-3 text-sm transition-colors',
                        activeToolId === tool.id 
                          ? 'bg-neutral-700 text-white' 
                          : 'text-neutral-400 hover:text-white hover:bg-neutral-700/50'
                      ]"
                      @click="activeToolId = tool.id"
                    >
                      <component :is="tool.icon" class="w-5 h-5" />
                      <span class="text-xs">{{ tool.label }}</span>
                    </button>
                  </div>

                  <!-- Tool Content -->
                  <div class="flex-1 overflow-y-auto p-4">
                    <!-- Crop Tool -->
                    <div v-if="activeToolId === 'crop'" class="space-y-6">
                      <div>
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          Соотношение сторон
                        </label>
                        <div class="grid grid-cols-3 gap-2">
                          <button
                            v-for="ratio in aspectRatios"
                            :key="ratio.value"
                            :class="[
                              'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                              settings.crop.aspectRatio === ratio.value
                                ? 'bg-blue-600 text-white'
                                : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                            ]"
                            @click="setAspectRatio(ratio.value)"
                          >
                            {{ ratio.label }}
                          </button>
                        </div>
                      </div>

                      <!-- Crop Dimensions -->
                      <div class="grid grid-cols-2 gap-4">
                        <div>
                          <label class="block text-xs font-medium text-neutral-400 mb-1">Ширина</label>
                          <input
                            v-model.number="settings.crop.width"
                            type="number"
                            min="1"
                            class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                   text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-neutral-400 mb-1">Высота</label>
                          <input
                            v-model.number="settings.crop.height"
                            type="number"
                            min="1"
                            class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                   text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </div>

                      <button
                        class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                               transition-colors text-sm font-medium"
                        @click="applyCrop"
                      >
                        Применить обрезку
                      </button>
                    </div>

                    <!-- Resize Tool -->
                    <div v-if="activeToolId === 'resize'" class="space-y-6">
                      <div>
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          Размер изображения
                        </label>
                        
                        <div class="space-y-4">
                          <div>
                            <label class="block text-xs font-medium text-neutral-400 mb-1">
                              Ширина (px)
                            </label>
                            <input
                              v-model.number="settings.resize.width"
                              type="number"
                              min="1"
                              max="10000"
                              class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                     text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              @input="handleWidthChange"
                            />
                          </div>

                          <div>
                            <label class="block text-xs font-medium text-neutral-400 mb-1">
                              Высота (px)
                            </label>
                            <input
                              v-model.number="settings.resize.height"
                              type="number"
                              min="1"
                              max="10000"
                              class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                     text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              @input="handleHeightChange"
                            />
                          </div>

                          <label class="flex items-center gap-2">
                            <input
                              v-model="settings.resize.maintainAspect"
                              type="checkbox"
                              class="w-4 h-4 rounded border-neutral-600 bg-neutral-700 
                                     text-blue-600 focus:ring-blue-500"
                            />
                            <span class="text-sm text-neutral-300">Сохранять пропорции</span>
                          </label>
                        </div>
                      </div>

                      <!-- Preset Sizes -->
                      <div>
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          Быстрый выбор
                        </label>
                        <div class="space-y-2">
                          <button
                            v-for="preset in sizePresets"
                            :key="preset.label"
                            class="w-full flex items-center justify-between px-3 py-2 bg-neutral-700 
                                   rounded-lg hover:bg-neutral-600 transition-colors"
                            @click="applySizePreset(preset)"
                          >
                            <span class="text-sm text-neutral-300">{{ preset.label }}</span>
                            <span class="text-xs text-neutral-500">{{ preset.width }}×{{ preset.height }}</span>
                          </button>
                        </div>
                      </div>
                    </div>

                    <!-- Format Tool -->
                    <div v-if="activeToolId === 'format'" class="space-y-6">
                      <div>
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          Формат файла
                        </label>
                        <div class="space-y-2">
                          <button
                            v-for="format in formats"
                            :key="format.value"
                            :class="[
                              'w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors',
                              settings.format === format.value
                                ? 'bg-blue-600 text-white'
                                : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                            ]"
                            @click="settings.format = format.value"
                          >
                            <div class="flex items-center gap-3">
                              <span class="text-lg">{{ format.icon }}</span>
                              <div class="text-left">
                                <div class="font-medium">{{ format.label }}</div>
                                <div class="text-xs opacity-70">{{ format.description }}</div>
                              </div>
                            </div>
                            <CheckIcon 
                              v-if="settings.format === format.value" 
                              class="w-5 h-5" 
                            />
                          </button>
                        </div>
                      </div>

                      <!-- Quality Slider (for JPG/WEBP) -->
                      <div v-if="settings.format === 'jpg' || settings.format === 'webp'">
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          Качество: {{ settings.quality }}%
                        </label>
                        <input
                          v-model.number="settings.quality"
                          type="range"
                          min="10"
                          max="100"
                          step="5"
                          class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer
                                 accent-blue-500"
                        />
                        <div class="flex justify-between text-xs text-neutral-500 mt-1">
                          <span>Маленький файл</span>
                          <span>Высокое качество</span>
                        </div>
                      </div>
                    </div>

                    <!-- Adjust Tool -->
                    <div v-if="activeToolId === 'adjust'" class="space-y-6">
                      <div>
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          Коррекция
                        </label>
                        
                        <div class="space-y-5">
                          <div>
                            <div class="flex justify-between text-xs text-neutral-400 mb-2">
                              <span>Яркость</span>
                              <span>{{ settings.filters.brightness }}</span>
                            </div>
                            <input
                              v-model.number="settings.filters.brightness"
                              type="range"
                              min="-100"
                              max="100"
                              class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer
                                     accent-blue-500"
                            />
                          </div>

                          <div>
                            <div class="flex justify-between text-xs text-neutral-400 mb-2">
                              <span>Контраст</span>
                              <span>{{ settings.filters.contrast }}</span>
                            </div>
                            <input
                              v-model.number="settings.filters.contrast"
                              type="range"
                              min="-100"
                              max="100"
                              class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer
                                     accent-blue-500"
                            />
                          </div>

                          <div>
                            <div class="flex justify-between text-xs text-neutral-400 mb-2">
                              <span>Насыщенность</span>
                              <span>{{ settings.filters.saturation }}</span>
                            </div>
                            <input
                              v-model.number="settings.filters.saturation"
                              type="range"
                              min="-100"
                              max="100"
                              class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer
                                     accent-blue-500"
                            />
                          </div>
                        </div>
                      </div>

                      <button
                        class="w-full px-4 py-2 bg-neutral-700 text-neutral-300 rounded-lg 
                               hover:bg-neutral-600 transition-colors text-sm"
                        @click="resetFilters"
                      >
                        Сбросить настройки
                      </button>
                    </div>
                  </div>

                  <!-- Save Actions -->
                  <div class="p-4 border-t border-neutral-700 space-y-3 shrink-0">
                    <button
                      class="w-full flex items-center justify-center gap-2 px-4 py-3 
                             bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                             transition-colors font-medium disabled:opacity-50"
                      :disabled="isProcessing"
                      @click="handleSaveAsVersion"
                    >
                      <DocumentDuplicateIcon class="w-5 h-5" />
                      Сохранить как новую версию
                    </button>
                    <button
                      class="w-full flex items-center justify-center gap-2 px-4 py-3 
                             bg-neutral-700 text-white rounded-lg hover:bg-neutral-600 
                             transition-colors font-medium disabled:opacity-50"
                      :disabled="isProcessing"
                      @click="handleSaveAsCopy"
                    >
                      <FolderPlusIcon class="w-5 h-5" />
                      Сохранить как копию
                    </button>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch, markRaw, type Component } from 'vue'
import { 
  Dialog, 
  DialogPanel, 
  DialogTitle,
  TransitionRoot, 
  TransitionChild 
} from '@headlessui/vue'
import {
  XMarkIcon,
  CheckIcon,
  ScissorsIcon,
  ArrowsPointingOutIcon,
  DocumentIcon,
  AdjustmentsHorizontalIcon,
  DocumentDuplicateIcon,
  FolderPlusIcon
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notificationStore'
import type { Asset } from '@/types/api'
import {
  applyTransformation,
  type AspectRatio,
  type ImageFormat,
  type TransformationSettings
} from '@/mocks/ai'

interface Props {
  isOpen: boolean
  asset: Asset | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  saveVersion: [assetId: number, versionId: number]
  saveCopy: [originalId: number, newAssetId: number]
}>()

const notificationStore = useNotificationStore()

// Refs
const imageRef = ref<HTMLImageElement | null>(null)
const originalDimensions = ref({ width: 1920, height: 1080 })

// State
const activeToolId = ref<'crop' | 'resize' | 'format' | 'adjust'>('crop')
const isProcessing = ref(false)
const processingMessage = ref('')
const cropPreview = ref(false)

const settings = ref<TransformationSettings>({
  crop: {
    x: 0,
    y: 0,
    width: 1920,
    height: 1080,
    aspectRatio: 'free'
  },
  resize: {
    width: 1920,
    height: 1080,
    maintainAspect: true
  },
  format: 'jpg',
  quality: 85,
  rotation: 0,
  filters: {
    brightness: 0,
    contrast: 0,
    saturation: 0
  }
})

// Tool definitions
const tools = [
  { id: 'crop' as const, label: 'Обрезка', icon: markRaw(ScissorsIcon) },
  { id: 'resize' as const, label: 'Размер', icon: markRaw(ArrowsPointingOutIcon) },
  { id: 'format' as const, label: 'Формат', icon: markRaw(DocumentIcon) },
  { id: 'adjust' as const, label: 'Коррекция', icon: markRaw(AdjustmentsHorizontalIcon) }
]

const aspectRatios: { value: AspectRatio; label: string }[] = [
  { value: '1:1', label: '1:1' },
  { value: '4:3', label: '4:3' },
  { value: '16:9', label: '16:9' },
  { value: '9:16', label: '9:16' },
  { value: '3:2', label: '3:2' },
  { value: 'free', label: 'Свободно' }
]

const formats: { value: ImageFormat; label: string; icon: string; description: string }[] = [
  { value: 'jpg', label: 'JPEG', icon: '📷', description: 'Оптимально для фотографий' },
  { value: 'png', label: 'PNG', icon: '🖼️', description: 'Поддержка прозрачности' },
  { value: 'webp', label: 'WebP', icon: '🌐', description: 'Современный формат для веба' },
  { value: 'gif', label: 'GIF', icon: '🎬', description: 'Для анимаций' }
]

const sizePresets = [
  { label: 'Оригинал', width: 0, height: 0, useOriginal: true },
  { label: 'HD (1920×1080)', width: 1920, height: 1080 },
  { label: 'Full HD (1280×720)', width: 1280, height: 720 },
  { label: 'Социальные сети (1200×1200)', width: 1200, height: 1200 },
  { label: 'Миниатюра (400×400)', width: 400, height: 400 },
  { label: 'Превью (800×600)', width: 800, height: 600 }
]

// Computed
const imageStyle = computed(() => {
  const { brightness, contrast, saturation } = settings.value.filters!
  const filters = [
    `brightness(${100 + brightness}%)`,
    `contrast(${100 + contrast}%)`,
    `saturate(${100 + saturation}%)`
  ].join(' ')
  
  return {
    filter: filters,
    transform: `rotate(${settings.value.rotation}deg)`
  }
})

const cropOverlayStyle = computed(() => {
  if (!settings.value.crop || !originalDimensions.value.width) return {}
  
  const { x, y, width, height } = settings.value.crop
  const scaleX = (imageRef.value?.clientWidth || 0) / originalDimensions.value.width
  const scaleY = (imageRef.value?.clientHeight || 0) / originalDimensions.value.height
  
  return {
    left: `${x * scaleX}px`,
    top: `${y * scaleY}px`,
    width: `${width * scaleX}px`,
    height: `${height * scaleY}px`
  }
})

// Methods
function handleClose() {
  if (!isProcessing.value) {
    emit('close')
  }
}

function handleImageLoad() {
  if (imageRef.value) {
    // Get natural dimensions
    originalDimensions.value = {
      width: imageRef.value.naturalWidth || 1920,
      height: imageRef.value.naturalHeight || 1080
    }
    
    // Initialize settings with original dimensions
    settings.value.crop = {
      x: 0,
      y: 0,
      width: originalDimensions.value.width,
      height: originalDimensions.value.height,
      aspectRatio: 'free'
    }
    settings.value.resize = {
      width: originalDimensions.value.width,
      height: originalDimensions.value.height,
      maintainAspect: true
    }
  }
}

function setAspectRatio(ratio: AspectRatio) {
  settings.value.crop!.aspectRatio = ratio
  cropPreview.value = true
  
  if (ratio === 'free') return
  
  const { width } = originalDimensions.value
  const ratioMap: Record<AspectRatio, number> = {
    '1:1': 1,
    '4:3': 3 / 4,
    '16:9': 9 / 16,
    '9:16': 16 / 9,
    '3:2': 2 / 3,
    'free': 1
  }
  
  const newHeight = Math.round(width * ratioMap[ratio])
  settings.value.crop!.width = width
  settings.value.crop!.height = newHeight
}

function applyCrop() {
  notificationStore.addNotification({
    type: 'success',
    title: 'Обрезка применена',
    message: `Размер: ${settings.value.crop?.width}×${settings.value.crop?.height}`
  })
  cropPreview.value = false
}

function handleWidthChange() {
  if (settings.value.resize!.maintainAspect && originalDimensions.value.width) {
    const ratio = originalDimensions.value.height / originalDimensions.value.width
    settings.value.resize!.height = Math.round(settings.value.resize!.width * ratio)
  }
}

function handleHeightChange() {
  if (settings.value.resize!.maintainAspect && originalDimensions.value.height) {
    const ratio = originalDimensions.value.width / originalDimensions.value.height
    settings.value.resize!.width = Math.round(settings.value.resize!.height * ratio)
  }
}

function applySizePreset(preset: typeof sizePresets[0]) {
  if (preset.useOriginal) {
    settings.value.resize!.width = originalDimensions.value.width
    settings.value.resize!.height = originalDimensions.value.height
  } else {
    settings.value.resize!.width = preset.width
    settings.value.resize!.height = preset.height
  }
}

function resetFilters() {
  settings.value.filters = {
    brightness: 0,
    contrast: 0,
    saturation: 0
  }
}

async function handleSaveAsVersion() {
  if (!props.asset) return
  
  isProcessing.value = true
  processingMessage.value = 'Создание новой версии...'
  
  try {
    const result = await applyTransformation(props.asset.id, settings.value, 'new_version')
    
    if (result.success) {
      notificationStore.addNotification({
        type: 'success',
        title: 'Версия создана',
        message: `Новая версия #${result.newVersionId} сохранена`
      })
      emit('saveVersion', props.asset.id, result.newVersionId!)
      emit('close')
    }
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось сохранить изменения'
    })
  } finally {
    isProcessing.value = false
  }
}

async function handleSaveAsCopy() {
  if (!props.asset) return
  
  isProcessing.value = true
  processingMessage.value = 'Создание копии...'
  
  try {
    const result = await applyTransformation(props.asset.id, settings.value, 'new_copy')
    
    if (result.success) {
      notificationStore.addNotification({
        type: 'success',
        title: 'Копия создана',
        message: `Новый актив #${result.newAssetId} добавлен в галерею`
      })
      emit('saveCopy', props.asset.id, result.newAssetId!)
      emit('close')
    }
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось создать копию'
    })
  } finally {
    isProcessing.value = false
  }
}

// Watch for asset changes
watch(() => props.asset, (newAsset) => {
  if (newAsset) {
    // Reset settings when asset changes
    activeToolId.value = 'crop'
    cropPreview.value = false
    settings.value.filters = {
      brightness: 0,
      contrast: 0,
      saturation: 0
    }
    settings.value.quality = 85
    settings.value.format = 'jpg'
  }
})
</script>

<style scoped>
/* Custom range slider styling */
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);
}

input[type="range"]::-moz-range-thumb {
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.3);
}
</style>

