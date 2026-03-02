<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" class="relative z-50" @close="handleClose">
      <TransitionChild
        as="div"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="div"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel
              class="w-full max-w-md transform overflow-hidden rounded-2xl
                     bg-white dark:bg-neutral-800 shadow-2xl transition-all"
            >
              <div class="flex items-center justify-between p-5 border-b border-neutral-200 dark:border-neutral-700">
                <div class="flex items-center gap-3">
                  <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-primary-100 dark:bg-primary-900/30">
                    <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                  </div>
                  <div>
                    <DialogTitle class="text-lg font-semibold text-neutral-900 dark:text-white">
                      Поделиться подборкой
                    </DialogTitle>
                    <p class="text-sm text-neutral-500 dark:text-neutral-400">
                      {{ cabinetLabel || 'Подборка' }}
                    </p>
                  </div>
                </div>
                <button
                  class="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700
                         text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300
                         transition-colors"
                  @click="handleClose"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div class="p-5 space-y-4">
                <p class="text-sm text-neutral-600 dark:text-neutral-400">
                  Выберите пользователей организации для доступа к подборке.
                </p>

                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Поиск по имени или логину..."
                  class="w-full px-4 py-2 rounded-xl border border-neutral-300 dark:border-neutral-600
                         bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white
                         focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />

                <div class="max-h-64 overflow-y-auto space-y-2 border border-neutral-200 dark:border-neutral-700 rounded-xl p-2">
                  <label
                    v-for="user in filteredMembers"
                    :key="user.id"
                    class="flex items-center gap-3 p-2 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-700/50 cursor-pointer"
                  >
                    <input
                      v-model="selectedUserIds"
                      type="checkbox"
                      :value="user.id"
                      class="rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
                    />
                    <span class="text-sm font-medium text-neutral-900 dark:text-white">
                      {{ displayName(user) }}
                    </span>
                    <span class="text-xs text-neutral-500 dark:text-neutral-400">
                      {{ user.username }}
                    </span>
                  </label>
                  <p v-if="filteredMembers.length === 0" class="text-sm text-neutral-500 dark:text-neutral-400 p-2">
                    Нет пользователей для отображения
                  </p>
                </div>

                <p v-if="shareError" class="text-sm text-red-600 dark:text-red-400">
                  {{ shareError }}
                </p>
              </div>

              <div class="flex gap-2 justify-end p-5 border-t border-neutral-200 dark:border-neutral-700">
                <button
                  type="button"
                  class="px-4 py-2 rounded-xl border border-neutral-300 dark:border-neutral-600
                         text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700
                         transition-colors"
                  @click="handleClose"
                >
                  Отмена
                </button>
                <button
                  type="button"
                  class="px-4 py-2 rounded-xl bg-primary-600 text-white hover:bg-primary-700
                         disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  :disabled="selectedUserIds.length === 0 || isSubmitting"
                  @click="handleShare"
                >
                  {{ isSubmitting ? 'Отправка...' : 'Поделиться' }}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { cabinetService } from '@/services/cabinetService'

interface OrgMember {
  id: number
  username: string
  first_name: string
  last_name: string
}

const props = withDefaults(
  defineProps<{
    isOpen: boolean
    cabinetId: number | null
    cabinetLabel?: string
  }>(),
  { cabinetLabel: '' }
)

const emit = defineEmits<{
  close: []
  success: []
}>()

const searchQuery = ref('')
const members = ref<OrgMember[]>([])
const selectedUserIds = ref<number[]>([])
const isSubmitting = ref(false)
const shareError = ref('')

const filteredMembers = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return members.value
  return members.value.filter(
    (u) =>
      u.username.toLowerCase().includes(q) ||
      (u.first_name + ' ' + u.last_name).toLowerCase().includes(q)
  )
})

function displayName(u: OrgMember): string {
  const name = [u.first_name, u.last_name].filter(Boolean).join(' ').trim()
  return name || u.username
}

async function loadOrgMembers(): Promise<void> {
  if (!props.isOpen || !props.cabinetId) return
  try {
    members.value = await cabinetService.getOrgMembers()
  } catch {
    members.value = []
  }
}

function handleClose(): void {
  shareError.value = ''
  selectedUserIds.value = []
  emit('close')
}

async function handleShare(): void {
  if (!props.cabinetId || selectedUserIds.value.length === 0) return
  shareError.value = ''
  isSubmitting.value = true
  try {
    const res = await cabinetService.shareCabinetWithUsers(props.cabinetId, selectedUserIds.value)
    if (res.errors?.length) {
      shareError.value = res.errors.map((e) => `User ${e.user_id}: ${e.error}`).join('; ')
    } else {
      handleClose()
      emit('success')
    }
  } catch (e) {
    shareError.value = e instanceof Error ? e.message : 'Ошибка при отправке'
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => [props.isOpen, props.cabinetId],
  () => {
    if (props.isOpen && props.cabinetId) {
      loadOrgMembers()
      selectedUserIds.value = []
      shareError.value = ''
    }
  },
  { immediate: true }
)
</script>
