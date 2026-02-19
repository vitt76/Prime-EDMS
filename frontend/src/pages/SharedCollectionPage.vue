<!--
  Public view of a shared collection (cabinet) by UUID.
  No auth required. Handles expired link and password-protected shares.
-->
<template>
  <div class="shared-collection min-h-screen bg-neutral-50 dark:bg-neutral-900">
    <header class="shared-collection__header border-b border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 px-4 py-3">
      <h1 class="text-lg font-semibold text-neutral-800 dark:text-neutral-200">
        {{ pageTitle }}
      </h1>
    </header>

    <main class="shared-collection__main p-4">
      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-12">
        <span class="text-neutral-500">Загрузка…</span>
      </div>

      <!-- Expired -->
      <div v-else-if="errorExpired" class="max-w-md mx-auto text-center py-12">
        <p class="text-neutral-600 dark:text-neutral-400">Ссылка на коллекцию истекла.</p>
      </div>

      <!-- Password required -->
      <div v-else-if="errorRequiresPassword" class="max-w-sm mx-auto py-12">
        <form @submit.prevent="submitPassword" class="space-y-4">
          <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300">
            Введите пароль для доступа к коллекции
          </label>
          <input
            v-model="passwordInput"
            type="password"
            class="w-full rounded border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-3 py-2 text-neutral-900 dark:text-neutral-100"
            placeholder="Пароль"
            autocomplete="current-password"
          />
          <button
            type="submit"
            class="w-full rounded bg-primary-600 text-white py-2 px-4 hover:bg-primary-700"
          >
            Открыть
          </button>
        </form>
      </div>

      <!-- Other error -->
      <div v-else-if="errorMessage" class="max-w-md mx-auto text-center py-12">
        <p class="text-neutral-600 dark:text-neutral-400">{{ errorMessage }}</p>
      </div>

      <!-- Content -->
      <div v-else-if="shareData" class="shared-collection__content">
        <p class="text-sm text-neutral-500 dark:text-neutral-400 mb-4">
          Документов в коллекции: {{ shareData.documents.length }}
        </p>
        <ul class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <li
            v-for="doc in shareData.documents"
            :key="doc.id"
            class="rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800 overflow-hidden"
          >
            <div class="aspect-square bg-neutral-100 dark:bg-neutral-700 flex items-center justify-center">
              <img
                v-if="doc.thumbnail_url"
                :src="doc.thumbnail_url"
                :alt="doc.label"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-neutral-400 text-xs">Нет превью</span>
            </div>
            <p class="p-2 text-sm text-neutral-700 dark:text-neutral-300 truncate" :title="doc.label">
              {{ doc.label }}
            </p>
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { collectionsService } from '@/services/collectionsService'
import type { PublicShareResponse } from '@/services/collectionsService'

const route = useRoute()
const uuid = computed(() => String(route.params.uuid ?? ''))

const loading = ref(true)
const shareData = ref<PublicShareResponse | null>(null)
const errorExpired = ref(false)
const errorRequiresPassword = ref(false)
const errorMessage = ref('')
const passwordInput = ref('')

const pageTitle = computed(() => {
  if (shareData.value) return shareData.value.label
  if (errorExpired.value) return 'Ссылка истекла'
  if (errorRequiresPassword.value) return 'Требуется пароль'
  return 'Коллекция'
})

function getErrorPayload(err: unknown): { expired?: boolean; requires_password?: boolean; detail?: string } {
  const ax = err as { response?: { data?: unknown; status?: number } }
  const data = ax?.response?.data
  if (data && typeof data === 'object' && 'expired' in data) {
    return { expired: true, detail: (data as any).detail }
  }
  if (data && typeof data === 'object' && 'requires_password' in data) {
    return { requires_password: true, detail: (data as any).detail }
  }
  return { detail: (data as any)?.detail ?? (err instanceof Error ? err.message : String(err)) }
}

async function load() {
  loading.value = true
  errorExpired.value = false
  errorRequiresPassword.value = false
  errorMessage.value = ''
  const pwd = route.query.password as string | undefined
  try {
    const data = await collectionsService.getPublicShare(uuid.value, pwd)
    shareData.value = data
  } catch (err) {
    const payload = getErrorPayload(err)
    if (payload.expired) {
      errorExpired.value = true
    } else if (payload.requires_password) {
      errorRequiresPassword.value = true
    } else {
      errorMessage.value = payload.detail ?? 'Не удалось загрузить коллекцию.'
    }
  } finally {
    loading.value = false
  }
}

async function submitPassword() {
  const pwd = passwordInput.value.trim()
  if (!pwd) return
  loading.value = true
  errorRequiresPassword.value = false
  try {
    const data = await collectionsService.getPublicShare(uuid.value, pwd)
    shareData.value = data
  } catch (err) {
    const payload = getErrorPayload(err)
    if (payload.requires_password) {
      errorRequiresPassword.value = true
      errorMessage.value = 'Неверный пароль.'
    } else {
      errorMessage.value = payload.detail ?? 'Ошибка доступа.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
watch(uuid, () => load())
</script>
