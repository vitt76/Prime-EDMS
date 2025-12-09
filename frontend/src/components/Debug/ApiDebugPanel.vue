<script setup lang="ts">
/**
 * API Debug Panel
 * ===============
 * 
 * Development-only component that displays raw API responses
 * for debugging the Mayan → Frontend adapter transformation.
 */

import { computed, ref } from 'vue'
import { useAssetStore } from '@/stores/assetStore'

const assetStore = useAssetStore()

// Check if we're in dev mode
const isDev = ref(import.meta.env.DEV)

const isVisible = computed(() => isDev.value && assetStore.debugMode && assetStore.lastRawResponse)

const rawJson = computed(() => {
  if (!assetStore.lastRawResponse) return '{}'
  
  // Show first result only for cleaner display
  const data = assetStore.lastRawResponse
  return JSON.stringify({
    count: data.count,
    next: data.next,
    previous: data.previous,
    first_result: data.results?.[0] || null,
    results_count: data.results?.length || 0
  }, null, 2)
})

const adaptedJson = computed(() => {
  if (!assetStore.assets.length) return '{}'
  
  const firstAsset = assetStore.assets[0]
  return JSON.stringify(firstAsset, null, 2)
})

function toggleDebugMode() {
  assetStore.debugMode = !assetStore.debugMode
}
</script>

<template></template>

<style scoped>
.api-debug-panel {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  z-index: 9999;
}

.debug-toggle {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: #1f2937;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.debug-toggle:hover {
  background: #374151;
}

.debug-toggle.active {
  background: #7c3aed;
}

.debug-content {
  position: absolute;
  bottom: 100%;
  right: 0;
  margin-bottom: 0.5rem;
  width: 700px;
  max-width: calc(100vw - 2rem);
  max-height: 60vh;
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.debug-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  padding: 0.75rem;
  max-height: 300px;
  overflow-y: auto;
}

.debug-section {
  background: #f3f4f6;
  border-radius: 0.5rem;
  padding: 0.5rem;
}

.debug-section-title {
  display: flex;
  align-items: center;
  font-size: 0.7rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.debug-json {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.65rem;
  line-height: 1.4;
  color: #1f2937;
  background: white;
  padding: 0.5rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  max-height: 200px;
  white-space: pre-wrap;
  word-break: break-word;
}

.debug-footer {
  padding: 0.5rem 1rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

/* Transitions */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
