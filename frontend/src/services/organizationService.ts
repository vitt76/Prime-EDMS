/**
 * Organization API Service.
 *
 * Sprint 3: Frontend Integration — wraps organization REST endpoints.
 */

import { apiService } from './apiService'
import type {
  OrganizationDetail,
  OrganizationMember,
  OrganizationUpdateInput,
  OrganizationWithRole,
  Plan,
} from '@/types/organization'

const BASE = '/api/v4/headless/organizations'
const PLANS_BASE = '/api/v4/headless/plans'

class OrganizationService {
  /** GET /organizations/current/ */
  async getCurrentOrganization(): Promise<OrganizationDetail> {
    return apiService.get<OrganizationDetail>(`${BASE}/current/`, undefined, false)
  }

  /** GET /organizations/ (admin-only) */
  async listOrganizations(): Promise<OrganizationWithRole[]> {
    return apiService.get<OrganizationWithRole[]>(`${BASE}/`, undefined, false)
  }

  /** GET /organizations/:id/ */
  async getOrganization(id: string): Promise<OrganizationDetail> {
    return apiService.get<OrganizationDetail>(`${BASE}/${id}/`, undefined, false)
  }

  /** PATCH /organizations/:id/ */
  async updateOrganization(
    id: string,
    data: OrganizationUpdateInput
  ): Promise<OrganizationDetail> {
    return apiService.patch<OrganizationDetail>(`${BASE}/${id}/`, data)
  }

  /** GET /organizations/:id/members/ */
  async getMembers(id: string): Promise<OrganizationMember[]> {
    return apiService.get<OrganizationMember[]>(
      `${BASE}/${id}/members/`,
      undefined,
      false
    )
  }

  /** POST /organizations/:id/members/ */
  async addMember(
    id: string,
    userId: number,
    role: string
  ): Promise<OrganizationMember> {
    return apiService.post<OrganizationMember>(`${BASE}/${id}/members/`, {
      user_id: userId,
      role,
    })
  }

  /** DELETE /organizations/:id/members/ */
  async removeMember(id: string, userId: number): Promise<void> {
    return apiService.deleteWithBody<void>(
      `${BASE}/${id}/members/`,
      { user_id: userId }
    )
  }

  /** POST /organizations/:id/suspend/ — SuperAdmin only (ТЗ 4.5.3) */
  async suspendOrganization(
    id: string,
    reason?: string
  ): Promise<{ success: boolean; message: string; organization_id: string }> {
    return apiService.post(`${BASE}/${id}/suspend/`, reason ? { reason } : {})
  }

  /** POST /organizations/:id/activate/ — SuperAdmin only */
  async activateOrganization(
    id: string
  ): Promise<{ success: boolean; message: string; organization_id: string }> {
    return apiService.post(`${BASE}/${id}/activate/`, {})
  }

  /** GET /plans/ — plans live at /api/v4/headless/plans/, not under /organizations/ */
  async listPlans(): Promise<Plan[]> {
    return apiService.get<Plan[]>(`${PLANS_BASE}/`, undefined, true)
  }
}

export const organizationService = new OrganizationService()
