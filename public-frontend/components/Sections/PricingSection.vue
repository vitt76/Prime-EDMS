<template>
  <section id="pricing" class="mx-auto max-w-container px-4 py-20 lg:py-28">
    <!-- Header -->
    <div class="mx-auto max-w-2xl text-center">
      <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700">
        <CurrencyDollarIcon class="h-4 w-4" />
        <span>Тарифы</span>
      </div>
      <h2 class="mt-4 text-3xl font-bold tracking-tight text-neutral-900 md:text-4xl">
        Выберите подходящий план
      </h2>
      <p class="mt-4 text-lg leading-relaxed text-neutral-600">
        Начните бесплатно. Масштабируйтесь по мере роста вашего бизнеса.
      </p>
    </div>

    <!-- Billing Toggle -->
    <div class="mt-10 flex items-center justify-center gap-4">
      <span 
        class="text-sm font-medium"
        :class="billingPeriod === 'monthly' ? 'text-neutral-900' : 'text-neutral-500'"
      >
        Помесячно
      </span>
      <button
        @click="billingPeriod = billingPeriod === 'monthly' ? 'yearly' : 'monthly'"
        class="relative h-6 w-11 rounded-full transition-colors"
        :class="billingPeriod === 'yearly' ? 'bg-primary-600' : 'bg-neutral-300'"
        role="switch"
        :aria-checked="billingPeriod === 'yearly'"
        aria-label="Toggle billing period"
      >
        <span 
          class="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform"
          :class="billingPeriod === 'yearly' ? 'translate-x-5' : 'translate-x-0'"
        ></span>
      </button>
      <span 
        class="flex items-center gap-2 text-sm font-medium"
        :class="billingPeriod === 'yearly' ? 'text-neutral-900' : 'text-neutral-500'"
      >
        Ежегодно
        <span class="rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
          -20%
        </span>
      </span>
    </div>

    <!-- Type Toggle (SaaS / Standalone) -->
    <div class="mt-6 flex items-center justify-center">
      <div class="inline-flex rounded-lg bg-neutral-100 p-1">
        <button
          v-for="type in deploymentTypes"
          :key="type.id"
          @click="deploymentType = type.id"
          class="rounded-md px-4 py-2 text-sm font-medium transition"
          :class="deploymentType === type.id 
            ? 'bg-white text-neutral-900 shadow-sm' 
            : 'text-neutral-600 hover:text-neutral-900'"
        >
          {{ type.label }}
        </button>
      </div>
    </div>

    <!-- Plans Grid -->
    <div class="mt-12 grid gap-8 lg:grid-cols-3">
      <div 
        v-for="plan in displayPlans" 
        :key="plan.id"
        class="relative flex flex-col rounded-2xl p-8 transition-all duration-300"
        :class="plan.recommended 
          ? 'bg-primary-600 text-white shadow-2xl shadow-primary-600/20 ring-4 ring-primary-600 scale-105 z-10' 
          : 'bg-white shadow-sm ring-1 ring-neutral-200 hover:shadow-lg'"
      >
        <!-- Recommended Badge -->
        <div 
          v-if="plan.recommended" 
          class="absolute -top-3 left-1/2 -translate-x-1/2"
        >
          <span class="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1 text-xs font-semibold text-primary-600 shadow-lg">
            <SparklesIcon class="h-3.5 w-3.5" />
            Популярный
          </span>
        </div>

        <!-- Plan Name -->
        <h3 
          class="text-xl font-bold"
          :class="plan.recommended ? 'text-white' : 'text-neutral-900'"
        >
          {{ plan.name }}
        </h3>
        <p 
          class="mt-2 text-sm"
          :class="plan.recommended ? 'text-primary-100' : 'text-neutral-600'"
        >
          {{ plan.description }}
        </p>

        <!-- Price -->
        <div class="mt-6">
          <div class="flex items-baseline gap-1">
            <span 
              v-if="getPrice(plan) !== null"
              class="text-4xl font-bold tracking-tight"
              :class="plan.recommended ? 'text-white' : 'text-neutral-900'"
            >
              ${{ getPrice(plan) }}
            </span>
            <span 
              v-else
              class="text-2xl font-bold"
              :class="plan.recommended ? 'text-white' : 'text-neutral-900'"
            >
              Индивидуально
            </span>
            <span 
              v-if="getPrice(plan) !== null"
              class="text-sm"
              :class="plan.recommended ? 'text-primary-200' : 'text-neutral-500'"
            >
              /{{ billingPeriod === 'monthly' ? 'мес' : 'год' }}
            </span>
          </div>
          <p 
            v-if="billingPeriod === 'yearly' && plan.price_monthly"
            class="mt-1 text-sm"
            :class="plan.recommended ? 'text-primary-200' : 'text-neutral-500'"
          >
            ${{ plan.price_monthly }}/мес при помесячной оплате
          </p>
        </div>

        <!-- Features -->
        <ul class="mt-8 flex-1 space-y-4">
          <li 
            v-for="feature in plan.features" 
            :key="feature"
            class="flex items-start gap-3 text-sm"
          >
            <CheckIcon 
              class="h-5 w-5 flex-shrink-0"
              :class="plan.recommended ? 'text-primary-200' : 'text-primary-600'"
            />
            <span :class="plan.recommended ? 'text-primary-50' : 'text-neutral-600'">
              {{ feature }}
            </span>
          </li>
        </ul>

        <!-- CTA -->
        <NuxtLink 
          :to="plan.cta_url || '/auth/register'"
          class="mt-8 flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold transition"
          :class="plan.recommended 
            ? 'bg-white text-primary-600 hover:bg-primary-50' 
            : 'bg-primary-600 text-white hover:bg-primary-700'"
        >
          {{ plan.cta_text || 'Начать' }}
          <ArrowRightIcon class="h-4 w-4" />
        </NuxtLink>
      </div>
    </div>

    <!-- Compare Link -->
    <div class="mt-12 text-center">
      <NuxtLink 
        to="/pricing" 
        class="inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        Сравнить все возможности
        <ArrowRightIcon class="h-4 w-4" />
      </NuxtLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { PublicPlan } from '~/types/content'
import { 
  CheckIcon, 
  ArrowRightIcon, 
  SparklesIcon,
  CurrencyDollarIcon
} from '@heroicons/vue/24/outline'

const props = withDefaults(
  defineProps<{
    plans?: PublicPlan[]
  }>(),
  {
    plans: () => []
  }
)

const billingPeriod = ref<'monthly' | 'yearly'>('monthly')
const deploymentType = ref<'saas' | 'standalone'>('saas')

const deploymentTypes = [
  { id: 'saas' as const, label: 'SaaS (Облако)' },
  { id: 'standalone' as const, label: 'On-Premise' }
]

// Default plans if not provided
const defaultPlans: PublicPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    description: 'Для небольших команд и стартапов',
    price_monthly: 29,
    price_yearly: 278,
    currency: 'USD',
    features: [
      '5 пользователей',
      '10 ГБ хранилища',
      'Базовый AI-поиск',
      'Email поддержка',
      'API доступ'
    ],
    recommended: false,
    type: 'saas',
    cta_text: 'Начать бесплатно'
  },
  {
    id: 'pro',
    name: 'Professional',
    description: 'Для растущих компаний',
    price_monthly: 99,
    price_yearly: 950,
    currency: 'USD',
    features: [
      '25 пользователей',
      '100 ГБ хранилища',
      'Продвинутый AI-поиск',
      'Приоритетная поддержка',
      'API доступ + Webhooks',
      'Брендирование',
      'SSO интеграция'
    ],
    recommended: true,
    type: 'saas',
    cta_text: 'Начать Pro'
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    description: 'Для крупных организаций',
    price_monthly: null,
    price_yearly: null,
    currency: 'USD',
    features: [
      'Неограниченно пользователей',
      'Неограниченно хранилища',
      'Кастомный AI-поиск',
      'Выделенная поддержка 24/7',
      'Полный API доступ',
      'White-label решение',
      'On-premise развертывание',
      'SLA 99.99%'
    ],
    recommended: false,
    type: 'standalone',
    cta_text: 'Связаться с нами'
  }
]

const displayPlans = computed(() => {
  const plans = props.plans.length ? props.plans : defaultPlans
  return plans.filter(plan => {
    if (deploymentType.value === 'standalone') {
      return plan.type === 'standalone' || plan.id === 'enterprise'
    }
    return plan.type === 'saas' || !plan.type
  })
})

const getPrice = (plan: PublicPlan) => {
  if (billingPeriod.value === 'yearly' && plan.price_yearly) {
    return plan.price_yearly
  }
  return plan.price_monthly
}
</script>
