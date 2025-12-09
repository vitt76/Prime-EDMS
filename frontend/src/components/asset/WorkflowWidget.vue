<template>
  <div class="workflow-widget bg-white rounded-xl border border-neutral-200 overflow-hidden">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-neutral-100 bg-neutral-50">
      <h3 class="text-sm font-semibold text-neutral-900 flex items-center gap-2">
        <ArrowPathRoundedSquareIcon class="w-4 h-4 text-neutral-500" />
        Статус и согласование
      </h3>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="p-4 flex items-center justify-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
    </div>

    <template v-else>
      <!-- Current Status -->
      <div class="p-4 border-b border-neutral-100">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-medium text-neutral-500 uppercase tracking-wide">
            Текущий статус
          </span>
          <span class="text-xs text-neutral-400">
            {{ formatRelativeTime(workflowState?.enteredAt) }}
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
              :is="getStateIcon(currentState.icon)" 
              :class="['w-5 h-5', stateColorClasses.text]" 
            />
          </div>
          <div>
            <div :class="['font-semibold', stateColorClasses.text]">
              {{ currentState.label }}
            </div>
            <div class="text-xs text-neutral-500">
              {{ currentState.description }}
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
            :class="[
              'inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg',
              'transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
              getTransitionButtonClasses(transition.color)
            ]"
            :disabled="isTransitioning"
            @click="initiateTransition(transition)"
          >
            <component :is="getTransitionIcon(transition.icon)" class="w-4 h-4" />
            {{ transition.label }}
          </button>
        </div>
      </div>

      <!-- Workflow History -->
      <div class="p-4">
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
                      {{ getTransitionLabel(item.transitionId) || 'Создано' }}
                    </div>
                    <div class="text-xs text-neutral-500">
                      {{ item.fromState ? `${getStateLabel(item.fromState)} → ` : '' }}
                      <span class="font-medium">{{ getStateLabel(item.toState) }}</span>
                    </div>
                  </div>
                  <div class="text-xs text-neutral-400 whitespace-nowrap">
                    {{ formatRelativeTime(item.performedAt) }}
                  </div>
                </div>

                <!-- User info -->
                <div class="mt-1 flex items-center gap-1.5">
                  <img 
                    v-if="item.performedBy.avatar"
                    :src="item.performedBy.avatar" 
                    :alt="item.performedBy.name"
                    class="w-4 h-4 rounded-full"
                  />
                  <span class="text-xs text-neutral-500">
                    {{ item.performedBy.name }}
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
                    <div 
                      :class="[
                        'flex h-10 w-10 items-center justify-center rounded-full',
                        pendingTransition?.color === 'danger' ? 'bg-red-100' :
                        pendingTransition?.color === 'warning' ? 'bg-amber-100' :
                        pendingTransition?.color === 'success' ? 'bg-green-100' :
                        'bg-primary-100'
                      ]"
                    >
                      <component 
                        :is="getTransitionIcon(pendingTransition?.icon || 'ArrowRightIcon')" 
                        :class="[
                          'h-5 w-5',
                          pendingTransition?.color === 'danger' ? 'text-red-600' :
                          pendingTransition?.color === 'warning' ? 'text-amber-600' :
                          pendingTransition?.color === 'success' ? 'text-green-600' :
                          'text-primary-600'
                        ]"
                      />
                    </div>
                    <DialogTitle class="text-lg font-semibold text-neutral-900">
                      {{ pendingTransition?.label }}
                    </DialogTitle>
                  </div>
                </div>

                <!-- Content -->
                <div class="px-5 pb-4">
                  <p class="text-sm text-neutral-600 mb-4">
                    {{ pendingTransition?.confirmationMessage || pendingTransition?.description }}
                  </p>

                  <!-- Comment field -->
                  <div v-if="pendingTransition?.requiresComment">
                    <label class="block text-sm font-medium text-neutral-700 mb-1.5">
                      Комментарий <span class="text-red-500">*</span>
                    </label>
                    <textarea
                      v-model="transitionComment"
                      rows="3"
                      class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm
                             focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                             placeholder:text-neutral-400 resize-none"
                      placeholder="Укажите причину..."
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
                    :class="[
                      'px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors',
                      'disabled:opacity-50 disabled:cursor-not-allowed',
                      pendingTransition?.color === 'danger' ? 'bg-red-600 hover:bg-red-700' :
                      pendingTransition?.color === 'warning' ? 'bg-amber-600 hover:bg-amber-700' :
                      pendingTransition?.color === 'success' ? 'bg-green-600 hover:bg-green-700' :
                      'bg-primary-600 hover:bg-primary-700'
                    ]"
                    :disabled="isTransitioning || (pendingTransition?.requiresComment && !transitionComment.trim())"
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
import {
  getDefaultWorkflow,
  getAssetWorkflowState,
  getCurrentState,
  getAvailableTransitions,
  executeTransition,
  getWorkflowHistory,
  getStateLabel as getStateLabelFn,
  getTransitionLabel as getTransitionLabelFn,
  type WorkflowState,
  type WorkflowTransition,
  type WorkflowHistoryEntry,
  type AssetWorkflowState
} from '@/mocks/workflows'

interface Props {
  assetId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  statusChange: [newState: WorkflowState]
}>()

const notificationStore = useNotificationStore()

// State
const isLoading = ref(true)
const isTransitioning = ref(false)
const showAllHistory = ref(false)
const showTransitionModal = ref(false)
const pendingTransition = ref<WorkflowTransition | null>(null)
const transitionComment = ref('')
const workflowState = ref<AssetWorkflowState | null>(null)
const currentState = ref<WorkflowState | null>(null)
const availableTransitions = ref<WorkflowTransition[]>([])
const historyItems = ref<WorkflowHistoryEntry[]>([])

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

function getHistoryIcon(transitionId: string | null): Component {
  if (!transitionId) return transitionIconComponents.DocumentPlusIcon
  
  const workflow = getDefaultWorkflow()
  const transition = workflow.transitions.find(t => t.id === transitionId)
  if (!transition) return transitionIconComponents.ArrowRightIcon
  
  return getTransitionIcon(transition.icon)
}

// Computed
const stateColorClasses = computed(() => {
  const colorMap: Record<string, { bg: string; text: string }> = {
    gray: { bg: 'bg-neutral-100', text: 'text-neutral-600' },
    amber: { bg: 'bg-amber-100', text: 'text-amber-600' },
    orange: { bg: 'bg-orange-100', text: 'text-orange-600' },
    green: { bg: 'bg-green-100', text: 'text-green-600' },
    blue: { bg: 'bg-blue-100', text: 'text-blue-600' },
    slate: { bg: 'bg-slate-100', text: 'text-slate-600' },
    red: { bg: 'bg-red-100', text: 'text-red-600' }
  }
  return colorMap[currentState.value?.color || 'gray'] || colorMap.gray
})

const displayedHistory = computed(() => {
  const reversed = [...historyItems.value].reverse()
  return showAllHistory.value ? reversed : reversed.slice(0, 3)
})

// Methods
function loadData() {
  isLoading.value = true
  
  setTimeout(() => {
    workflowState.value = getAssetWorkflowState(props.assetId) || null
    currentState.value = getCurrentState(props.assetId) || null
    availableTransitions.value = getAvailableTransitions(props.assetId)
    historyItems.value = getWorkflowHistory(props.assetId)
    
    isLoading.value = false
  }, 200)
}

function getStateLabel(stateId: string): string {
  return getStateLabelFn(stateId)
}

function getTransitionLabel(transitionId: string | null): string {
  if (!transitionId) return ''
  return getTransitionLabelFn(transitionId)
}

function getTransitionButtonClasses(color: string): string {
  const classes: Record<string, string> = {
    primary: 'bg-primary-100 text-primary-700 hover:bg-primary-200 focus:ring-primary-500',
    success: 'bg-green-100 text-green-700 hover:bg-green-200 focus:ring-green-500',
    warning: 'bg-amber-100 text-amber-700 hover:bg-amber-200 focus:ring-amber-500',
    danger: 'bg-red-100 text-red-700 hover:bg-red-200 focus:ring-red-500',
    neutral: 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200 focus:ring-neutral-500'
  }
  return classes[color] || classes.neutral
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
  if (!pendingTransition.value) return
  
  isTransitioning.value = true
  
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const result = executeTransition(
      props.assetId,
      pendingTransition.value.id,
      transitionComment.value || null,
      { id: 1, name: 'Текущий пользователь' }
    )
    
    if (result.success) {
      notificationStore.addNotification({
        type: 'success',
        title: 'Статус обновлён',
        message: `Актив переведён в статус "${result.newState?.label}"`
      })
      
      // Reload data
      loadData()
      
      // Emit event
      if (result.newState) {
        emit('statusChange', result.newState)
      }
      
      showTransitionModal.value = false
      pendingTransition.value = null
      transitionComment.value = ''
    } else {
      notificationStore.addNotification({
        type: 'error',
        title: 'Ошибка',
        message: result.error || 'Не удалось выполнить переход'
      })
    }
  } catch (error) {
    notificationStore.addNotification({
      type: 'error',
      title: 'Ошибка',
      message: 'Произошла ошибка при выполнении действия'
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

