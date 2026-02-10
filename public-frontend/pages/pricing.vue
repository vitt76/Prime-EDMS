<template>
  <div>
    <SEOPageMeta 
      title="Тарифы | MADDAM" 
      description="Выберите тариф MADDAM: SaaS или On-Premise решение для управления цифровыми активами"
    />

    <!-- Hero -->
    <section class="bg-gradient-to-b from-primary-50 to-white py-16 lg:py-20 dark:from-neutral-900 dark:to-neutral-950">
      <div class="mx-auto max-w-container px-4 text-center">
        <h1 class="text-4xl font-bold tracking-tight text-neutral-900 md:text-5xl dark:text-white">
          Простое и прозрачное ценообразование
        </h1>
        <p class="mt-4 text-lg text-neutral-600 dark:text-neutral-400">
          Выберите план, который подходит вашей команде. Начните бесплатно.
        </p>
      </div>
    </section>

    <!-- Pricing Section -->
    <SectionsPricingSection :plans="plans" />

    <SectionsPricingCalculator />

    <!-- Feature Comparison Table -->
    <section class="mx-auto max-w-container px-4 py-16">
      <h2 class="text-center text-2xl font-bold text-neutral-900 md:text-3xl dark:text-white">
        Сравнение функций
      </h2>
      <p class="mt-2 text-center text-neutral-600 dark:text-neutral-400">
        Детальное сравнение всех тарифных планов
      </p>

      <div class="mt-12 overflow-x-auto">
        <table class="w-full min-w-[640px] border-collapse">
          <thead>
            <tr>
              <th class="border-b border-neutral-200 py-4 text-left text-sm font-semibold text-neutral-900">
                Функция
              </th>
              <th 
                v-for="plan in comparisonPlans" 
                :key="plan.name"
                class="border-b border-neutral-200 py-4 text-center text-sm font-semibold"
                :class="plan.recommended ? 'bg-primary-50 text-primary-900' : 'text-neutral-900'"
              >
                {{ plan.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(category, catIdx) in featureCategories" :key="catIdx">
              <!-- Category Header -->
              <td 
                colspan="4" 
                class="border-b border-neutral-200 bg-neutral-50 px-4 py-3 text-sm font-semibold text-neutral-700"
              >
                {{ category.name }}
              </td>
            </tr>
            <template v-for="(category, catIdx) in featureCategories" :key="`cat-${catIdx}`">
              <tr 
                v-for="(feature, featureIdx) in category.features" 
                :key="`${catIdx}-${featureIdx}`"
                class="group"
              >
                <td class="border-b border-neutral-100 py-3 text-sm text-neutral-600 group-hover:bg-neutral-50">
                  {{ feature.name }}
                </td>
                <td 
                  v-for="(plan, planIdx) in comparisonPlans" 
                  :key="planIdx"
                  class="border-b border-neutral-100 py-3 text-center text-sm"
                  :class="plan.recommended ? 'bg-primary-50/50 group-hover:bg-primary-50' : 'group-hover:bg-neutral-50'"
                >
                  <template v-if="typeof feature.values[planIdx] === 'boolean'">
                    <CheckIcon v-if="feature.values[planIdx]" class="mx-auto h-5 w-5 text-success" />
                    <XMarkIcon v-else class="mx-auto h-5 w-5 text-neutral-300" />
                  </template>
                  <template v-else>
                    <span class="font-medium text-neutral-900">{{ feature.values[planIdx] }}</span>
                  </template>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </section>

    <!-- FAQ Section -->
    <section class="bg-neutral-50 py-16 lg:py-20 dark:bg-neutral-900">
      <div class="mx-auto max-w-container px-4">
        <h2 class="text-center text-2xl font-bold text-neutral-900 md:text-3xl dark:text-white">
          Часто задаваемые вопросы
        </h2>
        <p class="mt-2 text-center text-neutral-600 dark:text-neutral-400">
          Ответы на популярные вопросы о тарифах
        </p>

        <div class="mt-12 mx-auto max-w-3xl divide-y divide-neutral-200">
          <div 
            v-for="(faq, idx) in displayFaqs" 
            :key="idx"
            class="py-6"
          >
            <button
              @click="toggleFaq(idx)"
              class="flex w-full items-center justify-between text-left"
            >
              <span class="text-base font-semibold text-neutral-900 dark:text-white">{{ faq.question }}</span>
              <ChevronDownIcon 
                class="h-5 w-5 flex-shrink-0 text-neutral-500 transition-transform"
                :class="openFaqs.has(idx) ? 'rotate-180' : ''"
              />
            </button>
            <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="opacity-0 -translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-2"
            >
              <p 
                v-if="openFaqs.has(idx)"
                class="mt-4 text-sm leading-relaxed text-neutral-600 dark:text-neutral-400"
              >
                {{ faq.answer }}
              </p>
            </Transition>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <SectionsCTASection />
  </div>
</template>

<script setup lang="ts">
import type { PublicFAQ, PublicPlan } from '~/types/content'
import { CheckIcon, XMarkIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'

const { getPlans, getFaq } = useApi()
const { locale } = useI18n()

const { data: plans } = await useAsyncData<PublicPlan[]>(
  `plans-page-${locale.value}`,
  () => getPlans(locale.value),
  { default: () => [], watch: [locale] }
)

const { data: faqs } = await useAsyncData<PublicFAQ[]>(
  `pricing-faq-${locale.value}`,
  () => getFaq({ section: 'pricing', lang: locale.value }),
  { default: () => [], watch: [locale] }
)

// Comparison table data
interface ComparisonPlan {
  name: string
  recommended: boolean
}

interface Feature {
  name: string
  values: (boolean | string)[]
}

interface FeatureCategory {
  name: string
  features: Feature[]
}

const comparisonPlans: ComparisonPlan[] = [
  { name: 'Starter', recommended: false },
  { name: 'Professional', recommended: true },
  { name: 'Enterprise', recommended: false }
]

const featureCategories: FeatureCategory[] = [
  {
    name: 'Хранение',
    features: [
      { name: 'Объем хранилища', values: ['10 ГБ', '100 ГБ', 'Неограниченно'] },
      { name: 'Максимальный размер файла', values: ['500 МБ', '2 ГБ', 'Неограниченно'] },
      { name: 'Версионирование файлов', values: ['30 дней', '1 год', 'Навсегда'] },
    ]
  },
  {
    name: 'Команда',
    features: [
      { name: 'Количество пользователей', values: ['5', '25', 'Неограниченно'] },
      { name: 'Командные рабочие пространства', values: [true, true, true] },
      { name: 'Гостевой доступ', values: [false, true, true] },
      { name: 'SSO интеграция', values: [false, true, true] },
    ]
  },
  {
    name: 'AI и Поиск',
    features: [
      { name: 'AI-поиск по содержимому', values: ['Базовый', 'Продвинутый', 'Кастомный'] },
      { name: 'Распознавание лиц', values: [false, true, true] },
      { name: 'Автоматические теги', values: [true, true, true] },
      { name: 'Кастомные ML-модели', values: [false, false, true] },
    ]
  },
  {
    name: 'Интеграции',
    features: [
      { name: 'API доступ', values: [true, true, true] },
      { name: 'Webhooks', values: [false, true, true] },
      { name: 'Интеграция с Slack/Teams', values: [false, true, true] },
      { name: 'White-label', values: [false, false, true] },
    ]
  },
  {
    name: 'Поддержка',
    features: [
      { name: 'Email поддержка', values: [true, true, true] },
      { name: 'Чат поддержка', values: [false, true, true] },
      { name: 'Выделенный менеджер', values: [false, false, true] },
      { name: 'SLA', values: ['99.5%', '99.9%', '99.99%'] },
    ]
  }
]

// Default FAQs
const defaultFaqs = [
  {
    question: 'Могу ли я изменить тариф в любое время?',
    answer: 'Да, вы можете повысить или понизить тариф в любое время. При повышении изменения вступят в силу немедленно, при понижении — с начала следующего расчетного периода.'
  },
  {
    question: 'Есть ли бесплатный пробный период?',
    answer: 'Да, все тарифы включают 14-дневный бесплатный пробный период без необходимости ввода данных банковской карты.'
  },
  {
    question: 'Какие способы оплаты принимаются?',
    answer: 'Мы принимаем все основные кредитные карты (Visa, MasterCard, American Express), а также PayPal. Для Enterprise клиентов доступна оплата по счету.'
  },
  {
    question: 'Что произойдет, если я превышу лимиты тарифа?',
    answer: 'При приближении к лимитам мы уведомим вас заранее. Вы сможете либо перейти на более высокий тариф, либо оплатить дополнительное хранилище по отдельному тарифу.'
  },
  {
    question: 'Доступна ли On-Premise установка?',
    answer: 'Да, Enterprise тариф включает возможность On-Premise развертывания на вашей инфраструктуре с полной поддержкой нашей команды.'
  }
]

const displayFaqs = computed(() => faqs.value?.length ? faqs.value : defaultFaqs)

const openFaqs = ref<Set<number>>(new Set([0]))

const toggleFaq = (idx: number) => {
  if (openFaqs.value.has(idx)) {
    openFaqs.value.delete(idx)
  } else {
    openFaqs.value.add(idx)
  }
}
</script>
