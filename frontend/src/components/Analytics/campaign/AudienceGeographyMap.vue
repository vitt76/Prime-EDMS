<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-2">
      <h3 class="text-base font-semibold text-neutral-900">Audience Geography</h3>
      <div class="text-xs text-neutral-500">heat map</div>
    </div>

    <div class="text-sm text-neutral-500">
      Гео-аналитика для кампаний требует привязки событий (views/downloads) к geo_country.
      Сейчас данных нет — компонент подготовлен под Phase 3 интеграции.
    </div>
  </Card>
</template>

<script setup lang="ts">
import Card from '@/components/Common/Card.vue'
</script>


