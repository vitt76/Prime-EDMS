<template>
  <div class="distribution-page">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-900">
          Публикации
        </h1>
        <p class="text-sm text-neutral-600 dark:text-neutral-600 mt-1">
          Управление публикациями и их распространением
        </p>
      </div>
      <Button variant="primary" @click="showCreateModal = true">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 4v16m8-8H4"
          />
        </svg>
        Создать публикацию
      </Button>
    </div>

    <!-- Filters -->
    <div class="mb-6 flex items-center gap-4">
      <Select
        v-model="statusFilter"
        :options="statusOptions"
        placeholder="Все статусы"
        class="w-48"
        @change="handleStatusFilterChange"
      />
      <Input
        v-model="searchQuery"
        placeholder="Поиск публикаций..."
        class="flex-1 max-w-md"
        @input="handleSearch"
      >
        <template #prefix>
          <svg class="w-5 h-5 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </template>
      </Input>
    </div>

    <!-- Loading State -->
    <div v-if="distributionStore.isLoading && distributionStore.publications.length === 0" class="text-center py-12">
      <div class="animate-spin h-8 w-8 mx-auto text-primary-500"></div>
      <p class="mt-4 text-neutral-600 dark:text-neutral-600">Загрузка публикаций...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="distributionStore.error && distributionStore.publications.length === 0" class="text-center py-12">
      <div class="max-w-md mx-auto">
        <svg
          class="mx-auto h-12 w-12 text-error"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-neutral-900 dark:text-neutral-900">
          Ошибка загрузки
        </h3>
        <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-600">
          {{ distributionStore.error }}
        </p>
        <Button variant="primary" class="mt-4" @click="handleRetry">
          Попробовать снова
        </Button>
      </div>
    </div>

    <!-- Publications List -->
    <div v-else-if="distributionStore.publications.length > 0" class="space-y-4">
      <PublicationCard
        v-for="publication in distributionStore.publications"
        :key="publication.id"
        :publication="publication"
        @preview="handlePreview(publication)"
        @edit="handleEdit(publication)"
        @delete="handleDelete(publication)"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <svg
        class="mx-auto h-16 w-16 text-neutral-400 mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
        />
      </svg>
      <h3 class="text-lg font-medium text-neutral-900 dark:text-neutral-900 mb-2">
        Нет публикаций
      </h3>
      <p class="text-sm text-neutral-600 dark:text-neutral-600 mb-4">
        Создайте первую публикацию для распространения активов
      </p>
      <Button variant="primary" @click="showCreateModal = true">
        Создать публикацию
      </Button>
    </div>

    <!-- Pagination -->
    <div v-if="distributionStore.totalCount > 0" class="mt-6">
      <Pagination
        :current-page="distributionStore.currentPage"
        :total-items="distributionStore.totalCount"
        :page-size="distributionStore.pageSize"
        @page-change="handlePageChange"
      />
    </div>

    <!-- Create Publication Modal -->
    <CreatePublicationModal
      :is-open="showCreateModal"
      @close="showCreateModal = false"
      @created="handlePublicationCreated"
    />

    <!-- Edit Publication Modal -->
    <EditPublicationModal
      :is-open="showEditModal"
      :publication="publicationToEdit"
      @close="showEditModal = false"
      @updated="handlePublicationUpdated"
    />
    <!-- Delete Confirmation Modal -->
    <Modal
      :is-open="showDeleteModal"
      @close="showDeleteModal = false"
    >
      <template #header>
        <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-900">
          Удалить публикацию?
        </h2>
      </template>
      <template #body>
        <p class="text-neutral-900 dark:text-neutral-900">
          Вы уверены, что хотите удалить публикацию "{{ publicationToDelete?.title }}"?
          Это действие нельзя отменить.
        </p>
      </template>
      <template #footer>
        <div class="flex justify-end gap-2">
          <Button variant="outline" @click="showDeleteModal = false">
            Отмена
          </Button>
          <Button
            variant="danger"
            :loading="isDeleting"
            @click="confirmDelete"
          >
            Удалить
          </Button>
        </div>
      </template>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDistributionStore } from '@/stores/distributionStore'
import type { Publication } from '@/types/api'
import Button from '@/components/Common/Button.vue'
import Input from '@/components/Common/Input.vue'
import Select from '@/components/Common/Select.vue'
import Modal from '@/components/Common/Modal.vue'
import Pagination from '@/components/Common/Pagination.vue'
import PublicationCard from '@/components/Distribution/PublicationCard.vue'
import CreatePublicationModal from '@/components/Distribution/CreatePublicationModal.vue'
import EditPublicationModal from '@/components/Distribution/EditPublicationModal.vue'

const router = useRouter()
const distributionStore = useDistributionStore()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const publicationToEdit = ref<Publication | null>(null)
const publicationToDelete = ref<Publication | null>(null)
const isDeleting = ref(false)
const statusFilter = ref<string>('')
const searchQuery = ref('')

const statusOptions = [
  { value: '', label: 'Все статусы' },
  { value: 'draft', label: 'Черновик' },
  { value: 'scheduled', label: 'Запланировано' },
  { value: 'published', label: 'Опубликовано' },
  { value: 'archived', label: 'Архив' }
]

onMounted(async () => {
  await distributionStore.fetchPublications()
})

watch(() => distributionStore.filters, () => {
  // Auto-refresh when filters change
}, { deep: true })

function handleStatusFilterChange(value: string) {
  const status = value ? (value as Publication['status']) : undefined
  distributionStore.applyFilters({ status })
}

function handleSearch() {
  distributionStore.applyFilters({ search: searchQuery.value || undefined })
}

function handlePageChange(page: number) {
  distributionStore.setPage(page)
}

function handleRetry() {
  distributionStore.fetchPublications()
}

function handlePreview(publication: Publication) {
  // TODO: Open preview modal or navigate to detail page
  console.log('Preview publication:', publication.id)
}

function handleEdit(publication: Publication) {
  publicationToEdit.value = publication
  showEditModal.value = true
}

function handleDelete(publication: Publication) {
  publicationToDelete.value = publication
  showDeleteModal.value = true
}

async function confirmDelete() {
  if (!publicationToDelete.value) return

  isDeleting.value = true
  try {
    await distributionStore.deletePublication(publicationToDelete.value.id)
    showDeleteModal.value = false
    publicationToDelete.value = null
    // TODO: Show success toast
  } catch (error) {
    console.error('Failed to delete publication:', error)
    // TODO: Show error toast
  } finally {
    isDeleting.value = false
  }
}

function handlePublicationCreated(publication: Publication) {
  // Refresh publications list
  distributionStore.fetchPublications()
  // TODO: Show success toast
}

function handlePublicationUpdated(publication: Publication) {
  // Refresh publications list
  distributionStore.fetchPublications()
  showEditModal.value = false
  publicationToEdit.value = null
  // TODO: Show success toast
}
</script>

<style scoped>
.distribution-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
