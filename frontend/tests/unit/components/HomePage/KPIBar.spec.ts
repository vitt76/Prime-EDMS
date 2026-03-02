import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import KPIBar from '@/components/HomePage/KPIBar.vue'
import { createPinia, setActivePinia } from 'pinia'
import { useHomeStore } from '@/stores/homeStore'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/dam', name: 'dam-gallery', component: {} }
  ]
})

describe('KPIBar.vue', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders kpi cards with data from homeStore', async () => {
    const store = useHomeStore()
    store.documentsStats = { total: 100, new_7days: 5, new_30days: 10 }
    store.aiStats = { analyzed: 50, queued: 2, pending: 0, failed: 0 }
    store.inboxStats = { unread_total: 3, comments_new: 1, approvals_pending: 1, collections_shared: 1, mentions: 0 }

    const wrapper = mount(KPIBar, {
      global: {
        plugins: [router],
        stubs: {
          RouterLink: true
        }
      }
    })

    const text = wrapper.text()
    expect(text).toContain('Всего документов')
    expect(text).toContain('100')
    expect(text).toContain('+5')
    
    expect(text).toContain('Завершённых анализов')
    expect(text).toContain('50')
    expect(text).toContain('2 в очереди')
    
    expect(text).toContain('Требуется действие')
    expect(text).toContain('3')
  })
})
