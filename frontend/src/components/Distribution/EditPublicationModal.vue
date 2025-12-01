<template>
  <Modal :is-open="isOpen" @close="$emit('close')" size="lg">
    <template #header>
      <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900">
        Редактировать публикацию
      </h2>
    </template>

    <template #body>
      <div class="space-y-4">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Название публикации
          </label>
          <Input
            v-model="publicationData.title"
            placeholder="Введите название"
            required
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Описание (необязательно)
          </label>
          <textarea
            v-model="publicationData.description"
            class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-0 dark:text-neutral-900"
            rows="3"
            placeholder="Введите описание"
          ></textarea>
        </div>

        <!-- Assets -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Активы
          </label>
          <div class="border border-neutral-300 dark:border-neutral-300 rounded-md p-4 min-h-[150px]">
            <div v-if="selectedAssets.length === 0" class="text-center py-8 text-neutral-600 dark:text-neutral-600">
              <p>Нет активов</p>
              <Button variant="outline" size="sm" class="mt-4" @click="openAssetSelector">
                Добавить активы
              </Button>
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="asset in selectedAssets"
                :key="asset.id"
                class="flex items-center justify-between p-2 bg-neutral-50 dark:bg-neutral-50 rounded-md"
              >
                <div class="flex items-center gap-3">
                  <img
                    v-if="asset.thumbnail_url"
                    :src="asset.thumbnail_url"
                    :alt="asset.label"
                    class="w-12 h-12 object-cover rounded"
                  />
                  <div>
                    <div class="font-medium text-sm text-neutral-900 dark:text-neutral-900">
                      {{ asset.label }}
                    </div>
                    <div class="text-xs text-neutral-600 dark:text-neutral-600">
                      {{ formatFileSize(asset.size) }}
                    </div>
                  </div>
                </div>
                <button
                  class="text-error hover:text-error-dark"
                  @click="removeAsset(asset.id)"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Channels -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Каналы
          </label>
          <div v-if="availableChannels.length === 0" class="text-center py-4 text-neutral-600 dark:text-neutral-600">
            <p>Загрузка каналов...</p>
          </div>
          <div v-else class="space-y-2">
            <label
              v-for="channel in availableChannels"
              :key="channel.id"
              class="flex items-center p-3 border border-neutral-300 dark:border-neutral-300 rounded-md hover:bg-neutral-50 dark:hover:bg-neutral-50 cursor-pointer"
            >
              <input
                type="checkbox"
                :value="channel.id"
                :checked="selectedChannels.includes(channel.id)"
                @change="toggleChannel(channel.id)"
                class="mr-3"
              />
              <div class="flex-1">
                <div class="font-medium text-sm text-neutral-900 dark:text-neutral-900">
                  {{ channel.name }}
                </div>
                <div class="text-xs text-neutral-600 dark:text-neutral-600">
                  {{ channel.type }}
                </div>
              </div>
            </label>
          </div>
        </div>

        <!-- Schedule -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
              Дата начала
            </label>
            <input
              v-model="publicationData.schedule.start_date"
              type="datetime-local"
              class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-0 dark:text-neutral-900"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
              Дата окончания
            </label>
            <input
              v-model="publicationData.schedule.end_date"
              type="datetime-local"
              class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-0 dark:text-neutral-900"
            />
          </div>
        </div>

        <!-- Status -->
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Статус
          </label>
          <select
            v-model="publicationData.status"
            class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 dark:bg-neutral-0 dark:text-neutral-900"
          >
            <option value="draft">Черновик</option>
            <option value="scheduled">Запланировано</option>
            <option value="published">Опубликовано</option>
            <option value="archived">Архив</option>
          </select>
        </div>

        <!-- Error Display -->
        <div v-if="error" class="p-3 bg-error-50 dark:bg-error-50 rounded-md">
          <p class="text-sm font-medium text-error">{{ error }}</p>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button variant="outline" @click="$emit('close')">
          Отмена
        </Button>
        <Button
          variant="primary"
          :disabled="!canSave || isSubmitting"
          :loading="isSubmitting"
          @click="handleSave"
        >
          Сохранить
        </Button>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Asset, Publication, PublicationChannel, UpdatePublicationRequest } from '@/types/api'
import { distributionService } from '@/services/distributionService'
import { formatFileSize } from '@/utils/formatters'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'

interface Props {
  isOpen: boolean
  publication: Publication | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  updated: [publication: Publication]
}>()

const selectedAssets = ref<Asset[]>([])
const availableChannels = ref<PublicationChannel[]>([])
const selectedChannels = ref<number[]>([])
const isSubmitting = ref(false)
const error = ref<string | null>(null)

const publicationData = ref<UpdatePublicationRequest>({
  title: '',
  description: '',
  asset_ids: [],
  channel_ids: [],
  schedule: {},
  status: 'draft'
})

const canSave = computed(() => {
  return (
    publicationData.value.title.trim().length > 0 &&
    selectedAssets.value.length > 0 &&
    selectedChannels.value.length > 0
  )
})

// Load publication data when modal opens
watch(
  () => props.isOpen,
  async (isOpen) => {
    if (isOpen && props.publication) {
      await loadPublicationData()
      await loadChannels()
    } else if (!isOpen) {
      resetForm()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await loadChannels()
})

async function loadChannels() {
  try {
    availableChannels.value = await distributionService.getChannels()
  } catch (err) {
    console.error('Failed to load channels:', err)
  }
}

function loadPublicationData() {
  if (!props.publication) return

  publicationData.value = {
    title: props.publication.title,
    description: props.publication.description || '',
    asset_ids: props.publication.assets.map((a) => a.id),
    channel_ids: props.publication.channels.map((c) => c.id),
    schedule: props.publication.schedule || {},
    status: props.publication.status
  }

  selectedAssets.value = [...props.publication.assets]
  selectedChannels.value = props.publication.channels.map((c) => c.id)
}

function openAssetSelector() {
  // TODO: Open asset selector modal
  console.log('Open asset selector')
}

function removeAsset(assetId: number) {
  selectedAssets.value = selectedAssets.value.filter((a) => a.id !== assetId)
  publicationData.value.asset_ids = selectedAssets.value.map((a) => a.id)
}

function toggleChannel(channelId: number) {
  const index = selectedChannels.value.indexOf(channelId)
  if (index === -1) {
    selectedChannels.value.push(channelId)
  } else {
    selectedChannels.value.splice(index, 1)
  }
  publicationData.value.channel_ids = selectedChannels.value
}

async function handleSave() {
  if (!canSave.value || isSubmitting.value || !props.publication) return

  isSubmitting.value = true
  error.value = null

  try {
    publicationData.value.asset_ids = selectedAssets.value.map((a) => a.id)
    publicationData.value.channel_ids = selectedChannels.value

    const updated = await distributionService.updatePublication(props.publication.id, publicationData.value)
    emit('updated', updated)
    emit('close')
  } catch (err: any) {
    error.value = err.message || 'Не удалось сохранить публикацию'
    console.error('Failed to update publication:', err)
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  selectedAssets.value = []
  selectedChannels.value = []
  error.value = null
  publicationData.value = {
    title: '',
    description: '',
    asset_ids: [],
    channel_ids: [],
    schedule: {},
    status: 'draft'
  }
}
</script>








