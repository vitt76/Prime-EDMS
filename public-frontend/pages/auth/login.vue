<template>
  <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-sm">
    <h1 class="text-2xl font-semibold">Login</h1>
    <p class="mt-2 text-sm text-neutral-600">Вход в систему выполняется в основном приложении.</p>
    <div class="mt-6">
      <LoginForm />
    </div>
    <NuxtLink to="/" class="mt-4 inline-block text-sm text-primary-600">Back to site</NuxtLink>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })
</script>
