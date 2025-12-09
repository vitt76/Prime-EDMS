<template>
  <TransitionRoot as="div" :show="isOpen">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="div"
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
            as="div"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel 
              class="w-full max-w-6xl transform overflow-hidden rounded-2xl 
                     bg-neutral-900 text-white shadow-2xl flex flex-col"
              style="height: 90vh;"
            >
              <!-- Header with Undo/Redo -->
              <div class="flex items-center justify-between px-6 py-3 border-b border-neutral-700 shrink-0 bg-neutral-800">
                <div class="flex items-center gap-4">
                  <DialogTitle class="text-lg font-semibold">
                    Редактор изображений
                  </DialogTitle>
                  <span class="text-sm text-neutral-400 truncate max-w-[200px]">{{ asset?.label }}</span>
                </div>

                <!-- Global Controls -->
                <div class="flex items-center gap-2">
                  <!-- Undo/Redo -->
                  <div class="flex items-center bg-neutral-700 rounded-lg p-1">
                    <button
                      :disabled="!editorStore.canUndo"
                      class="p-2 rounded-md transition-colors disabled:opacity-30 disabled:cursor-not-allowed
                             hover:bg-neutral-600"
                      title="Отменить (Ctrl+Z)"
                      @click="handleUndo"
                    >
                      <ArrowUturnLeftIcon class="w-4 h-4" />
                    </button>
                    <button
                      :disabled="!editorStore.canRedo"
                      class="p-2 rounded-md transition-colors disabled:opacity-30 disabled:cursor-not-allowed
                             hover:bg-neutral-600"
                      title="Повторить (Ctrl+Y)"
                      @click="handleRedo"
                    >
                      <ArrowUturnRightIcon class="w-4 h-4" />
                    </button>
                  </div>

                  <!-- History Label -->
                  <span class="text-xs text-neutral-500 min-w-[80px]">
                    {{ editorStore.currentHistoryLabel }}
                  </span>

                  <div class="w-px h-6 bg-neutral-600" />

                  <!-- Close -->
                  <button
                    class="p-2 text-neutral-400 hover:text-white hover:bg-neutral-700 rounded-lg transition-colors"
                    @click="handleClose"
                  >
                    <XMarkIcon class="w-5 h-5" />
                  </button>
                </div>
              </div>

              <!-- Main Content -->
              <div class="flex flex-1 overflow-hidden">
                <!-- Canvas Area -->
                <div class="flex-1 flex flex-col bg-neutral-950 relative overflow-hidden">
                  <!-- Transform Toolbar -->
                  <div class="flex items-center justify-center gap-2 py-2 px-4 bg-neutral-900 border-b border-neutral-800 shrink-0">
                    <span class="text-xs text-neutral-500 mr-2">Трансформация:</span>
                    
                    <button
                      class="p-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 transition-colors group"
                      title="Повернуть влево на 90°"
                      @click="editorStore.rotateLeft()"
                    >
                      <ArrowPathIcon class="w-4 h-4 -scale-x-100 group-hover:text-blue-400" />
                    </button>
                    
                    <button
                      class="p-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 transition-colors group"
                      title="Повернуть вправо на 90°"
                      @click="editorStore.rotateRight()"
                    >
                      <ArrowPathIcon class="w-4 h-4 group-hover:text-blue-400" />
                    </button>

                    <div class="w-px h-5 bg-neutral-700" />

                    <button
                      :class="[
                        'p-2 rounded-lg transition-colors',
                        editorStore.currentState.transform.flipHorizontal 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-neutral-800 hover:bg-neutral-700'
                      ]"
                      title="Отразить по горизонтали"
                      @click="editorStore.flipHorizontal()"
                    >
                      <ArrowsRightLeftIcon class="w-4 h-4" />
                    </button>
                    
                    <button
                      :class="[
                        'p-2 rounded-lg transition-colors',
                        editorStore.currentState.transform.flipVertical 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-neutral-800 hover:bg-neutral-700'
                      ]"
                      title="Отразить по вертикали"
                      @click="editorStore.flipVertical()"
                    >
                      <ArrowsUpDownIcon class="w-4 h-4" />
                    </button>

                    <div class="w-px h-5 bg-neutral-700" />

                    <button
                      v-if="hasTransformChanges"
                      class="px-3 py-1.5 text-xs rounded-lg bg-neutral-700 hover:bg-neutral-600 transition-colors"
                      @click="editorStore.resetTransform()"
                    >
                      Сбросить
                    </button>

                    <!-- Rotation indicator -->
                    <span 
                      v-if="editorStore.currentState.transform.rotation !== 0"
                      class="ml-2 px-2 py-1 text-xs bg-blue-600/20 text-blue-400 rounded"
                    >
                      {{ editorStore.currentState.transform.rotation }}°
                    </span>
                  </div>

                  <!-- Image Preview Container -->
                  <div class="flex-1 flex items-center justify-center p-8 relative">
                    <div class="relative max-w-full max-h-full">
                      <!-- Main Image -->
                      <img
                        ref="imageRef"
                        :src="asset?.preview_url || asset?.thumbnail_url"
                        :alt="asset?.label"
                        class="max-w-full max-h-[55vh] object-contain rounded-lg shadow-2xl transition-transform duration-200"
                        :style="imagePreviewStyle"
                        @load="handleImageLoad"
                      />
                      
                      <!-- Crop Overlay -->
                      <div 
                        v-if="activeToolId === 'crop' && cropPreview"
                        class="absolute border-2 border-blue-500 bg-blue-500/10 pointer-events-none"
                        :style="cropOverlayStyle"
                      />

                      <!-- Watermark Preview Overlay -->
                      <div 
                        v-if="editorStore.currentState.watermark.enabled"
                        class="absolute pointer-events-none"
                        :style="watermarkPreviewStyle"
                      >
                        <!-- Text Watermark -->
                        <span 
                          v-if="editorStore.currentState.watermark.type === 'text'"
                          class="whitespace-nowrap select-none"
                          :style="watermarkTextStyle"
                        >
                          {{ editorStore.currentState.watermark.text || 'Водяной знак' }}
                        </span>
                        
                        <!-- Image Watermark -->
                        <img
                          v-else-if="watermarkImagePreview"
                          :src="watermarkImagePreview"
                          alt="Watermark"
                          class="max-w-[150px] max-h-[80px] object-contain"
                          :style="{ opacity: editorStore.currentState.watermark.opacity / 100 }"
                        />
                      </div>
                    </div>

                    <!-- Processing Overlay -->
                    <div 
                      v-if="isProcessing"
                      class="absolute inset-0 bg-black/60 flex flex-col items-center justify-center"
                    >
                      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                      <p class="text-white font-medium">{{ processingMessage }}</p>
                    </div>
                  </div>

                  <!-- Info Bar -->
                  <div class="flex items-center justify-between px-4 py-2 bg-neutral-900 border-t border-neutral-800 text-xs text-neutral-400 shrink-0">
                    <div class="flex items-center gap-4">
                      <span>Оригинал: {{ editorStore.originalDimensions.width }}×{{ editorStore.originalDimensions.height }}</span>
                      <span>→</span>
                      <span class="text-white">
                        {{ editorStore.currentState.resize.width }}×{{ editorStore.currentState.resize.height }}
                      </span>
                    </div>
                    <div class="flex items-center gap-4">
                      <span>{{ editorStore.currentState.resize.dpi }} DPI</span>
                      <span>{{ editorStore.currentState.format.toUpperCase() }}</span>
                      <span class="text-blue-400">~{{ editorStore.estimatedFileSizeFormatted }}</span>
                    </div>
                  </div>
                </div>

                <!-- Tools Sidebar -->
                <div class="w-80 bg-neutral-800 border-l border-neutral-700 flex flex-col shrink-0">
                  <!-- Tool Tabs -->
                  <div class="grid grid-cols-5 border-b border-neutral-700 shrink-0">
                    <button
                      v-for="tool in tools"
                      :key="tool.id"
                      :class="[
                        'flex flex-col items-center gap-0.5 px-2 py-3 text-[10px] transition-colors relative',
                        activeToolId === tool.id 
                          ? 'bg-neutral-700 text-white' 
                          : 'text-neutral-400 hover:text-white hover:bg-neutral-700/50'
                      ]"
                      @click="activeToolId = tool.id"
                    >
                      <component :is="tool.icon" class="w-4 h-4" />
                      <span class="truncate">{{ tool.label }}</span>
                      <div 
                        v-if="activeToolId === tool.id"
                        class="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500"
                      />
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
                              'px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                              editorStore.currentState.crop.aspectRatio === ratio.value
                                ? 'bg-blue-600 text-white'
                                : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                            ]"
                            @click="setAspectRatio(ratio.value)"
                          >
                            {{ ratio.label }}
                          </button>
                        </div>
                      </div>

                      <div class="grid grid-cols-2 gap-3">
                        <div>
                          <label class="block text-xs font-medium text-neutral-400 mb-1">Ширина</label>
                          <input
                            :value="editorStore.currentState.crop.width"
                            type="number"
                            min="1"
                            class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                   text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            @input="updateCropWidth"
                          />
                        </div>
                        <div>
                          <label class="block text-xs font-medium text-neutral-400 mb-1">Высота</label>
                          <input
                            :value="editorStore.currentState.crop.height"
                            type="number"
                            min="1"
                            class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                   text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            @input="updateCropHeight"
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
                        
                        <div class="space-y-3">
                          <div class="grid grid-cols-2 gap-3">
                            <div>
                              <label class="block text-xs font-medium text-neutral-400 mb-1">Ширина (px)</label>
                              <input
                                :value="editorStore.currentState.resize.width"
                                type="number"
                                min="1"
                                max="10000"
                                class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                       text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                @input="handleWidthChange"
                              />
                            </div>
                            <div>
                              <label class="block text-xs font-medium text-neutral-400 mb-1">Высота (px)</label>
                              <input
                                :value="editorStore.currentState.resize.height"
                                type="number"
                                min="1"
                                max="10000"
                                class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                       text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                @input="handleHeightChange"
                              />
                            </div>
                          </div>

                          <label class="flex items-center gap-2">
                            <input
                              :checked="editorStore.currentState.resize.maintainAspect"
                              type="checkbox"
                              class="w-4 h-4 rounded border-neutral-600 bg-neutral-700 
                                     text-blue-600 focus:ring-blue-500"
                              @change="toggleMaintainAspect"
                            />
                            <span class="text-sm text-neutral-300">Сохранять пропорции</span>
                          </label>
                        </div>
                      </div>

                      <!-- DPI Setting -->
                      <div>
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          DPI (разрешение печати)
                        </label>
                        <div class="flex items-center gap-3">
                          <input
                            :value="editorStore.currentState.resize.dpi"
                            type="number"
                            min="72"
                            max="600"
                            class="w-24 px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                   text-white text-sm focus:ring-2 focus:ring-blue-500"
                            @input="handleDPIChange"
                          />
                          <div class="flex gap-2">
                            <button
                              :class="[
                                'px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                                editorStore.currentState.resize.dpi === 72 
                                  ? 'bg-blue-600 text-white' 
                                  : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                              ]"
                              @click="editorStore.setDPI(72)"
                            >
                              Веб (72)
                            </button>
                            <button
                              :class="[
                                'px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                                editorStore.currentState.resize.dpi === 150 
                                  ? 'bg-blue-600 text-white' 
                                  : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                              ]"
                              @click="editorStore.setDPI(150)"
                            >
                              Средн.
                            </button>
                            <button
                              :class="[
                                'px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                                editorStore.currentState.resize.dpi === 300 
                                  ? 'bg-blue-600 text-white' 
                                  : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                              ]"
                              @click="editorStore.setDPI(300)"
                            >
                              Печать (300)
                            </button>
                          </div>
                        </div>
                        <p class="mt-2 text-xs text-neutral-500">
                          {{ dpiDescription }}
                        </p>
                      </div>

                      <!-- Presets -->
                      <div>
                        <label class="block text-sm font-medium text-neutral-300 mb-3">Быстрый выбор</label>
                        <div class="space-y-2 max-h-32 overflow-y-auto">
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
                        <label class="block text-sm font-medium text-neutral-300 mb-3">Формат файла</label>
                        <div class="space-y-2">
                          <button
                            v-for="format in formats"
                            :key="format.value"
                            :class="[
                              'w-full flex items-center justify-between px-4 py-3 rounded-lg transition-colors',
                              editorStore.currentState.format === format.value
                                ? 'bg-blue-600 text-white'
                                : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                            ]"
                            @click="editorStore.setFormat(format.value)"
                          >
                            <div class="flex items-center gap-3">
                              <span class="text-lg">{{ format.icon }}</span>
                              <div class="text-left">
                                <div class="font-medium text-sm">{{ format.label }}</div>
                                <div class="text-xs opacity-70">{{ format.description }}</div>
                              </div>
                            </div>
                            <CheckIcon 
                              v-if="editorStore.currentState.format === format.value" 
                              class="w-5 h-5" 
                            />
                          </button>
                        </div>
                      </div>

                      <!-- Quality Slider -->
                      <div v-if="showQualitySlider">
                        <label class="block text-sm font-medium text-neutral-300 mb-3">
                          Качество: {{ editorStore.currentState.quality }}%
                        </label>
                        <input
                          :value="editorStore.currentState.quality"
                          type="range"
                          min="10"
                          max="100"
                          step="5"
                          class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                          @input="handleQualityChange"
                        />
                        <div class="flex justify-between text-xs text-neutral-500 mt-1">
                          <span>Маленький файл</span>
                          <span>Высокое качество</span>
                        </div>
                      </div>

                      <!-- File Size Estimation -->
                      <div class="p-4 bg-neutral-700/50 rounded-xl">
                        <div class="flex items-center justify-between mb-2">
                          <span class="text-sm text-neutral-400">Примерный размер:</span>
                          <span class="text-lg font-semibold text-blue-400">
                            {{ editorStore.estimatedFileSizeFormatted }}
                          </span>
                        </div>
                        <div class="flex items-center gap-2 text-xs text-neutral-500">
                          <span>Оригинал: {{ formatFileSize(editorStore.originalFileSize) }}</span>
                          <span>→</span>
                          <span :class="fileSizeChangeClass">
                            {{ fileSizeChangePercent }}
                          </span>
                        </div>
                      </div>
                    </div>

                    <!-- Watermark Tool -->
                    <div v-if="activeToolId === 'watermark'" class="space-y-6">
                      <!-- Enable Toggle -->
                      <label class="flex items-center justify-between p-3 bg-neutral-700 rounded-lg cursor-pointer">
                        <span class="text-sm font-medium text-neutral-300">Включить водяной знак</span>
                        <button
                          :class="[
                            'relative w-11 h-6 rounded-full transition-colors',
                            editorStore.currentState.watermark.enabled ? 'bg-blue-600' : 'bg-neutral-600'
                          ]"
                          @click="editorStore.enableWatermark(!editorStore.currentState.watermark.enabled)"
                        >
                          <span
                            :class="[
                              'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform',
                              editorStore.currentState.watermark.enabled ? 'translate-x-5' : 'translate-x-0'
                            ]"
                          />
                        </button>
                      </label>

                      <template v-if="editorStore.currentState.watermark.enabled">
                        <!-- Type Selection -->
                        <div>
                          <label class="block text-sm font-medium text-neutral-300 mb-3">Тип</label>
                          <div class="grid grid-cols-2 gap-2">
                            <button
                              :class="[
                                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                                editorStore.currentState.watermark.type === 'text'
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                              ]"
                              @click="editorStore.setWatermark({ type: 'text' })"
                            >
                              📝 Текст
                            </button>
                            <button
                              :class="[
                                'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                                editorStore.currentState.watermark.type === 'image'
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-neutral-700 text-neutral-300 hover:bg-neutral-600'
                              ]"
                              @click="editorStore.setWatermark({ type: 'image' })"
                            >
                              🖼️ Изображение
                            </button>
                          </div>
                        </div>

                        <!-- Text Input -->
                        <div v-if="editorStore.currentState.watermark.type === 'text'">
                          <label class="block text-sm font-medium text-neutral-300 mb-2">Текст</label>
                          <input
                            :value="editorStore.currentState.watermark.text"
                            type="text"
                            placeholder="© Copyright 2025"
                            class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                   text-white text-sm focus:ring-2 focus:ring-blue-500"
                            @input="updateWatermarkText"
                          />
                          
                          <div class="grid grid-cols-2 gap-3 mt-3">
                            <div>
                              <label class="block text-xs text-neutral-400 mb-1">Размер</label>
                              <input
                                :value="editorStore.currentState.watermark.fontSize"
                                type="number"
                                min="8"
                                max="120"
                                class="w-full px-3 py-2 bg-neutral-700 border border-neutral-600 rounded-lg
                                       text-white text-sm"
                                @input="updateWatermarkFontSize"
                              />
                            </div>
                            <div>
                              <label class="block text-xs text-neutral-400 mb-1">Цвет</label>
                              <input
                                :value="editorStore.currentState.watermark.color"
                                type="color"
                                class="w-full h-10 rounded-lg cursor-pointer bg-neutral-700 border border-neutral-600"
                                @input="updateWatermarkColor"
                              />
                            </div>
                          </div>
                        </div>

                        <!-- Image Upload -->
                        <div v-else>
                          <label class="block text-sm font-medium text-neutral-300 mb-2">Изображение логотипа</label>
                          <div 
                            class="border-2 border-dashed border-neutral-600 rounded-lg p-4 text-center
                                   hover:border-neutral-500 transition-colors cursor-pointer"
                            @click="triggerWatermarkUpload"
                            @drop.prevent="handleWatermarkDrop"
                            @dragover.prevent
                          >
                            <input
                              ref="watermarkInput"
                              type="file"
                              accept="image/png,image/svg+xml"
                              class="hidden"
                              @change="handleWatermarkUpload"
                            />
                            <template v-if="watermarkImagePreview">
                              <img 
                                :src="watermarkImagePreview" 
                                alt="Watermark preview"
                                class="max-h-16 mx-auto mb-2"
                              />
                              <p class="text-xs text-neutral-400">Кликните для замены</p>
                            </template>
                            <template v-else>
                              <PhotoIcon class="w-8 h-8 mx-auto text-neutral-500 mb-2" />
                              <p class="text-sm text-neutral-400">PNG или SVG</p>
                            </template>
                          </div>
                        </div>

                        <!-- Position Grid -->
                        <div>
                          <label class="block text-sm font-medium text-neutral-300 mb-2">Позиция</label>
                          <div class="grid grid-cols-3 gap-1 p-2 bg-neutral-700 rounded-lg">
                            <button
                              v-for="pos in watermarkPositions"
                              :key="pos.value"
                              :class="[
                                'p-2 rounded text-xs transition-colors',
                                editorStore.currentState.watermark.position === pos.value
                                  ? 'bg-blue-600 text-white'
                                  : 'bg-neutral-600 text-neutral-400 hover:bg-neutral-500'
                              ]"
                              @click="editorStore.setWatermark({ position: pos.value })"
                            >
                              {{ pos.icon }}
                            </button>
                          </div>
                        </div>

                        <!-- Opacity Slider -->
                        <div>
                          <label class="block text-sm font-medium text-neutral-300 mb-2">
                            Прозрачность: {{ editorStore.currentState.watermark.opacity }}%
                          </label>
                          <input
                            :value="editorStore.currentState.watermark.opacity"
                            type="range"
                            min="10"
                            max="100"
                            class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                            @input="updateWatermarkOpacity"
                          />
                        </div>

                        <button
                          class="w-full px-4 py-2 bg-neutral-700 text-neutral-300 rounded-lg 
                                 hover:bg-neutral-600 transition-colors text-sm"
                          @click="editorStore.resetWatermark()"
                        >
                          Удалить водяной знак
                        </button>
                      </template>
                    </div>

                    <!-- Adjust Tool -->
                    <div v-if="activeToolId === 'adjust'" class="space-y-6">
                      <div class="space-y-5">
                        <div>
                          <div class="flex justify-between text-xs text-neutral-400 mb-2">
                            <span>Яркость</span>
                            <span>{{ editorStore.currentState.filters.brightness }}</span>
                          </div>
                          <input
                            :value="editorStore.currentState.filters.brightness"
                            type="range"
                            min="-100"
                            max="100"
                            class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                            @input="updateFilter('brightness', $event)"
                          />
                        </div>

                        <div>
                          <div class="flex justify-between text-xs text-neutral-400 mb-2">
                            <span>Контраст</span>
                            <span>{{ editorStore.currentState.filters.contrast }}</span>
                          </div>
                          <input
                            :value="editorStore.currentState.filters.contrast"
                            type="range"
                            min="-100"
                            max="100"
                            class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                            @input="updateFilter('contrast', $event)"
                          />
                        </div>

                        <div>
                          <div class="flex justify-between text-xs text-neutral-400 mb-2">
                            <span>Насыщенность</span>
                            <span>{{ editorStore.currentState.filters.saturation }}</span>
                          </div>
                          <input
                            :value="editorStore.currentState.filters.saturation"
                            type="range"
                            min="-100"
                            max="100"
                            class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                            @input="updateFilter('saturation', $event)"
                          />
                        </div>

                        <div>
                          <div class="flex justify-between text-xs text-neutral-400 mb-2">
                            <span>Размытие</span>
                            <span>{{ editorStore.currentState.filters.blur }}px</span>
                          </div>
                          <input
                            :value="editorStore.currentState.filters.blur"
                            type="range"
                            min="0"
                            max="20"
                            class="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                            @input="updateFilter('blur', $event)"
                          />
                        </div>
                      </div>

                      <button
                        class="w-full px-4 py-2 bg-neutral-700 text-neutral-300 rounded-lg 
                               hover:bg-neutral-600 transition-colors text-sm"
                        @click="editorStore.resetFilters()"
                      >
                        Сбросить настройки
                      </button>
                    </div>
                  </div>

                  <!-- Save Actions -->
                  <div class="p-4 border-t border-neutral-700 space-y-2 shrink-0">
                    <button
                      class="w-full flex items-center justify-center gap-2 px-4 py-3 
                             bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                             transition-colors font-medium text-sm disabled:opacity-50"
                      :disabled="isProcessing"
                      @click="openSaveModal"
                    >
                      <DocumentDuplicateIcon class="w-5 h-5" />
                      Сохранить как версию
                    </button>
                    <div class="grid grid-cols-2 gap-2">
                      <button
                        class="flex items-center justify-center gap-2 px-4 py-2.5 
                               bg-neutral-700 text-white rounded-lg hover:bg-neutral-600 
                               transition-colors text-sm disabled:opacity-50"
                        :disabled="isProcessing"
                        @click="handleSaveAsCopy"
                      >
                        <FolderPlusIcon class="w-4 h-4" />
                        Копия
                      </button>
                      <button
                        class="flex items-center justify-center gap-2 px-4 py-2.5 
                               bg-neutral-700 text-white rounded-lg hover:bg-neutral-600 
                               transition-colors text-sm disabled:opacity-50"
                        :disabled="isProcessing"
                        @click="handleDownload"
                      >
                        <ArrowDownTrayIcon class="w-4 h-4" />
                        Скачать
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>

    <SaveVersionModal
      :is-open="isSaveModalOpen"
      :default-format="editorStore.currentState.format"
      :error-message="saveError"
      @close="isSaveModalOpen = false"
      @save="handleConfirmSave"
    />
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch, markRaw, onMounted, onUnmounted } from 'vue'
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
  FolderPlusIcon,
  ArrowDownTrayIcon,
  ArrowUturnLeftIcon,
  ArrowUturnRightIcon,
  ArrowPathIcon,
  ArrowsRightLeftIcon,
  ArrowsUpDownIcon,
  PhotoIcon
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notificationStore'
import { useEditorStore, type WatermarkPosition } from '@/stores/editorStore'
import { saveEditedImage } from '@/services/editorService'
import SaveVersionModal from '@/components/asset/SaveVersionModal.vue'
import type { Asset } from '@/types/api'

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
const editorStore = useEditorStore()

// Refs
const imageRef = ref<HTMLImageElement | null>(null)
const watermarkInput = ref<HTMLInputElement | null>(null)

// Local State
const activeToolId = ref<'crop' | 'resize' | 'format' | 'watermark' | 'adjust'>('crop')
const isProcessing = ref(false)
const processingMessage = ref('')
const cropPreview = ref(false)
const watermarkImagePreview = ref<string | null>(null)
const isSaveModalOpen = ref(false)
const saveError = ref<string | null>(null)

// Tool definitions
const tools = [
  { id: 'crop' as const, label: 'Обрезка', icon: markRaw(ScissorsIcon) },
  { id: 'resize' as const, label: 'Размер', icon: markRaw(ArrowsPointingOutIcon) },
  { id: 'format' as const, label: 'Формат', icon: markRaw(DocumentIcon) },
  { id: 'watermark' as const, label: 'Знак', icon: markRaw(PhotoIcon) },
  { id: 'adjust' as const, label: 'Корр.', icon: markRaw(AdjustmentsHorizontalIcon) }
]

const aspectRatios = [
  { value: '1:1' as const, label: '1:1' },
  { value: '4:3' as const, label: '4:3' },
  { value: '16:9' as const, label: '16:9' },
  { value: '9:16' as const, label: '9:16' },
  { value: '3:2' as const, label: '3:2' },
  { value: 'free' as const, label: 'Свободно' }
]

const formats = [
  { value: 'jpg' as const, label: 'JPEG', icon: '📷', description: 'Оптимально для фото' },
  { value: 'png' as const, label: 'PNG', icon: '🖼️', description: 'Прозрачность' },
  { value: 'webp' as const, label: 'WebP', icon: '🌐', description: 'Для веба' },
  { value: 'tiff' as const, label: 'TIFF', icon: '📄', description: 'Для печати' }
]

const sizePresets = [
  { label: 'Оригинал', width: 0, height: 0, useOriginal: true },
  { label: 'HD (1920×1080)', width: 1920, height: 1080 },
  { label: 'Full HD (1280×720)', width: 1280, height: 720 },
  { label: 'Соц. сети (1200×1200)', width: 1200, height: 1200 },
  { label: 'Превью (800×600)', width: 800, height: 600 }
]

const watermarkPositions: { value: WatermarkPosition; icon: string }[] = [
  { value: 'top-left', icon: '↖' },
  { value: 'top-center', icon: '↑' },
  { value: 'top-right', icon: '↗' },
  { value: 'middle-left', icon: '←' },
  { value: 'middle-center', icon: '⬤' },
  { value: 'middle-right', icon: '→' },
  { value: 'bottom-left', icon: '↙' },
  { value: 'bottom-center', icon: '↓' },
  { value: 'bottom-right', icon: '↘' }
]

// Computed
const hasTransformChanges = computed(() => {
  const t = editorStore.currentState.transform
  return t.rotation !== 0 || t.flipHorizontal || t.flipVertical
})

const showQualitySlider = computed(() => {
  return ['jpg', 'webp'].includes(editorStore.currentState.format)
})

const dpiDescription = computed(() => {
  const dpi = editorStore.currentState.resize.dpi
  if (dpi <= 72) return '72 DPI — стандарт для экрана и веб-использования'
  if (dpi <= 150) return '150 DPI — подходит для домашней печати'
  if (dpi <= 300) return '300 DPI — профессиональная печать'
  return 'Высокое разрешение для крупноформатной печати'
})

const imagePreviewStyle = computed(() => {
  return {
    transform: editorStore.previewTransform,
    filter: editorStore.previewFilter
  }
})

const cropOverlayStyle = computed(() => {
  if (!imageRef.value) return {}
  
  const { x, y, width, height } = editorStore.currentState.crop
  const { width: origW, height: origH } = editorStore.originalDimensions
  const scaleX = (imageRef.value.clientWidth || 1) / origW
  const scaleY = (imageRef.value.clientHeight || 1) / origH
  
  return {
    left: `${x * scaleX}px`,
    top: `${y * scaleY}px`,
    width: `${width * scaleX}px`,
    height: `${height * scaleY}px`
  }
})

const watermarkPreviewStyle = computed(() => {
  const { position, offsetX, offsetY } = editorStore.currentState.watermark
  const style: Record<string, string> = {}
  
  const posMap: Record<WatermarkPosition, { top?: string; bottom?: string; left?: string; right?: string; transform?: string }> = {
    'top-left': { top: `${offsetY}px`, left: `${offsetX}px` },
    'top-center': { top: `${offsetY}px`, left: '50%', transform: 'translateX(-50%)' },
    'top-right': { top: `${offsetY}px`, right: `${offsetX}px` },
    'middle-left': { top: '50%', left: `${offsetX}px`, transform: 'translateY(-50%)' },
    'middle-center': { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },
    'middle-right': { top: '50%', right: `${offsetX}px`, transform: 'translateY(-50%)' },
    'bottom-left': { bottom: `${offsetY}px`, left: `${offsetX}px` },
    'bottom-center': { bottom: `${offsetY}px`, left: '50%', transform: 'translateX(-50%)' },
    'bottom-right': { bottom: `${offsetY}px`, right: `${offsetX}px` }
  }
  
  return posMap[position] || {}
})

const watermarkTextStyle = computed(() => {
  const { fontSize, color, opacity } = editorStore.currentState.watermark
  return {
    fontSize: `${fontSize}px`,
    color: color,
    opacity: opacity / 100,
    textShadow: '1px 1px 2px rgba(0,0,0,0.5)'
  }
})

const fileSizeChangeClass = computed(() => {
  const original = editorStore.originalFileSize
  const estimated = editorStore.estimatedFileSize
  if (!original) return 'text-neutral-400'
  
  const change = ((estimated - original) / original) * 100
  if (change > 20) return 'text-red-400'
  if (change < -20) return 'text-green-400'
  return 'text-neutral-400'
})

const fileSizeChangePercent = computed(() => {
  const original = editorStore.originalFileSize
  const estimated = editorStore.estimatedFileSize
  if (!original) return ''
  
  const change = ((estimated - original) / original) * 100
  const sign = change > 0 ? '+' : ''
  return `${sign}${change.toFixed(0)}%`
})

// Methods
function formatFileSize(bytes: number): string {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function handleClose() {
  if (!isProcessing.value) {
    emit('close')
  }
}

function handleImageLoad() {
  if (imageRef.value && props.asset) {
    const width = imageRef.value.naturalWidth || 1920
    const height = imageRef.value.naturalHeight || 1080
    
    editorStore.initialize(
      { id: props.asset.id, label: props.asset.label, size: props.asset.size || 0 },
      width,
      height
    )
  }
}

// Keyboard shortcuts
function handleKeyDown(e: KeyboardEvent) {
  if (!props.isOpen) return
  
  if (e.ctrlKey || e.metaKey) {
    if (e.key === 'z' && !e.shiftKey) {
      e.preventDefault()
      handleUndo()
    } else if (e.key === 'z' && e.shiftKey || e.key === 'y') {
      e.preventDefault()
      handleRedo()
    }
  }
}

function handleUndo() {
  if (editorStore.undo()) {
    notificationStore.addNotification({
      type: 'info',
      title: 'Отменено',
      message: editorStore.currentHistoryLabel
    })
  }
}

function handleRedo() {
  if (editorStore.redo()) {
    notificationStore.addNotification({
      type: 'info',
      title: 'Повторено',
      message: editorStore.currentHistoryLabel
    })
  }
}

// Crop methods
function setAspectRatio(ratio: typeof aspectRatios[0]['value']) {
  editorStore.setCrop({ aspectRatio: ratio })
  cropPreview.value = true
  
  if (ratio === 'free') return
  
  const { width } = editorStore.originalDimensions
  const ratioMap: Record<string, number> = {
    '1:1': 1,
    '4:3': 3 / 4,
    '16:9': 9 / 16,
    '9:16': 16 / 9,
    '3:2': 2 / 3,
    '2:3': 3 / 2
  }
  
  const newHeight = Math.round(width * (ratioMap[ratio] || 1))
  editorStore.setCrop({ width, height: newHeight })
}

function updateCropWidth(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 0
  editorStore.setCrop({ width: value })
}

function updateCropHeight(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 0
  editorStore.setCrop({ height: value })
}

function applyCrop() {
  editorStore.applyCrop()
  notificationStore.addNotification({
    type: 'success',
    title: 'Обрезка применена',
    message: `${editorStore.currentState.crop.width}×${editorStore.currentState.crop.height}`
  })
  cropPreview.value = false
}

// Resize methods
function handleWidthChange(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 0
  const maintain = editorStore.currentState.resize.maintainAspect
  
  if (maintain && editorStore.originalDimensions.width) {
    const ratio = editorStore.originalDimensions.height / editorStore.originalDimensions.width
    editorStore.setResize({ width: value, height: Math.round(value * ratio) })
  } else {
    editorStore.setResize({ width: value })
  }
}

function handleHeightChange(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 0
  const maintain = editorStore.currentState.resize.maintainAspect
  
  if (maintain && editorStore.originalDimensions.height) {
    const ratio = editorStore.originalDimensions.width / editorStore.originalDimensions.height
    editorStore.setResize({ height: value, width: Math.round(value * ratio) })
  } else {
    editorStore.setResize({ height: value })
  }
}

function toggleMaintainAspect() {
  editorStore.setResize({ maintainAspect: !editorStore.currentState.resize.maintainAspect })
}

function handleDPIChange(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 72
  editorStore.setDPI(value)
}

function applySizePreset(preset: typeof sizePresets[0]) {
  if (preset.useOriginal) {
    editorStore.setResize({
      width: editorStore.originalDimensions.width,
      height: editorStore.originalDimensions.height
    })
  } else {
    editorStore.setResize({ width: preset.width, height: preset.height })
  }
  editorStore.applyResize()
}

// Format methods
function handleQualityChange(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 85
  editorStore.setQuality(value)
}

// Filter methods
function updateFilter(filter: 'brightness' | 'contrast' | 'saturation' | 'blur', e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 0
  editorStore.setFilters({ [filter]: value })
}

// Watermark methods
function triggerWatermarkUpload() {
  watermarkInput.value?.click()
}

function handleWatermarkUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = () => {
      watermarkImagePreview.value = reader.result as string
      editorStore.setWatermarkImage(file, reader.result as string)
    }
    reader.readAsDataURL(file)
  }
}

function handleWatermarkDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = () => {
      watermarkImagePreview.value = reader.result as string
      editorStore.setWatermarkImage(file, reader.result as string)
    }
    reader.readAsDataURL(file)
  }
}

function updateWatermarkText(e: Event) {
  const value = (e.target as HTMLInputElement).value
  editorStore.setWatermarkText(value)
}

function updateWatermarkFontSize(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 24
  editorStore.setWatermark({ fontSize: value })
}

function updateWatermarkColor(e: Event) {
  const value = (e.target as HTMLInputElement).value
  editorStore.setWatermark({ color: value })
}

function updateWatermarkOpacity(e: Event) {
  const value = parseInt((e.target as HTMLInputElement).value) || 50
  editorStore.setWatermark({ opacity: value })
}

function openSaveModal() {
  saveError.value = null
  isSaveModalOpen.value = true
}

function mapFormatToMime(format: string): string {
  const fmt = format.toLowerCase()
  if (fmt === 'jpg' || fmt === 'jpeg') return 'image/jpeg'
  if (fmt === 'png') return 'image/png'
  if (fmt === 'webp') return 'image/webp'
  return 'image/jpeg'
}

async function buildBlobFromImage(format: string): Promise<Blob> {
  if (!imageRef.value) {
    throw new Error('Изображение не загружено')
  }

  const canvas = document.createElement('canvas')
  const { width, height } = editorStore.currentState.resize
  canvas.width = width || imageRef.value.naturalWidth
  canvas.height = height || imageRef.value.naturalHeight

  const ctx = canvas.getContext('2d')
  if (!ctx) {
    throw new Error('Canvas не поддерживается')
  }

  ctx.drawImage(imageRef.value, 0, 0, canvas.width, canvas.height)

  const mime = format === 'original' ? mapFormatToMime(editorStore.currentState.format) : mapFormatToMime(format)

  return new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) return reject(new Error('Не удалось сформировать файл'))
      resolve(blob)
    }, mime, editorStore.currentState.quality / 100)
  })
}

async function handleConfirmSave(format: string, comment: string) {
  if (!props.asset) return
  isProcessing.value = true
  processingMessage.value = 'Создание новой версии...'
  saveError.value = null

  try {
    const blob = await buildBlobFromImage(format)
    const result = await saveEditedImage(
      props.asset.id,
      blob,
      {
        format: format === 'original' ? undefined : format,
        comment: comment || 'Edited via Web Editor'
      }
    )

    notificationStore.addNotification({
      type: 'success',
      title: 'Версия создана',
      message: `Версия #${result.version_id ?? ''} сохранена`
    })

    emit('saveVersion', props.asset.id, result.version_id || Date.now())
    isSaveModalOpen.value = false
    emit('close')
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.message || 'Не удалось сохранить изменения'
    saveError.value = message
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message
    })
  } finally {
    isProcessing.value = false
    processingMessage.value = ''
  }
}

async function handleSaveAsCopy() {
  if (!props.asset) return
  
  isProcessing.value = true
  processingMessage.value = 'Создание копии...'
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const newAssetId = Date.now()
    notificationStore.addNotification({
      type: 'success',
      title: 'Копия создана',
      message: `Новый актив #${newAssetId} добавлен`
    })
    emit('saveCopy', props.asset.id, newAssetId)
    emit('close')
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

async function handleDownload() {
  isProcessing.value = true
  processingMessage.value = 'Подготовка к скачиванию...'
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Скачивание началось',
      message: `${props.asset?.label}.${editorStore.currentState.format}`
    })
  } finally {
    isProcessing.value = false
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

// Watch for asset changes
watch(() => props.asset, (newAsset) => {
  if (newAsset) {
    activeToolId.value = 'crop'
    cropPreview.value = false
    watermarkImagePreview.value = null
  }
})
</script>

<style scoped>
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

input[type="color"] {
  -webkit-appearance: none;
  border: none;
  padding: 0;
}

input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
}

input[type="color"]::-webkit-color-swatch {
  border: none;
  border-radius: 0.5rem;
}
</style>
