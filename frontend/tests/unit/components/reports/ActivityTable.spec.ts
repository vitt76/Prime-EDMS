import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ActivityTable from '@/components/reports/ActivityTable.vue'
import type { UserActivity } from '@/types/reports'

describe('ActivityTable', () => {
  let wrapper: ReturnType<typeof mount>

  const mockActivities: UserActivity[] = [
    {
      username: 'user1',
      email: 'user1@example.com',
      action: 'upload',
      asset_id: 1,
      asset_name: 'test.jpg',
      timestamp: '2025-01-01T00:00:00Z'
    },
    {
      username: 'user2',
      email: 'user2@example.com',
      action: 'download',
      asset_id: 2,
      asset_name: 'test2.jpg',
      timestamp: '2025-01-02T00:00:00Z'
    },
    {
      username: 'user3',
      email: 'user3@example.com',
      action: 'view',
      asset_id: null,
      asset_name: null,
      timestamp: '2025-01-03T00:00:00Z'
    }
  ]

  beforeEach(() => {
    // Mock current time for timestamp formatting
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2025-01-15T12:00:00Z'))
  })

  afterEach(() => {
    vi.clearAllMocks()
    vi.useRealTimers()
    wrapper?.unmount()
  })

  it('renders correctly', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.activity-table').exists()).toBe(true)
  })

  it('displays loading state', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: [],
        isLoading: true
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.find('.activity-table__loading').exists()).toBe(true)
    expect(wrapper.find('.activity-table__skeleton-row').exists()).toBe(true)
  })

  it('displays empty state when no activities', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: [],
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.find('.activity-table__empty').exists()).toBe(true)
    expect(wrapper.text()).toContain('No activity data available')
  })

  it('displays activities in table', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.find('.activity-table__table').exists()).toBe(true)
    expect(wrapper.findAll('.activity-table__row').length).toBe(3)
  })

  it('formats action labels correctly', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.text()).toContain('Upload')
    expect(wrapper.text()).toContain('Download')
    expect(wrapper.text()).toContain('View')
  })

  it('formats timestamps correctly', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: [
          {
            username: 'user1',
            email: 'user1@example.com',
            action: 'upload',
            asset_id: 1,
            asset_name: 'test.jpg',
            timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString() // 5 minutes ago
          }
        ],
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.text()).toContain('5m ago')
  })

  it('displays user information correctly', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.text()).toContain('user1')
    expect(wrapper.text()).toContain('user1@example.com')
  })

  it('displays asset name when available', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.text()).toContain('test.jpg')
    expect(wrapper.text()).toContain('test2.jpg')
  })

  it('displays dash when asset name is not available', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: [
          {
            username: 'user1',
            email: 'user1@example.com',
            action: 'view',
            asset_id: null,
            asset_name: null,
            timestamp: '2025-01-01T00:00:00Z'
          }
        ],
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    expect(wrapper.text()).toContain('—')
  })

  it('applies correct badge classes for different actions', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: [
          {
            username: 'user1',
            email: 'user1@example.com',
            action: 'upload',
            asset_id: 1,
            asset_name: 'test.jpg',
            timestamp: '2025-01-01T00:00:00Z'
          },
          {
            username: 'user2',
            email: 'user2@example.com',
            action: 'delete',
            asset_id: 2,
            asset_name: 'test2.jpg',
            timestamp: '2025-01-02T00:00:00Z'
          }
        ],
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    const badges = wrapper.findAll('.activity-table__badge')
    expect(badges[0]?.classes()).toContain('activity-table__badge--upload')
    expect(badges[1]?.classes()).toContain('activity-table__badge--delete')
  })

  it('has correct ARIA attributes', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    const table = wrapper.find('.activity-table__table')
    expect(table.attributes('role')).toBe('table')
    expect(table.attributes('aria-label')).toBe('User activity log')
  })

  it('has semantic time element with datetime attribute', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false
      },
      global: {
        stubs: {
          Pagination: true
        }
      }
    })

    const timeElements = wrapper.findAll('time')
    expect(timeElements.length).toBeGreaterThan(0)
    expect(timeElements[0]?.attributes('datetime')).toBe('2025-01-01T00:00:00Z')
  })

  it('displays pagination when activities exceed page size', () => {
    const manyActivities: UserActivity[] = Array.from({ length: 25 }, (_, i) => ({
      username: `user${i}`,
      email: `user${i}@example.com`,
      action: 'upload' as const,
      asset_id: i,
      asset_name: `test${i}.jpg`,
      timestamp: new Date().toISOString()
    }))

    wrapper = mount(ActivityTable, {
      props: {
        activities: manyActivities,
        isLoading: false,
        pageSize: 10,
        showPagination: true
      }
    })

    const pagination = wrapper.findComponent({ name: 'Pagination' })
    expect(pagination.exists()).toBe(true)
  })

  it('does not display pagination when activities fit in one page', () => {
    wrapper = mount(ActivityTable, {
      props: {
        activities: mockActivities,
        isLoading: false,
        pageSize: 10,
        showPagination: true
      }
    })

    const pagination = wrapper.findComponent({ name: 'Pagination' })
    expect(pagination.exists()).toBe(false)
  })

  it('paginates activities correctly', async () => {
    const manyActivities: UserActivity[] = Array.from({ length: 25 }, (_, i) => ({
      username: `user${i}`,
      email: `user${i}@example.com`,
      action: 'upload' as const,
      asset_id: i,
      asset_name: `test${i}.jpg`,
      timestamp: new Date().toISOString()
    }))

    wrapper = mount(ActivityTable, {
      props: {
        activities: manyActivities,
        isLoading: false,
        pageSize: 10,
        showPagination: true
      }
    })

    // First page should show 10 items
    expect(wrapper.findAll('.activity-table__row').length).toBe(10)

    // Change to page 2
    const pagination = wrapper.findComponent({ name: 'Pagination' })
    if (pagination.exists()) {
      await pagination.vm.$emit('page-change', 2)
      await wrapper.vm.$nextTick()

      // Second page should show next 10 items
      expect(wrapper.findAll('.activity-table__row').length).toBe(10)
    }
  })

  it('handles pagination when showPagination is false', () => {
    const manyActivities: UserActivity[] = Array.from({ length: 25 }, (_, i) => ({
      username: `user${i}`,
      email: `user${i}@example.com`,
      action: 'upload' as const,
      asset_id: i,
      asset_name: `test${i}.jpg`,
      timestamp: new Date().toISOString()
    }))

    wrapper = mount(ActivityTable, {
      props: {
        activities: manyActivities,
        isLoading: false,
        pageSize: 10,
        showPagination: false
      }
    })

    // Should show all activities when pagination is disabled
    expect(wrapper.findAll('.activity-table__row').length).toBe(25)
    expect(wrapper.findComponent({ name: 'Pagination' }).exists()).toBe(false)
  })
})

