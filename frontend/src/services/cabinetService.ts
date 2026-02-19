import { apiService } from './apiService'
import { withRetry } from '@/utils/retry'
import type {
  BulkDocumentsPayload,
  CabinetDTO,
  CreateCabinetPayload,
  UpdateCabinetPayload
} from '@/types/cabinets'
import type { FolderNode } from '@/mocks/folders'

function mapCabinetDtoToFolder(dto: CabinetDTO): FolderNode {
  return {
    id: dto.id.toString(),
    name: dto.label,
    type: 'local',
    parentId: dto.parent_id !== null ? dto.parent_id.toString() : null,
    children: (dto.children || []).map(mapCabinetDtoToFolder),
    expanded: false,
    assetCount: dto.document_count || 0,
    createdAt: dto.created_at || '',
    updatedAt: dto.updated_at || '',
    canEdit: Boolean(dto.can_edit),
    canDelete: Boolean(dto.can_delete),
    canAddChildren: Boolean(dto.can_add_children),
  }
}

export function mapCabinetTreeToFolders(tree: CabinetDTO[]): FolderNode[] {
  return tree.map(mapCabinetDtoToFolder)
}

const CABINET_BASE = '/api/v4/cabinets'

class CabinetService {
  async getCabinetTree(useCache = false): Promise<FolderNode[]> {
    const operation = () =>
      apiService.get<CabinetDTO[]>(`${CABINET_BASE}/tree/`, undefined, useCache)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return mapCabinetTreeToFolders(result.data || [])
  }

  /** Get a single cabinet by ID (for collection detail). */
  async getCabinet(cabinetId: number, useCache = false): Promise<CabinetDTO> {
    const operation = () =>
      apiService.get<CabinetDTO>(`${CABINET_BASE}/${cabinetId}/`, undefined, useCache)
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    return result.data!
  }

  /** Get flat list of cabinets (for list views). */
  async getCabinetList(useCache = false): Promise<CabinetDTO[]> {
    const operation = () =>
      apiService.get<CabinetDTO[] | { results: CabinetDTO[] }>(
        `${CABINET_BASE}/`,
        undefined,
        useCache
      )
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    const data = result.data!
    const list = Array.isArray(data) ? data : (data as { results: CabinetDTO[] }).results || []
    return list
  }

  /** Get documents in a cabinet (paginated). */
  async getCabinetDocuments(
    cabinetId: number,
    params?: { page?: number; page_size?: number }
  ): Promise<{ results: unknown[]; count: number }> {
    const operation = () =>
      apiService.get<{ results: unknown[]; count: number }>(
        `${CABINET_BASE}/${cabinetId}/documents/`,
        { params }
      )
    const result = await withRetry(operation)
    if (!result.success) throw result.error
    const data = result.data!
    return {
      results: data.results || (Array.isArray(data) ? data : []),
      count: (data as { count?: number }).count ?? (data.results?.length ?? 0)
    }
  }

  async createCabinet(payload: CreateCabinetPayload): Promise<FolderNode> {
    const operation = () =>
      apiService.post<CabinetDTO>(`${CABINET_BASE}/`, payload)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return mapCabinetDtoToFolder(result.data!)
  }

  async updateCabinet(
    cabinetId: number,
    payload: UpdateCabinetPayload
  ): Promise<FolderNode> {
    const operation = () =>
      apiService.patch<CabinetDTO>(`${CABINET_BASE}/${cabinetId}/`, payload)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return mapCabinetDtoToFolder(result.data!)
  }

  async deleteCabinet(cabinetId: number): Promise<void> {
    const operation = () => apiService.delete(`${CABINET_BASE}/${cabinetId}/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  async addDocumentsToCabinet(
    cabinetId: number,
    documentIds: number[]
  ): Promise<void> {
    const payload: BulkDocumentsPayload = { documents: documentIds }
    const operation = () =>
      apiService.post(
        `${CABINET_BASE}/${cabinetId}/documents/bulk-add/`,
        payload
      )
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  async removeDocumentsFromCabinet(
    cabinetId: number,
    documentIds: number[]
  ): Promise<void> {
    const payload: BulkDocumentsPayload = { documents: documentIds }
    const operation = () =>
      apiService.post(
        `${CABINET_BASE}/${cabinetId}/documents/bulk-remove/`,
        payload
      )
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }
}

export const cabinetService = new CabinetService()

