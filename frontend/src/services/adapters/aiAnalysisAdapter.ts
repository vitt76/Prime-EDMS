/**
 * Adapter for converting backend AI analysis data to frontend format
 */

import type { AITag, SEOData, OCRData, ColorData, AIAnalysis } from '@/mocks/ai'

/**
 * Backend AI analysis response format
 */
export interface BackendAIAnalysis {
  id: number
  document: number
  ai_description: string | null
  ai_tags: string[]
  dominant_colors: Array<{ hex: string; rgb?: number[] }> | string[]
  alt_text: string | null
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed'
  ai_provider: string | null
  analysis_completed: string | null
  ocr_text?: string | null
  ocr_status?: 'not_run' | 'completed' | 'processing' | 'failed'
  tags_with_confidence?: AITag[]
  colors_with_percentage?: ColorData[]
  seo_keywords?: string[]
}

/**
 * Map backend analysis_status to frontend status
 */
function mapAnalysisStatus(
  status: 'pending' | 'processing' | 'completed' | 'failed'
): 'pending' | 'processing' | 'completed' | 'failed' {
  return status
}

/**
 * Adapt tags from backend format to frontend format
 */
function adaptTags(
  tags: AITag[] | string[] | undefined
): AITag[] {
  if (!tags || tags.length === 0) {
    return []
  }

  // If already in AITag format (from tags_with_confidence)
  if (tags.length > 0 && typeof tags[0] === 'object' && 'label' in tags[0]) {
    return tags as AITag[]
  }

  // If string array, convert to AITag format
  return (tags as string[]).map((tag, idx) => ({
    id: `tag-${idx}`,
    label: tag,
    confidence: 80,
    category: 'object' as const,
    source: 'unknown' as const
  }))
}

/**
 * Adapt SEO data from backend format to frontend format
 */
function adaptSEO(backendAnalysis: BackendAIAnalysis): SEOData | null {
  if (!backendAnalysis.ai_description && !backendAnalysis.alt_text) {
    return null
  }

  const keywords = backendAnalysis.seo_keywords || 
                   backendAnalysis.ai_tags?.slice(0, 10) || 
                   []

  return {
    altText: backendAnalysis.alt_text || '',
    description: backendAnalysis.ai_description || '',
    keywords
  }
}

/**
 * Adapt OCR data from backend format to frontend format
 */
function adaptOCR(backendAnalysis: BackendAIAnalysis): OCRData {
  const status = backendAnalysis.ocr_status || 'not_run'
  const text = backendAnalysis.ocr_text || undefined

  let wordCount: number | undefined
  if (text && text.trim()) {
    // Count words only if text is not empty
    const words = text.split(/\s+/).filter(word => word.length > 0)
    wordCount = words.length
  } else if (status === 'completed') {
    // If status is completed but no text, set wordCount to 0
    wordCount = 0
  }

  return {
    status: status as 'not_run' | 'processing' | 'completed' | 'failed',
    text: text?.trim() || undefined, // Normalize empty strings to undefined
    wordCount,
    confidence: undefined // Backend doesn't provide OCR confidence
  }
}

/**
 * Adapt colors from backend format to frontend format
 */
function adaptColors(
  colors: ColorData[] | Array<{ hex: string; rgb?: number[] }> | string[] | undefined
): ColorData[] {
  if (!colors || colors.length === 0) {
    return []
  }

  // If already in ColorData format (from colors_with_percentage)
  if (colors.length > 0 && typeof colors[0] === 'object' && 'percentage' in colors[0]) {
    return colors as ColorData[]
  }

  // If array of objects with hex
  if (colors.length > 0 && typeof colors[0] === 'object' && 'hex' in colors[0]) {
    const total = colors.length
    const percentage = total > 0 ? round(100 / total, 1) : 0
    return (colors as Array<{ hex: string }>).map(color => ({
      hex: color.hex,
      percentage
    }))
  }

  // If string array, treat as hex values
  const total = colors.length
  const percentage = total > 0 ? round(100 / total, 1) : 0
  return (colors as string[]).map(hex => ({
    hex,
    percentage
  }))
}

/**
 * Round number to specified decimal places
 */
function round(value: number, decimals: number): number {
  return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)
}

/**
 * Main adapter function: convert backend AI analysis to frontend format
 */
export function adaptBackendAIAnalysisToFrontend(
  backendAnalysis: BackendAIAnalysis | null
): AIAnalysis | null {
  if (!backendAnalysis) {
    if (import.meta.env.DEV) {
      console.log('[AIAnalysisAdapter] No backend analysis data')
    }
    return null
  }

  if (import.meta.env.DEV) {
    console.log('[AIAnalysisAdapter] Adapting backend analysis:', backendAnalysis)
  }

  const result = {
    status: mapAnalysisStatus(backendAnalysis.analysis_status),
    analyzedAt: backendAnalysis.analysis_completed || null,
    tags: adaptTags(
      backendAnalysis.tags_with_confidence || backendAnalysis.ai_tags
    ),
    seo: adaptSEO(backendAnalysis),
    ocr: adaptOCR(backendAnalysis),
    colorPalette: adaptColors(
      backendAnalysis.colors_with_percentage || backendAnalysis.dominant_colors
    )
  }

  if (import.meta.env.DEV) {
    console.log('[AIAnalysisAdapter] Adapted result:', result)
  }

  return result
}
