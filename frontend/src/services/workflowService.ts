import { apiService } from './apiService'

export interface WorkflowInstance {
  id: number
  workflow_template: {
    id: number
    label: string
    internal_name: string
  }
  current_state: {
    id: number
    label: string
    initial: boolean
    completion: boolean
  }
  last_log_entry: WorkflowLogEntry | null
  log_entries_url: string
  log_entry_transitions_url: string
  url: string
}

export interface WorkflowTransition {
  id: number
  label: string
  origin_state_id: number
  destination_state_id: number
  condition: string
  url: string
}

export interface WorkflowLogEntry {
  id: number
  transition: WorkflowTransition
  transition_id: number
  comment: string
  datetime: string
  user: {
    id: number
    username: string
    first_name: string
    last_name: string
  }
  extra_data: Record<string, any>
}

class WorkflowService {
  /**
   * Get all workflow instances for a document
   */
  async getWorkflowInstances(documentId: number): Promise<WorkflowInstance[]> {
    const response = await apiService.get<{ results: WorkflowInstance[] }>(
      `/api/v4/documents/${documentId}/workflow_instances/`
    )
    return Array.isArray(response) ? response : response.results || []
  }

  /**
   * Get workflow instance details
   */
  async getWorkflowInstance(
    documentId: number,
    workflowInstanceId: number
  ): Promise<WorkflowInstance> {
    return await apiService.get<WorkflowInstance>(
      `/api/v4/documents/${documentId}/workflow_instances/${workflowInstanceId}/`
    )
  }

  /**
   * Get available transitions for a workflow instance
   */
  async getAvailableTransitions(
    documentId: number,
    workflowInstanceId: number
  ): Promise<WorkflowTransition[]> {
    const response = await apiService.get<{ results: WorkflowTransition[] }>(
      `/api/v4/documents/${documentId}/workflow_instances/${workflowInstanceId}/log_entries/transitions/`,
      undefined,
      false // Disable cache to always get fresh transitions
    )
    const transitions = Array.isArray(response) ? response : response.results || []
    return transitions
  }

  /**
   * Get workflow log entries (history)
   */
  async getWorkflowHistory(
    documentId: number,
    workflowInstanceId: number
  ): Promise<WorkflowLogEntry[]> {
    const response = await apiService.get<{ results: WorkflowLogEntry[] }>(
      `/api/v4/documents/${documentId}/workflow_instances/${workflowInstanceId}/log_entries/`
    )
    return Array.isArray(response) ? response : response.results || []
  }

  /**
   * Execute a workflow transition
   */
  async executeTransition(
    documentId: number,
    workflowInstanceId: number,
    transitionId: number,
    comment?: string
  ): Promise<WorkflowLogEntry> {
    return await apiService.post<WorkflowLogEntry>(
      `/api/v4/documents/${documentId}/workflow_instances/${workflowInstanceId}/log_entries/`,
      {
        transition_id: transitionId,
        comment: comment || '',
        extra_data: '{}' // Backend expects JSON string, not object
      }
    )
  }

  /**
   * Launch a workflow for a document
   */
  async launchWorkflow(
    documentId: number,
    workflowTemplateId: number
  ): Promise<void> {
    await apiService.post(
      `/api/v4/documents/${documentId}/workflow_instances/launch/`,
      {
        workflow_template_id: workflowTemplateId
      }
    )
  }

  /**
   * Get available workflow templates for a document type
   * Note: API doesn't return document_types in workflow template list, so we need to check each template
   */
  async getAvailableWorkflowTemplates(documentTypeId: number): Promise<Array<{ id: number; label: string }>> {
    try {
      // Get all workflow templates
      const response = await apiService.get<{ results: Array<{ id: number; label: string }> }>(
        `/api/v4/workflow_templates/`
      )
      const allTemplates = Array.isArray(response) ? response : response.results || []
      
      if (allTemplates.length === 0) {
        return []
      }
      
      // Check document types for each workflow template
      const availableTemplates: Array<{ id: number; label: string }> = []
      
      for (const template of allTemplates) {
        try {
          // Get document types for this workflow template
          const docTypesResponse = await apiService.get<{ results: Array<{ id: number }> }>(
            `/api/v4/workflow_templates/${template.id}/document_types/`
          )
          const docTypes = Array.isArray(docTypesResponse) ? docTypesResponse : docTypesResponse.results || []
          
          // Check if this document type is in the list
          if (docTypes.some((dt: { id: number }) => dt.id === documentTypeId)) {
            availableTemplates.push({ id: template.id, label: template.label })
          }
        } catch (err) {
          console.warn(`[WorkflowService] Failed to get document types for workflow ${template.id}:`, err)
          // Continue to next template
        }
      }
      
      return availableTemplates
    } catch (error) {
      console.error('[WorkflowService] Failed to get available workflow templates:', error)
      return []
    }
  }
}

export const workflowService = new WorkflowService()

