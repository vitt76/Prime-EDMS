<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-[1050]"
        aria-hidden="true"
        @click="handleOverlayClick"
      />
    </Transition>
    <Transition
      enter-active-class="transition ease-out duration-250"
      enter-from-class="translate-x-full"
      enter-to-class="translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="translate-x-0"
      leave-to-class="translate-x-full"
    >
      <aside
        v-if="open && asset"
        ref="panelRef"
        class="fixed top-0 right-0 bottom-0 w-[400px] max-w-[90vw] z-[1060]
               bg-white dark:bg-neutral-900 border-l border-neutral-200 dark:border-neutral-700
               shadow-2xl overflow-y-auto flex flex-col"
        role="dialog"
        aria-label="Метаданные"
        @click.stop
      >
        <div class="flex items-center justify-between px-4 py-3 border-b border-neutral-200 dark:border-neutral-700 shrink-0">
          <h2 class="text-lg font-semibold text-neutral-900 dark:text-white truncate pr-2">
            Метаданные{{ asset?.label ? ` — ${asset.label.slice(0, 30)}${asset.label.length > 30 ? '…' : ''}` : '' }}
          </h2>
          <button
            type="button"
            class="p-2 rounded-lg text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
            @click="emit('close')"
            aria-label="Закрыть"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-4 space-y-4 flex-1 overflow-y-auto">
          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">Название</label>
            <input
              v-model="localLabel"
              type="text"
              class="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Название актива"
            />
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300">Описание</label>
              <button
                type="button"
                class="flex items-center gap-1.5 px-2 py-1 rounded-lg text-sm font-medium
                       bg-primary-500/15 text-primary-600 dark:text-primary-400 hover:bg-primary-500/25
                       disabled:opacity-50 disabled:pointer-events-none transition-colors"
                :disabled="isMagicLoading"
                @click="runMagic"
                title="Сгенерировать описание с помощью AI"
                aria-label="Сгенерировать описание с помощью AI"
              >
                <svg v-if="isMagicLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                {{ isMagicLoading ? 'Ожидание…' : 'Magic' }}
              </button>
            </div>
            <textarea
              v-model="localDescription"
              rows="4"
              class="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-y"
              placeholder="Описание"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">Теги</label>
            <div class="flex flex-wrap gap-2 mb-2">
              <span
                v-for="(tag, i) in localTags"
                :key="i"
                class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-neutral-200 dark:bg-neutral-700 text-neutral-800 dark:text-neutral-200 text-sm"
              >
                {{ tag }}
                <button
                  type="button"
                  class="p-0.5 rounded hover:bg-neutral-300 dark:hover:bg-neutral-600"
                  @click="removeTag(i)"
                  aria-label="Удалить тег"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </span>
            </div>
            <input
              v-model="tagInput"
              type="text"
              class="w-full px-3 py-2 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Добавить тег (сохранение тегов — в следующей версии)"
              @keydown.enter.prevent="addTagFromInput"
            />
            <p class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
              Сохранение тегов через API планируется в следующей итерации.
            </p>
          </div>
        </div>

        <div class="p-4 border-t border-neutral-200 dark:border-neutral-700 flex gap-2 shrink-0">
          <button
            type="button"
            class="flex-1 px-4 py-2.5 rounded-xl bg-neutral-200 dark:bg-neutral-700 text-neutral-800 dark:text-neutral-200 font-medium hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors"
            @click="emit('close')"
          >
            Отмена
          </button>
          <button
            type="button"
            class="flex-1 px-4 py-2.5 rounded-xl bg-primary-600 text-white font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors"
            :disabled="isSaving"
            @click="save"
          >
            {{ isSaving ? 'Сохранение…' : 'Сохранить' }}
          </button>
        </div>
      </aside>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useFocusTrap } from '@/composables/useFocusTrap'
import { aiAnalysisService } from '@/services/aiAnalysisService'
import { assetService } from '@/services/assetService'
import { useAssetStore } from '@/stores/assetStore'
import type { Asset } from '@/types/api'

const props = defineProps<{
  open: boolean
  asset: Asset | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
  error: [message: string]
}>()

const assetStore = useAssetStore()

const panelRef = ref<HTMLElement | null>(null)
const isFocusTrapActive = ref(false)
const { activate: activateFocusTrap, deactivate: deactivateFocusTrap } = useFocusTrap(panelRef, isFocusTrapActive)

watch(
  () => props.open && !!props.asset,
  (active) => {
    isFocusTrapActive.value = active
    if (active) {
      nextTick(() => activateFocusTrap())
      const onEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') emit('close')
      }
      document.addEventListener('keydown', onEscape)
      return () => {
        document.removeEventListener('keydown', onEscape)
        deactivateFocusTrap()
      }
    } else {
      deactivateFocusTrap()
    }
  },
  { immediate: true }
)

const localLabel = ref('')
const localDescription = ref('')
const localTags = ref<string[]>([])
const tagInput = ref('')
const isSaving = ref(false)
const isMagicLoading = ref(false)

watch(
  () => [props.open, props.asset] as const,
  ([open, asset]) => {
    if (open && asset) {
      localLabel.value = asset.label ?? ''
      localDescription.value = asset.description ?? (asset as any).metadata?.description ?? ''
      localTags.value = Array.isArray(asset.tags) ? [...asset.tags] : []
      tagInput.value = ''
    }
  },
  { immediate: true }
)

function handleOverlayClick() {
  emit('close')
}

function addTagFromInput() {
  const t = tagInput.value.trim()
  if (t && !localTags.value.includes(t)) {
    localTags.value.push(t)
    tagInput.value = ''
  }
}

function removeTag(index: number) {
  localTags.value.splice(index, 1)
}

async function runMagic() {
  if (!props.asset || isMagicLoading.value) return
  isMagicLoading.value = true
  try {
    await aiAnalysisService.runAIAnalysis(props.asset.id)
    // Backend runs async; poll for result a few times
    for (let i = 0; i < 5; i++) {
      await new Promise(r => setTimeout(r, 2000))
      const analysis = await aiAnalysisService.getAIAnalysis(props.asset.id)
      const desc = analysis?.seo?.description ?? (analysis as any)?.description
      if (desc) {
        localDescription.value = desc
        break
      }
    }
  } catch (err: any) {
    console.error('[MetadataPanel] Magic failed:', err)
    const msg = err?.response?.data?.detail ?? err?.message ?? 'Не удалось сгенерировать описание'
    emit('error', String(msg))
  } finally {
    isMagicLoading.value = false
  }
}

async function save() {
  if (!props.asset || isSaving.value) return
  isSaving.value = true
  try {
    await assetService.updateAsset(props.asset.id, {
      label: localLabel.value,
      metadata: { description: localDescription.value }
    })
    emit('saved')
    emit('close')
  } catch (err: any) {
    console.error('[MetadataPanel] Save failed:', err)
    const msg = err?.response?.data?.detail ?? err?.message ?? 'Не удалось сохранить'
    emit('error', String(msg))
  } finally {
    isSaving.value = false
  }
}
</script>
