<template>
  <ClientOnly>
    <Teleport to="body">
      <Transition name="consent-fade">
        <div
          v-if="visible"
          :class="[
            'fixed z-[9999] flex flex-col gap-4 rounded-lg border border-neutral-200 bg-white p-4 shadow-xl dark:border-neutral-700 dark:bg-neutral-900',
            position === 'banner'
              ? 'bottom-4 left-4 right-4 md:left-8 md:right-8 md:bottom-6'
              : 'left-1/2 top-1/2 w-[min(90vw,28rem)] -translate-x-1/2 -translate-y-1/2'
          ]"
          role="dialog"
          aria-labelledby="cookie-consent-title"
          aria-describedby="cookie-consent-desc"
        >
          <h2 id="cookie-consent-title" class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            Использование файлов cookie
          </h2>
          <p id="cookie-consent-desc" class="text-sm text-neutral-600 dark:text-neutral-400">
            Мы используем файлы cookie для работы сайта, аналитики и улучшения сервиса. Нажимая «Принять все», вы
            соглашаетесь с использованием всех cookie. Подробнее — в
            <NuxtLink to="/privacy" class="underline hover:no-underline">Политике конфиденциальности</NuxtLink>.
          </p>
          <div class="flex flex-wrap items-center gap-2">
            <button
              type="button"
              class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900"
              @click="acceptAll"
            >
              Принять все
            </button>
            <button
              type="button"
              class="rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700 dark:focus:ring-offset-neutral-900"
              @click="necessaryOnly"
            >
              Только обязательные
            </button>
            <button
              type="button"
              class="rounded-md px-3 py-2 text-sm font-medium text-neutral-600 hover:text-neutral-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:text-neutral-400 dark:hover:text-neutral-200 dark:focus:ring-offset-neutral-900"
              @click="decline"
            >
              Отказаться
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </ClientOnly>
</template>

<script setup lang="ts">
const CONSENT_KEY = 'maddam_consent'
const CONSENT_VALUES = ['full', 'necessary', 'rejected'] as const
type ConsentValue = (typeof CONSENT_VALUES)[number]

const props = withDefaults(
  defineProps<{
    position?: 'banner' | 'modal'
  }>(),
  { position: 'banner' }
)

const visible = ref(false)
const { submitConsent } = useApi()

function getStoredConsent(): ConsentValue | null {
  if (import.meta.server) return null
  const fromStorage = localStorage.getItem(CONSENT_KEY)
  if (fromStorage && CONSENT_VALUES.includes(fromStorage as ConsentValue)) {
    return fromStorage as ConsentValue
  }
  const cookies = document.cookie.split(';')
  for (const c of cookies) {
    const [name, value] = c.trim().split('=')
    if (name === CONSENT_KEY && value && CONSENT_VALUES.includes(value as ConsentValue)) {
      return value as ConsentValue
    }
  }
  return null
}

function setConsent(value: ConsentValue) {
  if (import.meta.server) return
  localStorage.setItem(CONSENT_KEY, value)
  document.cookie = `${CONSENT_KEY}=${value};path=/;max-age=31536000;samesite=lax`
}

function sendConsentToBackend(consentType: string) {
  const sessionId = typeof document !== 'undefined' ? document.cookie.match(/sessionid=([^;]+)/)?.[1] ?? '' : ''
  const urlReferer = typeof document !== 'undefined' ? document.referer || '' : ''
  submitConsent({
    consent_type: consentType,
    session_id: sessionId,
    url_referer: urlReferer
  }).catch(() => {
    // Non-blocking: consent stored locally even if backend fails
  })
}

function enableAnalytics() {
  if (import.meta.server) return
  const config = useRuntimeConfig().public
  // Только сервисы, соответствующие законодательству РФ (например, Яндекс.Метрика)
  const ymId = config.ymId as string | undefined
  if (ymId && typeof window !== 'undefined') {
    const script = document.createElement('script')
    script.async = true
    script.innerHTML = `(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");ym(${ymId}, "init", {clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true});`
    document.head.appendChild(script)
  }
}

function acceptAll() {
  setConsent('full')
  sendConsentToBackend('full')
  enableAnalytics()
  visible.value = false
}

function necessaryOnly() {
  setConsent('necessary')
  sendConsentToBackend('necessary')
  visible.value = false
}

function decline() {
  setConsent('rejected')
  sendConsentToBackend('rejected')
  visible.value = false
}

onMounted(() => {
  const consent = getStoredConsent()
  if (!consent) {
    visible.value = true
  }
})
</script>

<style scoped>
.consent-fade-enter-active,
.consent-fade-leave-active {
  transition: opacity 0.2s ease;
}
.consent-fade-enter-from,
.consent-fade-leave-to {
  opacity: 0;
}
</style>
