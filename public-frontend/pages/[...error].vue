<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-primary-50 via-white to-neutral-50">
    <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-5"></div>
    <div class="absolute -left-40 top-0 h-96 w-96 rounded-full bg-primary-200/30 blur-3xl"></div>
    <div class="absolute -right-40 bottom-0 h-96 w-96 rounded-full bg-primary-300/20 blur-3xl"></div>

    <div class="relative flex min-h-screen items-center justify-center px-4 py-16">
      <div class="mx-auto max-w-2xl text-center">
        <div class="relative">
          <h1 class="text-[180px] font-bold leading-none text-neutral-200 lg:text-[240px]">
            {{ error?.statusCode || 404 }}
          </h1>
          <div class="absolute inset-0 flex items-center justify-center">
            <ExclamationTriangleIcon class="h-24 w-24 text-primary-600 lg:h-32 lg:w-32" />
          </div>
        </div>

        <h2 class="mt-4 text-2xl font-bold text-neutral-900 md:text-3xl">
          {{ errorTitle }}
        </h2>
        <p class="mt-3 text-lg text-neutral-600">
          {{ errorMessage }}
        </p>

        <div class="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <NuxtLink 
            to="/"
            class="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-6 py-3 font-semibold text-white shadow-lg transition hover:bg-primary-700"
          >
            <HomeIcon class="h-5 w-5" />
            На главную
          </NuxtLink>
          <NuxtLink 
            to="/contact"
            class="inline-flex items-center gap-2 rounded-xl border-2 border-neutral-200 bg-white px-6 py-3 font-semibold text-neutral-700 transition hover:border-neutral-300 hover:bg-neutral-50"
          >
            <ChatBubbleLeftIcon class="h-5 w-5" />
            Связаться с нами
          </NuxtLink>
        </div>

        <div class="mt-16">
          <h3 class="text-sm font-semibold uppercase tracking-wider text-neutral-500">
            Популярные страницы
          </h3>
          <div class="mt-4 flex flex-wrap justify-center gap-3">
            <NuxtLink 
              v-for="link in popularLinks"
              :key="link.path"
              :to="link.path"
              class="rounded-lg bg-white px-4 py-2 text-sm font-medium text-neutral-700 shadow-sm ring-1 ring-neutral-200 transition hover:bg-neutral-50"
            >
              {{ link.label }}
            </NuxtLink>
          </div>
        </div>

        <div class="mt-8">
          <form @submit.prevent="search" class="mx-auto max-w-md">
            <div class="relative">
              <MagnifyingGlassIcon class="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-400" />
              <input
                v-model="searchQuery"
                type="search"
                placeholder="Поиск по сайту..."
                class="w-full rounded-lg border-neutral-200 py-3 pl-10 pr-4 text-sm shadow-sm transition focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20"
              />
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  ChatBubbleLeftIcon, 
  ExclamationTriangleIcon, 
  HomeIcon, 
  MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'

const error = useError()
const searchQuery = ref('')

const errorTitle = computed(() => {
  switch (error.value?.statusCode) {
    case 404:
      return 'Страница не найдена'
    case 500:
      return 'Ошибка сервера'
    case 403:
      return 'Доступ запрещен'
    default:
      return 'Что-то пошло не так'
  }
})

const errorMessage = computed(() => {
  switch (error.value?.statusCode) {
    case 404:
      return 'Возможно, страница была перемещена или удалена. Попробуйте вернуться на главную или воспользуйтесь поиском.'
    case 500:
      return 'У нас возникли технические проблемы. Мы уже работаем над их устранением.'
    case 403:
      return 'У вас нет прав для доступа к этой странице.'
    default:
      return 'Произошла неожиданная ошибка. Пожалуйста, попробуйте позже.'
  }
})

const popularLinks = [
  { path: '/pricing', label: 'Тарифы' },
  { path: '/blog', label: 'Блог' },
  { path: '/about', label: 'О нас' },
  { path: '/contact', label: 'Контакты' }
]

const search = () => {
  if (searchQuery.value) {
    navigateTo(`/blog?q=${encodeURIComponent(searchQuery.value)}`)
  }
}
</script>
