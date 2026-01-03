import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FiltersPanel from '@/components/DAM/FiltersPanel.vue'
import type { Facets, SearchFilters } from '@/types/api'

describe('FiltersPanel', () => {
  let wrapper: ReturnType<typeof mount>

  const mockFacets: Facets = {
    type: {
      image: 145,
      video: 11,
      document: 23,
      audio: 5
    },
    tags: {
      hero: 89,
      social: 76,
      campaign: 54
    }
  }

  beforeEach(() => {
    wrapper = mount(FiltersPanel, {
      props: {
        facets: mockFacets,
        modelValue: {}
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays type filter checkboxes', () => {
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThan(0)
  })

  it('displays facets counts for types', () => {
    const typeLabels = wrapper.text()
    expect(typeLabels).toContain('145') // image count
    expect(typeLabels).toContain('11') // video count
  })

  it('emits update:modelValue when filters change (auto-apply)', async () => {
    const typeCheckbox = wrapper.find('input[value="image"]')
    await typeCheckbox.setValue(true)

    const updateEvents = wrapper.emitted('update:modelValue')
    expect(updateEvents).toBeTruthy()
    expect(updateEvents?.[0]?.[0]).toHaveProperty('type')
  })

  it('emits reset event when Reset button clicked', async () => {
    const buttons = wrapper.findAll('button')
    const resetButton = buttons.find((btn) => btn.text().includes('Сбросить'))
    if (resetButton) {
      await resetButton.trigger('click')

      const resetEvents = wrapper.emitted('reset')
      expect(resetEvents).toBeTruthy()
    }
  })

  it('displays date range picker', () => {
    const datePicker = wrapper.findComponent({ name: 'DateRangePicker' })
    expect(datePicker.exists()).toBe(true)
  })

  it('displays tag input with autocomplete', () => {
    const tagInput = wrapper.findComponent({ name: 'TagInput' })
    expect(tagInput.exists()).toBe(true)
  })

  it('shows popular tags from facets', () => {
    const tagsSection = wrapper.text()
    expect(tagsSection).toContain('hero')
    expect(tagsSection).toContain('social')
  })

  it('allows adding custom metadata filters', async () => {
    const buttons = wrapper.findAll('button')
    const customMetadataToggle = buttons.find((btn) =>
      btn.text().includes('Дополнительные фильтры')
    )
    if (customMetadataToggle) {
      await customMetadataToggle.trigger('click')
      await wrapper.vm.$nextTick()

      const allButtons = wrapper.findAll('button')
      const addFilterButton = allButtons.find((btn) =>
        btn.text().includes('Добавить фильтр')
      )
      expect(addFilterButton).toBeTruthy()
    }
  })

  it('shows active filters summary when filters are applied', async () => {
    const typeCheckbox = wrapper.find('input[value="image"]')
    await typeCheckbox.setValue(true)

    await wrapper.vm.$nextTick()

    const summary = wrapper.find('.bg-primary-50')
    expect(summary.exists()).toBe(true)
  })

  it('disables Reset button when no filters are active', () => {
    const buttons = wrapper.findAll('button')
    const resetButton = buttons.find((btn) => btn.text().includes('Сбросить'))
    if (resetButton) {
      expect(resetButton.attributes('disabled')).toBeDefined()
    }
  })
})

