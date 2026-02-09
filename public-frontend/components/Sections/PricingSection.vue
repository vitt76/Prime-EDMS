<template>
  <section id="pricing" class="mx-auto max-w-container px-4 py-20 lg:py-28">
    <!-- Header -->
    <div class="mx-auto max-w-2xl text-center">
      <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700">
        <CurrencyDollarIcon class="h-4 w-4" />
        <span>{{ $t('pricing.badge') }}</span>
      </div>
      <h2 class="mt-4 text-3xl font-bold tracking-tight text-neutral-900 md:text-4xl">
        {{ $t('pricing.title') }}
      </h2>
      <p class="mt-4 text-lg leading-relaxed text-neutral-600">
        {{ $t('pricing.subtitle') }}
      </p>
    </div>

    <!-- Billing Toggle -->
    <div class="mt-10 flex items-center justify-center gap-4">
      <span 
        class="text-sm font-medium"
        :class="billingPeriod === 'monthly' ? 'text-neutral-900 dark:text-white' : 'text-neutral-500 dark:text-neutral-400'"
      >
        {{ $t('pricing.monthly') }}
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
        :class="billingPeriod === 'yearly' ? 'text-neutral-900 dark:text-white' : 'text-neutral-500 dark:text-neutral-400'"
      >
        {{ $t('pricing.yearly') }}
        <span class="rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
          {{ $t('pricing.discount') }}
        </span>
      </span>
    </div>

    <!-- Type Toggle (SaaS / Standalone) -->
    <div class="mt-6 flex items-center justify-center">
      <div class="inline-flex rounded-lg bg-neutral-100 p-1 dark:bg-neutral-800">
        <button
          v-for="type in deploymentTypes"
          :key="type.id"
          @click="deploymentType = type.id"
          class="rounded-md px-4 py-2 text-sm font-medium transition"
          :class="deploymentType === type.id 
            ? 'bg-white text-neutral-900 shadow-sm dark:bg-neutral-700 dark:text-white' 
            : 'text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-white'"
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
          : 'bg-white shadow-sm ring-1 ring-neutral-200 hover:shadow-lg dark:bg-neutral-800 dark:ring-neutral-700'"
      >
        <!-- Recommended Badge -->
        <div 
          v-if="plan.recommended" 
          class="absolute -top-3 left-1/2 -translate-x-1/2"
        >
          <span class="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1 text-xs font-semibold text-primary-600 shadow-lg">
            <SparklesIcon class="h-3.5 w-3.5" />
            {{ $t('pricing.popular') }}
          </span>
        </div>

        <!-- Plan Name -->
        <h3 
          class="text-xl font-bold"
          :class="plan.recommended ? 'text-white' : 'text-neutral-900 dark:text-white'"
        >
          {{ plan.name }}
        </h3>
        <p 
          class="mt-2 text-sm"
          :class="plan.recommended ? 'text-primary-100' : 'text-neutral-600 dark:text-neutral-400'"
        >
          {{ plan.description }}
        </p>

        <!-- Price -->
        <div class="mt-6">
          <div class="flex items-baseline gap-1">
            <span 
              v-if="getPrice(plan) !== null"
              class="text-4xl font-bold tracking-tight"
              :class="plan.recommended ? 'text-white' : 'text-neutral-900 dark:text-white'"
            >
              ${{ getPrice(plan) }}
            </span>
            <span 
              v-else
              class="text-2xl font-bold"
              :class="plan.recommended ? 'text-white' : 'text-neutral-900 dark:text-white'"
            >
              {{ $t('pricing.custom') }}
            </span>
            <span 
              v-if="getPrice(plan) !== null"
              class="text-sm"
              :class="plan.recommended ? 'text-primary-200' : 'text-neutral-500'"
            >
              {{ billingPeriod === 'monthly' ? $t('pricing.perMonth') : $t('pricing.perYear') }}
            </span>
          </div>
          <p 
            v-if="billingPeriod === 'yearly' && plan.price_monthly"
            class="mt-1 text-sm"
            :class="plan.recommended ? 'text-primary-200' : 'text-neutral-500'"
          >
            ${{ $t('pricing.monthlyBilling', { price: plan.price_monthly }) }}
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
          {{ plan.cta_text || $t('cta.getStarted') }}
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
        {{ $t('pricing.compareFeatures') }}
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

const { t } = useI18n()

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

const deploymentTypes = computed(() => [
  { id: 'saas' as const, label: t('pricing.saas') },
  { id: 'standalone' as const, label: t('pricing.onPremise') }
])

// Default plans using i18n
const defaultPlans = computed<PublicPlan[]>(() => [
  {
    id: 'starter',
    name: 'Starter',
    description: t('pricing.starterDesc'),
    price_monthly: 29,
    price_yearly: 278,
    currency: 'USD',
    features: [
      t('pricing.users5'),
      t('pricing.storage10'),
      t('pricing.basicAiSearch'),
      t('pricing.emailSupport'),
      t('pricing.apiAccess')
    ],
    recommended: false,
    type: 'saas',
    cta_text: t('pricing.startFree')
  },
  {
    id: 'pro',
    name: 'Professional',
    description: t('pricing.proDesc'),
    price_monthly: 99,
    price_yearly: 950,
    currency: 'USD',
    features: [
      t('pricing.users25'),
      t('pricing.storage100'),
      t('pricing.advancedAiSearch'),
      t('pricing.prioritySupport'),
      t('pricing.apiWebhooks'),
      t('pricing.branding'),
      t('pricing.ssoIntegration')
    ],
    recommended: true,
    type: 'saas',
    cta_text: t('pricing.startPro')
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    description: t('pricing.enterpriseDesc'),
    price_monthly: null,
    price_yearly: null,
    currency: 'USD',
    features: [
      t('pricing.unlimitedUsers'),
      t('pricing.unlimitedStorage'),
      t('pricing.customAiSearch'),
      t('pricing.dedicatedSupport'),
      t('pricing.fullApiAccess'),
      t('pricing.whiteLabel'),
      t('pricing.onPremiseDeploy'),
      t('pricing.sla9999')
    ],
    recommended: false,
    type: 'standalone',
    cta_text: t('cta.contact')
  }
])

const displayPlans = computed(() => {
  const plans = props.plans.length ? props.plans : defaultPlans.value
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
