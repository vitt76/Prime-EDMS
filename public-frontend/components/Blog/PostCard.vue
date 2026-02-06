<template>
  <article class="group overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-neutral-200/80 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:ring-primary-200">
    <!-- Image -->
    <div class="relative aspect-video overflow-hidden bg-neutral-100">
      <NuxtImg 
        v-if="post.featured_image"
        :src="post.featured_image"
        :alt="post.title"
        class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        loading="lazy"
        format="webp"
        quality="80"
      />
      <div v-else class="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary-100 to-primary-200">
        <DocumentTextIcon class="h-12 w-12 text-primary-400" />
      </div>

      <!-- Category Badge -->
      <div v-if="post.category" class="absolute left-4 top-4">
        <span class="inline-flex items-center rounded-full bg-primary-600 px-3 py-1 text-xs font-medium text-white shadow-lg">
          {{ post.category }}
        </span>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      <!-- Meta -->
      <div class="flex items-center gap-3 text-sm text-neutral-500">
        <time :datetime="post.published_at" class="flex items-center gap-1">
          <CalendarIcon class="h-4 w-4" />
          {{ formatDate(post.published_at) }}
        </time>
        <span class="text-neutral-300">•</span>
        <span class="flex items-center gap-1">
          <ClockIcon class="h-4 w-4" />
          {{ post.reading_time_minutes || 5 }} мин
        </span>
      </div>

      <!-- Title -->
      <h3 class="mt-3 line-clamp-2 text-xl font-semibold text-neutral-900 transition group-hover:text-primary-600">
        <NuxtLink :to="`/blog/${post.slug}`" class="hover:underline">
          {{ post.title }}
        </NuxtLink>
      </h3>

      <!-- Excerpt -->
      <p class="mt-2 line-clamp-3 text-sm leading-relaxed text-neutral-600">
        {{ post.excerpt }}
      </p>

      <!-- Tags -->
      <div v-if="post.tags?.length" class="mt-4 flex flex-wrap gap-2">
        <span 
          v-for="tag in post.tags.slice(0, 3)" 
          :key="tag" 
          class="inline-flex items-center rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-600"
        >
          #{{ tag }}
        </span>
        <span 
          v-if="post.tags.length > 3" 
          class="inline-flex items-center rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-500"
        >
          +{{ post.tags.length - 3 }}
        </span>
      </div>

      <!-- Author & CTA -->
      <div class="mt-6 flex items-center justify-between border-t border-neutral-100 pt-4">
        <div v-if="post.author_name" class="flex items-center gap-3">
          <div 
            v-if="post.author_avatar"
            class="h-9 w-9 overflow-hidden rounded-full ring-2 ring-white"
          >
            <img 
              :src="post.author_avatar"
              :alt="post.author_name"
              class="h-full w-full object-cover"
            />
          </div>
          <div v-else class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-sm font-bold text-white ring-2 ring-white">
            {{ post.author_name.charAt(0).toUpperCase() }}
          </div>
          <div>
            <span class="text-sm font-medium text-neutral-900">{{ post.author_name }}</span>
            <p v-if="post.author_role" class="text-xs text-neutral-500">{{ post.author_role }}</p>
          </div>
        </div>

        <NuxtLink 
          :to="`/blog/${post.slug}`"
          class="inline-flex items-center gap-1 text-sm font-medium text-primary-600 transition hover:text-primary-700 hover:gap-2"
        >
          Читать
          <ArrowRightIcon class="h-4 w-4" />
        </NuxtLink>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { PublicPost } from '~/types/content'
import { 
  ArrowRightIcon, 
  CalendarIcon, 
  ClockIcon,
  DocumentTextIcon 
} from '@heroicons/vue/24/outline'

defineProps<{
  post: PublicPost
}>()

const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>
