<template>
  <section class="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-neutral-50 py-16 md:py-24 lg:py-32">
    <!-- Background Pattern -->
    <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-5"></div>
    
    <!-- Decorative Blobs -->
    <div class="absolute -left-40 -top-40 h-80 w-80 rounded-full bg-primary-200/30 blur-3xl"></div>
    <div class="absolute -bottom-40 -right-40 h-80 w-80 rounded-full bg-primary-300/20 blur-3xl"></div>
    
    <div class="relative mx-auto grid max-w-container gap-12 px-4 md:grid-cols-2 md:items-center lg:gap-16">
      <!-- Content -->
      <div class="space-y-6 md:space-y-8">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-2 text-sm font-medium text-primary-700 ring-1 ring-primary-200/50">
          <SparklesIcon class="h-4 w-4" />
          <span>{{ badge }}</span>
        </div>
        
        <!-- Heading -->
        <h1 class="text-4xl font-bold leading-tight tracking-tight text-neutral-900 md:text-5xl lg:text-6xl">
          {{ heading }}
        </h1>
        
        <!-- Subheading -->
        <p class="text-lg leading-relaxed text-neutral-600 md:text-xl">
          {{ subheading }}
        </p>

        <!-- CTAs -->
        <div class="flex flex-col gap-3 sm:flex-row sm:gap-4">
          <NuxtLink 
            :to="ctaUrl" 
            class="group inline-flex items-center justify-center gap-2 rounded-xl bg-primary-600 px-6 py-3.5 text-base font-semibold text-white shadow-lg shadow-primary-600/30 transition-all hover:bg-primary-700 hover:shadow-xl hover:shadow-primary-600/40"
          >
            {{ ctaText }}
            <ArrowRightIcon class="h-5 w-5 transition-transform group-hover:translate-x-1" />
          </NuxtLink>
          
          <button 
            @click="showDemoModal = true"
            class="group inline-flex items-center justify-center gap-2 rounded-xl border-2 border-neutral-200 bg-white px-6 py-3.5 text-base font-semibold text-neutral-700 transition-all hover:border-neutral-300 hover:bg-neutral-50 hover:shadow-md"
          >
            <PlayCircleIcon class="h-5 w-5 text-primary-600" />
            {{ demoText }}
          </button>
        </div>

        <!-- Social Proof -->
        <div class="flex flex-col gap-4 pt-4 sm:flex-row sm:items-center">
          <div class="flex -space-x-3">
            <div 
              v-for="i in 4" 
              :key="i" 
              class="flex h-10 w-10 items-center justify-center rounded-full border-2 border-white bg-gradient-to-br from-primary-400 to-primary-600 text-xs font-bold text-white shadow-sm"
            >
              {{ ['AB', 'CD', 'EF', 'GH'][i-1] }}
            </div>
            <div class="flex h-10 w-10 items-center justify-center rounded-full border-2 border-white bg-neutral-100 text-xs font-semibold text-neutral-600 shadow-sm">
              +99
            </div>
          </div>
          <div class="text-sm">
            <div class="font-semibold text-neutral-900">{{ $t('hero.teams') }}</div>
            <div class="text-neutral-500">{{ $t('hero.socialProof') }}</div>
          </div>
        </div>
      </div>

      <!-- Visual -->
      <div class="relative">
        <!-- Main Visual Container -->
        <div class="relative rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 p-1.5 shadow-2xl shadow-primary-600/20">
          <div class="rounded-xl bg-white p-3 md:p-4">
            <NuxtImg 
              v-if="backgroundImage"
              :src="backgroundImage"
              :alt="heading"
              class="rounded-lg shadow-inner"
              loading="eager"
              format="webp"
              quality="80"
              width="600"
              height="400"
            />
            <div v-else class="aspect-[4/3] overflow-hidden rounded-lg bg-gradient-to-br from-neutral-100 to-neutral-200">
              <!-- Placeholder UI -->
              <div class="flex h-full flex-col">
                <div class="flex h-8 items-center gap-2 border-b border-neutral-200 bg-neutral-50 px-3">
                  <div class="flex gap-1.5">
                    <div class="h-2.5 w-2.5 rounded-full bg-red-400"></div>
                    <div class="h-2.5 w-2.5 rounded-full bg-yellow-400"></div>
                    <div class="h-2.5 w-2.5 rounded-full bg-green-400"></div>
                  </div>
                  <div class="h-4 flex-1 rounded bg-neutral-200"></div>
                </div>
                <div class="flex flex-1 p-3">
                  <div class="w-1/4 space-y-2 border-r border-neutral-200 pr-3">
                    <div class="h-3 w-full rounded bg-neutral-200"></div>
                    <div class="h-3 w-3/4 rounded bg-neutral-200"></div>
                    <div class="h-3 w-5/6 rounded bg-neutral-200"></div>
                  </div>
                  <div class="flex-1 grid grid-cols-3 gap-2 p-3">
                    <div v-for="n in 6" :key="n" class="aspect-square rounded-lg bg-gradient-to-br from-primary-100 to-primary-200"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Elements -->
        <div class="absolute -right-2 -top-2 rounded-xl bg-white p-3 shadow-xl ring-1 ring-neutral-100 md:-right-4 md:-top-4 md:p-4">
          <div class="flex items-center gap-2">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-success/10">
              <CheckCircleIcon class="h-5 w-5 text-success" />
            </div>
            <span class="text-sm font-semibold text-neutral-900">AI-powered</span>
          </div>
        </div>

        <div class="absolute -bottom-2 -left-2 rounded-xl bg-white p-3 shadow-xl ring-1 ring-neutral-100 md:-bottom-4 md:-left-4 md:p-4">
          <div class="flex items-center gap-2">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-100">
              <BoltIcon class="h-5 w-5 text-primary-600" />
            </div>
            <div class="text-sm">
              <div class="font-semibold text-neutral-900">99.9%</div>
              <div class="text-xs text-neutral-500">Uptime</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Demo Modal -->
    <DemoVideoModal v-model="showDemoModal" />
  </section>
</template>

<script setup lang="ts">
import { 
  ArrowRightIcon, 
  PlayCircleIcon, 
  SparklesIcon, 
  CheckCircleIcon,
  BoltIcon
} from '@heroicons/vue/24/outline'

withDefaults(
  defineProps<{
    heading: string
    subheading: string
    ctaText: string
    ctaUrl: string
    demoText?: string
    backgroundImage?: string
    badge?: string
  }>(),
  { 
    demoText: 'Демо видео',
    badge: 'Новинка: AI Search 2.0'
  }
)

const showDemoModal = ref(false)
</script>
