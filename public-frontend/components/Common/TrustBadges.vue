<template>
  <div class="flex flex-wrap items-center justify-center gap-6 lg:gap-8">
    <div class="flex items-center gap-2 rounded-lg bg-white px-4 py-2 shadow-sm ring-1 ring-neutral-200">
      <ShieldCheckIcon class="h-5 w-5 text-success" />
      <div class="text-left">
        <div class="text-xs font-semibold text-neutral-900">SOC 2 Type II</div>
        <div class="text-xs text-neutral-500">Certified</div>
      </div>
    </div>

    <div class="flex items-center gap-2 rounded-lg bg-white px-4 py-2 shadow-sm ring-1 ring-neutral-200">
      <LockClosedIcon class="h-5 w-5 text-primary-600" />
      <div class="text-left">
        <div class="text-xs font-semibold text-neutral-900">256-bit SSL</div>
        <div class="text-xs text-neutral-500">Encrypted</div>
      </div>
    </div>

    <div class="flex items-center gap-2 rounded-lg bg-white px-4 py-2 shadow-sm ring-1 ring-neutral-200">
      <DocumentCheckIcon class="h-5 w-5 text-info" />
      <div class="text-left">
        <div class="text-xs font-semibold text-neutral-900">GDPR</div>
        <div class="text-xs text-neutral-500">Compliant</div>
      </div>
    </div>

    <div class="flex items-center gap-2 rounded-lg bg-white px-4 py-2 shadow-sm ring-1 ring-neutral-200">
      <div class="flex">
        <StarIcon v-for="i in 5" :key="i" class="h-4 w-4 fill-yellow-400 text-yellow-400" />
      </div>
      <div class="text-left">
        <div class="text-xs font-semibold text-neutral-900">4.8/5 on G2</div>
        <div class="text-xs text-neutral-500">250+ reviews</div>
      </div>
    </div>

    <div class="flex items-center gap-2 rounded-lg bg-success/10 px-4 py-2">
      <BoltIcon class="h-5 w-5 text-success" />
      <div class="text-left">
        <div class="text-xs font-semibold text-success-700">99.9% Uptime</div>
        <div class="text-xs text-success-600">Last 12 months</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { BoltIcon, DocumentCheckIcon, LockClosedIcon, ShieldCheckIcon, StarIcon } from '@heroicons/vue/24/solid'
</script>
