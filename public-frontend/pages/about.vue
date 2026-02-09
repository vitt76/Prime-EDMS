<template>
  <div>
    <SEOPageMeta
      :title="$t('about.title') + ' | MADDAM'"
      :description="$t('about.subtitle')"
    />

    <!-- Hero -->
    <section class="bg-gradient-to-b from-primary-50 to-white py-16 lg:py-24 dark:from-neutral-900 dark:to-neutral-950">
      <div class="mx-auto max-w-container px-4 text-center">
        <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
          <BuildingOffice2Icon class="h-4 w-4" />
          <span>{{ $t('about.title') }}</span>
        </div>
        <h1 class="mt-6 text-4xl font-bold tracking-tight text-neutral-900 md:text-5xl dark:text-white">
          {{ $t('about.subtitle') }}
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-neutral-600 dark:text-neutral-400">
          MADDAM — облачная DAM-система нового поколения для централизованного управления медиафайлами.
          Мы помогаем командам быстрее находить, организовывать и распространять цифровые активы
          с помощью AI-поиска и продвинутой аналитики.
        </p>
      </div>
    </section>

    <!-- Mission -->
    <section class="py-16 lg:py-20">
      <div class="mx-auto max-w-container px-4">
        <div class="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <h2 class="text-3xl font-bold text-neutral-900 dark:text-white">
              {{ $t('about.mission') }}
            </h2>
            <p class="mt-4 text-lg leading-relaxed text-neutral-600 dark:text-neutral-400">
              Наша миссия — устранить хаос в управлении медиаконтентом. Мы верим, что каждая
              команда заслуживает инструмент, который экономит часы поиска, автоматизирует
              рутинные задачи и даёт полную видимость использования активов.
            </p>
            <p class="mt-4 text-lg leading-relaxed text-neutral-600 dark:text-neutral-400">
              MADDAM сочетает мощь AI-обогащения метаданных с интуитивным интерфейсом,
              позволяя сократить время поиска файлов с 30 минут до 5 и повысить
              переиспользование контента до 62%.
            </p>
            <div class="mt-8 grid grid-cols-2 gap-6 sm:grid-cols-4">
              <div v-for="stat in stats" :key="stat.label" class="text-center">
                <div class="text-2xl font-bold text-primary-600 dark:text-primary-400">{{ stat.value }}</div>
                <div class="mt-1 text-sm text-neutral-500 dark:text-neutral-400">{{ stat.label }}</div>
              </div>
            </div>
          </div>
          <div class="relative">
            <div class="aspect-video rounded-2xl bg-gradient-to-br from-primary-100 to-primary-50 p-8 dark:from-primary-900/30 dark:to-neutral-800">
              <div class="flex h-full flex-col items-center justify-center text-center">
                <RocketLaunchIcon class="h-16 w-16 text-primary-500" />
                <p class="mt-4 text-sm font-medium text-primary-700 dark:text-primary-300">
                  Управляйте контентом быстрее
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Values -->
    <section class="bg-neutral-50 py-16 lg:py-20 dark:bg-neutral-900">
      <div class="mx-auto max-w-container px-4">
        <div class="text-center">
          <h2 class="text-3xl font-bold text-neutral-900 dark:text-white">
            {{ $t('about.values') }}
          </h2>
          <p class="mt-4 text-lg text-neutral-600 dark:text-neutral-400">
            Принципы, которые определяют наш продукт и команду
          </p>
        </div>

        <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="value in values"
            :key="value.title"
            class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-neutral-200 transition hover:shadow-md dark:bg-neutral-800 dark:ring-neutral-700"
          >
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-100 dark:bg-primary-900/40">
              <component :is="value.icon" class="h-6 w-6 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="mt-4 text-lg font-semibold text-neutral-900 dark:text-white">{{ value.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">{{ value.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Team -->
    <section class="py-16 lg:py-20">
      <div class="mx-auto max-w-container px-4">
        <div class="text-center">
          <h2 class="text-3xl font-bold text-neutral-900 dark:text-white">
            {{ $t('about.team') }}
          </h2>
          <p class="mt-4 text-lg text-neutral-600 dark:text-neutral-400">
            Люди, стоящие за MADDAM
          </p>
        </div>

        <div class="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="member in team"
            :key="member.name"
            class="rounded-2xl bg-white p-6 text-center shadow-sm ring-1 ring-neutral-200 transition hover:shadow-md dark:bg-neutral-800 dark:ring-neutral-700"
          >
            <div class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-primary-100 text-2xl font-bold text-primary-600 dark:bg-primary-900/40 dark:text-primary-400">
              {{ member.initials }}
            </div>
            <h3 class="mt-4 text-lg font-semibold text-neutral-900 dark:text-white">{{ member.name }}</h3>
            <p class="text-sm text-primary-600 dark:text-primary-400">{{ member.role }}</p>
            <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">{{ member.bio }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <SectionsCTASection />
  </div>
</template>

<script setup lang="ts">
import {
  BuildingOffice2Icon,
  RocketLaunchIcon,
  ShieldCheckIcon,
  BoltIcon,
  UserGroupIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'

const stats = [
  { value: '2,500+', label: 'Команд' },
  { value: '10M+', label: 'Файлов' },
  { value: '99.9%', label: 'Uptime' },
  { value: '4.8/5', label: 'Рейтинг' }
]

const values = [
  {
    icon: BoltIcon,
    title: 'Скорость',
    description: 'Мгновенный AI-поиск по содержимому и метаданным. Находите нужный файл за секунды, а не минуты.'
  },
  {
    icon: ShieldCheckIcon,
    title: 'Безопасность',
    description: 'Соответствие ФЗ-152, контроль доступа на уровне объектов, аудит всех операций.'
  },
  {
    icon: UserGroupIcon,
    title: 'Командная работа',
    description: 'Workflow согласования, роли и права, совместное использование активов в команде.'
  },
  {
    icon: SparklesIcon,
    title: 'AI-интеллект',
    description: 'Автоматическое обогащение метаданных, распознавание лиц, категоризация контента.'
  }
]

const team = [
  {
    name: 'Дмитрий Владимиров',
    initials: 'ДВ',
    role: 'Основатель и CEO',
    bio: 'Более 15 лет опыта в разработке enterprise-систем и управлении продуктами.'
  },
  {
    name: 'Команда разработки',
    initials: 'КР',
    role: 'Engineering Team',
    bio: 'Опытные инженеры, специализирующиеся на Django, Vue.js и AI/ML технологиях.'
  },
  {
    name: 'Команда продукта',
    initials: 'КП',
    role: 'Product Team',
    bio: 'Эксперты в UX/UI дизайне и управлении цифровыми активами.'
  }
]
</script>
