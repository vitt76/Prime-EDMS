import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import AssetContextMenu from '@/components/DAM/AssetContextMenu.vue'
import type { Asset } from '@/types/api'

const mockAsset: Asset = {
  id: 1,
  label: 'Test asset',
  filename: 'test.jpg',
  size: 1024,
  mime_type: 'image/jpeg',
  date_added: '2024-01-01T00:00:00Z'
}

/** Component uses Teleport to="body", so menu/overlay live in document.body. */
function getTeleportedMenu() {
  return document.body.querySelector<HTMLElement>('[role="menu"]')
}
function getTeleportedOverlay() {
  return document.body.querySelector<HTMLElement>('.fixed.inset-0')
}
function getTeleportedMenuButtons() {
  return document.body.querySelectorAll<HTMLButtonElement>('[role="menu"] button[role="menuitem"]')
}

describe('AssetContextMenu', () => {
  it('does not render menu when open is false', () => {
    const wrapper = mount(AssetContextMenu, {
      props: { open: false, x: 100, y: 100, asset: mockAsset },
      attachTo: document.body
    })
    expect(getTeleportedMenu()).toBeNull()
    wrapper.unmount()
  })

  it('renders menu when open is true and asset is set', async () => {
    const wrapper = mount(AssetContextMenu, {
      props: { open: true, x: 100, y: 100, asset: mockAsset },
      attachTo: document.body
    })
    await nextTick()
    const menu = getTeleportedMenu()
    expect(menu).toBeTruthy()
    expect(menu?.getAttribute('aria-label')).toBe('Действия с активом')
    expect(menu?.textContent).toMatch(/Открыть|Скачать|Поделиться|Редактировать|Удалить/)
    wrapper.unmount()
  })

  it('emits close when overlay is clicked', async () => {
    const wrapper = mount(AssetContextMenu, {
      props: { open: true, x: 100, y: 100, asset: mockAsset },
      attachTo: document.body
    })
    await nextTick()
    const overlay = getTeleportedOverlay()
    expect(overlay).toBeTruthy()
    overlay!.click()
    await nextTick()
    expect(wrapper.emitted('close')).toHaveLength(1)
    wrapper.unmount()
  })

  it('emits close when Escape is pressed', async () => {
    const wrapper = mount(AssetContextMenu, {
      props: { open: true, x: 100, y: 100, asset: mockAsset },
      attachTo: document.body
    })
    await nextTick()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await nextTick()
    expect(wrapper.emitted('close')).toHaveLength(1)
    wrapper.unmount()
  })

  it('emits download and close when Download is clicked', async () => {
    const wrapper = mount(AssetContextMenu, {
      props: { open: true, x: 100, y: 100, asset: mockAsset },
      attachTo: document.body
    })
    await nextTick()
    const buttons = getTeleportedMenuButtons()
    const downloadBtn = Array.from(buttons).find((b) => b.textContent?.includes('Скачать'))
    expect(downloadBtn).toBeDefined()
    downloadBtn!.click()
    await nextTick()
    expect(wrapper.emitted('download')).toHaveLength(1)
    expect(wrapper.emitted('download')![0]).toEqual([mockAsset])
    expect(wrapper.emitted('close')).toHaveLength(1)
    wrapper.unmount()
  })

  it('emits open and close when Open is clicked', async () => {
    const wrapper = mount(AssetContextMenu, {
      props: { open: true, x: 100, y: 100, asset: mockAsset },
      attachTo: document.body
    })
    await nextTick()
    const buttons = getTeleportedMenuButtons()
    const openBtn = Array.from(buttons).find((b) => b.textContent?.includes('Открыть'))
    expect(openBtn).toBeDefined()
    openBtn!.click()
    await nextTick()
    expect(wrapper.emitted('open')).toHaveLength(1)
    expect(wrapper.emitted('open')![0]).toEqual([mockAsset])
    expect(wrapper.emitted('close')).toHaveLength(1)
    wrapper.unmount()
  })
})
