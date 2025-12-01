import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import TagInput from '@/components/Common/TagInput.vue'

describe('TagInput', () => {
  let wrapper: ReturnType<typeof mount>

  const mockSuggestions = ['tag1', 'tag2', 'tag3', 'campaign', 'hero']

  beforeEach(() => {
    wrapper = mount(TagInput, {
      props: {
        modelValue: [],
        suggestions: mockSuggestions
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays input field', () => {
    const input = wrapper.find('input[type="text"]')
    expect(input.exists()).toBe(true)
  })

  it('emits update:modelValue when tag is added', async () => {
    const input = wrapper.find('input[type="text"]')
    await input.setValue('new-tag')
    await input.trigger('keydown.enter')

    const events = wrapper.emitted('update:modelValue')
    expect(events).toBeTruthy()
    expect(events?.[0]?.[0]).toContain('new-tag')
  })

  it('shows suggestions dropdown when input is focused', async () => {
    const input = wrapper.find('input[type="text"]')
    await input.trigger('focus')

    await wrapper.vm.$nextTick()

    const suggestions = wrapper.find('.absolute')
    expect(suggestions.exists()).toBe(true)
  })

  it('filters suggestions based on input', async () => {
    const input = wrapper.find('input[type="text"]')
    await input.setValue('tag')
    await input.trigger('input')

    await wrapper.vm.$nextTick()

    const suggestions = wrapper.findAll('button')
    expect(suggestions.length).toBeGreaterThan(0)
  })

  it('allows selecting suggestion from dropdown', async () => {
    const input = wrapper.find('input[type="text"]')
    await input.trigger('focus')

    await wrapper.vm.$nextTick()

    const suggestionButton = wrapper.findAll('button').find((btn) => btn.text().includes('tag1'))
    if (suggestionButton) {
      await suggestionButton.trigger('mousedown')

      const events = wrapper.emitted('update:modelValue')
      expect(events).toBeTruthy()
    }
  })

  it('displays selected tags as badges', async () => {
    await wrapper.setProps({ modelValue: ['tag1', 'tag2'] })

    await wrapper.vm.$nextTick()

    const badges = wrapper.findAllComponents({ name: 'Badge' })
    expect(badges.length).toBe(2)
  })

  it('allows removing tag by clicking X button', async () => {
    await wrapper.setProps({ modelValue: ['tag1'] })

    await wrapper.vm.$nextTick()

    const removeButton = wrapper.find('button[aria-label="Удалить тег"]')
    await removeButton.trigger('click')

    const events = wrapper.emitted('update:modelValue')
    expect(events).toBeTruthy()
    expect(events?.[0]?.[0]).not.toContain('tag1')
  })

  it('removes last tag on backspace when input is empty', async () => {
    await wrapper.setProps({ modelValue: ['tag1'] })

    await wrapper.vm.$nextTick()

    const input = wrapper.find('input[type="text"]')
    await input.trigger('keydown.backspace')

    const events = wrapper.emitted('update:modelValue')
    expect(events).toBeTruthy()
  })
})

