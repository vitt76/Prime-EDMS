<template>
  <Modal
    :is-open="true"
    title="Поделиться коллекцией"
    @close="$emit('close')"
    size="md"
  >
    <div class="share-collection-modal">
      <!-- Create new share -->
      <template v-if="!createdShare">
        <form @submit.prevent="handleCreate" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
              Срок действия (необязательно)
            </label>
            <input
              v-model="expiresAt"
              type="datetime-local"
              class="w-full rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-3 py-2 text-neutral-900 dark:text-neutral-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
              Пароль (необязательно)
            </label>
            <input
              v-model="password"
              type="password"
              class="w-full rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-3 py-2 text-neutral-900 dark:text-neutral-100"
              placeholder="Оставьте пустым для доступа без пароля"
            />
          </div>
          <p v-if="errorMessage" class="text-sm text-red-600 dark:text-red-400">
            {{ errorMessage }}
          </p>
        </form>
      </template>

      <!-- After create: show URL and copy -->
      <template v-else>
        <p class="text-sm text-neutral-600 dark:text-neutral-400 mb-2">
          Ссылка создана. Любой, у кого есть эта ссылка, сможет просматривать коллекцию.
        </p>
        <div class="flex gap-2">
          <input
            :value="publicPageUrl"
            readonly
            class="flex-1 rounded border border-neutral-300 dark:border-neutral-600 bg-neutral-50 dark:bg-neutral-800 px-3 py-2 text-sm text-neutral-700 dark:text-neutral-300"
          />
          <button
            type="button"
            class="rounded bg-primary-600 text-white px-4 py-2 text-sm hover:bg-primary-700"
            @click="copyUrl"
          >
            {{ copied ? 'Скопировано' : 'Копировать' }}
          </button>
        </div>
      </template>

      <!-- Existing shares -->
      <div v-if="existingShares.length > 0" class="mt-6 pt-4 border-t border-neutral-200 dark:border-neutral-700">
        <p class="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
          Активные ссылки
        </p>
        <ul class="space-y-2">
          <li
            v-for="s in existingShares"
            :key="s.uuid"
            class="flex items-center justify-between rounded border border-neutral-200 dark:border-neutral-700 px-3 py-2 text-sm"
          >
            <span class="truncate text-neutral-600 dark:text-neutral-400">
              {{ getPublicShareUrl(s.uuid) }}
              <span v-if="s.expires_at"> (до {{ formatDate(s.expires_at) }})</span>
            </span>
            <button
              type="button"
              class="ml-2 text-red-600 hover:text-red-700"
              :disabled="revoking === s.uuid"
              @click="revoke(s)"
            >
              Отозвать
            </button>
          </li>
        </ul>
      </div>
    </div>

    <template #footer>
      <template v-if="!createdShare">
        <Button variant="ghost" @click="$emit('close')" type="button">
          Отмена
        </Button>
        <Button
          variant="primary"
          :loading="creating"
          @click="handleCreate"
        >
          Создать ссылку
        </Button>
      </template>
      <template v-else>
        <Button variant="primary" @click="$emit('close')">
          Готово
        </Button>
      </template>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import { collectionsService } from '@/services/collectionsService'
import type { CabinetShareDTO } from '@/services/collectionsService'

const props = defineProps<{
  collectionId: number | string
}>()

const emit = defineEmits<{
  close: []
}>()

const expiresAt = ref('')
const password = ref('')
const creating = ref(false)
const errorMessage = ref('')
const createdShare = ref<{ share_url: string; share_id: string; expires_at?: string } | null>(null)
const copied = ref(false)
const existingShares = ref<CabinetShareDTO[]>([])
const revoking = ref<string | null>(null)

function getPublicShareUrl(uuid: string): string {
  const base = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '')
  return `${window.location.origin}${base}/shared/${uuid}`
}

/** URL of the public shared collection page (SPA route). */
const publicPageUrl = computed(() => {
  if (!createdShare.value?.share_id) return ''
  return getPublicShareUrl(createdShare.value.share_id)
})

function formatDate(iso: string | null | undefined): string {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, { dateStyle: 'short' })
  } catch {
    return iso
  }
}

async function loadExisting() {
  try {
    const list = await collectionsService.getCollectionShares(String(props.collectionId))
    existingShares.value = list
  } catch {
    existingShares.value = []
  }
}

async function handleCreate() {
  creating.value = true
  errorMessage.value = ''
  try {
    const opts: { expires_at?: string | null; password?: string } = {}
    if (expiresAt.value.trim()) {
      const d = new Date(expiresAt.value.trim())
      if (!Number.isNaN(d.getTime())) opts.expires_at = d.toISOString()
    }
    if (password.value.trim()) opts.password = password.value.trim()
    const result = await collectionsService.shareCollection(String(props.collectionId), opts)
    createdShare.value = result
    await loadExisting()
  } catch (e) {
    errorMessage.value = e instanceof Error ? e.message : String(e)
  } finally {
    creating.value = false
  }
}

function copyUrl() {
  const url = publicPageUrl.value
  if (!url) return
  navigator.clipboard.writeText(url).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}

async function revoke(s: CabinetShareDTO) {
  revoking.value = s.uuid
  try {
    await collectionsService.revokeCollectionShare(String(props.collectionId), s.uuid)
    await loadExisting()
    if (createdShare.value?.share_id === s.uuid) createdShare.value = null
  } finally {
    revoking.value = null
  }
}

onMounted(() => loadExisting())
</script>
