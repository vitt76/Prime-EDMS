<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Campaign Timeline</h3>
      <div class="text-xs text-neutral-500">
        <span v-if="velocity.days_to_launch !== undefined">to launch: {{ velocity.days_to_launch }}d</span>
        <span v-if="velocity.days_to_peak !== undefined" class="ml-2">to peak: {{ velocity.days_to_peak }}d</span>
      </div>
    </div>

    <div v-if="milestones.length === 0" class="text-sm text-neutral-500">Нет данных</div>

    <div v-else class="flex flex-wrap gap-3">
      <div
        v-for="m in milestones"
        :key="`${m.type}-${m.date}`"
        class="px-3 py-2 rounded-md border border-neutral-200 bg-white"
      >
        <div class="text-xs text-neutral-500">{{ m.type }}</div>
        <div class="text-sm font-semibold text-neutral-900">{{ m.label }}</div>
        <div class="text-xs text-neutral-500">{{ m.date }}</div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
import type { CampaignTimelineResponse } from '@/stores/analyticsStore'

defineProps<{
  milestones: CampaignTimelineResponse['milestones']
  velocity: CampaignTimelineResponse['velocity']
}>()
</script>


