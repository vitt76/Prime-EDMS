<template>
  <div class="workflow-widget">
    <!-- Loading State -->
    <div v-if="isLoading" class="p-4 flex items-center justify-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
    </div>

    <template v-else>
      <!-- No Workflow Instance - Show Launch Button -->
      <div v-if="!workflowInstance" class="p-4 border-b border-neutral-100">
        <div class="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-3">
          Статус и согласование
        </div>
        
        <!-- Show Draft Status -->
        <div class="mb-4">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center bg-blue-100">
              <PencilSquareIcon class="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div class="font-semibold text-blue-600">
                Черновик
              </div>
              <div class="text-xs text-neutral-500">
                Начальное состояние
              </div>
            </div>
          </div>
          <div class="text-sm text-neutral-600">
            Согласование не запущено для этого документа
          </div>
        </div>
        <button
          v-if="availableWorkflowTemplates.length > 0"
          class="w-full inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-lg
                 bg-primary-600 text-white hover:bg-primary-700 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isLaunching"
          @click="launchWorkflow"
        >
          <PaperAirplaneIcon v-if="!isLaunching" class="w-4 h-4" />
          <svg v-else class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          {{ isLaunching ? 'Запуск...' : `Запустить ${availableWorkflowTemplates[0]?.label || 'согласование'}` }}
        </button>
        <div v-else class="text-xs text-neutral-500">
          Нет доступных workflow для этого типа документа
        </div>
      </div>

      <!-- Current Status -->
      <div v-else class="p-4 border-b border-neutral-100">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">
            Текущий статус
          </span>
          <span v-if="workflowInstance?.last_log_entry" class="text-xs text-neutral-400">
            {{ formatRelativeTime(workflowInstance.last_log_entry.datetime) }}
          </span>
        </div>
        
        <div 
          v-if="currentState"
          class="flex items-center gap-3"
        >
          <div 
            :class="[
              'w-10 h-10 rounded-lg flex items-center justify-center',
              stateColorClasses.bg
            ]"
          >
            <component 
              :is="currentState.initial ? PencilSquareIcon : currentState.completion ? CheckCircleIcon : ClockIcon" 
              :class="['w-5 h-5', stateColorClasses.text]" 
            />
          </div>
          <div>
            <div :class="['font-semibold', stateColorClasses.text]">
              {{ currentState.label }}
            </div>
            <div class="text-xs text-neutral-500">
              {{ currentState.initial ? 'Начальное состояние' : currentState.completion ? 'Завершающее состояние' : 'Промежуточное состояние' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Available Transitions -->
      <div v-if="availableTransitions.length > 0" class="p-4 border-b border-neutral-100">
        <div class="text-xs font-medium text-neutral-500 uppercase tracking-wide mb-3">
          Доступные действия
        </div>
        <div class="flex flex-wrap gap-2">
            <button
              v-for="transition in availableTransitions"
              :key="transition.id"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg
                     bg-primary-100 text-primary-700 hover:bg-primary-200 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                     transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isTransitioning"
              @click="initiateTransition(transition)"
            >
              <ArrowRightIcon class="w-4 h-4" />
              {{ transition.label }}
            </button>
        </div>
      </div>

      <!-- Workflow History -->
      <div v-if="historyItems.length > 0" class="p-4">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">
            История изменений
          </span>
          <button 
            v-if="historyItems.length > 3"
            class="text-xs text-primary-600 hover:text-primary-700"
            @click="showAllHistory = !showAllHistory"
          >
            {{ showAllHistory ? 'Скрыть' : `Показать все (${historyItems.length})` }}
          </button>
        </div>

        <div class="relative">
          <!-- Timeline line -->
          <div 
            v-if="displayedHistory.length > 1"
            class="absolute left-4 top-6 bottom-6 w-0.5 bg-neutral-200"
          ></div>

          <!-- Timeline items -->
          <div class="space-y-4">
            <div 
              v-for="(item, index) in displayedHistory" 
              :key="item.id"
              class="relative flex gap-3"
            >
              <!-- Timeline dot -->
              <div 
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10',
                  index === 0 ? 'bg-primary-100 text-primary-600' : 'bg-neutral-100 text-neutral-500'
                ]"
              >
                <component 
                  :is="getHistoryIcon(item.transitionId)" 
                  class="w-4 h-4" 
                />
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <div class="text-sm font-medium text-neutral-900">
                      {{ item.transition?.label || 'Создано' }}
                    </div>
                    <div class="text-xs text-neutral-500">
                      {{ item.transition?.origin_state_id ? `Состояние ${item.transition.origin_state_id} → ` : '' }}
                      <span class="font-medium">{{ item.transition?.destination_state_id ? `Состояние ${item.transition.destination_state_id}` : 'Новое состояние' }}</span>
                    </div>
                  </div>
                  <div class="text-xs text-neutral-400 whitespace-nowrap">
                    {{ formatRelativeTime(item.datetime) }}
                  </div>
                </div>

                <!-- User info -->
                <div class="mt-1 flex items-center gap-1.5">
                  <span class="text-xs text-neutral-500">
                    {{ item.user?.first_name && item.user?.last_name 
                      ? `${item.user.first_name} ${item.user.last_name}` 
                      : item.user?.username || 'Система' }}
                  </span>
                </div>

                <!-- Comment -->
                <div 
                  v-if="item.comment"
                  class="mt-2 p-2 bg-neutral-50 rounded-lg text-xs text-neutral-600 italic"
                >
                  "{{ item.comment }}"
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Transition Modal -->
    <TransitionRoot as="template" :show="showTransitionModal">
      <Dialog as="div" class="relative z-50" @close="cancelTransition">
        <TransitionChild
          as="div"
          enter="ease-out duration-200"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-150"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" />
        </TransitionChild>

        <div class="fixed inset-0 z-50 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4">
            <TransitionChild
              as="div"
              enter="ease-out duration-200"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="ease-in duration-150"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-xl bg-white shadow-2xl">
                <!-- Header -->
                <div class="px-5 pt-5 pb-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100">
                      <ArrowRightIcon class="h-5 w-5 text-primary-600" />
                    </div>
                    <DialogTitle class="text-lg font-semibold text-neutral-900">
                      {{ pendingTransition?.label }}
                    </DialogTitle>
                  </div>
                </div>

                <!-- Content -->
                <div class="px-5 pb-4">
                  <p class="text-sm text-neutral-600 mb-4">
                    Выполнить переход "{{ pendingTransition?.label }}"?
                  </p>

                  <!-- Comment field -->
                  <div>
                    <label class="block text-sm font-medium text-neutral-700 mb-1.5">
                      Комментарий (необязательно)
                    </label>
                    <textarea
                      v-model="transitionComment"
                      rows="3"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             placeholder:text-neutral-400 resize-none"
                      placeholder="Добавьте комментарий к переходу..."
                    />
                  </div>
                </div>

                <!-- Footer -->
                <div class="flex justify-end gap-2 px-5 py-4 bg-neutral-50 border-t border-neutral-100">
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-neutral-700 bg-white border border-neutral-300
                           rounded-lg hover:bg-neutral-50 transition-colors"
                    :disabled="isTransitioning"
                    @click="cancelTransition"
                  >
                    Отмена
                  </button>
                  <button
                    type="button"
                    class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700
                           rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    :disabled="isTransitioning"
                    @click="confirmTransition"
                  >
                    <span v-if="isTransitioning" class="flex items-center gap-2">
                      <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Выполнение...
                    </span>
                    <span v-else>Подтвердить</span>
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, markRaw, type Component } from 'vue'
import { 
  Dialog, 
  DialogPanel, 
  DialogTitle, 
  TransitionChild, 
  TransitionRoot 
} from '@headlessui/vue'
import {
  ArrowPathRoundedSquareIcon,
  PencilSquareIcon,
  ClockIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  GlobeAltIcon,
  ArchiveBoxIcon,
  XCircleIcon,
  PaperAirplaneIcon,
  CheckIcon,
  ArrowUturnLeftIcon,
  XMarkIcon,
  EyeSlashIcon,
  ArrowUpTrayIcon,
  ArrowRightIcon,
  DocumentPlusIcon
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notificationStore'
import { workflowService, type WorkflowInstance, type WorkflowTransition, type WorkflowLogEntry } from '@/services/workflowService'
import { apiService } from '@/services/apiService'

interface Props {
  assetId: number
  documentTypeId?: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  statusChange: [newState: { id: number; label: string }]
}>()

const notificationStore = useNotificationStore()

// State
const isLoading = ref(true)
const isTransitioning = ref(false)
const isLaunching = ref(false)
const showAllHistory = ref(false)
const showTransitionModal = ref(false)
const pendingTransition = ref<WorkflowTransition | null>(null)
const transitionComment = ref('')
const workflowInstance = ref<WorkflowInstance | null>(null)
const availableTransitions = ref<WorkflowTransition[]>([])
const historyItems = ref<WorkflowLogEntry[]>([])
const availableWorkflowTemplates = ref<Array<{ id: number; label: string }>>([])

// Icon mapping for states
const stateIconComponents: Record<string, Component> = {
  PencilSquareIcon: markRaw(PencilSquareIcon),
  ClockIcon: markRaw(ClockIcon),
  ArrowPathIcon: markRaw(ArrowPathIcon),
  CheckCircleIcon: markRaw(CheckCircleIcon),
  GlobeAltIcon: markRaw(GlobeAltIcon),
  ArchiveBoxIcon: markRaw(ArchiveBoxIcon),
  XCircleIcon: markRaw(XCircleIcon)
}

// Icon mapping for transitions
const transitionIconComponents: Record<string, Component> = {
  PaperAirplaneIcon: markRaw(PaperAirplaneIcon),
  CheckIcon: markRaw(CheckIcon),
  ArrowUturnLeftIcon: markRaw(ArrowUturnLeftIcon),
  XMarkIcon: markRaw(XMarkIcon),
  ArrowPathIcon: markRaw(ArrowPathIcon),
  GlobeAltIcon: markRaw(GlobeAltIcon),
  EyeSlashIcon: markRaw(EyeSlashIcon),
  ArchiveBoxIcon: markRaw(ArchiveBoxIcon),
  ArrowUpTrayIcon: markRaw(ArrowUpTrayIcon),
  ArrowRightIcon: markRaw(ArrowRightIcon),
  DocumentPlusIcon: markRaw(DocumentPlusIcon)
}

function getStateIcon(iconName: string): Component {
  return stateIconComponents[iconName] || stateIconComponents.CheckCircleIcon
}

function getTransitionIcon(iconName: string): Component {
  return transitionIconComponents[iconName] || transitionIconComponents.ArrowRightIcon
}

function getHistoryIcon(transitionId: number | null): Component {
  if (!transitionId) return transitionIconComponents.DocumentPlusIcon
  return transitionIconComponents.ArrowRightIcon
}

// Computed
const currentState = computed(() => {
  return workflowInstance.value?.current_state || null
})

const stateColorClasses = computed(() => {
  if (!currentState.value) {
    return { bg: 'bg-neutral-100', text: 'text-neutral-600' }
  }
  
  if (currentState.value.initial) {
    return { bg: 'bg-blue-100', text: 'text-blue-600' }
  }
  if (currentState.value.completion) {
    return { bg: 'bg-green-100', text: 'text-green-600' }
  }
  
  return { bg: 'bg-neutral-100', text: 'text-neutral-600' }
})

const displayedHistory = computed(() => {
  const reversed = [...historyItems.value].reverse()
  return showAllHistory.value ? reversed : reversed.slice(0, 3)
})

// Methods
async function loadData() {
  isLoading.value = true
  
  try {
    // Get workflow instances for this document
    const instances = await workflowService.getWorkflowInstances(props.assetId)
    
    if (instances.length === 0) {
      // No workflow instance found - load available templates if document type is provided
      workflowInstance.value = null
      availableTransitions.value = []
      historyItems.value = []
      
      if (props.documentTypeId) {
        try {
          availableWorkflowTemplates.value = await workflowService.getAvailableWorkflowTemplates(props.documentTypeId)
        } catch (err) {
          console.warn('[WorkflowWidget] Failed to load available workflow templates:', err)
        }
      }
      
      isLoading.value = false
      return
    }
    
    // Use the first workflow instance (or could allow selecting which one)
    const instance = instances[0]
    
    // Clear cache for transitions to ensure we get fresh data
    apiService.clearCache(`/api/v4/documents/${props.assetId}/workflow_instances/${instance.id}/log_entries/transitions/`)
    
    workflowInstance.value = await workflowService.getWorkflowInstance(props.assetId, instance.id)
    
    // Load available transitions
    availableTransitions.value = await workflowService.getAvailableTransitions(props.assetId, instance.id)
    
    // Load history
    historyItems.value = await workflowService.getWorkflowHistory(props.assetId, instance.id)
  } catch (error: any) {
    console.error('[WorkflowWidget] Failed to load workflow data:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка загрузки',
      message: error.message || 'Не удалось загрузить данные workflow'
    })
  } finally {
    isLoading.value = false
  }
}

async function launchWorkflow() {
  if (availableWorkflowTemplates.value.length === 0) return
  
  isLaunching.value = true
  
  try {
    const templateId = availableWorkflowTemplates.value[0].id
    const templateLabel = availableWorkflowTemplates.value[0].label
    
    await workflowService.launchWorkflow(
      props.assetId,
      templateId
    )
    
    // Clear cache for workflow instances to force fresh fetch
    apiService.clearCache(`/api/v4/documents/${props.assetId}/workflow_instances/`)
    
    // Wait a bit for server to process the launch request
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Reload data (this will fetch fresh workflow instances)
    await loadData()
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Согласование запущено',
      message: `Согласование "${templateLabel}" успешно запущено`
    })
  } catch (error: any) {
    console.error('[WorkflowWidget] Failed to launch workflow:', error)
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: error.message || 'Не удалось запустить согласование'
    })
  } finally {
    isLaunching.value = false
  }
}


function formatRelativeTime(dateString: string | undefined): string {
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
  
  return date.toLocaleDateString('ru-RU', { 
    day: 'numeric', 
    month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

function initiateTransition(transition: WorkflowTransition) {
  pendingTransition.value = transition
  transitionComment.value = ''
  showTransitionModal.value = true
}

function cancelTransition() {
  showTransitionModal.value = false
  pendingTransition.value = null
  transitionComment.value = ''
}

async function confirmTransition() {
  if (!pendingTransition.value || !workflowInstance.value) return
  
  isTransitioning.value = true
  
  try {
    await workflowService.executeTransition(
      props.assetId,
      workflowInstance.value.id,
      pendingTransition.value.id,
      transitionComment.value || undefined
    )
    
    notificationStore.addNotification({
      type: 'success',
      title: 'Статус обновлён',
      message: `Переход "${pendingTransition.value.label}" выполнен успешно`
    })
    
    // Clear cache before reloading
    apiService.clearCache(`/api/v4/documents/${props.assetId}/workflow_instances/`)
    apiService.clearCache(`/api/v4/documents/${props.assetId}/workflow_instances/${workflowInstance.value.id}/`)
    
    // Reload data
    await loadData()
    
    // Emit event with new state
    if (workflowInstance.value?.current_state) {
      emit('statusChange', {
        id: workflowInstance.value.current_state.id,
        label: workflowInstance.value.current_state.label
      })
    }
    
    // Close modal after successful transition
    showTransitionModal.value = false
    pendingTransition.value = null
    transitionComment.value = ''
  } catch (error: any) {
    console.error('[WorkflowWidget] Failed to execute transition:', error)
    const errorMessage = error.response?.data?.detail || error.response?.data?.non_field_errors?.[0] || error.message || 'Не удалось выполнить переход'
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: errorMessage
    })
  } finally {
    isTransitioning.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})

// Watch for asset changes
watch(() => props.assetId, () => {
  loadData()
})
</script>

