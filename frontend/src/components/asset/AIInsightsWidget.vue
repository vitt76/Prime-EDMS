<template>
  <div class="ai-insights-widget bg-white rounded-xl border border-neutral-200 overflow-hidden">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-neutral-100 bg-gradient-to-r from-purple-50 to-blue-50">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-neutral-900 flex items-center gap-2">
          <SparklesIcon class="w-4 h-4 text-purple-500" />
          AI Анализ
        </h3>
        <span 
          v-if="props.analysis?.status === 'completed' && props.analysis.analyzedAt"
          class="text-xs text-neutral-500"
        >
          {{ formatRelativeTime(props.analysis.analyzedAt) }}
        </span>
      </div>
    </div>

    <!-- Run Analysis Button (always visible at top) -->
    <div class="p-4 border-b border-neutral-100">
      <button
        class="w-full flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium
               text-white bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg
               hover:from-purple-700 hover:to-blue-700 transition-all
               disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
        :disabled="isAnalyzing || isLoading"
        @click="handleRunAnalysis"
      >
        <SparklesIcon v-if="!isAnalyzing && !isLoading" class="w-5 h-5" />
        <ArrowPathIcon v-else class="w-5 h-5 animate-spin" />
        <span v-if="isAnalyzing || isLoading">Анализируем...</span>
        <span v-else-if="props.analysis && props.analysis.status === 'completed'">Сделать анализ повторно</span>
        <span v-else>Запустить AI анализ</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="p-6 flex flex-col items-center justify-center gap-3">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="text-sm text-neutral-500">Загрузка данных анализа...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-6 flex flex-col items-center justify-center gap-3">
      <ExclamationCircleIcon class="w-8 h-8 text-red-500" />
      <p class="text-sm text-red-600">{{ error }}</p>
      <p class="text-xs text-neutral-500 mt-2">Попробуйте запустить анализ снова</p>
    </div>

    <!-- Content -->
    <div v-else-if="props.analysis" class="divide-y divide-neutral-100">
      <!-- Auto-Tagging Section -->
      <Disclosure v-slot="{ open }" default-open>
        <DisclosureButton
          class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <TagIcon class="w-4 h-4 text-blue-500" />
            <span class="text-sm font-medium text-neutral-900">Авто-теги</span>
            <span class="px-1.5 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-700">
              {{ pendingTags.length }}
            </span>
          </div>
          <ChevronDownIcon 
            :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']" 
          />
        </DisclosureButton>
        
        <DisclosurePanel class="px-4 pb-4">
          <div v-if="pendingTags.length === 0 && acceptedTags.length === 0" class="text-center py-4">
            <p class="text-sm text-neutral-500">Нет предложенных тегов</p>
            <button
              class="mt-2 text-sm text-purple-600 hover:text-purple-700"
              @click="regenerateTags"
              :disabled="isAnalyzing"
            >
              Сгенерировать теги
            </button>
          </div>

          <div v-else class="space-y-3">
            <!-- Pending Tags -->
            <div v-if="pendingTags.length > 0" class="space-y-2">
              <p class="text-xs font-medium text-neutral-500 uppercase">Предложения AI</p>
              <div class="flex flex-wrap gap-2">
                <div
                  v-for="tag in pendingTags"
                  :key="tag.id"
                  class="group flex items-center gap-1 px-2 py-1 rounded-lg border border-neutral-200 
                         bg-white hover:border-neutral-300 transition-colors"
                >
                  <span class="text-sm text-neutral-700">{{ tag.label }}</span>
                  <span 
                    class="text-[10px] px-1 py-0.5 rounded font-medium"
                    :class="getConfidenceClass(tag.confidence)"
                  >
                    {{ tag.confidence }}%
                  </span>
                  <div class="flex items-center gap-0.5 ml-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      class="p-0.5 rounded hover:bg-green-100 text-green-600"
                      title="Принять"
                      @click="acceptTag(tag.id)"
                    >
                      <CheckIcon class="w-3.5 h-3.5" />
                    </button>
                    <button
                      class="p-0.5 rounded hover:bg-red-100 text-red-600"
                      title="Отклонить"
                      @click="rejectTag(tag.id)"
                    >
                      <XMarkIcon class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Accepted Tags -->
            <div v-if="acceptedTags.length > 0" class="space-y-2">
              <p class="text-xs font-medium text-neutral-500 uppercase">Принятые</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tag in acceptedTags"
                  :key="tag.id"
                  class="px-2 py-1 text-sm rounded-lg bg-green-100 text-green-700 flex items-center gap-1"
                >
                  <CheckIcon class="w-3 h-3" />
                  {{ tag.label }}
                </span>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="flex items-center gap-2 pt-2">
              <button
                v-if="pendingTags.length > 0"
                class="text-xs text-green-600 hover:text-green-700"
                @click="acceptAllTags"
              >
                ✓ Принять все
              </button>
              <button
                v-if="pendingTags.length > 0"
                class="text-xs text-red-600 hover:text-red-700"
                @click="rejectAllTags"
              >
                ✗ Отклонить все
              </button>
            </div>
          </div>
        </DisclosurePanel>
      </Disclosure>

      <!-- SEO Description Section -->
      <Disclosure v-slot="{ open }">
        <DisclosureButton
          class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <DocumentTextIcon class="w-4 h-4 text-amber-500" />
            <span class="text-sm font-medium text-neutral-900">SEO Описание</span>
          </div>
          <ChevronDownIcon 
            :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']" 
          />
        </DisclosureButton>
        
        <DisclosurePanel class="px-4 pb-4">
          <div v-if="!props.analysis?.seo" class="text-center py-4">
            <p class="text-sm text-neutral-500">Описание не сгенерировано</p>
            <button
              class="mt-2 text-sm text-purple-600 hover:text-purple-700"
              :disabled="isRegeneratingSEO"
              @click="handleRegenerateSEO"
            >
              Сгенерировать описание
            </button>
          </div>

          <div v-else-if="props.analysis?.seo" class="space-y-4">
            <!-- Alt Text -->
            <div>
              <label class="block text-xs font-medium text-neutral-500 mb-1">Alt-текст</label>
              <div class="relative">
                <input
                  :value="props.analysis.seo.altText"
                  class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg
                         focus:ring-2 focus:ring-purple-500 focus:border-purple-500 pr-8"
                  readonly
                />
                <button
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-neutral-400 hover:text-neutral-600"
                  title="Копировать"
                  @click="copyToClipboard(props.analysis.seo.altText, 'Alt-текст')"
                >
                  <ClipboardDocumentIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Description -->
            <div>
              <label class="block text-xs font-medium text-neutral-500 mb-1">Описание</label>
              <div class="relative">
                <textarea
                  :value="props.analysis.seo.description"
                  rows="3"
                  class="w-full px-3 py-2 text-sm border border-neutral-200 rounded-lg
                         focus:ring-2 focus:ring-purple-500 focus:border-purple-500 resize-none pr-8"
                  readonly
                />
                <button
                  class="absolute right-2 top-2 p-1 text-neutral-400 hover:text-neutral-600"
                  title="Копировать"
                  @click="copyToClipboard(props.analysis.seo.description, 'Описание')"
                >
                  <ClipboardDocumentIcon class="w-4 h-4" />
                </button>
              </div>
            </div>

            <!-- Keywords -->
            <div>
              <label class="block text-xs font-medium text-neutral-500 mb-1">Ключевые слова</label>
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="keyword in props.analysis.seo.keywords"
                  :key="keyword"
                  class="px-2 py-0.5 text-xs rounded bg-amber-50 text-amber-700"
                >
                  {{ keyword }}
                </span>
              </div>
            </div>

            <!-- Regenerate Button -->
            <button
              class="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium
                     text-purple-600 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isRegeneratingSEO"
              @click="handleRegenerateSEO"
            >
              <ArrowPathIcon v-if="isRegeneratingSEO" class="w-4 h-4 animate-spin" />
              <ArrowPathIcon v-else class="w-4 h-4" />
              {{ isRegeneratingSEO ? 'Генерация...' : 'Пересгенерировать' }}
            </button>
          </div>
        </DisclosurePanel>
      </Disclosure>

      <!-- OCR Section -->
      <Disclosure v-slot="{ open }">
        <DisclosureButton
          class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <DocumentMagnifyingGlassIcon class="w-4 h-4 text-teal-500" />
            <span class="text-sm font-medium text-neutral-900">OCR (Распознавание текста)</span>
            <span 
              v-if="props.analysis?.ocr?.status === 'completed' && props.analysis.ocr.wordCount"
              class="px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-teal-100 text-teal-700"
            >
              {{ props.analysis.ocr.wordCount }} слов
            </span>
          </div>
          <ChevronDownIcon 
            :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']" 
          />
        </DisclosureButton>
        
        <DisclosurePanel class="px-4 pb-4">
          <!-- Not Run State -->
          <div v-if="!props.analysis?.ocr || props.analysis.ocr.status === 'not_run'" class="text-center py-4">
            <DocumentMagnifyingGlassIcon class="w-10 h-10 mx-auto text-neutral-300 mb-3" />
            <p class="text-sm text-neutral-500 mb-3">Текст ещё не распознан</p>
            <button
              class="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg
                     hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isLoading"
              @click="handleRunOCR"
            >
              Извлечь текст
            </button>
          </div>

          <!-- Processing State -->
          <div v-else-if="props.analysis.ocr.status === 'processing'" class="text-center py-6">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600 mx-auto mb-3"></div>
            <p class="text-sm text-neutral-500">Распознавание текста...</p>
            <p class="text-xs text-neutral-400 mt-1">Это может занять несколько секунд</p>
          </div>

          <!-- Completed State -->
          <div v-else-if="props.analysis.ocr.status === 'completed'" class="space-y-3">
            <!-- No Text Found -->
            <div v-if="!props.analysis.ocr.text || !props.analysis.ocr.text.trim() || (props.analysis.ocr.wordCount !== undefined && props.analysis.ocr.wordCount === 0)" class="text-center py-4">
              <DocumentMagnifyingGlassIcon class="w-10 h-10 mx-auto text-neutral-300 mb-3" />
              <p class="text-sm text-neutral-600 font-medium mb-1">Текст отсутствует</p>
              <p class="text-xs text-neutral-500">На изображении не обнаружен текст</p>
              <button
                class="mt-3 px-4 py-2 text-sm font-medium text-teal-600 bg-teal-50 rounded-lg
                       hover:bg-teal-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="isLoading"
                @click="handleRunOCR"
              >
                <ArrowPathIcon class="w-4 h-4 inline mr-1" />
                Попробовать снова
              </button>
            </div>

            <!-- Text Found -->
            <div v-else class="space-y-3">
              <!-- Stats -->
              <div class="flex items-center justify-between text-xs text-neutral-500">
                <span v-if="props.analysis.ocr.confidence">Точность: {{ props.analysis.ocr.confidence }}%</span>
                <span v-if="props.analysis.ocr.wordCount">{{ props.analysis.ocr.wordCount }} слов</span>
              </div>

              <!-- Text Result -->
              <div class="relative">
                <pre 
                  class="p-3 bg-neutral-50 rounded-lg text-xs text-neutral-700 
                         overflow-auto max-h-[200px] whitespace-pre-wrap font-mono"
                >{{ props.analysis.ocr.text }}</pre>
                <button
                  class="absolute top-2 right-2 p-1.5 bg-white rounded shadow-sm
                         text-neutral-500 hover:text-neutral-700 transition-colors"
                  title="Копировать текст"
                  @click="copyToClipboard(props.analysis.ocr.text!, 'Распознанный текст')"
                >
                  <ClipboardDocumentIcon class="w-4 h-4" />
                </button>
              </div>

              <!-- Actions -->
              <div class="flex items-center gap-2">
              <button
                class="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm
                       text-teal-600 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="isLoading"
                @click="handleRunOCR"
              >
                <ArrowPathIcon class="w-4 h-4" />
                Повторить
              </button>
                <button
                  class="flex-1 flex items-center justify-center gap-1 px-3 py-2 text-sm
                         text-neutral-600 bg-neutral-100 rounded-lg hover:bg-neutral-200 transition-colors"
                  @click="copyToClipboard(props.analysis.ocr.text!, 'Распознанный текст')"
                >
                  <ClipboardDocumentIcon class="w-4 h-4" />
                  Копировать
                </button>
              </div>
            </div>
          </div>

          <!-- Failed State -->
          <div v-else-if="props.analysis.ocr.status === 'failed'" class="text-center py-4">
            <ExclamationCircleIcon class="w-10 h-10 mx-auto text-red-300 mb-3" />
            <p class="text-sm text-neutral-500 mb-3">Не удалось распознать текст</p>
            <button
              class="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-lg
                     hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isLoading"
              @click="handleRunOCR"
            >
              Попробовать снова
            </button>
          </div>
        </DisclosurePanel>
      </Disclosure>

      <!-- Color Palette (if available) -->
      <Disclosure v-if="props.analysis?.colorPalette?.length" v-slot="{ open }">
        <DisclosureButton
          class="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-2">
            <SwatchIcon class="w-4 h-4 text-pink-500" />
            <span class="text-sm font-medium text-neutral-900">Цветовая палитра</span>
          </div>
          <ChevronDownIcon 
            :class="['w-4 h-4 text-neutral-500 transition-transform', open ? 'rotate-180' : '']" 
          />
        </DisclosureButton>
        
        <DisclosurePanel class="px-4 pb-4">
          <div class="space-y-2">
            <div
              v-for="color in props.analysis.colorPalette"
              :key="color.hex"
              class="flex items-center gap-3"
            >
              <div 
                class="w-8 h-8 rounded-lg shadow-inner border border-neutral-200"
                :style="{ backgroundColor: color.hex }"
              ></div>
              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-mono text-neutral-700">{{ color.hex }}</span>
                  <span class="text-xs text-neutral-500">{{ color.percentage }}%</span>
                </div>
                <div class="h-1.5 bg-neutral-100 rounded-full overflow-hidden mt-1">
                  <div 
                    class="h-full rounded-full"
                    :style="{ width: `${color.percentage}%`, backgroundColor: color.hex }"
                  ></div>
                </div>
              </div>
              <button
                class="p-1 text-neutral-400 hover:text-neutral-600"
                title="Копировать HEX"
                @click="copyToClipboard(color.hex, 'Цвет')"
              >
                <ClipboardDocumentIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </DisclosurePanel>
      </Disclosure>
    </div>

    <!-- Empty State (if no analysis data) -->
    <div v-else class="p-6 text-center">
      <SparklesIcon class="w-12 h-12 mx-auto text-neutral-300 mb-3" />
      <p class="text-sm text-neutral-500 mb-2">AI анализ ещё не выполнен</p>
      <p class="text-xs text-neutral-400">Нажмите кнопку выше, чтобы запустить анализ</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
  SparklesIcon,
  TagIcon,
  DocumentTextIcon,
  DocumentMagnifyingGlassIcon,
  SwatchIcon,
  ChevronDownIcon,
  CheckIcon,
  XMarkIcon,
  ArrowPathIcon,
  ClipboardDocumentIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notificationStore'
import type { AIAnalysis, AITag } from '@/mocks/ai'

interface Props {
  analysis: AIAnalysis | null
  isLoading?: boolean
  error?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  error: null
})

const emit = defineEmits<{
  runAnalysis: []
  runOcr: []
  regenerateSeo: []
  tagAccepted: [tagId: string]
  tagRejected: [tagId: string]
  analysisComplete: [analysis: AIAnalysis]
}>()

const notificationStore = useNotificationStore()

// State
const isAnalyzing = ref(false)
const isRegeneratingSEO = ref(false)

// Computed
const pendingTags = computed(() => 
  props.analysis?.tags?.filter(t => !t.accepted && !t.rejected) || []
)

const acceptedTags = computed(() => 
  props.analysis?.tags?.filter(t => t.accepted) || []
)

function getConfidenceClass(confidence: number): string {
  if (confidence >= 90) return 'bg-green-100 text-green-700'
  if (confidence >= 75) return 'bg-amber-100 text-amber-700'
  return 'bg-neutral-100 text-neutral-600'
}

function formatRelativeTime(dateString: string | null): string {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'только что'
  if (minutes < 60) return `${minutes} мин. назад`
  if (hours < 24) return `${hours} ч. назад`
  if (days < 7) return `${days} дн. назад`
  
  return date.toLocaleDateString('ru-RU')
}

function handleRunAnalysis() {
  isAnalyzing.value = true
  emit('runAnalysis')
  // Parent will handle the actual API call and reload
  setTimeout(() => {
    isAnalyzing.value = false
  }, 1000)
}

function handleRunOCR() {
  if (!props.analysis) return
  emit('runOcr')
  // Parent will handle the actual API call and reload
}

function handleRegenerateSEO() {
  if (!props.analysis) return
  isRegeneratingSEO.value = true
  emit('regenerateSeo')
  // Parent will handle the actual API call and reload
  setTimeout(() => {
    isRegeneratingSEO.value = false
  }, 1000)
}

function acceptTag(tagId: string) {
  emit('tagAccepted', tagId)
  // Parent will handle the actual API call and reload
}

function rejectTag(tagId: string) {
  emit('tagRejected', tagId)
  // Parent will handle the actual API call and reload
}

function acceptAllTags() {
  pendingTags.value.forEach(tag => acceptTag(tag.id))
  
  notificationStore.addNotification({
    type: 'success',
    title: 'Теги приняты',
    message: `${acceptedTags.value.length} тегов добавлено`
  })
}

function rejectAllTags() {
  pendingTags.value.forEach(tag => rejectTag(tag.id))
  
  notificationStore.addNotification({
    type: 'info',
    title: 'Теги отклонены',
    message: 'Все предложенные теги отклонены'
  })
}

function regenerateTags() {
  handleRunAnalysis()
}

async function copyToClipboard(text: string, label: string) {
  try {
    await navigator.clipboard.writeText(text)
    notificationStore.addNotification({
      type: 'success',
      title: 'Скопировано',
      message: `${label} скопирован в буфер обмена`
    })
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось скопировать текст'
    })
  }
}

// No lifecycle hooks needed - data comes from props
</script>

