<template>
  <div class="bg-white rounded-xl shadow-sm border border-neutral-200 overflow-hidden">
    <!-- Header -->
    <div class="px-5 py-4 border-b border-neutral-200 bg-gradient-to-r from-violet-50 to-indigo-50">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="p-2 bg-gradient-to-br from-violet-500 to-indigo-600 rounded-lg">
            <SparklesIcon class="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 class="font-semibold text-neutral-900">AI-Анализ</h3>
            <p class="text-xs text-neutral-500">
              {{ aiInsights.aiProvider === 'yandex' ? 'YandexGPT' : 
                 aiInsights.aiProvider === 'gigachat' ? 'GigaChat' : 'Смешанный' }}
            </p>
          </div>
        </div>
        <button
          @click="handleReanalyze"
          :disabled="isAnalyzing"
          class="p-2 text-violet-600 hover:bg-violet-100 rounded-lg transition-colors disabled:opacity-50"
          title="Повторный анализ"
        >
          <ArrowPathIcon :class="['w-5 h-5', isAnalyzing && 'animate-spin']" />
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="divide-y divide-neutral-100">
      <!-- Auto-Tagging Section -->
      <div class="p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <TagIcon class="w-4 h-4 text-violet-500" />
            <span class="text-sm font-medium text-neutral-700">Авто-теги</span>
          </div>
          <span 
            :class="[
              'px-2 py-0.5 text-xs font-medium rounded-full',
              aiInsights.analysisStatus.autoTagging === 'completed' 
                ? 'bg-green-100 text-green-700'
                : aiInsights.analysisStatus.autoTagging === 'processing'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-neutral-100 text-neutral-500'
            ]"
          >
            {{ getStatusLabel(aiInsights.analysisStatus.autoTagging) }}
          </span>
        </div>

        <div v-if="aiInsights.suggestedTags.length > 0" class="space-y-2">
          <TransitionGroup
            name="tag-list"
            tag="div"
            class="flex flex-wrap gap-2"
          >
            <div
              v-for="tag in visibleTags"
              :key="tag.id"
              :class="[
                'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-all duration-200',
                tag.accepted 
                  ? 'bg-green-100 text-green-800 ring-1 ring-green-300' 
                  : tag.rejected
                    ? 'bg-neutral-100 text-neutral-400 line-through opacity-60'
                    : 'bg-violet-50 text-violet-700 hover:bg-violet-100'
              ]"
            >
              <span>{{ tag.name }}</span>
              <span 
                class="text-[10px] px-1 rounded bg-white/50"
                :title="`Уверенность: ${tag.confidence}%`"
              >
                {{ tag.confidence }}%
              </span>
              
              <!-- Action buttons -->
              <div v-if="!tag.accepted && !tag.rejected" class="flex items-center gap-0.5 ml-1">
                <button
                  @click.stop="handleAcceptTag(tag.id)"
                  class="p-0.5 text-green-600 hover:bg-green-100 rounded transition-colors"
                  title="Принять"
                >
                  <CheckIcon class="w-3 h-3" />
                </button>
                <button
                  @click.stop="handleRejectTag(tag.id)"
                  class="p-0.5 text-red-500 hover:bg-red-100 rounded transition-colors"
                  title="Отклонить"
                >
                  <XMarkIcon class="w-3 h-3" />
                </button>
              </div>
            </div>
          </TransitionGroup>

          <button
            v-if="aiInsights.suggestedTags.length > 5"
            @click="showAllTags = !showAllTags"
            class="text-xs text-violet-600 hover:text-violet-700 font-medium mt-2"
          >
            {{ showAllTags ? 'Показать меньше' : `Ещё ${aiInsights.suggestedTags.length - 5} тегов` }}
          </button>
        </div>

        <p v-else class="text-sm text-neutral-500 italic">
          Нет предложенных тегов
        </p>
      </div>

      <!-- SEO Description Section -->
      <div class="p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <DocumentTextIcon class="w-4 h-4 text-indigo-500" />
            <span class="text-sm font-medium text-neutral-700">SEO-описание</span>
          </div>
          <button
            @click="handleRegenerateSEO"
            :disabled="isRegeneratingSEO"
            class="text-xs text-indigo-600 hover:text-indigo-700 font-medium disabled:opacity-50 flex items-center gap-1"
          >
            <ArrowPathIcon :class="['w-3 h-3', isRegeneratingSEO && 'animate-spin']" />
            Перегенерировать
          </button>
        </div>

        <div v-if="aiInsights.seoDescription" class="space-y-2">
          <div class="p-3 bg-neutral-50 rounded-lg">
            <p class="text-sm text-neutral-700 leading-relaxed">
              {{ aiInsights.seoDescription.text }}
            </p>
          </div>
          <div class="flex items-center justify-between text-xs text-neutral-500">
            <span>
              v{{ aiInsights.seoDescription.version }} • 
              {{ aiInsights.seoDescription.provider === 'yandex' ? 'YandexGPT' : 'GigaChat' }}
            </span>
            <div class="flex items-center gap-2">
              <button
                @click="handleCopySEO"
                class="flex items-center gap-1 text-neutral-500 hover:text-neutral-700 transition-colors"
                title="Скопировать"
              >
                <ClipboardDocumentIcon class="w-3.5 h-3.5" />
                Копировать
              </button>
            </div>
          </div>
        </div>

        <div 
          v-else 
          class="flex items-center justify-center p-4 bg-neutral-50 rounded-lg"
        >
          <button
            @click="handleRegenerateSEO"
            :disabled="isRegeneratingSEO"
            class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 
                   rounded-lg hover:bg-indigo-100 transition-colors disabled:opacity-50"
          >
            <SparklesIcon class="w-4 h-4" />
            Сгенерировать описание
          </button>
        </div>
      </div>

      <!-- OCR Section -->
      <div class="p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <LanguageIcon class="w-4 h-4 text-cyan-500" />
            <span class="text-sm font-medium text-neutral-700">Распознавание текста (OCR)</span>
          </div>
          <span 
            :class="[
              'px-2 py-0.5 text-xs font-medium rounded-full',
              aiInsights.analysisStatus.ocr === 'completed' 
                ? 'bg-green-100 text-green-700'
                : aiInsights.analysisStatus.ocr === 'processing'
                  ? 'bg-yellow-100 text-yellow-700'
                  : 'bg-neutral-100 text-neutral-500'
            ]"
          >
            {{ getStatusLabel(aiInsights.analysisStatus.ocr) }}
          </span>
        </div>

        <!-- OCR Result -->
        <div v-if="aiInsights.ocrResult" class="space-y-2">
          <Disclosure v-slot="{ open }">
            <DisclosureButton
              class="flex items-center justify-between w-full p-3 text-left bg-neutral-50 
                     rounded-lg hover:bg-neutral-100 transition-colors"
            >
              <div class="flex items-center gap-2">
                <DocumentMagnifyingGlassIcon class="w-4 h-4 text-neutral-500" />
                <span class="text-sm text-neutral-700">
                  Распознанный текст 
                  <span class="text-neutral-400">({{ aiInsights.ocrResult.confidence }}% уверенность)</span>
                </span>
              </div>
              <ChevronDownIcon 
                :class="['w-4 h-4 text-neutral-500 transition-transform duration-200', open && 'rotate-180']" 
              />
            </DisclosureButton>

            <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-1"
            >
              <DisclosurePanel class="mt-2">
                <div class="p-3 bg-white border border-neutral-200 rounded-lg max-h-48 overflow-y-auto">
                  <pre class="text-xs text-neutral-700 whitespace-pre-wrap font-mono leading-relaxed">{{ aiInsights.ocrResult.text }}</pre>
                </div>
                <div class="flex items-center justify-end gap-2 mt-2">
                  <button
                    @click="handleCopyOCR"
                    class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-cyan-600 
                           bg-cyan-50 rounded-lg hover:bg-cyan-100 transition-colors"
                  >
                    <ClipboardDocumentIcon class="w-3.5 h-3.5" />
                    Копировать текст
                  </button>
                </div>
              </DisclosurePanel>
            </Transition>
          </Disclosure>
        </div>

        <!-- OCR Not Available or Processing -->
        <div v-else class="flex flex-col items-center justify-center p-4 bg-neutral-50 rounded-lg gap-2">
          <div v-if="aiInsights.analysisStatus.ocr === 'processing'" class="flex items-center gap-2 text-yellow-600">
            <ArrowPathIcon class="w-4 h-4 animate-spin" />
            <span class="text-sm">Распознавание текста...</span>
          </div>
          <template v-else>
            <p class="text-sm text-neutral-500 text-center">
              Текст не распознан или файл не содержит текста
            </p>
            <button
              @click="handleExtractOCR"
              :disabled="isExtractingOCR"
              class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-cyan-600 
                     bg-cyan-50 rounded-lg hover:bg-cyan-100 transition-colors disabled:opacity-50"
            >
              <LanguageIcon class="w-4 h-4" />
              Извлечь текст
            </button>
          </template>
        </div>
      </div>

      <!-- Analysis Timestamp -->
      <div class="px-5 py-3 bg-neutral-50">
        <p class="text-xs text-neutral-500 text-center">
          <template v-if="aiInsights.lastAnalyzedAt">
            Последний анализ: {{ formatRelativeDate(aiInsights.lastAnalyzedAt) }}
          </template>
          <template v-else>
            Анализ не проводился
          </template>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import {
  SparklesIcon,
  ArrowPathIcon,
  TagIcon,
  DocumentTextIcon,
  LanguageIcon,
  CheckIcon,
  XMarkIcon,
  ClipboardDocumentIcon,
  ChevronDownIcon,
  DocumentMagnifyingGlassIcon,
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notificationStore'
import {
  getAIInsightsForAsset,
  acceptSuggestedTag,
  rejectSuggestedTag,
  regenerateSEODescription,
  extractOCR,
  runFullAIAnalysis,
  type AIInsights,
} from '@/mocks/ai'

const props = defineProps<{
  assetId: number
  assetType?: string
}>()

const emit = defineEmits<{
  (e: 'tagsUpdated', tags: string[]): void
  (e: 'seoUpdated', text: string): void
}>()

const notificationStore = useNotificationStore()

// State
const aiInsights = ref<AIInsights>(getAIInsightsForAsset(props.assetId, props.assetType || 'image'))
const isAnalyzing = ref(false)
const isRegeneratingSEO = ref(false)
const isExtractingOCR = ref(false)
const showAllTags = ref(false)

// Computed
const visibleTags = computed(() => {
  if (showAllTags.value) {
    return aiInsights.value.suggestedTags
  }
  return aiInsights.value.suggestedTags.slice(0, 5)
})

const acceptedTagNames = computed(() => 
  aiInsights.value.suggestedTags
    .filter(t => t.accepted)
    .map(t => t.name)
)

// Methods
function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    idle: 'Не проведён',
    processing: 'Обработка...',
    completed: 'Готово',
    error: 'Ошибка',
  }
  return labels[status] || status
}

function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'только что'
  if (diffMins < 60) return `${diffMins} мин. назад`
  if (diffHours < 24) return `${diffHours} ч. назад`
  if (diffDays < 7) return `${diffDays} дн. назад`
  
  return date.toLocaleDateString('ru-RU')
}

async function handleReanalyze() {
  isAnalyzing.value = true
  try {
    const newInsights = await runFullAIAnalysis(props.assetId, props.assetType || 'image')
    aiInsights.value = newInsights
    notificationStore.addNotification({
      type: 'success',
      title: 'AI-анализ завершён',
      message: `Найдено ${newInsights.suggestedTags.length} тегов`,
    })
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка анализа',
      message: 'Не удалось провести AI-анализ',
    })
  } finally {
    isAnalyzing.value = false
  }
}

function handleAcceptTag(tagId: number) {
  const tag = acceptSuggestedTag(props.assetId, tagId)
  if (tag) {
    // Refresh local state
    aiInsights.value = { ...getAIInsightsForAsset(props.assetId, props.assetType || 'image') }
    emit('tagsUpdated', acceptedTagNames.value)
    notificationStore.addNotification({
      type: 'success',
      title: 'Тег принят',
      message: `Тег "${tag.name}" добавлен к активу`,
    })
  }
}

function handleRejectTag(tagId: number) {
  const tag = rejectSuggestedTag(props.assetId, tagId)
  if (tag) {
    // Refresh local state
    aiInsights.value = { ...getAIInsightsForAsset(props.assetId, props.assetType || 'image') }
    notificationStore.addNotification({
      type: 'info',
      title: 'Тег отклонён',
      message: `Тег "${tag.name}" не будет использован`,
    })
  }
}

async function handleRegenerateSEO() {
  isRegeneratingSEO.value = true
  try {
    const newSEO = await regenerateSEODescription(props.assetId, props.assetType || 'image')
    aiInsights.value = { ...getAIInsightsForAsset(props.assetId, props.assetType || 'image') }
    emit('seoUpdated', newSEO.text)
    notificationStore.addNotification({
      type: 'success',
      title: 'SEO-описание обновлено',
      message: `Версия ${newSEO.version} сгенерирована`,
    })
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка генерации',
      message: 'Не удалось сгенерировать SEO-описание',
    })
  } finally {
    isRegeneratingSEO.value = false
  }
}

async function handleExtractOCR() {
  isExtractingOCR.value = true
  aiInsights.value.analysisStatus.ocr = 'processing'
  
  try {
    await extractOCR(props.assetId)
    aiInsights.value = { ...getAIInsightsForAsset(props.assetId, props.assetType || 'image') }
    notificationStore.addNotification({
      type: 'success',
      title: 'Текст распознан',
      message: 'OCR-анализ успешно завершён',
    })
  } catch (error) {
    aiInsights.value.analysisStatus.ocr = 'error'
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка OCR',
      message: 'Не удалось распознать текст',
    })
  } finally {
    isExtractingOCR.value = false
  }
}

async function handleCopySEO() {
  if (!aiInsights.value.seoDescription) return
  
  try {
    await navigator.clipboard.writeText(aiInsights.value.seoDescription.text)
    notificationStore.addNotification({
      type: 'success',
      title: 'Скопировано',
      message: 'SEO-описание скопировано в буфер обмена',
    })
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось скопировать текст',
    })
  }
}

async function handleCopyOCR() {
  if (!aiInsights.value.ocrResult) return
  
  try {
    await navigator.clipboard.writeText(aiInsights.value.ocrResult.text)
    notificationStore.addNotification({
      type: 'success',
      title: 'Скопировано',
      message: 'Распознанный текст скопирован в буфер обмена',
    })
  } catch {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Не удалось скопировать текст',
    })
  }
}

// Initialize
onMounted(() => {
  aiInsights.value = getAIInsightsForAsset(props.assetId, props.assetType || 'image')
})
</script>

<style scoped>
.tag-list-enter-active,
.tag-list-leave-active {
  transition: all 0.3s ease;
}

.tag-list-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}

.tag-list-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>

