<template>
  <nav
    v-if="items.length > 0"
    class="breadcrumbs"
    aria-label="Breadcrumb navigation"
  >
    <ol class="breadcrumbs__list">
      <li
        v-for="(item, index) in items"
        :key="index"
        class="breadcrumbs__item"
      >
        <router-link
          v-if="item.to"
          :to="item.to"
          class="breadcrumbs__link"
          :aria-current="index === items.length - 1 ? 'page' : undefined"
        >
          {{ item.label }}
        </router-link>
        <span
          v-else
          class="breadcrumbs__current"
          :aria-current="index === items.length - 1 ? 'page' : undefined"
        >
          {{ item.label }}
        </span>
        <span
          v-if="index < items.length - 1"
          class="breadcrumbs__separator"
          aria-hidden="true"
        >
          /
        </span>
      </li>
    </ol>
  </nav>
</template>

<script setup lang="ts">
interface BreadcrumbItem {
  label: string
  to?: string | null
}

defineProps<{
  items: BreadcrumbItem[]
}>()
</script>

<style scoped>
.breadcrumbs {
  margin-bottom: 1rem;
}

.breadcrumbs__list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0.5rem;
}

.breadcrumbs__item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.breadcrumbs__link {
  color: var(--color-text-secondary, #6b7280);
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 200ms ease;
}

.breadcrumbs__link:hover {
  color: var(--color-primary, #3b82f6);
}

.breadcrumbs__current {
  color: var(--color-text, #111827);
  font-size: 0.875rem;
  font-weight: 500;
}

.breadcrumbs__separator {
  color: var(--color-text-secondary, #9ca3af);
  font-size: 0.875rem;
}

@media (prefers-reduced-motion: reduce) {
  .breadcrumbs__link {
    transition: none;
  }
}
</style>



