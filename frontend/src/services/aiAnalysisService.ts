import { apiService } from './apiService'
import { adaptBackendAIAnalysisToFrontend, type BackendAIAnalysis } from '@/services/adapters/aiAnalysisAdapter'
import type { AIAnalysis, OCRData, SEOData } from '@/mocks/ai'

class AIAnalysisService {
  /**
   * Get AI analysis for a document
   * @param assetId - Document ID
   */
  async getAIAnalysis(assetId: number): Promise<AIAnalysis | null> {
    try {
      // Use DAM document detail endpoint which includes ai_analysis
      // Note: DAM URLs are registered directly under /api/v4/ without 'dam/' prefix
      const response = await apiService.get<{ ai_analysis: BackendAIAnalysis | null }>(
        `/api/v4/document-detail/${assetId}/`,
        undefined,
        false // Don't cache AI analysis
      )

      if (import.meta.env.DEV) {
        console.log('[AIAnalysisService] Raw response:', response)
      }

      const backendAnalysis = response?.ai_analysis || null
      if (import.meta.env.DEV) {
        console.log('[AIAnalysisService] Backend analysis:', backendAnalysis)
      }
      
      return adaptBackendAIAnalysisToFrontend(backendAnalysis)
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[AIAnalysisService] Failed to get AI analysis:', {
          assetId,
          error: err,
          status: err?.response?.status,
          data: err?.response?.data
        })
      }
      throw err
    }
  }

  /**
   * Run AI analysis for a document
   * @param assetId - Document ID
   */
  async runAIAnalysis(assetId: number): Promise<void> {
    try {
      // PrimaryKeyRelatedField accepts the ID directly as document_instance
      // Note: DAM URLs are registered directly under /api/v4/ without 'dam/' prefix
      await apiService.post(
        '/api/v4/ai-analysis/analyze/',
        { document_instance: assetId }
      )
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[AIAnalysisService] Failed to run AI analysis:', {
          assetId,
          error: err,
          status: err?.response?.status,
          data: err?.response?.data
        })
      }
      throw err
    }
  }

  /**
   * Run OCR extraction for a document
   * @param assetId - Document ID
   */
  async runOCR(assetId: number): Promise<OCRData> {
    try {
      // Use the standard OCR submit endpoint from OCR module
      // This endpoint submits the document for OCR processing
      const response = await apiService.post<{ task_id?: string; status?: string }>(
        `/api/v4/documents/${assetId}/ocr/submit/`
      )

      if (import.meta.env.DEV) {
        console.log('[AIAnalysisService] OCR submit response:', response)
      }

      // Return processing status - frontend should poll for completion
      return {
        status: 'processing',
        text: undefined,
        wordCount: undefined,
        confidence: undefined
      }
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[AIAnalysisService] Failed to run OCR:', {
          assetId,
          error: err,
          status: err?.response?.status,
          data: err?.response?.data
        })
      }
      throw err
    }
  }

  /**
   * Regenerate SEO description for a document
   * @param assetId - Document ID
   */
  async regenerateSEO(assetId: number): Promise<SEOData> {
    try {
      // Trigger new AI analysis
      await this.runAIAnalysis(assetId)

      // Wait a bit and then fetch updated data
      // In a real implementation, you might want to poll for completion
      await new Promise(resolve => setTimeout(resolve, 2000))

      const analysis = await this.getAIAnalysis(assetId)
      if (!analysis || !analysis.seo) {
        throw new Error('Failed to regenerate SEO data')
      }

      return analysis.seo
    } catch (err: any) {
      if (import.meta.env.DEV) {
        console.error('[AIAnalysisService] Failed to regenerate SEO:', {
          assetId,
          error: err
        })
      }
      throw err
    }
  }

  /**
   * Accept a tag (placeholder - backend doesn't support this yet)
   * @param assetId - Document ID
   * @param tagId - Tag ID
   */
  async acceptTag(assetId: number, tagId: string): Promise<void> {
    // TODO: Implement when backend supports tag acceptance
    if (import.meta.env.DEV) {
      console.warn('[AIAnalysisService] acceptTag not implemented yet')
    }
  }

  /**
   * Reject a tag (placeholder - backend doesn't support this yet)
   * @param assetId - Document ID
   * @param tagId - Tag ID
   */
  async rejectTag(assetId: number, tagId: string): Promise<void> {
    // TODO: Implement when backend supports tag rejection
    if (import.meta.env.DEV) {
      console.warn('[AIAnalysisService] rejectTag not implemented yet')
    }
  }
}

export const aiAnalysisService = new AIAnalysisService()
