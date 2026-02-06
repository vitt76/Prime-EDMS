<template>
  <TransitionRoot :show="show" as="template">
    <Dialog @close="emit('close')">
      <TransitionChild
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/30 backdrop-blur-sm" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
              <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-success/10">
                <CheckCircleIcon class="h-10 w-10 animate-scale-in text-success" />
              </div>

              <DialogTitle class="mt-6 text-center text-2xl font-bold text-neutral-900">
                Подписка оформлена!
              </DialogTitle>

              <p class="mt-3 text-center text-neutral-600">
                Проверьте вашу почту {{ email }} для подтверждения подписки.
              </p>

              <ul class="mt-6 space-y-3">
                <li class="flex items-center gap-3 text-sm text-neutral-700">
                  <CheckIcon class="h-5 w-5 flex-shrink-0 text-success" />
                  Эксклюзивные новости продукта
                </li>
                <li class="flex items-center gap-3 text-sm text-neutral-700">
                  <CheckIcon class="h-5 w-5 flex-shrink-0 text-success" />
                  Обучающие материалы и гайды
                </li>
                <li class="flex items-center gap-3 text-sm text-neutral-700">
                  <CheckIcon class="h-5 w-5 flex-shrink-0 text-success" />
                  Специальные предложения
                </li>
              </ul>

              <button
                @click="emit('close')"
                class="mt-8 w-full rounded-xl bg-primary-600 py-3 font-semibold text-white transition hover:bg-primary-700"
              >
                Отлично, спасибо!
              </button>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { CheckCircleIcon, CheckIcon } from '@heroicons/vue/24/outline'

defineProps<{
  show: boolean
  email: string
}>()

const emit = defineEmits(['close'])
</script>
