<template>
  <div class="w-full max-w-md rounded-lg bg-white p-8 shadow-sm">
    <h1 class="text-2xl font-semibold">Create account</h1>
    <p class="mt-2 text-sm text-neutral-600">Заполните форму и подтвердите email.</p>
    <div class="mt-6">
      <RegisterForm />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })
</script>
