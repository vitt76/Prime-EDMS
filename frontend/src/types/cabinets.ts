export interface CabinetDTO {
  id: number
  label: string
  parent_id: number | null
  children?: CabinetDTO[]
  document_count?: number
  can_add_children?: boolean
  can_delete?: boolean
  can_edit?: boolean
  created_at?: string | null
  updated_at?: string | null
}

export interface CreateCabinetPayload {
  label: string
  parent?: number | null
}

export interface UpdateCabinetPayload {
  label?: string
  parent?: number | null
}

export interface BulkDocumentsPayload {
  documents: number[]
}

