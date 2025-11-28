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
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" />
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
              class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden"
            >
              <!-- Header -->
              <div class="flex items-center justify-between px-6 py-4 border-b border-neutral-200 bg-gradient-to-r from-orange-50 to-amber-50">
                <div class="flex items-center gap-3">
                  <div class="p-2 bg-gradient-to-br from-orange-500 to-amber-600 rounded-lg">
                    <PhotoIcon class="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <DialogTitle class="text-lg font-semibold text-neutral-900">
                      Редактирование и трансформация
                    </DialogTitle>
                    <p class="text-sm text-neutral-500">{{ asset?.label || 'Изображение' }}</p>
                  </div>
                </div>
                <button
                  @click="handleClose"
                  class="p-2 text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors"
                >
                  <XMarkIcon class="w-5 h-5" />
                </button>
              </div>

              <!-- Main Content -->
              <div class="flex h-[500px]">
                <!-- Preview Panel -->
                <div class="flex-1 bg-neutral-900 flex items-center justify-center p-6 relative">
                  <img
                    v-if="asset?.thumbnail_url"
                    :src="asset.thumbnail_url"
                    :alt="asset.label"
                    class="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
                    :style="previewStyle"
                  />
                  <div v-else class="text-neutral-500 text-center">
                    <PhotoIcon class="w-16 h-16 mx-auto mb-2 opacity-50" />
                    <p>Предпросмотр недоступен</p>
                  </div>

                  <!-- Crop Overlay (mock) -->
                  <div 
                    v-if="activeTab === 'crop' && cropArea.width > 0"
                    class="absolute border-2 border-white/70 border-dashed bg-black/30 pointer-events-none"
                    :style="cropOverlayStyle"
                  />
                </div>

                <!-- Tools Panel -->
                <div class="w-80 border-l border-neutral-200 bg-neutral-50 flex flex-col">
                  <!-- Tabs -->
                  <div class="flex border-b border-neutral-200">
                    <button
                      v-for="tab in tabs"
                      :key="tab.id"
                      @click="activeTab = tab.id"
                      :class="[
                        'flex-1 py-3 text-sm font-medium transition-colors relative',
                        activeTab === tab.id
                          ? 'text-orange-600 bg-white'
                          : 'text-neutral-500 hover:text-neutral-700 hover:bg-neutral-100'
                      ]"
                    >
                      <component :is="tab.icon" class="w-4 h-4 mx-auto mb-1" />
                      {{ tab.label }}
                      <div 
                        v-if="activeTab === tab.id" 
                        class="absolute bottom-0 left-0 right-0 h-0.5 bg-orange-500"
                      />
                    </button>
                  </div>

                  <!-- Tab Content -->
                  <div class="flex-1 overflow-y-auto p-4">
                    <!-- Crop Tab -->
                    <div v-if="activeTab === 'crop'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">
                          Соотношение сторон
                        </label>
                        <div class="grid grid-cols-2 gap-2">
                          <button
                            v-for="ratio in aspectRatios"
                            :key="ratio.value"
                            @click="setAspectRatio(ratio.value)"
                            :class="[
                              'px-3 py-2 text-xs font-medium rounded-lg border transition-all',
                              selectedAspectRatio === ratio.value
                                ? 'border-orange-500 bg-orange-50 text-orange-700'
                                : 'border-neutral-200 bg-white text-neutral-600 hover:border-neutral-300'
                            ]"
                          >
                            {{ ratio.label }}
                          </button>
                        </div>
                      </div>

                      <div class="grid grid-cols-2 gap-3">
                        <div>
                          <label class="block text-xs text-neutral-500 mb-1">X</label>
                          <input
                            v-model.number="cropArea.x"
                            type="number"
                            class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                            min="0"
                          />
                        </div>
                        <div>
                          <label class="block text-xs text-neutral-500 mb-1">Y</label>
                          <input
                            v-model.number="cropArea.y"
                            type="number"
                            class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                            min="0"
                          />
                        </div>
                        <div>
                          <label class="block text-xs text-neutral-500 mb-1">Ширина</label>
                          <input
                            v-model.number="cropArea.width"
                            type="number"
                            class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                            min="1"
                          />
                        </div>
                        <div>
                          <label class="block text-xs text-neutral-500 mb-1">Высота</label>
                          <input
                            v-model.number="cropArea.height"
                            type="number"
                            class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                            min="1"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Format Tab -->
                    <div v-if="activeTab === 'format'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">
                          Формат файла
                        </label>
                        <RadioGroup v-model="selectedFormat">
                          <div class="space-y-2">
                            <RadioGroupOption
                              v-for="format in formatOptions"
                              :key="format.value"
                              :value="format.value"
                              v-slot="{ checked }"
                            >
                              <div
                                :class="[
                                  'flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-all',
                                  checked
                                    ? 'border-orange-500 bg-orange-50 ring-2 ring-orange-500/20'
                                    : 'border-neutral-200 bg-white hover:border-neutral-300'
                                ]"
                              >
                                <div>
                                  <p 
                                    :class="[
                                      'text-sm font-medium',
                                      checked ? 'text-orange-700' : 'text-neutral-700'
                                    ]"
                                  >
                                    {{ format.label }}
                                  </p>
                                  <p class="text-xs text-neutral-500">{{ format.description }}</p>
                                </div>
                                <div 
                                  :class="[
                                    'w-4 h-4 rounded-full border-2 transition-colors',
                                    checked 
                                      ? 'border-orange-500 bg-orange-500' 
                                      : 'border-neutral-300 bg-white'
                                  ]"
                                >
                                  <CheckIcon v-if="checked" class="w-full h-full text-white p-0.5" />
                                </div>
                              </div>
                            </RadioGroupOption>
                          </div>
                        </RadioGroup>
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">
                          Качество: {{ formatQuality }}%
                        </label>
                        <input
                          v-model.number="formatQuality"
                          type="range"
                          min="10"
                          max="100"
                          step="5"
                          class="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-orange-500"
                        />
                        <div class="flex justify-between text-xs text-neutral-400 mt-1">
                          <span>Мин. размер</span>
                          <span>Макс. качество</span>
                        </div>
                      </div>

                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">
                          DPI (для печати)
                        </label>
                        <select
                          v-model="formatDPI"
                          class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        >
                          <option :value="72">72 DPI (экран)</option>
                          <option :value="150">150 DPI (средняя печать)</option>
                          <option :value="300">300 DPI (высокая печать)</option>
                          <option :value="600">600 DPI (профессиональная)</option>
                        </select>
                      </div>
                    </div>

                    <!-- Resize Tab -->
                    <div v-if="activeTab === 'resize'" class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-neutral-700 mb-2">
                          Быстрые пресеты
                        </label>
                        <div class="space-y-2">
                          <button
                            v-for="preset in resizePresets"
                            :key="preset.id"
                            @click="applyPreset(preset)"
                            :class="[
                              'w-full flex items-center gap-3 p-3 border rounded-lg transition-all text-left',
                              selectedPreset === preset.id
                                ? 'border-orange-500 bg-orange-50'
                                : 'border-neutral-200 bg-white hover:border-neutral-300'
                            ]"
                          >
                            <span class="text-2xl">{{ preset.icon }}</span>
                            <div class="flex-1">
                              <p class="text-sm font-medium text-neutral-700">{{ preset.name }}</p>
                              <p class="text-xs text-neutral-500">{{ preset.description }}</p>
                            </div>
                          </button>
                        </div>
                      </div>

                      <div class="pt-2 border-t border-neutral-200">
                        <label class="block text-sm font-medium text-neutral-700 mb-2">
                          Произвольный размер
                        </label>
                        <div class="grid grid-cols-2 gap-3">
                          <div>
                            <label class="block text-xs text-neutral-500 mb-1">Ширина (px)</label>
                            <input
                              v-model.number="resizeWidth"
                              type="number"
                              class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                              min="1"
                              max="10000"
                            />
                          </div>
                          <div>
                            <label class="block text-xs text-neutral-500 mb-1">Высота (px)</label>
                            <input
                              v-model.number="resizeHeight"
                              type="number"
                              class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                              min="1"
                              max="10000"
                            />
                          </div>
                        </div>
                        
                        <label class="flex items-center gap-2 mt-3 cursor-pointer">
                          <input
                            v-model="maintainAspect"
                            type="checkbox"
                            class="w-4 h-4 rounded border-neutral-300 text-orange-500 focus:ring-orange-500"
                          />
                          <span class="text-sm text-neutral-600">Сохранять пропорции</span>
                        </label>
                      </div>
                    </div>
                  </div>

                  <!-- Footer Actions -->
                  <div class="p-4 border-t border-neutral-200 bg-white space-y-2">
                    <button
                      @click="handleSaveAsVersion"
                      :disabled="isProcessing"
                      class="w-full flex items-center justify-center gap-2 px-4 py-2.5 
                             bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg 
                             hover:from-orange-600 hover:to-amber-600 
                             disabled:opacity-50 disabled:cursor-not-allowed
                             transition-all font-medium text-sm"
                    >
                      <ArrowPathIcon v-if="isProcessing" class="w-4 h-4 animate-spin" />
                      <CloudArrowUpIcon v-else class="w-4 h-4" />
                      {{ isProcessing ? 'Обработка...' : 'Сохранить как новую версию' }}
                    </button>
                    <button
                      @click="handleSaveAsCopy"
                      :disabled="isProcessing"
                      class="w-full flex items-center justify-center gap-2 px-4 py-2 
                             border border-neutral-200 text-neutral-700 rounded-lg 
                             hover:bg-neutral-50 disabled:opacity-50 
                             transition-colors font-medium text-sm"
                    >
                      <DocumentDuplicateIcon class="w-4 h-4" />
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
import { ref, computed, watch } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
  RadioGroup,
  RadioGroupOption,
} from '@headlessui/vue'
import {
  XMarkIcon,
  PhotoIcon,
  ScissorsIcon,
  DocumentIcon,
  ArrowsPointingOutIcon,
  CheckIcon,
  ArrowPathIcon,
  CloudArrowUpIcon,
  DocumentDuplicateIcon,
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notificationStore'
import {
  TRANSFORMATION_PRESETS,
  ASPECT_RATIO_PRESETS,
  FORMAT_OPTIONS,
  applyTransformation,
  type TransformationOptions,
} from '@/mocks/ai'
import type { Asset } from '@/types/api'

const props = defineProps<{
  isOpen: boolean
  asset: Asset | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'success', result: { type: 'version' | 'copy'; id: number }): void
}>()

const notificationStore = useNotificationStore()

// Tabs
const tabs = [
  { id: 'crop', label: 'Обрезка', icon: ScissorsIcon },
  { id: 'format', label: 'Формат', icon: DocumentIcon },
  { id: 'resize', label: 'Размер', icon: ArrowsPointingOutIcon },
]
const activeTab = ref('crop')

// Crop State
const cropArea = ref({ x: 0, y: 0, width: 800, height: 600 })
const selectedAspectRatio = ref('free')

const aspectRatios = ASPECT_RATIO_PRESETS

// Format State
const selectedFormat = ref<'jpg' | 'png' | 'webp' | 'tiff'>('jpg')
const formatQuality = ref(85)
const formatDPI = ref(72)

const formatOptions = FORMAT_OPTIONS

// Resize State
const resizeWidth = ref(1920)
const resizeHeight = ref(1080)
const maintainAspect = ref(true)
const selectedPreset = ref<string | null>(null)

const resizePresets = TRANSFORMATION_PRESETS

// Processing State
const isProcessing = ref(false)

// Computed
const previewStyle = computed(() => {
  // Simple preview styling based on current settings
  return {}
})

const cropOverlayStyle = computed(() => {
  // Simplified crop overlay positioning
  return {
    left: `${cropArea.value.x / 10}%`,
    top: `${cropArea.value.y / 10}%`,
    width: `${Math.min(cropArea.value.width / 20, 80)}%`,
    height: `${Math.min(cropArea.value.height / 15, 80)}%`,
  }
})

// Methods
function setAspectRatio(ratio: string) {
  selectedAspectRatio.value = ratio
  
  if (ratio === 'free') return
  
  const [w, h] = ratio.split(':').map(Number)
  if (w && h) {
    // Adjust crop area to match aspect ratio
    const currentWidth = cropArea.value.width
    cropArea.value.height = Math.round(currentWidth * (h / w))
  }
}

function applyPreset(preset: typeof TRANSFORMATION_PRESETS[0]) {
  selectedPreset.value = preset.id
  
  if (preset.options.resize) {
    resizeWidth.value = preset.options.resize.width
    resizeHeight.value = preset.options.resize.height
    maintainAspect.value = preset.options.resize.maintainAspect
  }
  
  if (preset.options.format) {
    selectedFormat.value = preset.options.format.type
    formatQuality.value = preset.options.format.quality
    if (preset.options.format.dpi) {
      formatDPI.value = preset.options.format.dpi
    }
  }
  
  if (preset.options.crop) {
    cropArea.value = { ...preset.options.crop, x: cropArea.value.x, y: cropArea.value.y }
    selectedAspectRatio.value = preset.options.crop.aspectRatio || 'free'
  }
}

function buildTransformationOptions(): TransformationOptions {
  return {
    crop: cropArea.value.width > 0 ? {
      x: cropArea.value.x,
      y: cropArea.value.y,
      width: cropArea.value.width,
      height: cropArea.value.height,
      aspectRatio: selectedAspectRatio.value !== 'free' ? selectedAspectRatio.value : undefined,
    } : undefined,
    resize: {
      width: resizeWidth.value,
      height: resizeHeight.value,
      maintainAspect: maintainAspect.value,
    },
    format: {
      type: selectedFormat.value,
      quality: formatQuality.value,
      dpi: formatDPI.value,
    },
  }
}

async function handleSaveAsVersion() {
  if (!props.asset) return
  
  isProcessing.value = true
  try {
    const options = buildTransformationOptions()
    const result = await applyTransformation(props.asset.id, options, 'new_version')
    
    if (result.success) {
      notificationStore.addNotification({
        type: 'success',
        title: 'Версия создана',
        message: 'Новая версия актива успешно сохранена',
      })
      emit('success', { type: 'version', id: result.newVersionId! })
      emit('close')
    }
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось сохранить новую версию',
    })
  } finally {
    isProcessing.value = false
  }
}

async function handleSaveAsCopy() {
  if (!props.asset) return
  
  isProcessing.value = true
  try {
    const options = buildTransformationOptions()
    const result = await applyTransformation(props.asset.id, options, 'new_copy')
    
    if (result.success) {
      notificationStore.addNotification({
        type: 'success',
        title: 'Копия создана',
        message: 'Копия актива с изменениями успешно сохранена',
      })
      emit('success', { type: 'copy', id: result.newAssetId! })
      emit('close')
    }
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось сохранить копию',
    })
  } finally {
    isProcessing.value = false
  }
}

function handleClose() {
  if (!isProcessing.value) {
    emit('close')
  }
}

// Reset state when asset changes
watch(() => props.asset, (newAsset) => {
  if (newAsset) {
    // Reset to defaults
    activeTab.value = 'crop'
    cropArea.value = { x: 0, y: 0, width: 800, height: 600 }
    selectedAspectRatio.value = 'free'
    selectedFormat.value = 'jpg'
    formatQuality.value = 85
    formatDPI.value = 72
    resizeWidth.value = 1920
    resizeHeight.value = 1080
    maintainAspect.value = true
    selectedPreset.value = null
  }
})
</script>

