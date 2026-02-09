<template>
  <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-sm dark:bg-neutral-800">
    <h1 class="text-2xl font-semibold text-neutral-900 dark:text-white">
      {{ $t('auth.registerTitle') }}
    </h1>
    <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
      {{ $t('auth.registerSubtitle') }}
    </p>
    <div class="mt-6">
      <FormsRegisterForm />
    </div>
    <NuxtLink to="/" class="mt-4 inline-block text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
      &larr; {{ $t('errors.backHome') }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })
</script>
