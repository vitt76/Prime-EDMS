import { apiService } from './apiService'

export interface MetadataFieldConfig {
  id: number
  name: string
  label: string
  type: 'text' | 'number' | 'date' | 'select' | 'email' | 'url'
  required: boolean
  validation_regex?: string | null
  default_value?: string | null
  options?: string[]
}

export interface WorkflowConfig {
  id: number
  label: string
  initial_state: string | null
}

export interface RetentionPolicy {
  enabled: boolean
  days: number
}

export interface Capabilities {
  ocr_enabled: boolean
  ai_analysis_enabled: boolean
  preview_enabled: boolean
}

export interface DocumentTypeBasic {
  id: number
  label: string
  description: string
  url: string
}

export interface DocumentTypeConfig {
  id: number
  label: string
  description: string
  required_metadata: MetadataFieldConfig[]
  optional_metadata: MetadataFieldConfig[]
  workflows: WorkflowConfig[]
  retention_policy: RetentionPolicy
  capabilities: Capabilities
}

const BFF_ENABLED = import.meta.env.VITE_BFF_ENABLED === 'true'

export async function getAllDocumentTypes(): Promise<DocumentTypeBasic[]> {
  if (!BFF_ENABLED) return []
  return apiService.get<DocumentTypeBasic[]>('/api/v4/headless/config/document_types/')
}

export async function getDocumentTypeConfig(documentTypeId: number): Promise<DocumentTypeConfig> {
  if (!BFF_ENABLED) {
    throw new Error('Headless API не включен. Невозможно получить конфигурацию типов документов.')
  }
  return apiService.get<DocumentTypeConfig>(
    `/api/v4/headless/config/document_types/${documentTypeId}/`
  )
}

export function validateMetadata(
  config: DocumentTypeConfig,
  metadata: Record<string, string | undefined>
): string[] {
  const errors: string[] = []

  for (const field of config.required_metadata) {
    const value = metadata[field.name]

    if (!value || value.trim() === '') {
      errors.push(`Поле "${field.label}" обязательно для заполнения`)
      continue
    }

    if (field.validation_regex) {
      const regex = new RegExp(field.validation_regex)
      if (!regex.test(value)) {
        errors.push(`Поле "${field.label}" имеет неверный формат`)
      }
    }

    if (field.options && field.options.length > 0 && !field.options.includes(value)) {
      errors.push(`Поле "${field.label}" должно быть одним из: ${field.options.join(', ')}`)
    }
  }

  return errors
}

