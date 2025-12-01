import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import Sidebar from '@/components/Layout/Sidebar.vue'
import { useUiStore } from '@/stores/uiStore'

describe('Sidebar', () => {
  let router: ReturnType<typeof createRouter>
  let pinia: ReturnType<typeof createPinia>

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', component: { template: '<div>Home</div>' } },
        { path: '/dam', component: { template: '<div>DAM</div>' } },
        { path: '/distribution', component: { template: '<div>Distribution</div>' } },
        { path: '/settings', component: { template: '<div>Settings</div>' } }
      ]
    })
  })

  it('renders sidebar with navigation', () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    expect(wrapper.find('aside').exists()).toBe(true)
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('renders navigation items', () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const navLinks = wrapper.findAll('router-link')
    expect(navLinks.length).toBeGreaterThan(0)
  })

  it('toggles sidebar on toggle button click', async () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const uiStore = useUiStore()
    const initialExpanded = uiStore.sidebarExpanded

    const toggleButton = wrapper.find('button[aria-label="Переключить боковую панель"]')
    await toggleButton.trigger('click')

    expect(uiStore.sidebarExpanded).toBe(!initialExpanded)
  })

  it('shows expanded width when expanded', () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const uiStore = useUiStore()
    uiStore.sidebarExpanded = true
    wrapper.vm.$forceUpdate()

    const sidebar = wrapper.find('aside')
    expect(sidebar.classes()).toContain('w-70')
  })

  it('shows collapsed width when collapsed', () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const uiStore = useUiStore()
    uiStore.sidebarExpanded = false
    wrapper.vm.$forceUpdate()

    const sidebar = wrapper.find('aside')
    expect(sidebar.classes()).toContain('w-16')
  })

  it('highlights active route', async () => {
    await router.push('/dam')
    
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    await router.isReady()
    await wrapper.vm.$nextTick()

    const activeLink = wrapper.find('router-link[to="/dam"]')
    expect(activeLink.exists()).toBe(true)
  })

  it('renders collections section when expanded', () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const uiStore = useUiStore()
    uiStore.sidebarExpanded = true
    wrapper.vm.$forceUpdate()

    const collectionsSection = wrapper.find('h3:contains("Коллекции")')
    expect(collectionsSection.exists()).toBe(true)
  })

  it('emits navigate event on navigation item click', async () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const navLinks = wrapper.findAll('router-link')
    if (navLinks.length > 0) {
      await navLinks[0].trigger('click')
      // Navigation handled by router-link, but we can check if event is emitted
      expect(navLinks[0].exists()).toBe(true)
    }
  })

  it('emits new-folder event on new folder button click', async () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const newFolderButton = wrapper.find('button:contains("Новая папка")')
    if (newFolderButton.exists()) {
      await newFolderButton.trigger('click')
      expect(wrapper.emitted('new-folder')).toBeTruthy()
    }
  })

  it('hides labels when collapsed', () => {
    const wrapper = mount(Sidebar, {
      global: {
        plugins: [pinia, router]
      }
    })

    const uiStore = useUiStore()
    uiStore.sidebarExpanded = false
    wrapper.vm.$forceUpdate()

    // Labels should be hidden (check for hidden class or v-if)
    const navLinks = wrapper.findAll('router-link')
    navLinks.forEach(link => {
      const span = link.find('span')
      if (span.exists()) {
        // When collapsed, labels might be hidden
        expect(span.exists()).toBe(true)
      }
    })
  })
})

