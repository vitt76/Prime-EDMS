<template>
  <section class="mx-auto max-w-container px-4 py-16 lg:py-20">
    <!-- Header -->
    <div class="mx-auto max-w-2xl text-center">
      <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700">
        <QuestionMarkCircleIcon class="h-4 w-4" />
        <span>FAQ</span>
      </div>
      <h2 class="mt-4 text-3xl font-bold tracking-tight text-neutral-900 md:text-4xl">
        {{ title }}
      </h2>
      <p class="mt-4 text-lg text-neutral-600">
        {{ subtitle }}
      </p>
    </div>

    <!-- FAQ Accordion -->
    <div class="mx-auto mt-12 max-w-3xl divide-y divide-neutral-200 rounded-2xl bg-white shadow-sm ring-1 ring-neutral-200">
      <Disclosure 
        v-for="(item, idx) in displayFaqs" 
        :key="item.id || idx"
        v-slot="{ open }"
        :default-open="idx === 0"
      >
        <DisclosureButton
          class="flex w-full items-center justify-between px-6 py-5 text-left transition hover:bg-neutral-50"
        >
          <span class="pr-4 text-base font-semibold text-neutral-900">{{ item.question }}</span>
          <ChevronDownIcon 
            class="h-5 w-5 flex-shrink-0 text-neutral-500 transition-transform duration-200"
            :class="open ? 'rotate-180' : ''"
          />
        </DisclosureButton>
        <transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <DisclosurePanel class="px-6 pb-5">
            <p class="text-sm leading-relaxed text-neutral-600">{{ item.answer }}</p>
          </DisclosurePanel>
        </transition>
      </Disclosure>
    </div>

    <!-- Contact CTA -->
    <div class="mt-12 text-center">
      <p class="text-neutral-600">
        Не нашли ответ на свой вопрос?
      </p>
      <NuxtLink 
        to="/contact" 
        class="mt-2 inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        Свяжитесь с нами
        <ArrowRightIcon class="h-4 w-4" />
      </NuxtLink>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { PublicFAQ } from '~/types/content'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/vue'
import { ChevronDownIcon, QuestionMarkCircleIcon, ArrowRightIcon } from '@heroicons/vue/24/outline'

const props = withDefaults(
  defineProps<{
    faqs?: PublicFAQ[]
    title?: string
    subtitle?: string
  }>(),
  {
    title: 'Часто задаваемые вопросы',
    subtitle: 'Ответы на популярные вопросы о MADDAM'
  }
)

// Default FAQs
const defaultFaqs = [
  {
    id: '1',
    section: 'general',
    question: 'Что такое MADDAM?',
    answer: 'MADDAM — это облачная DAM-система (Digital Asset Management) для управления медиафайлами. Она позволяет хранить, организовывать, искать и распространять цифровые активы вашей компании.',
    order: 1
  },
  {
    id: '2',
    section: 'general',
    question: 'Как работает AI-поиск?',
    answer: 'Наш AI-поиск использует современные модели машинного обучения для анализа содержимого файлов. Он распознает объекты на изображениях, извлекает текст из документов и понимает семантику запросов.',
    order: 2
  },
  {
    id: '3',
    section: 'general',
    question: 'Безопасны ли мои данные?',
    answer: 'Абсолютно. Мы используем шифрование AES-256 для данных в покое и TLS 1.3 для данных в передаче. Все данные хранятся в сертифицированных дата-центрах с SOC 2 Type II.',
    order: 3
  },
  {
    id: '4',
    section: 'general',
    question: 'Какие форматы файлов поддерживаются?',
    answer: 'MADDAM поддерживает все популярные форматы: изображения (JPG, PNG, WebP, AVIF, RAW), видео (MP4, MOV, AVI), документы (PDF, DOCX, PPTX), аудио (MP3, WAV) и многие другие.',
    order: 4
  }
]

const displayFaqs = computed(() => props.faqs?.length ? props.faqs : defaultFaqs)
</script>
