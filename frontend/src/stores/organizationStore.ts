/**
 * Organization Pinia Store.
 *
 * Sprint 3: Manages current organization context, org switching,
 * and role-based getters for the frontend.
 *
 * Sprint 4: Fixed isLoading usage, race condition guard,
 * replaced dynamic require() with async import().
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { OrganizationWithRole } from '@/types/organization'

const ORG_STORAGE_KEY = 'current_organization_id'

export const useOrganizationStore = defineStore('organization', () => {
  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  const currentOrganization = ref<OrganizationWithRole | null>(null)
  const userOrganizations = ref<OrganizationWithRole[]>([])
  const isLoading = ref(false)
  const isSwitching = ref(false)

  /** Guard flag to prevent concurrent initialize() calls. */
  let _initializing = false

  // ---------------------------------------------------------------------------
  // Getters
  // ---------------------------------------------------------------------------
  const isOwner = computed(
    () => currentOrganization.value?.role === 'owner'
  )
  const isAdmin = computed(() =>
    ['owner', 'admin'].includes(currentOrganization.value?.role ?? '')
  )
  const isMember = computed(() =>
    ['owner', 'admin', 'member'].includes(
      currentOrganization.value?.role ?? ''
    )
  )
  const isViewer = computed(
    () => currentOrganization.value?.role === 'viewer'
  )
  const canManageMembers = computed(() => isAdmin.value)
  const isSaasMode = computed(
    () => currentOrganization.value?.deployment_mode === 'saas'
  )
  const hasMultipleOrgs = computed(
    () => userOrganizations.value.length > 1
  )

  // ---------------------------------------------------------------------------
  // Actions
  // ---------------------------------------------------------------------------

  /**
   * Initialize from auth/me response (called after login / token validation).
   *
   * Guarded against concurrent calls to avoid race conditions.
   *
   * @param organization  Current organization from response.
   * @param organizations All orgs the user belongs to.
   */
  function initialize(
    organization: OrganizationWithRole | null,
    organizations: OrganizationWithRole[]
  ) {
    if (_initializing) return
    _initializing = true
    isLoading.value = true

    try {
      userOrganizations.value = organizations

      // If we have a stored org preference, try to use it
      const storedOrgId = localStorage.getItem(ORG_STORAGE_KEY)
      if (storedOrgId) {
        const stored = organizations.find((o) => o.id === storedOrgId)
        if (stored) {
          currentOrganization.value = stored
          return
        }
      }

      // Fallback to the one resolved by middleware (from auth/me)
      if (organization) {
        currentOrganization.value = organization
        localStorage.setItem(ORG_STORAGE_KEY, organization.id)
        return
      }

      // Fallback to first org in the list
      if (organizations.length > 0) {
        currentOrganization.value = organizations[0]
        localStorage.setItem(ORG_STORAGE_KEY, organizations[0].id)
      }
    } finally {
      isLoading.value = false
      _initializing = false
    }
  }

  /**
   * Switch the active organization (SPA-side).
   * Updates localStorage and triggers a full store/cache clear.
   */
  async function switchOrganization(orgId: string) {
    const org = userOrganizations.value.find((o) => o.id === orgId)
    if (!org) {
      console.warn('[OrgStore] Cannot switch to unknown organization:', orgId)
      return
    }

    isSwitching.value = true
    currentOrganization.value = org
    localStorage.setItem(ORG_STORAGE_KEY, orgId)

    // Clear all cached data — different org means different data
    try {
      const { cacheService } = await import('@/services/cacheService')
      cacheService.clear()
    } catch {
      // Ignore if cache service is not available
    } finally {
      isSwitching.value = false
    }
  }

  /**
   * Refresh organization data from the organizations list
   * (useful after backend-side updates).
   */
  function refreshOrganization(updatedOrg: OrganizationWithRole) {
    currentOrganization.value = updatedOrg
    const idx = userOrganizations.value.findIndex(
      (o) => o.id === updatedOrg.id
    )
    if (idx !== -1) {
      userOrganizations.value[idx] = updatedOrg
    }
  }

  /**
   * Clear organization state (called on logout).
   */
  function $reset() {
    currentOrganization.value = null
    userOrganizations.value = []
    isLoading.value = false
    isSwitching.value = false
    _initializing = false
    localStorage.removeItem(ORG_STORAGE_KEY)
  }

  return {
    // State
    currentOrganization,
    userOrganizations,
    isLoading,
    isSwitching,
    // Getters
    isOwner,
    isAdmin,
    isMember,
    isViewer,
    canManageMembers,
    isSaasMode,
    hasMultipleOrgs,
    // Actions
    initialize,
    switchOrganization,
    refreshOrganization,
    $reset,
  }
})
