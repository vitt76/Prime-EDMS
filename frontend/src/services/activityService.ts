import { apiService } from './apiService'

export interface ActivityActor {
  id: number | null
  username: string
  full_name: string
}

export interface ActivityTarget {
  id: number
  type: string
  label: string
  url: string | null
}

export interface HeadlessActivityItem {
  id: number
  timestamp: string
  actor: ActivityActor
  verb: string
  verb_code: string
  target: ActivityTarget | null
  description: string
}

export interface ActivityFeedResponse {
  count: number
  page: number
  page_size: number
  total_pages?: number
  results: HeadlessActivityItem[]
}

export interface ActivityFeedOptions {
  filter?: 'my_actions' | 'my_documents' | 'all'
  page?: number
  page_size?: number
}

export interface ActivityItem {
  id: number
  user: string
  user_id: number | null
  timestamp: string
  description: string
  target?: string | null
}

const BFF_ENABLED = import.meta.env.VITE_BFF_ENABLED === 'true'

export async function getActivityFeed(
  options: ActivityFeedOptions = {}
): Promise<ActivityFeedResponse> {
  if (!BFF_ENABLED) {
    return {
      count: 0,
      page: options.page || 1,
      page_size: options.page_size || 20,
      results: []
    }
  }

  const params = new URLSearchParams()
  if (options.filter) params.append('filter', options.filter)
  if (options.page) params.append('page', options.page.toString())
  if (options.page_size) params.append('page_size', options.page_size.toString())

  const queryString = params.toString()
  const url = queryString
    ? `/api/v4/headless/activity/feed/?${queryString}`
    : '/api/v4/headless/activity/feed/'

  return apiService.get<ActivityFeedResponse>(url)
}

export async function getActivityFeedNormalized(
  limit = 20
): Promise<ActivityItem[]> {
  const response = await getActivityFeed({
    filter: 'my_actions',
    page: 1,
    page_size: limit
  })

  return response.results.map((item) => ({
    id: item.id,
    user: item.actor?.username || 'system',
    user_id: item.actor?.id ?? null,
    timestamp: item.timestamp,
    description: item.description,
    target: item.target?.label ?? null
  }))
}

