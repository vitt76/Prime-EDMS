/**
 * Editor Store - History management and state for MediaEditorModal
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ==================== Types ====================

export type AspectRatio = '1:1' | '4:3' | '16:9' | '9:16' | '3:2' | '2:3' | 'free'
export type ImageFormat = 'jpg' | 'png' | 'webp' | 'gif' | 'tiff'
export type WatermarkPosition = 
  | 'top-left' | 'top-center' | 'top-right'
  | 'middle-left' | 'middle-center' | 'middle-right'
  | 'bottom-left' | 'bottom-center' | 'bottom-right'
export type WatermarkType = 'text' | 'image'

export interface CropSettings {
  x: number
  y: number
  width: number
  height: number
  aspectRatio: AspectRatio
}

export interface ResizeSettings {
  width: number
  height: number
  maintainAspect: boolean
  dpi: number
}

export interface FilterSettings {
  brightness: number
  contrast: number
  saturation: number
  blur: number
  sharpen: number
}

export interface TransformSettings {
  rotation: number // -180 to 180
  flipHorizontal: boolean
  flipVertical: boolean
}

export interface WatermarkSettings {
  enabled: boolean
  type: WatermarkType
  text: string
  fontFamily: string
  fontSize: number
  color: string
  assetId: number | null
  imageUrl: string | null
  imageFile: File | null
  position: WatermarkPosition
  opacity: number // 0-100
  scale: number // 10-200 %
  offsetX: number
  offsetY: number
}

export interface EditorState {
  crop: CropSettings
  resize: ResizeSettings
  format: ImageFormat
  quality: number
  transform: TransformSettings
  filters: FilterSettings
  watermark: WatermarkSettings
}

export interface HistoryEntry {
  id: number
  timestamp: number
  label: string
  state: EditorState
}

// ==================== Default Values ====================

const DEFAULT_WATERMARK: WatermarkSettings = {
  enabled: false,
  type: 'text',
  text: '',
  fontFamily: 'Arial',
  fontSize: 24,
  color: '#ffffff',
  assetId: null,
  imageUrl: null,
  imageFile: null,
  position: 'bottom-right',
  opacity: 50,
  scale: 100,
  offsetX: 20,
  offsetY: 20
}

const DEFAULT_TRANSFORM: TransformSettings = {
  rotation: 0,
  flipHorizontal: false,
  flipVertical: false
}

const DEFAULT_FILTERS: FilterSettings = {
  brightness: 0,
  contrast: 0,
  saturation: 0,
  blur: 0,
  sharpen: 0
}

function createDefaultState(width = 1920, height = 1080): EditorState {
  return {
    crop: {
      x: 0,
      y: 0,
      width,
      height,
      aspectRatio: 'free'
    },
    resize: {
      width,
      height,
      maintainAspect: true,
      dpi: 72
    },
    format: 'jpg',
    quality: 85,
    transform: { ...DEFAULT_TRANSFORM },
    filters: { ...DEFAULT_FILTERS },
    watermark: { ...DEFAULT_WATERMARK }
  }
}

// ==================== Store ====================

export const useEditorStore = defineStore('editor', () => {
  // State
  const originalDimensions = ref({ width: 1920, height: 1080 })
  const currentState = ref<EditorState>(createDefaultState())
  const history = ref<HistoryEntry[]>([])
  const historyIndex = ref(-1)
  const maxHistorySize = 50
  let historyIdCounter = 0
  
  // Active asset info
  const assetId = ref<number | null>(null)
  const assetName = ref<string>('')
  const originalFileSize = ref<number>(0) // bytes
  
  // Computed
  const canUndo = computed(() => historyIndex.value > 0)
  const canRedo = computed(() => historyIndex.value < history.value.length - 1)
  
  const currentHistoryLabel = computed(() => {
    if (historyIndex.value >= 0 && historyIndex.value < history.value.length) {
      return history.value[historyIndex.value].label
    }
    return 'Начало'
  })
  
  // Estimated file size based on settings
  const estimatedFileSize = computed(() => {
    const { resize, format, quality, watermark } = currentState.value
    const pixels = resize.width * resize.height
    
    // Base size estimation (bytes per pixel)
    let bytesPerPixel: number
    switch (format) {
      case 'png':
        bytesPerPixel = 3.5 // Lossless, larger
        break
      case 'gif':
        bytesPerPixel = 0.5 // Limited colors
        break
      case 'tiff':
        bytesPerPixel = 4.0 // High quality
        break
      case 'webp':
        bytesPerPixel = 0.8 * (quality / 100) // Efficient
        break
      case 'jpg':
      default:
        bytesPerPixel = 0.3 + (2.7 * (quality / 100)) // 0.3 at Q10, 3 at Q100
        break
    }
    
    let estimated = pixels * bytesPerPixel
    
    // DPI impact (higher DPI = potentially more data for same pixel count at print)
    if (resize.dpi > 150) {
      estimated *= 1.1
    }
    if (resize.dpi > 250) {
      estimated *= 1.2
    }
    
    // Watermark adds some overhead
    if (watermark.enabled) {
      estimated *= 1.05
    }
    
    return Math.round(estimated)
  })
  
  const estimatedFileSizeFormatted = computed(() => {
    const bytes = estimatedFileSize.value
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  })
  
  // CSS Transform string for preview
  const previewTransform = computed(() => {
    const { transform, filters } = currentState.value
    const transforms: string[] = []
    
    if (transform.rotation !== 0) {
      transforms.push(`rotate(${transform.rotation}deg)`)
    }
    if (transform.flipHorizontal) {
      transforms.push('scaleX(-1)')
    }
    if (transform.flipVertical) {
      transforms.push('scaleY(-1)')
    }
    
    return transforms.join(' ')
  })
  
  // CSS Filter string for preview
  const previewFilter = computed(() => {
    const { filters } = currentState.value
    const filterParts: string[] = []
    
    if (filters.brightness !== 0) {
      filterParts.push(`brightness(${100 + filters.brightness}%)`)
    }
    if (filters.contrast !== 0) {
      filterParts.push(`contrast(${100 + filters.contrast}%)`)
    }
    if (filters.saturation !== 0) {
      filterParts.push(`saturate(${100 + filters.saturation}%)`)
    }
    if (filters.blur > 0) {
      filterParts.push(`blur(${filters.blur}px)`)
    }
    
    return filterParts.join(' ') || 'none'
  })
  
  // Methods
  function initialize(asset: { id: number; label: string; size: number }, width: number, height: number) {
    assetId.value = asset.id
    assetName.value = asset.label
    originalFileSize.value = asset.size
    originalDimensions.value = { width, height }
    
    currentState.value = createDefaultState(width, height)
    
    // Clear history and add initial state
    history.value = []
    historyIndex.value = -1
    pushHistory('Начало')
  }
  
  function pushHistory(label: string) {
    // Remove any redo states
    if (historyIndex.value < history.value.length - 1) {
      history.value = history.value.slice(0, historyIndex.value + 1)
    }
    
    // Deep clone current state
    const entry: HistoryEntry = {
      id: ++historyIdCounter,
      timestamp: Date.now(),
      label,
      state: JSON.parse(JSON.stringify(currentState.value))
    }
    
    history.value.push(entry)
    historyIndex.value = history.value.length - 1
    
    // Limit history size
    if (history.value.length > maxHistorySize) {
      history.value.shift()
      historyIndex.value--
    }
  }
  
  function undo() {
    if (!canUndo.value) return false
    
    historyIndex.value--
    currentState.value = JSON.parse(JSON.stringify(history.value[historyIndex.value].state))
    return true
  }
  
  function redo() {
    if (!canRedo.value) return false
    
    historyIndex.value++
    currentState.value = JSON.parse(JSON.stringify(history.value[historyIndex.value].state))
    return true
  }
  
  // Transform actions
  function rotateLeft() {
    currentState.value.transform.rotation = (currentState.value.transform.rotation - 90 + 360) % 360
    if (currentState.value.transform.rotation > 180) {
      currentState.value.transform.rotation -= 360
    }
    pushHistory('Поворот влево')
  }
  
  function rotateRight() {
    currentState.value.transform.rotation = (currentState.value.transform.rotation + 90) % 360
    if (currentState.value.transform.rotation > 180) {
      currentState.value.transform.rotation -= 360
    }
    pushHistory('Поворот вправо')
  }
  
  function flipHorizontal() {
    currentState.value.transform.flipHorizontal = !currentState.value.transform.flipHorizontal
    pushHistory('Отразить по горизонтали')
  }
  
  function flipVertical() {
    currentState.value.transform.flipVertical = !currentState.value.transform.flipVertical
    pushHistory('Отразить по вертикали')
  }
  
  function resetTransform() {
    currentState.value.transform = { ...DEFAULT_TRANSFORM }
    pushHistory('Сброс трансформации')
  }
  
  // Crop actions
  function setCrop(crop: Partial<CropSettings>) {
    currentState.value.crop = { ...currentState.value.crop, ...crop }
  }
  
  function applyCrop() {
    pushHistory(`Обрезка ${currentState.value.crop.width}×${currentState.value.crop.height}`)
  }
  
  // Resize actions
  function setResize(resize: Partial<ResizeSettings>) {
    currentState.value.resize = { ...currentState.value.resize, ...resize }
  }
  
  function applyResize() {
    pushHistory(`Размер ${currentState.value.resize.width}×${currentState.value.resize.height}`)
  }
  
  function setDPI(dpi: number) {
    currentState.value.resize.dpi = Math.max(72, Math.min(600, dpi))
    pushHistory(`DPI: ${dpi}`)
  }
  
  // Format actions
  function setFormat(format: ImageFormat) {
    currentState.value.format = format
    pushHistory(`Формат: ${format.toUpperCase()}`)
  }
  
  function setQuality(quality: number) {
    currentState.value.quality = Math.max(10, Math.min(100, quality))
  }
  
  // Filter actions
  function setFilters(filters: Partial<FilterSettings>) {
    currentState.value.filters = { ...currentState.value.filters, ...filters }
  }
  
  function applyFilters() {
    pushHistory('Применение фильтров')
  }
  
  function resetFilters() {
    currentState.value.filters = { ...DEFAULT_FILTERS }
    pushHistory('Сброс фильтров')
  }
  
  // Watermark actions
  function setWatermark(watermark: Partial<WatermarkSettings>) {
    currentState.value.watermark = { ...currentState.value.watermark, ...watermark }
  }
  
  function enableWatermark(enabled: boolean) {
    currentState.value.watermark.enabled = enabled
    if (enabled) {
      pushHistory('Водяной знак включён')
    }
  }
  
  function setWatermarkImage(file: File | null, url: string | null) {
    currentState.value.watermark.imageFile = file
    currentState.value.watermark.imageUrl = url
    currentState.value.watermark.type = 'image'
    if (file) {
      pushHistory(`Водяной знак: ${file.name}`)
    }
  }
  
  function setWatermarkText(text: string) {
    currentState.value.watermark.text = text
    currentState.value.watermark.type = 'text'
  }
  
  function applyWatermark() {
    if (currentState.value.watermark.enabled) {
      pushHistory('Водяной знак применён')
    }
  }
  
  function resetWatermark() {
    currentState.value.watermark = { ...DEFAULT_WATERMARK }
    pushHistory('Водяной знак удалён')
  }
  
  // Reset everything
  function reset() {
    const { width, height } = originalDimensions.value
    currentState.value = createDefaultState(width, height)
    history.value = []
    historyIndex.value = -1
    pushHistory('Сброс')
  }
  
  // Export state for saving
  function getExportState() {
    return {
      ...currentState.value,
      originalDimensions: originalDimensions.value,
      assetId: assetId.value
    }
  }
  
  return {
    // State
    originalDimensions,
    currentState,
    history,
    historyIndex,
    assetId,
    assetName,
    originalFileSize,
    
    // Computed
    canUndo,
    canRedo,
    currentHistoryLabel,
    estimatedFileSize,
    estimatedFileSizeFormatted,
    previewTransform,
    previewFilter,
    
    // Methods
    initialize,
    pushHistory,
    undo,
    redo,
    
    // Transform
    rotateLeft,
    rotateRight,
    flipHorizontal,
    flipVertical,
    resetTransform,
    
    // Crop
    setCrop,
    applyCrop,
    
    // Resize
    setResize,
    applyResize,
    setDPI,
    
    // Format
    setFormat,
    setQuality,
    
    // Filters
    setFilters,
    applyFilters,
    resetFilters,
    
    // Watermark
    setWatermark,
    enableWatermark,
    setWatermarkImage,
    setWatermarkText,
    applyWatermark,
    resetWatermark,
    
    // General
    reset,
    getExportState
  }
})

