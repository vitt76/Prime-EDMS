/**
 * Metadata Service
 *
 * Handles metadata schema operations, field management,
 * and dynamic form generation for assets.
 */

import { apiService } from './apiService'
import { withRetry } from '@/utils/retry'

export interface MetadataField {
  name: string
  label: string
  type: 'text' | 'textarea' | 'select' | 'date' | 'number' | 'boolean' | 'tags' | 'file'
  required: boolean
  placeholder?: string
  help_text?: string
  description?: string
  options?: Array<{ value: string; label: string }>
  min_value?: number
  max_value?: number
  pattern?: string
  default_value?: any
  validation_rules?: Record<string, any>
  display_order: number
  is_system?: boolean
  is_visible: boolean
  permissions?: {
    can_read: boolean
    can_write: boolean
  }
}

export interface MetadataSchema {
  id: string
  name: string
  description?: string
  fields: MetadataField[]
  is_default: boolean
  is_system: boolean
  created_at: string
  updated_at: string
  created_by: string
  applies_to: string[] // Asset types this schema applies to
}

export interface CreateMetadataSchemaRequest {
  name: string
  description?: string
  fields: Omit<MetadataField, 'display_order' | 'is_system' | 'is_visible'>[]
  is_default?: boolean
  applies_to?: string[]
}

export interface UpdateMetadataSchemaRequest {
  name?: string
  description?: string
  fields?: MetadataField[]
  is_default?: boolean
  applies_to?: string[]
}

export interface AssetMetadata {
  [fieldName: string]: any
}

export interface BulkMetadataUpdate {
  asset_ids: string[]
  metadata: AssetMetadata
  schema_id?: string
}

class MetadataService {
  /**
   * Get all metadata schemas
   */
  async getMetadataSchemas(): Promise<MetadataSchema[]> {
    const operation = () => apiService.get<MetadataSchema[]>('/v4/metadata/schemas/')
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get default asset metadata schema
   */
  async getAssetMetadataSchema(): Promise<MetadataSchema> {
    const operation = () => apiService.get<MetadataSchema>('/v4/metadata/schemas/default/')
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get metadata schema by ID
   */
  async getMetadataSchema(id: string): Promise<MetadataSchema> {
    const operation = () => apiService.get<MetadataSchema>(`/v4/metadata/schemas/${id}/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Create new metadata schema
   */
  async createMetadataSchema(data: CreateMetadataSchemaRequest): Promise<MetadataSchema> {
    const operation = () => apiService.post<MetadataSchema>('/v4/metadata/schemas/', data)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Update metadata schema
   */
  async updateMetadataSchema(id: string, data: UpdateMetadataSchemaRequest): Promise<MetadataSchema> {
    const operation = () => apiService.patch<MetadataSchema>(`/v4/metadata/schemas/${id}/`, data)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Delete metadata schema
   */
  async deleteMetadataSchema(id: string): Promise<void> {
    const operation = () => apiService.delete(`/v4/metadata/schemas/${id}/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Get metadata for specific asset
   */
  async getAssetMetadata(assetId: string): Promise<AssetMetadata> {
    const operation = () => apiService.get<AssetMetadata>(`/v4/assets/${assetId}/metadata/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Update metadata for specific asset
   */
  async updateAssetMetadata(assetId: string, metadata: AssetMetadata): Promise<AssetMetadata> {
    const operation = () => apiService.patch<AssetMetadata>(`/v4/assets/${assetId}/metadata/`, metadata)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Bulk update metadata for multiple assets
   */
  async bulkUpdateMetadata(data: BulkMetadataUpdate): Promise<{
    updated_count: number
    errors: Array<{ asset_id: string; error: string }>
  }> {
    const operation = () => apiService.post('/v4/assets/metadata/bulk/', data)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get metadata field definitions
   */
  async getMetadataFields(): Promise<MetadataField[]> {
    const operation = () => apiService.get<MetadataField[]>('/v4/metadata/fields/')
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Validate metadata against schema
   */
  async validateMetadata(metadata: AssetMetadata, schemaId?: string): Promise<{
    is_valid: boolean
    errors: Record<string, string[]>
  }> {
    const operation = () => apiService.post('/v4/metadata/validate/', {
      metadata,
      schema_id: schemaId
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get metadata templates/presets
   */
  async getMetadataTemplates(): Promise<Array<{
    id: string
    name: string
    description?: string
    metadata: AssetMetadata
    schema_id?: string
    created_by: string
    is_public: boolean
  }>> {
    const operation = () => apiService.get('/v4/metadata/templates/')
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Create metadata template
   */
  async createMetadataTemplate(data: {
    name: string
    description?: string
    metadata: AssetMetadata
    schema_id?: string
    is_public?: boolean
  }): Promise<any> {
    const operation = () => apiService.post('/v4/metadata/templates/', data)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Apply metadata template to asset(s)
   */
  async applyMetadataTemplate(templateId: string, assetIds: string[]): Promise<void> {
    const operation = () => apiService.post(`/v4/metadata/templates/${templateId}/apply/`, {
      asset_ids: assetIds
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
  }

  /**
   * Get metadata extraction rules (for AI/auto-tagging)
   */
  async getMetadataExtractionRules(): Promise<Array<{
    id: string
    name: string
    field_name: string
    extraction_type: 'ai_tagging' | 'regex' | 'filename_pattern' | 'exif' | 'custom'
    config: Record<string, any>
    is_active: boolean
  }>> {
    const operation = () => apiService.get('/v4/metadata/extraction-rules/')
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Extract metadata from asset using AI/rules
   */
  async extractMetadata(assetId: string, rules?: string[]): Promise<AssetMetadata> {
    const operation = () => apiService.post<AssetMetadata>(`/v4/assets/${assetId}/metadata/extract/`, {
      rules
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Get metadata history for asset
   */
  async getMetadataHistory(assetId: string): Promise<Array<{
    id: string
    timestamp: string
    user: string
    changes: Record<string, { old_value: any; new_value: any }>
    change_type: 'created' | 'updated' | 'deleted'
  }>> {
    const operation = () => apiService.get(`/v4/assets/${assetId}/metadata/history/`)
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Export metadata for assets
   */
  async exportMetadata(assetIds: string[], format: 'csv' | 'json' | 'xml' = 'csv'): Promise<string> {
    const operation = () => apiService.post<{ download_url: string }>('/v4/assets/metadata/export/', {
      asset_ids: assetIds,
      format
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!.download_url
  }

  /**
   * Import metadata from file
   */
  async importMetadata(file: File, options: {
    schema_id?: string
    update_existing?: boolean
    skip_errors?: boolean
  } = {}): Promise<{
    imported_count: number
    errors: Array<{ row: number; error: string }>
  }> {
    const formData = new FormData()
    formData.append('file', file)
    Object.entries(options).forEach(([key, value]) => {
      formData.append(key, String(value))
    })

    const operation = () => apiService.post('/v4/assets/metadata/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }

  /**
   * Search assets by metadata
   */
  async searchByMetadata(query: {
    field: string
    operator: 'equals' | 'contains' | 'starts_with' | 'ends_with' | 'greater_than' | 'less_than' | 'between' | 'in'
    value: any
    value2?: any // For between operator
  }[], options: {
    limit?: number
    offset?: number
    sort_by?: string
    sort_order?: 'asc' | 'desc'
  } = {}): Promise<any> {
    const operation = () => apiService.post('/v4/assets/search/metadata/', {
      filters: query,
      ...options
    })
    const result = await withRetry(operation)

    if (!result.success) throw result.error
    return result.data!
  }
}

export const metadataService = new MetadataService()






