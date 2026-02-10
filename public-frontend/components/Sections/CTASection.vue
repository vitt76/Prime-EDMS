<template>
  <section class="relative overflow-hidden bg-gradient-to-br from-primary-600 to-primary-700 py-16 lg:py-20">
    <!-- Background Pattern -->
    <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
    
    <!-- Decorative Elements -->
    <div class="absolute -left-20 -top-20 h-60 w-60 rounded-full bg-white/10 blur-3xl"></div>
    <div class="absolute -bottom-20 -right-20 h-60 w-60 rounded-full bg-white/10 blur-3xl"></div>
    
    <div class="relative mx-auto max-w-container px-4">
      <div class="flex flex-col items-center gap-8 text-center md:flex-row md:justify-between md:text-left">
        <!-- Content -->
        <div class="max-w-xl">
          <h2 class="text-3xl font-bold text-white md:text-4xl">
            {{ title }}
          </h2>
          <p class="mt-4 text-lg text-primary-100">
            {{ subtitle }}
          </p>
          
          <!-- Stats/Trust Badges -->
          <div class="mt-6 flex flex-wrap items-center justify-center gap-6 md:justify-start">
            <div v-for="stat in stats" :key="stat.label" class="text-center">
              <div class="text-2xl font-bold text-white">{{ stat.value }}</div>
              <div class="text-sm text-primary-200">{{ stat.label }}</div>
            </div>
          </div>
        </div>

        <!-- CTA Buttons -->
        <div class="flex flex-col gap-4 sm:flex-row">
          <NuxtLink 
            :to="ctaUrl" 
            class="group inline-flex items-center justify-center gap-2 rounded-xl bg-white px-6 py-3.5 text-base font-semibold text-primary-600 shadow-lg transition hover:bg-primary-50"
          >
            {{ ctaText }}
            <ArrowRightIcon class="h-5 w-5 transition group-hover:translate-x-1" />
          </NuxtLink>
          
          <NuxtLink 
            v-if="secondaryCtaText"
            :to="secondaryCtaUrl" 
            class="inline-flex items-center justify-center gap-2 rounded-xl border-2 border-white/30 px-6 py-3.5 text-base font-semibold text-white transition hover:border-white/50 hover:bg-white/10"
          >
            {{ secondaryCtaText }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ArrowRightIcon } from '@heroicons/vue/24/outline'

interface Stat {
  value: string
  label: string
}

const { t } = useI18n()

withDefaults(
  defineProps<{
    ctaUrl?: string
    secondaryCtaUrl?: string
  }>(),
  {
    ctaUrl: '/auth/register',
    secondaryCtaUrl: '/contact'
  }
)

const title = computed(() => t('cta.title'))
const subtitle = computed(() => t('cta.subtitle'))
const ctaText = computed(() => t('cta.start'))
const secondaryCtaText = computed(() => t('cta.contact'))
const stats = computed<Stat[]>(() => [
  { value: t('cta.trialDays'), label: t('cta.trialPeriod') },
  { value: t('cta.setupMinutes'), label: t('cta.setupTime') },
  { value: t('cta.support247'), label: t('cta.support') }
])
</script>
