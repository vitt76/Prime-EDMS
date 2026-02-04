<template>
  <section class="border-y border-neutral-200 bg-neutral-50 py-16 lg:py-20">
    <div class="mx-auto max-w-container px-4">
      <!-- Client Logos -->
      <div class="text-center">
        <p class="text-sm font-medium uppercase tracking-wider text-neutral-500">
          {{ trustedByText }}
        </p>
        <div class="mt-8 flex flex-wrap items-center justify-center gap-x-12 gap-y-8">
          <div 
            v-for="(logo, idx) in clientLogos" 
            :key="idx"
            class="flex h-8 items-center text-neutral-400 grayscale transition hover:text-neutral-600 hover:grayscale-0"
          >
            <!-- Placeholder logos - replace with actual client logos -->
            <div class="flex items-center gap-2">
              <div class="h-8 w-8 rounded-lg bg-neutral-300"></div>
              <span class="text-lg font-semibold">{{ logo.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Testimonials -->
      <div class="mt-16 grid gap-8 lg:grid-cols-3">
        <div 
          v-for="(testimonial, idx) in testimonials" 
          :key="idx"
          class="relative rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-200/80"
        >
          <!-- Quote Icon -->
          <div class="absolute -top-3 left-6">
            <div class="flex h-6 w-6 items-center justify-center rounded-full bg-primary-600 text-white">
              <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 24 24">
                <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
              </svg>
            </div>
          </div>

          <!-- Content -->
          <p class="mt-4 text-sm leading-relaxed text-neutral-600">
            "{{ testimonial.quote }}"
          </p>

          <!-- Author -->
          <div class="mt-6 flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-sm font-bold text-white">
              {{ testimonial.author.charAt(0) }}
            </div>
            <div>
              <div class="text-sm font-semibold text-neutral-900">{{ testimonial.author }}</div>
              <div class="text-xs text-neutral-500">{{ testimonial.role }}, {{ testimonial.company }}</div>
            </div>
          </div>

          <!-- Rating -->
          <div class="mt-4 flex gap-1">
            <StarIcon 
              v-for="star in 5" 
              :key="star" 
              class="h-4 w-4"
              :class="star <= testimonial.rating ? 'text-yellow-400 fill-yellow-400' : 'text-neutral-200'"
            />
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="mt-16 grid gap-8 rounded-2xl bg-white p-8 shadow-sm ring-1 ring-neutral-200/80 md:grid-cols-4">
        <div v-for="stat in stats" :key="stat.label" class="text-center">
          <div class="text-3xl font-bold text-primary-600 md:text-4xl">{{ stat.value }}</div>
          <div class="mt-1 text-sm text-neutral-600">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { StarIcon } from '@heroicons/vue/24/solid'

interface ClientLogo {
  name: string
  logo?: string
}

interface Testimonial {
  quote: string
  author: string
  role: string
  company: string
  rating: number
}

interface Stat {
  value: string
  label: string
}

withDefaults(
  defineProps<{
    trustedByText?: string
    clientLogos?: ClientLogo[]
    testimonials?: Testimonial[]
    stats?: Stat[]
  }>(),
  {
    trustedByText: 'Нам доверяют компании по всему миру'
  }
)

// Default data
const clientLogos: ClientLogo[] = [
  { name: 'Yandex' },
  { name: 'Sber' },
  { name: 'VK' },
  { name: 'Tinkoff' },
  { name: 'Ozon' }
]

const testimonials: Testimonial[] = [
  {
    quote: 'MADDAM полностью изменила наш подход к управлению медиаактивами. AI-поиск экономит нам часы работы каждый день.',
    author: 'Анна Петрова',
    role: 'Creative Director',
    company: 'Digital Agency',
    rating: 5
  },
  {
    quote: 'Наконец-то решение, которое понимает потребности маркетологов. Интеграция с нашими инструментами заняла минуты.',
    author: 'Михаил Сидоров',
    role: 'Head of Marketing',
    company: 'E-commerce Corp',
    rating: 5
  },
  {
    quote: 'Отличная поддержка и постоянные обновления. Команда MADDAM реально слушает обратную связь.',
    author: 'Елена Козлова',
    role: 'Product Manager',
    company: 'Tech Startup',
    rating: 5
  }
]

const stats: Stat[] = [
  { value: '2,500+', label: 'Активных команд' },
  { value: '10M+', label: 'Файлов под управлением' },
  { value: '99.9%', label: 'Uptime' },
  { value: '4.8/5', label: 'Средний рейтинг' }
]
</script>
