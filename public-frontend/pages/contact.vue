<template>
  <div>
    <SEOPageMeta
      :title="page?.meta_title || $t('contact.title') + ' | MADDAM'"
      :description="page?.meta_description || $t('contact.heroDesc')"
    />

    <!-- Hero Section -->
    <section class="relative overflow-hidden bg-gradient-to-b from-primary-50 to-white dark:from-neutral-900 dark:to-neutral-950">
      <!-- Decorative background -->
      <div class="absolute inset-0 opacity-30 dark:opacity-10" aria-hidden="true">
        <div class="absolute -top-24 right-0 h-72 w-72 rounded-full bg-primary-200 blur-3xl dark:bg-primary-800" />
        <div class="absolute bottom-0 left-1/4 h-48 w-48 rounded-full bg-indigo-200 blur-3xl dark:bg-indigo-900" />
      </div>

      <div class="relative mx-auto max-w-container px-4 py-16 text-center sm:py-20">
        <span class="mb-4 inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
          <EnvelopeIcon class="h-4 w-4" />
          {{ $t('contact.title') }}
        </span>

        <h1 class="mt-4 text-3xl font-bold tracking-tight text-neutral-900 sm:text-4xl lg:text-5xl dark:text-white">
          {{ page?.title || $t('contact.title') }}
        </h1>

        <p class="mx-auto mt-4 max-w-2xl text-lg text-neutral-600 dark:text-neutral-400">
          {{ $t('contact.heroDesc') }}
        </p>

        <!-- Trust Badges -->
        <div class="mt-8 flex flex-wrap items-center justify-center gap-6 sm:gap-10">
          <div class="flex flex-col items-center">
            <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ $t('contact.trustResponseValue') }}
            </span>
            <span class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
              {{ $t('contact.trustResponse') }}
            </span>
          </div>
          <div class="hidden h-8 w-px bg-neutral-200 sm:block dark:bg-neutral-700" />
          <div class="flex flex-col items-center">
            <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ $t('contact.trustClientsValue') }}
            </span>
            <span class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
              {{ $t('contact.trustClients') }}
            </span>
          </div>
          <div class="hidden h-8 w-px bg-neutral-200 sm:block dark:bg-neutral-700" />
          <div class="flex flex-col items-center">
            <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ $t('contact.trustSatisfactionValue') }}
            </span>
            <span class="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
              {{ $t('contact.trustSatisfaction') }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content: Info + Form -->
    <section class="mx-auto max-w-container px-4 py-12 lg:py-16">
      <div class="grid gap-10 lg:grid-cols-5 lg:gap-16">

        <!-- Left Column: Contact Info -->
        <div class="lg:col-span-2">
          <h2 class="text-xl font-semibold text-neutral-900 dark:text-white">
            {{ $t('contact.subtitle') }}
          </h2>

          <!-- CMS content if available -->
          <div
            v-if="contentHtml"
            v-html="contentHtml"
            class="prose prose-sm mt-4 max-w-none text-neutral-600 dark:prose-invert dark:text-neutral-400"
          />

          <!-- Contact Info Cards -->
          <div class="mt-8 space-y-4">
            <div
              v-for="info in contactInfo"
              :key="info.label"
              class="flex items-center gap-4 rounded-xl border border-neutral-100 bg-neutral-50 p-4 transition hover:border-primary-200 hover:bg-primary-50/50 dark:border-neutral-800 dark:bg-neutral-800/50 dark:hover:border-primary-800 dark:hover:bg-primary-900/10"
            >
              <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-primary-100 dark:bg-primary-900/30">
                <component :is="info.icon" class="h-5 w-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div class="min-w-0">
                <p class="text-xs font-medium text-neutral-500 dark:text-neutral-400">
                  {{ info.label }}
                </p>
                <a
                  v-if="info.href"
                  :href="info.href"
                  class="text-sm font-medium text-neutral-900 transition hover:text-primary-600 dark:text-white dark:hover:text-primary-400"
                >
                  {{ info.value }}
                </a>
                <p v-else class="text-sm font-medium text-neutral-900 dark:text-white">
                  {{ info.value }}
                </p>
              </div>
            </div>
          </div>

          <!-- Social Links -->
          <div class="mt-8 border-t border-neutral-200 pt-6 dark:border-neutral-800">
            <p class="mb-3 text-sm font-medium text-neutral-500 dark:text-neutral-400">
              {{ $t('footer.company') }}
            </p>
            <CommonSocialIcons />
          </div>
        </div>

        <!-- Right Column: Form -->
        <div class="lg:col-span-3">
          <div class="rounded-2xl border border-neutral-200 bg-white p-6 shadow-sm sm:p-8 dark:border-neutral-800 dark:bg-neutral-900">
            <h2 class="mb-6 text-xl font-semibold text-neutral-900 dark:text-white">
              {{ $t('contact.formTitle') }}
            </h2>
            <FormsContactForm />
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Teaser -->
    <section class="border-t border-neutral-200 bg-neutral-50 dark:border-neutral-800 dark:bg-neutral-900/50">
      <div class="mx-auto max-w-container px-4 py-12 text-center">
        <QuestionMarkCircleIcon class="mx-auto h-10 w-10 text-primary-500 dark:text-primary-400" />
        <h2 class="mt-4 text-xl font-semibold text-neutral-900 dark:text-white">
          {{ $t('contact.faq.title') }}
        </h2>
        <p class="mx-auto mt-2 max-w-lg text-sm text-neutral-600 dark:text-neutral-400">
          {{ $t('contact.faq.desc') }}
        </p>
        <NuxtLink
          to="/pricing#faq"
          class="mt-5 inline-flex items-center gap-2 rounded-lg border border-neutral-300 px-5 py-2.5 text-sm font-medium text-neutral-700 transition hover:bg-neutral-100 dark:border-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-800"
        >
          {{ $t('contact.faq.link') }}
          <ArrowRightIcon class="h-4 w-4" />
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  EnvelopeIcon,
  PhoneIcon,
  BuildingOfficeIcon,
  ClockIcon,
  QuestionMarkCircleIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/outline'
import type { PublicPage } from '~/types/content'
import type { Component } from 'vue'

const { getPage } = useApi()
const { locale, t } = useI18n()

const { data: page } = await useAsyncData<PublicPage | null>(
  `page-contact-${locale.value}`,
  () => getPage('contact', locale.value).catch(() => null),
  { watch: [locale] }
)

const contentHtml = computed(() => {
  const section = page.value?.sections?.[0]
  return section?.content?.html || null
})

interface ContactInfoItem {
  icon: Component
  label: string
  value: string
  href?: string
}

const contactInfo = computed<ContactInfoItem[]>(() => [
  {
    icon: EnvelopeIcon,
    label: t('contact.infoEmail'),
    value: t('contact.infoEmailValue'),
    href: `mailto:${t('contact.infoEmailValue')}`
  },
  {
    icon: PhoneIcon,
    label: t('contact.infoPhone'),
    value: t('contact.infoPhoneValue'),
    href: `tel:${t('contact.infoPhoneValue').replace(/[\s()-]/g, '')}`
  },
  {
    icon: BuildingOfficeIcon,
    label: t('contact.infoOffice'),
    value: t('contact.infoOfficeValue')
  },
  {
    icon: ClockIcon,
    label: t('contact.infoHours'),
    value: t('contact.infoHoursValue')
  }
])
</script>
