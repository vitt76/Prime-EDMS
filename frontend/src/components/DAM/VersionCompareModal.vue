<!--
  Side-by-side version comparison for a document.
  User selects two versions; previews are loaded from existing document files API.
-->
<template>
  <Modal
    :is-open="true"
    title="Сравнение версий"
    @close="$emit('close')"
    size="lg"
  >
    <div class="version-compare">
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
            Версия A
          </label>
          <select
            v-model="selectedA"
            class="w-full rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-3 py-2 text-neutral-900 dark:text-neutral-100"
          >
            <option :value="null">Выберите версию</option>
            <option
              v-for="v in versions"
              :key="v.id"
              :value="v.id"
            >
              v{{ v.versionNumber ?? v.id }} — {{ v.filename }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
            Версия B
          </label>
          <select
            v-model="selectedB"
            class="w-full rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-3 py-2 text-neutral-900 dark:text-neutral-100"
          >
            <option :value="null">Выберите версию</option>
            <option
              v-for="v in versions"
              :key="v.id"
              :value="v.id"
            >
              v{{ v.versionNumber ?? v.id }} — {{ v.filename }}
            </option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 border-t border-neutral-200 dark:border-neutral-700 pt-4">
        <div class="flex flex-col">
          <p class="text-xs text-neutral-500 dark:text-neutral-400 mb-2">
            {{ labelA || '—' }}
          </p>
          <div class="aspect-square bg-neutral-100 dark:bg-neutral-800 rounded-lg flex items-center justify-center min-h-[200px]">
            <img
              v-if="previewUrlA"
              :src="previewUrlA"
              alt="Версия A"
              class="max-w-full max-h-full object-contain"
            />
            <span v-else class="text-neutral-400 text-sm">
              {{ loadingA ? 'Загрузка…' : 'Выберите версию A' }}
            </span>
          </div>
        </div>
        <div class="flex flex-col">
          <p class="text-xs text-neutral-500 dark:text-neutral-400 mb-2">
            {{ labelB || '—' }}
          </p>
          <div class="aspect-square bg-neutral-100 dark:bg-neutral-800 rounded-lg flex items-center justify-center min-h-[200px]">
            <img
              v-if="previewUrlB"
              :src="previewUrlB"
              alt="Версия B"
              class="max-w-full max-h-full object-contain"
            />
            <span v-else class="text-neutral-400 text-sm">
              {{ loadingB ? 'Загрузка…' : 'Выберите версию B' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button variant="primary" @click="$emit('close')">Закрыть</Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
interface VersionItem {
  id: number
  filename: string
  versionNumber?: number
  _file?: { pages_first?: { image_url?: string } }
}

const props = defineProps<{
  versions: VersionItem[]
  /** Fetch image URL (relative or absolute) and return a blob object URL for display. */
  fetchPreviewAsBlobUrl: (imageUrl: string) => Promise<string | null>
}>()

defineEmits<{ close: [] }>()

const selectedA = ref<number | null>(null)
const selectedB = ref<number | null>(null)
const previewUrlA = ref<string | null>(null)
const previewUrlB = ref<string | null>(null)
const loadingA = ref(false)
const loadingB = ref(false)
const objectUrlsToRevoke: string[] = []

async function loadPreview(
  fileId: number | null,
  side: 'A' | 'B'
): Promise<void> {
  const loading = side === 'A' ? loadingA : loadingB
  const urlRef = side === 'A' ? previewUrlA : previewUrlB
  if (!fileId) {
    urlRef.value = null
    return
  }
  const ver = props.versions.find((v) => v.id === fileId)
  const file = ver?._file ?? ver
  if (!file) {
    urlRef.value = null
    return
  }
  const imageUrl = (file as any)?.pages_first?.image_url ?? (file as any)?._file?.pages_first?.image_url ?? null
  if (!imageUrl) {
    urlRef.value = null
    return
  }
  loading.value = true
  urlRef.value = null
  try {
    const blobUrl = await props.fetchPreviewAsBlobUrl(imageUrl)
    if (blobUrl) {
      urlRef.value = blobUrl
      objectUrlsToRevoke.push(blobUrl)
    }
  } finally {
    loading.value = false
  }
}

const labelA = computed(() => {
  if (!selectedA.value) return ''
  const v = props.versions.find((x) => x.id === selectedA.value)
  return v ? `v${v.versionNumber ?? v.id} — ${v.filename}` : ''
})
const labelB = computed(() => {
  if (!selectedB.value) return ''
  const v = props.versions.find((x) => x.id === selectedB.value)
  return v ? `v${v.versionNumber ?? v.id} — ${v.filename}` : ''
})

watch(selectedA, (id) => loadPreview(id, 'A'))
watch(selectedB, (id) => loadPreview(id, 'B'))

onUnmounted(() => {
  objectUrlsToRevoke.forEach((u) => {
    try { URL.revokeObjectURL(u) } catch { /* ignore */ }
  })
})
</script>
