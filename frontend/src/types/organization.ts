/**
 * TypeScript types for multi-tenancy / organization support.
 *
 * Sprint 3: Frontend Integration.
 */

export type OrganizationStatus = 'trial' | 'active' | 'suspended' | 'archived'
export type DeploymentMode = 'saas' | 'standalone'
export type OrganizationRole = 'owner' | 'admin' | 'member' | 'viewer'

export interface Organization {
  id: string
  name: string
  slug: string
  status: OrganizationStatus
  deployment_mode: DeploymentMode
  branding_color: string
  logo: string | null
}

export interface OrganizationWithRole extends Organization {
  role: OrganizationRole
  is_default?: boolean
}

export interface OrganizationDetail extends Organization {
  description: string
  email: string
  phone: string
  website: string
  industry: string
  is_active: boolean
  storage_limit_gb: number | null
  max_users: number
  max_ai_analyses_monthly: number
  subscription?: OrganizationSubscription
  domain_settings?: DomainSettings
  member_count: number
  storage_used_gb: number
  active_users_count: number
  is_storage_exceeded: boolean
  is_user_limit_exceeded: boolean
  can_perform_ai_analysis: boolean
  created_at: string
  updated_at: string
}

export interface OrganizationSubscription {
  id: string
  plan: string
  plan_detail?: Plan
  billing_cycle: 'monthly' | 'yearly'
  amount: number
  currency: string
  status: 'trial' | 'active' | 'paused' | 'cancelled' | 'expired'
  started_at: string
  trial_ends_at: string | null
  current_period_start: string | null
  current_period_end: string | null
}

export interface Plan {
  id: string
  name: string
  description: string
  price_monthly: number
  price_yearly: number
  currency: string
  storage_gb: number
  max_users: number
  max_ai_analyses_monthly: number
  max_documents: number | null
  has_advanced_ai: boolean
  has_analytics: boolean
  has_distribution: boolean
  has_custom_domain: boolean
  has_api_access: boolean
  has_workflow: boolean
  sort_order: number
  is_active: boolean
  is_public: boolean
}

export interface DomainSettings {
  custom_domain: string
  is_verified: boolean
  verification_token: string
  ssl_enabled: boolean
  verified_at: string | null
  created_at: string
}

/**
 * Payload type for updating an organization (PATCH).
 * Only includes mutable fields.
 */
export interface OrganizationUpdateInput {
  name?: string
  slug?: string
  description?: string
  email?: string
  phone?: string
  website?: string
  industry?: string
  branding_color?: string
  storage_limit_gb?: number | null
  max_users?: number
  max_ai_analyses_monthly?: number
}

export interface OrganizationMember {
  id: number
  user_detail: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
  }
  role: OrganizationRole
  is_default: boolean
  joined_at: string
}
