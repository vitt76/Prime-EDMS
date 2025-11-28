/**
 * AI Insights Mock Data
 * Mock data for AI-powered features: Auto-tagging, SEO descriptions, OCR
 */

// ==================== Types (for AIInsightsWidget.vue) ====================

export interface AITag {
  id: string
  label: string
  confidence: number
  category: 'object' | 'scene' | 'color' | 'style' | 'emotion' | 'action'
  source: 'yandex' | 'gigachat' | 'local'
  accepted?: boolean
  rejected?: boolean
}

export interface SEOData {
  altText: string
  description: string
  keywords: string[]
}

export interface OCRData {
  status: 'not_run' | 'processing' | 'completed' | 'failed'
  text?: string
  confidence?: number
  wordCount?: number
}

export interface ColorData {
  hex: string
  percentage: number
}

export interface AIAnalysis {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  analyzedAt: string | null
  tags: AITag[]
  seo: SEOData | null
  ocr: OCRData
  colorPalette?: ColorData[]
}

// Legacy types for backward compatibility
export interface SuggestedTag {
  id: number
  name: string
  confidence: number // 0-100
  category: 'object' | 'scene' | 'color' | 'style' | 'emotion' | 'action'
  source: 'yandex' | 'gigachat' | 'local'
  accepted?: boolean
  rejected?: boolean
}

export interface SEODescription {
  text: string
  language: 'ru' | 'en'
  generatedAt: string
  provider: 'yandex' | 'gigachat'
  version: number
}

export interface OCRResult {
  text: string
  confidence: number
  language: string
  extractedAt: string
  boundingBoxes?: {
    text: string
    x: number
    y: number
    width: number
    height: number
  }[]
}

export interface AIAnalysisStatus {
  autoTagging: 'idle' | 'processing' | 'completed' | 'error'
  seoGeneration: 'idle' | 'processing' | 'completed' | 'error'
  ocr: 'idle' | 'processing' | 'completed' | 'error'
  faceDetection: 'idle' | 'processing' | 'completed' | 'error'
  objectDetection: 'idle' | 'processing' | 'completed' | 'error'
}

export interface AIInsights {
  suggestedTags: SuggestedTag[]
  seoDescription: SEODescription | null
  ocrResult: OCRResult | null
  analysisStatus: AIAnalysisStatus
  lastAnalyzedAt: string | null
  aiProvider: 'yandex' | 'gigachat' | 'mixed'
}

// ==================== Mock Data Generators ====================

const TAG_CATEGORIES = ['object', 'scene', 'color', 'style', 'emotion', 'action'] as const

const MOCK_TAGS_BY_TYPE: Record<string, SuggestedTag[]> = {
  image: [
    { id: 1, name: 'природа', confidence: 95, category: 'scene', source: 'yandex' },
    { id: 2, name: 'пейзаж', confidence: 92, category: 'scene', source: 'yandex' },
    { id: 3, name: 'небо', confidence: 88, category: 'object', source: 'gigachat' },
    { id: 4, name: 'облака', confidence: 85, category: 'object', source: 'gigachat' },
    { id: 5, name: 'синий', confidence: 78, category: 'color', source: 'local' },
    { id: 6, name: 'зелёный', confidence: 72, category: 'color', source: 'local' },
    { id: 7, name: 'спокойствие', confidence: 65, category: 'emotion', source: 'gigachat' },
    { id: 8, name: 'яркий', confidence: 60, category: 'style', source: 'yandex' },
  ],
  video: [
    { id: 1, name: 'видеоролик', confidence: 98, category: 'object', source: 'yandex' },
    { id: 2, name: 'движение', confidence: 85, category: 'action', source: 'gigachat' },
    { id: 3, name: 'люди', confidence: 82, category: 'object', source: 'yandex' },
    { id: 4, name: 'городская съёмка', confidence: 75, category: 'scene', source: 'gigachat' },
    { id: 5, name: 'динамика', confidence: 70, category: 'style', source: 'local' },
    { id: 6, name: 'интервью', confidence: 65, category: 'scene', source: 'yandex' },
  ],
  document: [
    { id: 1, name: 'документ', confidence: 99, category: 'object', source: 'local' },
    { id: 2, name: 'текст', confidence: 95, category: 'object', source: 'local' },
    { id: 3, name: 'таблица', confidence: 78, category: 'object', source: 'yandex' },
    { id: 4, name: 'отчёт', confidence: 72, category: 'scene', source: 'gigachat' },
    { id: 5, name: 'финансы', confidence: 65, category: 'scene', source: 'gigachat' },
  ],
  audio: [
    { id: 1, name: 'аудио', confidence: 99, category: 'object', source: 'local' },
    { id: 2, name: 'музыка', confidence: 85, category: 'scene', source: 'yandex' },
    { id: 3, name: 'голос', confidence: 80, category: 'object', source: 'yandex' },
    { id: 4, name: 'подкаст', confidence: 70, category: 'scene', source: 'gigachat' },
  ],
}

const SEO_TEMPLATES: Record<string, string[]> = {
  image: [
    'Красивый снимок {subject} в {style} стиле. Идеально подходит для {use_case}. Высокое качество, профессиональная съёмка.',
    'Профессиональная фотография {subject}. {description}. Подходит для коммерческого использования в {industry}.',
    '{description}. Атмосферный кадр с {mood} настроением. Отличный выбор для {use_case}.',
  ],
  video: [
    'Видеоролик с {subject}. Длительность: {duration}. Качество: {quality}. Идеально для {use_case}.',
    'Профессиональная видеосъёмка {subject}. {description}. Готово к использованию в {industry}.',
  ],
  document: [
    'Документ "{title}". Содержит информацию о {subject}. Формат: {format}. Количество страниц: {pages}.',
    'Официальный документ: {title}. {description}. Подготовлен для {use_case}.',
  ],
}

const SAMPLE_SUBJECTS = ['природа', 'архитектура', 'люди', 'продукция', 'интерьер', 'мероприятие', 'город']
const SAMPLE_STYLES = ['минималистичный', 'яркий', 'винтажный', 'современный', 'классический']
const SAMPLE_USE_CASES = ['маркетинговых материалов', 'социальных сетей', 'презентаций', 'веб-сайта', 'рекламы']
const SAMPLE_INDUSTRIES = ['IT', 'маркетинг', 'HR', 'финансы', 'образование']
const SAMPLE_MOODS = ['позитивным', 'спокойным', 'деловым', 'творческим', 'энергичным']

const OCR_SAMPLE_TEXTS = [
  `ДОГОВОР № 123/2025

О поставке товаров

г. Москва                                                    15 января 2025 г.

ООО "Рога и Копыта", именуемое в дальнейшем "Поставщик", в лице генерального директора Иванова И.И., действующего на основании Устава, с одной стороны, и ООО "Покупатель", именуемое в дальнейшем "Покупатель", в лице директора Петрова П.П., действующего на основании Устава, с другой стороны, заключили настоящий Договор о нижеследующем:

1. ПРЕДМЕТ ДОГОВОРА
1.1. Поставщик обязуется передать в собственность Покупателю, а Покупатель обязуется принять и оплатить товары согласно Спецификации.`,

  `ОТЧЁТ ПО ПРОДАЖАМ
Q4 2024

Общий объём продаж: 15,750,000 ₽
Рост по сравнению с Q3: +23%

Топ-5 продуктов:
1. Продукт А — 4,200,000 ₽
2. Продукт Б — 3,150,000 ₽
3. Продукт В — 2,800,000 ₽
4. Продукт Г — 2,100,000 ₽
5. Продукт Д — 1,500,000 ₽

Рекомендации:
- Увеличить маркетинговый бюджет на Продукт А
- Оптимизировать ценообразование на Продукт Д`,

  `ТЕХНИЧЕСКОЕ ЗАДАНИЕ

Проект: Разработка DAM-системы
Версия: 2.0
Дата: Январь 2025

Цели проекта:
• Централизованное хранение цифровых активов
• AI-анализ и автоматическая категоризация
• Интеграция с Яндекс.Диском
• Поддержка workflow согласования

Требования к системе:
1. Поддержка форматов: JPEG, PNG, RAW, MP4, PDF
2. Максимальный размер файла: 10 ГБ
3. Время отклика API: < 200 мс`,
]

// ==================== Helper Functions ====================

function randomElement<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function generateSEOText(type: string): string {
  const templates = SEO_TEMPLATES[type] || SEO_TEMPLATES.image
  let text = randomElement(templates)
  
  text = text.replace('{subject}', randomElement(SAMPLE_SUBJECTS))
  text = text.replace('{style}', randomElement(SAMPLE_STYLES))
  text = text.replace('{use_case}', randomElement(SAMPLE_USE_CASES))
  text = text.replace('{industry}', randomElement(SAMPLE_INDUSTRIES))
  text = text.replace('{mood}', randomElement(SAMPLE_MOODS))
  text = text.replace('{description}', 'Качественное изображение с высоким разрешением')
  text = text.replace('{duration}', '2:35')
  text = text.replace('{quality}', '4K')
  text = text.replace('{title}', 'Бизнес-документ')
  text = text.replace('{format}', 'PDF')
  text = text.replace('{pages}', String(randomInt(5, 50)))
  
  return text
}

// ==================== Mock Data Generators ====================

export function generateAIInsights(assetId: number, assetType: string = 'image'): AIInsights {
  const type = assetType.toLowerCase()
  const baseTags = MOCK_TAGS_BY_TYPE[type] || MOCK_TAGS_BY_TYPE.image
  
  // Vary tags slightly based on assetId for variety
  const suggestedTags = baseTags.map((tag, index) => ({
    ...tag,
    id: assetId * 100 + index,
    confidence: Math.max(40, Math.min(99, tag.confidence + randomInt(-10, 10))),
    accepted: Math.random() < 0.3 ? true : undefined,
    rejected: Math.random() < 0.1 ? true : undefined,
  }))
  
  const seoDescription: SEODescription = {
    text: generateSEOText(type),
    language: 'ru',
    generatedAt: new Date(Date.now() - randomInt(0, 7) * 86400000).toISOString(),
    provider: Math.random() > 0.5 ? 'yandex' : 'gigachat',
    version: randomInt(1, 3),
  }
  
  const hasOCR = type === 'document' || Math.random() < 0.2
  const ocrResult: OCRResult | null = hasOCR ? {
    text: randomElement(OCR_SAMPLE_TEXTS),
    confidence: randomInt(85, 98),
    language: 'ru',
    extractedAt: new Date(Date.now() - randomInt(0, 3) * 86400000).toISOString(),
  } : null
  
  return {
    suggestedTags,
    seoDescription,
    ocrResult,
    analysisStatus: {
      autoTagging: 'completed',
      seoGeneration: 'completed',
      ocr: hasOCR ? 'completed' : 'idle',
      faceDetection: type === 'image' || type === 'video' ? 'completed' : 'idle',
      objectDetection: type === 'image' || type === 'video' ? 'completed' : 'idle',
    },
    lastAnalyzedAt: new Date(Date.now() - randomInt(0, 7) * 86400000).toISOString(),
    aiProvider: 'mixed',
  }
}

// ==================== Store-like Functions ====================

const assetAIInsightsCache: Map<number, AIInsights> = new Map()

export function getAIInsightsForAsset(assetId: number, assetType: string = 'image'): AIInsights {
  if (!assetAIInsightsCache.has(assetId)) {
    assetAIInsightsCache.set(assetId, generateAIInsights(assetId, assetType))
  }
  return assetAIInsightsCache.get(assetId)!
}

export function acceptSuggestedTag(assetId: number, tagId: number): SuggestedTag | undefined {
  const insights = assetAIInsightsCache.get(assetId)
  if (!insights) return undefined
  
  const tag = insights.suggestedTags.find(t => t.id === tagId)
  if (tag) {
    tag.accepted = true
    tag.rejected = false
  }
  return tag
}

export function rejectSuggestedTag(assetId: number, tagId: number): SuggestedTag | undefined {
  const insights = assetAIInsightsCache.get(assetId)
  if (!insights) return undefined
  
  const tag = insights.suggestedTags.find(t => t.id === tagId)
  if (tag) {
    tag.rejected = true
    tag.accepted = false
  }
  return tag
}

export async function regenerateSEODescription(assetId: number, assetType: string = 'image'): Promise<SEODescription> {
  const insights = getAIInsightsForAsset(assetId, assetType)
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  const newDescription: SEODescription = {
    text: generateSEOText(assetType),
    language: 'ru',
    generatedAt: new Date().toISOString(),
    provider: Math.random() > 0.5 ? 'yandex' : 'gigachat',
    version: (insights.seoDescription?.version || 0) + 1,
  }
  
  insights.seoDescription = newDescription
  return newDescription
}

export async function extractOCR(assetId: number): Promise<OCRResult> {
  const insights = assetAIInsightsCache.get(assetId)
  if (!insights) {
    throw new Error('Asset not found')
  }
  
  // Set status to processing
  insights.analysisStatus.ocr = 'processing'
  
  // Simulate OCR processing time
  await new Promise(resolve => setTimeout(resolve, 2500))
  
  const ocrResult: OCRResult = {
    text: randomElement(OCR_SAMPLE_TEXTS),
    confidence: randomInt(85, 98),
    language: 'ru',
    extractedAt: new Date().toISOString(),
  }
  
  insights.ocrResult = ocrResult
  insights.analysisStatus.ocr = 'completed'
  
  return ocrResult
}

export async function runFullAIAnalysis(assetId: number, assetType: string = 'image'): Promise<AIInsights> {
  // Clear cache to regenerate fresh analysis
  assetAIInsightsCache.delete(assetId)
  
  // Simulate full analysis
  await new Promise(resolve => setTimeout(resolve, 3000))
  
  const insights = generateAIInsights(assetId, assetType)
  assetAIInsightsCache.set(assetId, insights)
  
  return insights
}

// ==================== Transformation Types ====================

export interface TransformationOptions {
  crop?: {
    x: number
    y: number
    width: number
    height: number
    aspectRatio?: string
  }
  resize?: {
    width: number
    height: number
    maintainAspect: boolean
  }
  format?: {
    type: 'jpg' | 'png' | 'webp' | 'gif' | 'tiff'
    quality: number // 1-100
    dpi?: number
  }
  watermark?: {
    text?: string
    image_url?: string
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center'
    opacity: number
  }
}

export interface TransformationPreset {
  id: string
  name: string
  description: string
  options: TransformationOptions
  icon: string
}

export const TRANSFORMATION_PRESETS: TransformationPreset[] = [
  {
    id: 'web_optimized',
    name: 'Для веба',
    description: 'JPG 72dpi, макс. 1920px',
    icon: '🌐',
    options: {
      resize: { width: 1920, height: 1080, maintainAspect: true },
      format: { type: 'jpg', quality: 85, dpi: 72 },
    },
  },
  {
    id: 'social_square',
    name: 'Соц. сети (квадрат)',
    description: '1080x1080px, JPG',
    icon: '📱',
    options: {
      resize: { width: 1080, height: 1080, maintainAspect: false },
      crop: { x: 0, y: 0, width: 1080, height: 1080, aspectRatio: '1:1' },
      format: { type: 'jpg', quality: 90 },
    },
  },
  {
    id: 'print_a4',
    name: 'Печать A4',
    description: 'PNG 300dpi, A4 формат',
    icon: '🖨️',
    options: {
      resize: { width: 2480, height: 3508, maintainAspect: true },
      format: { type: 'png', quality: 100, dpi: 300 },
    },
  },
  {
    id: 'thumbnail',
    name: 'Миниатюра',
    description: '300x300px, WebP',
    icon: '🖼️',
    options: {
      resize: { width: 300, height: 300, maintainAspect: true },
      format: { type: 'webp', quality: 80 },
    },
  },
  {
    id: 'email_banner',
    name: 'Email баннер',
    description: '600x200px, JPG',
    icon: '📧',
    options: {
      resize: { width: 600, height: 200, maintainAspect: false },
      crop: { x: 0, y: 0, width: 600, height: 200, aspectRatio: '3:1' },
      format: { type: 'jpg', quality: 85 },
    },
  },
]

export const ASPECT_RATIO_PRESETS = [
  { label: 'Свободно', value: 'free' },
  { label: '1:1 (Квадрат)', value: '1:1' },
  { label: '4:3', value: '4:3' },
  { label: '3:2', value: '3:2' },
  { label: '16:9', value: '16:9' },
  { label: '9:16 (Сторис)', value: '9:16' },
  { label: '2:3 (Портрет)', value: '2:3' },
  { label: 'A4 (210:297)', value: '210:297' },
]

export const FORMAT_OPTIONS = [
  { value: 'jpg', label: 'JPEG', description: 'Лучше для фото, меньший размер' },
  { value: 'png', label: 'PNG', description: 'Поддержка прозрачности, без потерь' },
  { value: 'webp', label: 'WebP', description: 'Современный формат, отличное сжатие' },
  { value: 'tiff', label: 'TIFF', description: 'Для печати, без потерь' },
]

export async function applyTransformation(
  assetId: number,
  options: TransformationOptions,
  saveAs: 'new_version' | 'new_copy'
): Promise<{ success: boolean; newAssetId?: number; newVersionId?: number }> {
  // Simulate transformation processing
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  if (saveAs === 'new_version') {
    return { success: true, newVersionId: Date.now() }
  } else {
    return { success: true, newAssetId: Date.now() }
  }
}

// ==================== AIInsightsWidget API ====================

const MOCK_TAGS_DATA: Record<string, AITag[]> = {
  image: [
    { id: 'tag-1', label: 'природа', confidence: 95, category: 'scene', source: 'yandex' },
    { id: 'tag-2', label: 'пейзаж', confidence: 92, category: 'scene', source: 'yandex' },
    { id: 'tag-3', label: 'небо', confidence: 88, category: 'object', source: 'gigachat' },
    { id: 'tag-4', label: 'облака', confidence: 85, category: 'object', source: 'gigachat' },
    { id: 'tag-5', label: 'синий', confidence: 78, category: 'color', source: 'local' },
    { id: 'tag-6', label: 'зелёный', confidence: 72, category: 'color', source: 'local' },
    { id: 'tag-7', label: 'спокойствие', confidence: 65, category: 'emotion', source: 'gigachat' },
    { id: 'tag-8', label: 'яркий', confidence: 60, category: 'style', source: 'yandex' },
  ],
  document: [
    { id: 'tag-1', label: 'документ', confidence: 99, category: 'object', source: 'local' },
    { id: 'tag-2', label: 'текст', confidence: 95, category: 'object', source: 'local' },
    { id: 'tag-3', label: 'таблица', confidence: 78, category: 'object', source: 'yandex' },
    { id: 'tag-4', label: 'отчёт', confidence: 72, category: 'scene', source: 'gigachat' },
    { id: 'tag-5', label: 'бизнес', confidence: 68, category: 'scene', source: 'gigachat' },
  ],
}

const assetAnalysisCache: Map<number, AIAnalysis> = new Map()

function generateAnalysisForAsset(assetId: number): AIAnalysis {
  const isDocument = assetId % 3 === 0
  const type = isDocument ? 'document' : 'image'
  const baseTags = MOCK_TAGS_DATA[type] || MOCK_TAGS_DATA.image
  
  // Vary tags based on assetId
  const tags: AITag[] = baseTags.map((tag, idx) => ({
    ...tag,
    id: `tag-${assetId}-${idx}`,
    confidence: Math.max(50, Math.min(99, tag.confidence + randomInt(-10, 10))),
  }))
  
  const colors: ColorData[] = isDocument ? [] : [
    { hex: '#3B82F6', percentage: 35 },
    { hex: '#10B981', percentage: 28 },
    { hex: '#F59E0B', percentage: 20 },
    { hex: '#EF4444', percentage: 12 },
    { hex: '#8B5CF6', percentage: 5 },
  ]
  
  return {
    status: 'completed',
    analyzedAt: new Date(Date.now() - randomInt(1, 7) * 86400000).toISOString(),
    tags,
    seo: {
      altText: `Профессиональное изображение #${assetId} в высоком качестве`,
      description: `Качественный контент для использования в маркетинговых материалах и презентациях. Идеально подходит для корпоративных нужд.`,
      keywords: ['профессиональный', 'качество', 'бизнес', 'маркетинг', 'презентация'],
    },
    ocr: {
      status: isDocument ? 'completed' : 'not_run',
      text: isDocument ? OCR_SAMPLE_TEXTS[assetId % OCR_SAMPLE_TEXTS.length] : undefined,
      confidence: isDocument ? randomInt(85, 98) : undefined,
      wordCount: isDocument ? randomInt(100, 500) : undefined,
    },
    colorPalette: colors,
  }
}

export function getAssetAIAnalysis(assetId: number): AIAnalysis | null {
  if (!assetAnalysisCache.has(assetId)) {
    // 70% chance to have existing analysis
    if (Math.random() < 0.7) {
      assetAnalysisCache.set(assetId, generateAnalysisForAsset(assetId))
    } else {
      // Return pending analysis
      return {
        status: 'pending',
        analyzedAt: null,
        tags: [],
        seo: null,
        ocr: { status: 'not_run' },
      }
    }
  }
  return assetAnalysisCache.get(assetId) || null
}

export async function runAIAnalysis(assetId: number): Promise<AIAnalysis> {
  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 2500))
  
  const analysis = generateAnalysisForAsset(assetId)
  assetAnalysisCache.set(assetId, analysis)
  return analysis
}

export async function runOCR(assetId: number): Promise<OCRData> {
  // Simulate OCR processing
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  const text = OCR_SAMPLE_TEXTS[assetId % OCR_SAMPLE_TEXTS.length]
  const wordCount = text.split(/\s+/).length
  
  const result: OCRData = {
    status: 'completed',
    text,
    confidence: randomInt(88, 98),
    wordCount,
  }
  
  const analysis = assetAnalysisCache.get(assetId)
  if (analysis) {
    analysis.ocr = result
  }
  
  return result
}

export async function regenerateSEO(assetId: number): Promise<SEOData> {
  // Simulate SEO generation
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  const seo: SEOData = {
    altText: `Обновлённое описание изображения #${assetId} для SEO оптимизации`,
    description: `Новое профессиональное описание. Контент высокого качества для использования в цифровых кампаниях. Оптимизировано для поисковых систем. (Версия ${Date.now()})`,
    keywords: ['обновлённый', 'SEO', 'качество', 'контент', 'оптимизация', 'цифровой'],
  }
  
  const analysis = assetAnalysisCache.get(assetId)
  if (analysis) {
    analysis.seo = seo
  }
  
  return seo
}

export function setTagStatus(assetId: number, tagId: string, status: 'accepted' | 'rejected'): AITag | null {
  const analysis = assetAnalysisCache.get(assetId)
  if (!analysis) return null
  
  const tag = analysis.tags.find(t => t.id === tagId)
  if (!tag) return null
  
  if (status === 'accepted') {
    tag.accepted = true
    tag.rejected = false
  } else {
    tag.rejected = true
    tag.accepted = false
  }
  
  return tag
}
