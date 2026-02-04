<template>
  <section class="bg-gradient-to-br from-primary-50 via-white to-neutral-50 py-16 lg:py-20">
    <div class="mx-auto max-w-3xl px-4">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-neutral-900">Рассчитайте свою цену</h2>
        <p class="mt-2 text-neutral-600">Настройте параметры под ваши потребности</p>
      </div>

      <div class="mt-10 rounded-2xl bg-white p-8 shadow-lg ring-1 ring-neutral-200">
        <div class="space-y-8">
          <div>
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-neutral-700">Количество пользователей</label>
              <span class="text-2xl font-bold text-primary-600">{{ users }}</span>
            </div>
            <input
              v-model.number="users"
              type="range"
              min="1"
              max="100"
              step="1"
              class="mt-3 w-full accent-primary-600"
            />
            <div class="mt-1 flex justify-between text-xs text-neutral-500">
              <span>1</span>
              <span>100</span>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-neutral-700">Хранилище (ГБ)</label>
              <span class="text-2xl font-bold text-primary-600">{{ storage }}</span>
            </div>
            <input
              v-model.number="storage"
              type="range"
              min="10"
              max="1000"
              step="10"
              class="mt-3 w-full accent-primary-600"
            />
            <div class="mt-1 flex justify-between text-xs text-neutral-500">
              <span>10 ГБ</span>
              <span>1000 ГБ</span>
            </div>
          </div>

          <label class="flex items-center justify-between">
            <span class="text-sm font-medium text-neutral-700">Продвинутый AI-поиск</span>
            <input
              v-model="aiFeatures"
              type="checkbox"
              class="h-5 w-5 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
          </label>
        </div>

        <div class="mt-8 border-t border-neutral-200 pt-8">
          <div class="flex flex-col items-start gap-6 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div class="text-sm text-neutral-600">Итого в месяц</div>
              <div class="mt-1 flex items-baseline gap-2">
                <span class="text-4xl font-bold text-neutral-900">{{ calculatedPrice }}</span>
                <span class="text-xl text-neutral-500">/мес</span>
              </div>
              <div class="mt-1 text-sm text-neutral-500">
                или {{ yearlyPrice }} при оплате за год <span class="text-success">(-20%)</span>
              </div>
            </div>
            <NuxtLink
              to="/auth/register"
              class="rounded-xl bg-primary-600 px-6 py-3 font-semibold text-white shadow-lg transition hover:bg-primary-700"
            >
              Начать пробный период
            </NuxtLink>
          </div>
        </div>

        <div v-if="recommendedPlan" class="mt-6 rounded-lg bg-primary-50 p-4">
          <div class="flex items-center gap-2">
            <SparklesIcon class="h-5 w-5 text-primary-600" />
            <span class="text-sm font-medium text-primary-900">
              Мы рекомендуем план "{{ recommendedPlan }}"
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { SparklesIcon } from '@heroicons/vue/24/outline'

const users = ref(5)
const storage = ref(50)
const aiFeatures = ref(false)

const calculatedPrice = computed(() => {
  let basePrice = 0

  if (users.value <= 5) basePrice = 29
  else if (users.value <= 25) basePrice = 99
  else basePrice = 299

  const baseStorage = users.value <= 5 ? 10 : users.value <= 25 ? 100 : 500
  const extraStorage = Math.max(0, storage.value - baseStorage)
  const storagePrice = Math.ceil(extraStorage / 10) * 2

  const aiPrice = aiFeatures.value ? 30 : 0

  return `$${basePrice + storagePrice + aiPrice}`
})

const yearlyPrice = computed(() => {
  const monthly = parseInt(calculatedPrice.value.replace('$', ''), 10)
  const yearly = Math.round(monthly * 12 * 0.8)
  return `$${yearly}/год`
})

const recommendedPlan = computed(() => {
  if (users.value <= 5 && storage.value <= 50) return 'Starter'
  if (users.value <= 25) return 'Professional'
  return 'Enterprise'
})
</script>
