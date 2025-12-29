<template>
  <Card padding="lg">
    <div class="flex items-center justify-between gap-4 mb-4">
      <h3 class="text-base font-semibold text-neutral-900">Most Downloaded Assets</h3>
      <div class="flex items-center gap-2">
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          :disabled="rows.length === 0"
          @click="exportCsv"
        >
          CSV
        </button>
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          :disabled="rows.length === 0"
          @click="exportJson"
        >
          JSON
        </button>
        <button
          class="px-3 py-2 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          :disabled="rows.length === 0"
          @click="exportPdf"
        >
          PDF
        </button>
      </div>
    </div>

    <div class="overflow-auto border border-neutral-200 rounded-lg">
      <table class="min-w-full text-sm">
        <thead class="bg-neutral-50">
          <tr class="text-left">
            <th class="px-3 py-2 font-semibold text-neutral-700">Asset</th>
            <th class="px-3 py-2 font-semibold text-neutral-700 cursor-pointer" @click="toggleSort('downloads')">
              Downloads
              <span v-if="sortKey === 'downloads'">{{ sortDir === 'desc' ? '↓' : '↑' }}</span>
            </th>
            <th class="px-3 py-2 font-semibold text-neutral-700 cursor-pointer" @click="toggleSort('views')">
              Views
              <span v-if="sortKey === 'views'">{{ sortDir === 'desc' ? '↓' : '↑' }}</span>
            </th>
            <th class="px-3 py-2 font-semibold text-neutral-700 cursor-pointer" @click="toggleSort('shares')">
              Shares
              <span v-if="sortKey === 'shares'">{{ sortDir === 'desc' ? '↓' : '↑' }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="rows.length === 0">
            <td class="px-3 py-4 text-neutral-500" colspan="4">Нет данных</td>
          </tr>
          <tr
            v-for="row in pagedRows"
            :key="row.document_id"
            class="border-t border-neutral-200 hover:bg-neutral-50"
          >
            <td class="px-3 py-2">
              <div class="font-medium text-neutral-900">
                {{ row.document__label || `Document #${row.document_id}` }}
              </div>
              <div class="text-xs text-neutral-500">ID: {{ row.document_id }}</div>
            </td>
            <td class="px-3 py-2">{{ row.downloads }}</td>
            <td class="px-3 py-2">{{ row.views }}</td>
            <td class="px-3 py-2">{{ row.shares }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="totalPages > 1" class="flex items-center justify-between mt-4">
      <div class="text-xs text-neutral-500">
        Показано {{ startRow + 1 }}–{{ endRow }} из {{ rowsSorted.length }}
      </div>
      <div class="flex items-center gap-2">
        <button
          class="px-3 py-1.5 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          :disabled="page === 1"
          @click="page--"
        >
          Назад
        </button>
        <div class="text-sm text-neutral-700">Стр. {{ page }} / {{ totalPages }}</div>
        <button
          class="px-3 py-1.5 text-sm rounded-md border border-neutral-300 hover:bg-neutral-50"
          :disabled="page === totalPages"
          @click="page++"
        >
          Вперед
        </button>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import Card from '@/components/Common/Card.vue'
import type { MostDownloadedAssetRow } from '@/stores/analyticsStore'

const props = defineProps<{
  rows: MostDownloadedAssetRow[]
  pageSize?: number
}>()

const page = ref(1)
const pageSize = computed(() => props.pageSize ?? 10)

const sortKey = ref<'downloads' | 'views' | 'shares'>('downloads')
const sortDir = ref<'asc' | 'desc'>('desc')

watch(
  () => props.rows,
  () => {
    page.value = 1
  }
)

const rowsSorted = computed(() => {
  const key = sortKey.value
  const dir = sortDir.value
  return [...(props.rows || [])].sort((a, b) => {
    const av = a[key] ?? 0
    const bv = b[key] ?? 0
    return dir === 'desc' ? bv - av : av - bv
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(rowsSorted.value.length / pageSize.value)))
const startRow = computed(() => (page.value - 1) * pageSize.value)
const endRow = computed(() => Math.min(rowsSorted.value.length, startRow.value + pageSize.value))
const pagedRows = computed(() => rowsSorted.value.slice(startRow.value, endRow.value))

function toggleSort(key: 'downloads' | 'views' | 'shares'): void {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortKey.value = key
    sortDir.value = 'desc'
  }
}

function exportCsv(): void {
  const headers = ['document_id', 'label', 'downloads', 'views', 'shares']
  const lines = [headers.join(',')]
  for (const row of rowsSorted.value) {
    const label = (row.document__label || '').replaceAll('"', '""')
    lines.push(
      [
        row.document_id,
        `"${label}"`,
        row.downloads,
        row.views,
        row.shares,
      ].join(',')
    )
  }

  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'most-downloaded-assets.csv'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function exportJson(): void {
  const payload = rowsSorted.value.map((row) => ({
    document_id: row.document_id,
    label: row.document__label || '',
    downloads: row.downloads,
    views: row.views,
    shares: row.shares,
  }))

  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'most-downloaded-assets.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

async function exportPdf(): Promise<void> {
  const { jsPDF } = await import('jspdf')
  const autoTable = (await import('jspdf-autotable')).default

  const doc = new jsPDF({ orientation: 'landscape' })
  doc.setFontSize(14)
  doc.text('Most Downloaded Assets', 14, 14)

  const head = [['ID', 'Asset', 'Downloads', 'Views', 'Shares']]
  const body = rowsSorted.value.map((row) => [
    String(row.document_id),
    row.document__label || `Document #${row.document_id}`,
    String(row.downloads ?? 0),
    String(row.views ?? 0),
    String(row.shares ?? 0),
  ])

  autoTable(doc, {
    head,
    body,
    startY: 20,
    styles: { fontSize: 9 },
    headStyles: { fillColor: [245, 245, 245], textColor: [17, 24, 39] },
    alternateRowStyles: { fillColor: [250, 250, 250] },
  })

  doc.save('most-downloaded-assets.pdf')
}
</script>


