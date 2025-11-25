<template>
  <Modal :is-open="isOpen" @close="$emit('close')" size="lg">
    <template #header>
      <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900">
        Создать публикацию
      </h2>
    </template>

    <template #body>
      <!-- Step Indicator -->
      <div class="mb-6">
        <div class="flex items-center justify-between">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="flex items-center"
          >
            <div
              :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold',
                currentStep > index
                  ? 'bg-primary-500 text-white'
                  : currentStep === index
                  ? 'bg-primary-500 text-white'
                  : 'bg-neutral-200 dark:bg-neutral-200 text-neutral-600 dark:text-neutral-600'
              ]"
            >
              <span v-if="currentStep > index">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span
              :class="[
                'ml-2 text-sm',
                currentStep >= index
                  ? 'text-neutral-900 dark:text-neutral-900 font-medium'
                  : 'text-neutral-600 dark:text-neutral-600'
              ]"
            >
              {{ step.label }}
            </span>
            <div
              v-if="index < steps.length - 1"
              :class="[
                'w-12 h-0.5 mx-4',
                currentStep > index ? 'bg-primary-500' : 'bg-neutral-200 dark:bg-neutral-200'
              ]"
            ></div>
          </div>
        </div>
      </div>

      <!-- Step 1: Select Assets -->
      <div v-if="currentStep === 0" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Выберите активы
          </label>
          <div class="border border-neutral-300 dark:border-neutral-300 rounded-md p-4 min-h-[200px]">
            <div v-if="selectedAssets.length === 0" class="text-center py-8 text-neutral-600 dark:text-neutral-600">
              <p>Выберите активы для публикации</p>
              <Button variant="outline" size="sm" class="mt-4" @click="openAssetSelector">
                Выбрать активы
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
      </div>

      <!-- Step 2: Configure Channels -->
      <div v-if="currentStep === 1" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-neutral-900 dark:text-neutral-900 mb-2">
            Выберите каналы
          </label>
          <div v-if="availableChannels.length === 0" class="text-center py-8 text-neutral-600 dark:text-neutral-600">
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
      </div>

      <!-- Step 3: Set Schedule & Permissions -->
      <div v-if="currentStep === 2" class="space-y-4">
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
      </div>

      <!-- Step 4: Preview & Publish -->
      <div v-if="currentStep === 3" class="space-y-4">
        <div class="bg-neutral-50 dark:bg-neutral-50 rounded-lg p-4">
          <h3 class="font-semibold text-neutral-900 dark:text-neutral-900 mb-3">
            Предпросмотр публикации
          </h3>
          <div class="space-y-2 text-sm">
            <div>
              <span class="text-neutral-600 dark:text-neutral-600">Название:</span>
              <span class="ml-2 text-neutral-900 dark:text-neutral-900">{{ publicationData.title }}</span>
            </div>
            <div>
              <span class="text-neutral-600 dark:text-neutral-600">Активов:</span>
              <span class="ml-2 text-neutral-900 dark:text-neutral-900">{{ selectedAssets.length }}</span>
            </div>
            <div>
              <span class="text-neutral-600 dark:text-neutral-600">Каналов:</span>
              <span class="ml-2 text-neutral-900 dark:text-neutral-900">{{ selectedChannels.length }}</span>
            </div>
            <div v-if="publicationData.schedule.start_date">
              <span class="text-neutral-600 dark:text-neutral-600">Начало:</span>
              <span class="ml-2 text-neutral-900 dark:text-neutral-900">
                {{ formatDate(publicationData.schedule.start_date) }}
              </span>
            </div>
          </div>
        </div>

        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="publishImmediately"
              type="checkbox"
              class="rounded"
            />
            <span class="text-sm text-neutral-900 dark:text-neutral-900">
              Опубликовать сразу
            </span>
          </label>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-between">
        <Button
          v-if="currentStep > 0"
          variant="outline"
          @click="previousStep"
        >
          Назад
        </Button>
        <div></div>
        <div class="flex gap-2">
          <Button variant="outline" @click="$emit('close')">
            Отмена
          </Button>
          <Button
            v-if="currentStep < steps.length - 1"
            variant="primary"
            :disabled="!canProceed"
            @click="nextStep"
          >
            Далее
          </Button>
          <Button
            v-else
            variant="primary"
            :disabled="!canPublish || isSubmitting"
            :loading="isSubmitting"
            @click="handlePublish"
          >
            {{ publishImmediately ? 'Опубликовать' : 'Создать' }}
          </Button>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Asset, Publication, PublicationChannel, CreatePublicationRequest } from '@/types/api'
import { distributionService } from '@/services/distributionService'
import { formatFileSize, formatDate } from '@/utils/formatters'
import Modal from '@/components/Common/Modal.vue'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  created: [publication: Publication]
}>()

const steps = [
  { label: 'Выбор активов', key: 'assets' },
  { label: 'Каналы', key: 'channels' },
  { label: 'Настройки', key: 'settings' },
  { label: 'Предпросмотр', key: 'preview' }
]

const currentStep = ref(0)
const selectedAssets = ref<Asset[]>([])
const availableChannels = ref<PublicationChannel[]>([])
const selectedChannels = ref<number[]>([])
const publishImmediately = ref(false)
const isSubmitting = ref(false)

const publicationData = ref<CreatePublicationRequest>({
  title: '',
  description: '',
  asset_ids: [],
  channel_ids: [],
  schedule: {}
})

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return selectedAssets.value.length > 0
    case 1:
      return selectedChannels.value.length > 0
    case 2:
      return publicationData.value.title.trim().length > 0
    default:
      return true
  }
})

const canPublish = computed(() => {
  return (
    publicationData.value.title.trim().length > 0 &&
    selectedAssets.value.length > 0 &&
    selectedChannels.value.length > 0
  )
})

onMounted(async () => {
  await loadChannels()
})

async function loadChannels() {
  try {
    availableChannels.value = await distributionService.getChannels()
  } catch (error) {
    console.error('Failed to load channels:', error)
  }
}

function nextStep() {
  if (currentStep.value < steps.length - 1 && canProceed.value) {
    currentStep.value++
    updatePublicationData()
  }
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function updatePublicationData() {
  publicationData.value.asset_ids = selectedAssets.value.map((a) => a.id)
  publicationData.value.channel_ids = selectedChannels.value
}

function openAssetSelector() {
  // TODO: Open asset selector modal
  // For now, we'll use a placeholder
  console.log('Open asset selector')
}

function removeAsset(assetId: number) {
  selectedAssets.value = selectedAssets.value.filter((a) => a.id !== assetId)
}

function toggleChannel(channelId: number) {
  const index = selectedChannels.value.indexOf(channelId)
  if (index === -1) {
    selectedChannels.value.push(channelId)
  } else {
    selectedChannels.value.splice(index, 1)
  }
}

async function handlePublish() {
  if (!canPublish.value || isSubmitting.value) return

  isSubmitting.value = true
  updatePublicationData()

  try {
    const publication = await distributionService.createPublication(publicationData.value)
    
    if (publishImmediately.value) {
      await distributionService.publishPublication(publication.id)
    }

    emit('created', publication)
    emit('close')
    
    // Reset form
    resetForm()
  } catch (error) {
    console.error('Failed to create publication:', error)
    // TODO: Show error toast
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  currentStep.value = 0
  selectedAssets.value = []
  selectedChannels.value = []
  publishImmediately.value = false
  publicationData.value = {
    title: '',
    description: '',
    asset_ids: [],
    channel_ids: [],
    schedule: {}
  }
}
</script>

