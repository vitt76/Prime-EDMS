<template>
  <footer class="border-t border-neutral-200 bg-neutral-50">
    <div class="mx-auto max-w-container px-4 py-12 lg:py-16">
      <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-5">
        <!-- Brand -->
        <div class="lg:col-span-2">
          <NuxtLink to="/" class="flex items-center gap-2">
            <CommonIconLogo class="h-8 w-8 text-primary-600" />
            <span class="text-lg font-bold text-neutral-900">MADDAM</span>
          </NuxtLink>
          <p class="mt-4 max-w-sm text-sm leading-relaxed text-neutral-600">
            Облачная DAM-система для управления медиафайлами с AI-поиском, аналитикой и командной работой.
          </p>

          <!-- Social Links -->
          <div class="mt-6 flex gap-3">
            <a 
              v-for="social in socialLinks" 
              :key="social.name"
              :href="social.url"
              target="_blank"
              rel="noopener noreferrer"
              class="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-neutral-500 shadow-sm ring-1 ring-neutral-200 transition hover:bg-primary-50 hover:text-primary-600 hover:ring-primary-200"
              :aria-label="social.name"
            >
              <component :is="social.icon" class="h-5 w-5" />
            </a>
          </div>
        </div>

        <!-- Links Sections -->
        <div v-for="section in linkSections" :key="section.title">
          <h4 class="text-sm font-semibold text-neutral-900">{{ section.title }}</h4>
          <ul class="mt-4 space-y-3">
            <li v-for="link in section.links" :key="link.path">
              <NuxtLink 
                :to="link.external ? undefined : link.path"
                :href="link.external ? link.path : undefined"
                :target="link.external ? '_blank' : undefined"
                :rel="link.external ? 'noopener noreferrer' : undefined"
                class="text-sm text-neutral-600 transition hover:text-primary-600"
              >
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- Newsletter -->
        <div>
          <h4 class="text-sm font-semibold text-neutral-900">Newsletter</h4>
          <p class="mt-2 text-sm text-neutral-600">Получайте новости и обновления</p>
          <form @submit.prevent="subscribeNewsletter" class="mt-4">
            <div class="flex gap-2">
              <input
                v-model="email"
                type="email"
                placeholder="Email"
                required
                :disabled="loading"
                class="flex-1 rounded-lg border-neutral-200 px-3 py-2.5 text-sm shadow-sm transition focus:border-primary-500 focus:ring-primary-500 disabled:opacity-50"
                aria-label="Email for newsletter"
              />
              <button 
                type="submit"
                :disabled="loading || subscribed"
                class="flex items-center justify-center rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <span v-if="loading" class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                <CheckIcon v-else-if="subscribed" class="h-5 w-5" />
                <span v-else>OK</span>
              </button>
            </div>
            <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="opacity-0 translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
            >
              <p v-if="subscribed" class="mt-2 text-xs text-success">
                Подписка оформлена! Проверьте почту.
              </p>
              <p v-else-if="error" class="mt-2 text-xs text-error">
                {{ error }}
              </p>
            </Transition>
          </form>
        </div>
      </div>

      <div class="mt-12 border-t border-neutral-200 pt-8">
        <CommonTrustBadges />
      </div>

      <!-- Bottom Bar -->
      <div class="mt-12 flex flex-col items-center justify-between gap-4 border-t border-neutral-200 pt-8 text-sm text-neutral-500 md:flex-row">
        <p>© {{ currentYear }} MADDAM. Все права защищены.</p>
        <div class="flex gap-6">
          <NuxtLink to="/terms" class="transition hover:text-neutral-900">Условия использования</NuxtLink>
          <NuxtLink to="/privacy" class="transition hover:text-neutral-900">Политика конфиденциальности</NuxtLink>
        </div>
      </div>
    </div>

    <CommonNewsletterSuccessModal
      :show="showSuccessModal"
      :email="subscribedEmail"
      @close="showSuccessModal = false"
    />
  </footer>
</template>

<script setup lang="ts">
import { CheckIcon } from '@heroicons/vue/24/outline'
import IconLinkedIn from '~/components/Common/IconLinkedIn.vue'
import IconTwitter from '~/components/Common/IconTwitter.vue'
import IconGithub from '~/components/Common/IconGithub.vue'

interface SocialLink {
  name: string
  url: string
  icon: any
}

interface LinkItem {
  label: string
  path: string
  external?: boolean
}

interface LinkSection {
  title: string
  links: LinkItem[]
}

const email = ref('')
const loading = ref(false)
const subscribed = ref(false)
const error = ref('')
const showSuccessModal = ref(false)
const subscribedEmail = ref('')

const currentYear = new Date().getFullYear()

const socialLinks: SocialLink[] = [
  { name: 'LinkedIn', url: 'https://linkedin.com/company/maddam', icon: IconLinkedIn },
  { name: 'Twitter', url: 'https://twitter.com/maddam_dam', icon: IconTwitter },
  { name: 'GitHub', url: 'https://github.com/maddam', icon: IconGithub }
]

const linkSections: LinkSection[] = [
  {
    title: 'Продукт',
    links: [
      { label: 'Возможности', path: '/#features' },
      { label: 'Тарифы', path: '/pricing' },
      { label: 'Roadmap', path: '/roadmap' },
      { label: 'Changelog', path: '/changelog' }
    ]
  },
  {
    title: 'Компания',
    links: [
      { label: 'О нас', path: '/about' },
      { label: 'Блог', path: '/blog' },
      { label: 'Контакты', path: '/contact' },
      { label: 'Документация', path: 'https://docs.maddam.ru', external: true }
    ]
  }
]

const subscribeNewsletter = async () => {
  if (loading.value || subscribed.value) return
  
  error.value = ''
  loading.value = true
  
  try {
    await $fetch('/api/v4/public/newsletter/', {
      method: 'POST',
      body: { email: email.value }
    })
    subscribed.value = true
    subscribedEmail.value = email.value
    showSuccessModal.value = true
    email.value = ''
  } catch (err: any) {
    console.error('Newsletter subscription failed:', err)
    error.value = err?.data?.message || 'Произошла ошибка. Попробуйте позже.'
  } finally {
    loading.value = false
  }
}
</script>
