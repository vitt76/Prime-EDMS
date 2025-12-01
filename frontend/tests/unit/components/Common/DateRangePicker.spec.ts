import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DateRangePicker from '@/components/Common/DateRangePicker.vue'

describe('DateRangePicker', () => {
  let wrapper: ReturnType<typeof mount>

  beforeEach(() => {
    wrapper = mount(DateRangePicker)
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('displays start and end date inputs', () => {
    const inputs = wrapper.findAll('input[type="date"]')
    expect(inputs.length).toBe(2)
  })

  it('emits update:modelValue when dates are selected', async () => {
    const startInput = wrapper.findAll('input[type="date"]')[0]
    const endInput = wrapper.findAll('input[type="date"]')[1]

    await startInput.setValue('2025-01-01')
    await endInput.setValue('2025-01-31')

    await wrapper.vm.$nextTick()

    const events = wrapper.emitted('update:modelValue')
    expect(events).toBeTruthy()
    expect(events?.[0]?.[0]).toEqual(['2025-01-01', '2025-01-31'])
  })

  it('has quick preset buttons', () => {
    const presets = ['Сегодня', 'Неделя', 'Месяц', 'Год']
    presets.forEach((preset) => {
      expect(wrapper.text()).toContain(preset)
    })
  })

  it('applies preset when clicked', async () => {
    const todayButton = wrapper.findAll('button').find((btn) => btn.text().includes('Сегодня'))
    if (todayButton) {
      await todayButton.trigger('click')

      await wrapper.vm.$nextTick()

      const events = wrapper.emitted('update:modelValue')
      expect(events).toBeTruthy()
      const [start, end] = events?.[0]?.[0] as [string, string]
      expect(start).toBe(end) // Today preset sets same date for start and end
    }
  })

  it('sets end date min to start date', async () => {
    const startInput = wrapper.findAll('input[type="date"]')[0]
    await startInput.setValue('2025-01-15')

    await wrapper.vm.$nextTick()

    const endInput = wrapper.findAll('input[type="date"]')[1]
    expect(endInput.attributes('min')).toBe('2025-01-15')
  })

  it('initializes from modelValue prop', async () => {
    await wrapper.setProps({
      modelValue: ['2025-01-01', '2025-01-31']
    })

    await wrapper.vm.$nextTick()

    const startInput = wrapper.findAll('input[type="date"]')[0]
    const endInput = wrapper.findAll('input[type="date"]')[1]

    expect(startInput.element.value).toBe('2025-01-01')
    expect(endInput.element.value).toBe('2025-01-31')
  })
})

