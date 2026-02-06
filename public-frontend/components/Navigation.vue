<template>
  <header class="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-neutral-200 shadow-sm dark:bg-neutral-950/95 dark:border-neutral-800">
    <div class="mx-auto flex h-16 max-w-container items-center justify-between px-4">
      <!-- Logo with icon -->
      <NuxtLink to="/" class="flex items-center gap-2 text-lg font-bold text-primary-600 transition hover:text-primary-700">
        <CommonIconLogo class="h-8 w-8" />
        <span>MADDAM</span>
      </NuxtLink>

      <!-- Desktop Navigation -->
      <nav class="hidden items-center gap-6 lg:flex">
        <NuxtLink 
          v-for="link in navLinks" 
          :key="link.path"
          :to="link.external ? undefined : link.path"
          :href="link.external ? link.path : undefined"
          :target="link.external ? '_blank' : undefined"
          :rel="link.external ? 'noopener noreferrer' : undefined"
          class="text-sm font-medium transition-colors"
          :class="isActive(link.path) ? 'text-primary-600' : 'text-neutral-600 hover:text-neutral-900'"
        >
          {{ $t(link.label) }}
        </NuxtLink>
      </nav>

      <!-- Auth & Language -->
      <div class="flex items-center gap-3">
        <NuxtLink 
          to="/auth/login" 
          class="hidden text-sm font-medium text-neutral-600 transition hover:text-neutral-900 md:inline"
        >
          {{ $t('nav.login') }}
        </NuxtLink>
        <NuxtLink 
          to="/auth/register" 
          class="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-primary-700 hover:shadow-md"
        >
          {{ $t('nav.signup') }}
        </NuxtLink>

        <!-- Language Switcher -->
        <Menu as="div" class="relative">
          <MenuButton 
            class="flex items-center gap-1 rounded-lg p-2 text-sm text-neutral-600 transition hover:bg-neutral-100 hover:text-neutral-900"
            aria-label="Change language"
          >
            <GlobeAltIcon class="h-5 w-5" />
            <span class="hidden md:inline">{{ currentLocaleName }}</span>
            <ChevronDownIcon class="h-4 w-4" />
          </MenuButton>
          <transition
            enter-active-class="transition duration-100 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <MenuItems class="absolute right-0 mt-2 w-36 origin-top-right rounded-lg bg-white py-1 shadow-lg ring-1 ring-black/5 focus:outline-none">
              <MenuItem v-for="loc in availableLocales" :key="loc.code" v-slot="{ active }">
                <NuxtLink 
                  :to="switchLocalePath(loc.code)"
                  class="flex items-center gap-2 px-4 py-2 text-sm"
                  :class="active ? 'bg-neutral-50 text-neutral-900' : 'text-neutral-700'"
                >
                  <span>{{ loc.name }}</span>
                  <CheckIcon v-if="locale === loc.code" class="ml-auto h-4 w-4 text-primary-600" />
                </NuxtLink>
              </MenuItem>
            </MenuItems>
          </transition>
        </Menu>

        <!-- Color Mode Toggle -->
        <CommonColorModeToggle />

        <!-- Mobile Menu Button -->
        <button 
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="rounded-lg p-2 text-neutral-600 transition hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800 lg:hidden"
          :aria-label="mobileMenuOpen ? 'Close menu' : 'Open menu'"
          :aria-expanded="mobileMenuOpen"
        >
          <XMarkIcon v-if="mobileMenuOpen" class="h-6 w-6" />
          <Bars3Icon v-else class="h-6 w-6" />
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div 
        v-if="mobileMenuOpen" 
        class="border-t border-neutral-200 bg-white lg:hidden"
      >
        <nav class="flex flex-col px-4 py-4">
          <NuxtLink 
            v-for="link in navLinks" 
            :key="link.path"
            :to="link.external ? undefined : link.path"
            :href="link.external ? link.path : undefined"
            :target="link.external ? '_blank' : undefined"
            class="flex items-center justify-between rounded-lg px-3 py-3 text-base font-medium transition"
            :class="isActive(link.path) ? 'bg-primary-50 text-primary-600' : 'text-neutral-700 hover:bg-neutral-50'"
            @click="!link.external && (mobileMenuOpen = false)"
          >
            <span>{{ $t(link.label) }}</span>
            <ArrowTopRightOnSquareIcon v-if="link.external" class="h-4 w-4 text-neutral-400" />
          </NuxtLink>
          
          <!-- Mobile Auth Links -->
          <div class="mt-4 border-t border-neutral-200 pt-4">
            <NuxtLink 
              to="/auth/login"
              class="block rounded-lg px-3 py-3 text-base font-medium text-neutral-700 transition hover:bg-neutral-50"
              @click="mobileMenuOpen = false"
            >
              {{ $t('nav.login') }}
            </NuxtLink>
          </div>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'
import { 
  Bars3Icon, 
  XMarkIcon, 
  GlobeAltIcon, 
  ChevronDownIcon,
  CheckIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline'

interface NavLink {
  path: string
  label: string
  external?: boolean
}

const navLinks: NavLink[] = [
  { path: '/pricing', label: 'nav.pricing' },
  { path: '/blog', label: 'nav.blog' },
  { path: '/about', label: 'nav.about' },
  { path: '/contact', label: 'nav.contact' },
  { path: 'https://docs.maddam.ru', label: 'nav.docs', external: true }
]

const route = useRoute()
const { locales, locale } = useI18n()
const switchLocalePath = useSwitchLocalePath()
const mobileMenuOpen = ref(false)

const availableLocales = computed(() => 
  (locales.value as Array<{ code: string; name: string }>).filter(l => l.code !== locale.value).concat(
    (locales.value as Array<{ code: string; name: string }>).filter(l => l.code === locale.value)
  )
)

const currentLocaleName = computed(() => {
  const current = (locales.value as Array<{ code: string; name: string }>).find(l => l.code === locale.value)
  return current?.name || locale.value.toUpperCase()
})

const isActive = (path: string) => {
  if (path.startsWith('http')) return false
  return route.path === path || route.path.startsWith(path + '/')
}

// Close mobile menu on route change
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

// Close mobile menu on escape key
onMounted(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && mobileMenuOpen.value) {
      mobileMenuOpen.value = false
    }
  }
  window.addEventListener('keydown', handleEscape)
  onUnmounted(() => window.removeEventListener('keydown', handleEscape))
})
</script>
