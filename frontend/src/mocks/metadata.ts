/**
 * Mock Metadata Types and Schemas
 * Maps to Backend: /api/v4/metadata/metadata_types/
 * 
 * Each MetadataType defines a schema with fields that can be attached to assets.
 * Fields support various types: text, date, select, boolean, number, textarea
 */

export type FieldType = 'text' | 'textarea' | 'date' | 'datetime' | 'select' | 'boolean' | 'number' | 'email' | 'url'

export interface MetadataFieldOption {
  value: string
  label: string
}

export interface MetadataField {
  id: string
  name: string
  label: string
  type: FieldType
  required: boolean
  placeholder?: string
  helpText?: string
  defaultValue?: string | number | boolean | null
  options?: MetadataFieldOption[] // For select fields
  min?: number // For number fields
  max?: number // For number fields
  pattern?: string // Regex for validation
  order: number
}

export interface MetadataType {
  id: number
  name: string
  label: string
  description: string
  icon: string // Heroicon name
  color: string // Tailwind color
  fields: MetadataField[]
  isRequired: boolean // Is this type required for certain document types?
  documentTypes: string[] // Which document types this applies to
  createdAt: string
  updatedAt: string
}

export interface AssetMetadataValue {
  fieldId: string
  value: string | number | boolean | null
  updatedAt: string
  updatedBy: string
}

export interface AssetMetadata {
  assetId: number
  typeId: number
  values: AssetMetadataValue[]
  isComplete: boolean // All required fields filled?
  completeness: number // 0-100%
}

// ============================================================
// MOCK METADATA TYPES
// ============================================================

export const METADATA_TYPES: MetadataType[] = [
  {
    id: 1,
    name: 'campaign_data',
    label: 'Данные кампании',
    description: 'Информация о маркетинговой кампании',
    icon: 'MegaphoneIcon',
    color: 'purple',
    isRequired: false,
    documentTypes: ['image', 'video', 'document'],
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2025-11-20T14:30:00Z',
    fields: [
      {
        id: 'campaign_name',
        name: 'campaign_name',
        label: 'Название кампании',
        type: 'text',
        required: true,
        placeholder: 'Введите название кампании',
        helpText: 'Уникальное название маркетинговой кампании',
        order: 1
      },
      {
        id: 'campaign_type',
        name: 'campaign_type',
        label: 'Тип кампании',
        type: 'select',
        required: true,
        options: [
          { value: 'brand', label: 'Брендовая' },
          { value: 'product', label: 'Продуктовая' },
          { value: 'seasonal', label: 'Сезонная' },
          { value: 'promo', label: 'Промо-акция' },
          { value: 'event', label: 'Мероприятие' }
        ],
        order: 2
      },
      {
        id: 'launch_date',
        name: 'launch_date',
        label: 'Дата запуска',
        type: 'date',
        required: true,
        helpText: 'Планируемая дата запуска кампании',
        order: 3
      },
      {
        id: 'end_date',
        name: 'end_date',
        label: 'Дата окончания',
        type: 'date',
        required: false,
        order: 4
      },
      {
        id: 'budget',
        name: 'budget',
        label: 'Бюджет (₽)',
        type: 'number',
        required: false,
        min: 0,
        placeholder: '0',
        order: 5
      },
      {
        id: 'target_audience',
        name: 'target_audience',
        label: 'Целевая аудитория',
        type: 'textarea',
        required: false,
        placeholder: 'Опишите целевую аудиторию кампании',
        order: 6
      },
      {
        id: 'is_active',
        name: 'is_active',
        label: 'Активна',
        type: 'boolean',
        required: false,
        defaultValue: true,
        order: 7
      }
    ]
  },
  {
    id: 2,
    name: 'legal_info',
    label: 'Юридическая информация',
    description: 'Правовые данные и лицензии',
    icon: 'ScaleIcon',
    color: 'amber',
    isRequired: true,
    documentTypes: ['image', 'video', 'audio'],
    createdAt: '2024-02-10T09:00:00Z',
    updatedAt: '2025-10-15T11:20:00Z',
    fields: [
      {
        id: 'copyright_holder',
        name: 'copyright_holder',
        label: 'Правообладатель',
        type: 'text',
        required: true,
        placeholder: 'Имя или название организации',
        order: 1
      },
      {
        id: 'license_type',
        name: 'license_type',
        label: 'Тип лицензии',
        type: 'select',
        required: true,
        options: [
          { value: 'royalty_free', label: 'Royalty Free' },
          { value: 'rights_managed', label: 'Rights Managed' },
          { value: 'editorial', label: 'Editorial Use Only' },
          { value: 'creative_commons', label: 'Creative Commons' },
          { value: 'internal', label: 'Только для внутреннего использования' },
          { value: 'exclusive', label: 'Эксклюзивная лицензия' }
        ],
        order: 2
      },
      {
        id: 'contract_number',
        name: 'contract_number',
        label: 'Номер договора',
        type: 'text',
        required: false,
        placeholder: 'ДГ-2025-XXX',
        pattern: '^[А-Яа-яA-Za-z0-9-]+$',
        order: 3
      },
      {
        id: 'license_start',
        name: 'license_start',
        label: 'Начало действия лицензии',
        type: 'date',
        required: false,
        order: 4
      },
      {
        id: 'license_end',
        name: 'license_end',
        label: 'Окончание лицензии',
        type: 'date',
        required: false,
        helpText: 'Оставьте пустым для бессрочной лицензии',
        order: 5
      },
      {
        id: 'usage_restrictions',
        name: 'usage_restrictions',
        label: 'Ограничения использования',
        type: 'textarea',
        required: false,
        placeholder: 'Укажите ограничения на использование материала',
        order: 6
      },
      {
        id: 'model_release',
        name: 'model_release',
        label: 'Релиз модели',
        type: 'boolean',
        required: false,
        helpText: 'Есть ли подписанное согласие на использование изображения',
        defaultValue: false,
        order: 7
      },
      {
        id: 'property_release',
        name: 'property_release',
        label: 'Релиз собственности',
        type: 'boolean',
        required: false,
        helpText: 'Есть ли разрешение на съёмку объекта/здания',
        defaultValue: false,
        order: 8
      }
    ]
  },
  {
    id: 3,
    name: 'technical_specs',
    label: 'Технические характеристики',
    description: 'Технические параметры медиафайла',
    icon: 'CpuChipIcon',
    color: 'slate',
    isRequired: false,
    documentTypes: ['image', 'video'],
    createdAt: '2024-03-01T14:00:00Z',
    updatedAt: '2025-09-10T16:45:00Z',
    fields: [
      {
        id: 'color_space',
        name: 'color_space',
        label: 'Цветовое пространство',
        type: 'select',
        required: false,
        options: [
          { value: 'srgb', label: 'sRGB' },
          { value: 'adobe_rgb', label: 'Adobe RGB' },
          { value: 'prophoto', label: 'ProPhoto RGB' },
          { value: 'cmyk', label: 'CMYK' },
          { value: 'rec709', label: 'Rec.709 (Video)' },
          { value: 'rec2020', label: 'Rec.2020 (HDR)' }
        ],
        order: 1
      },
      {
        id: 'dpi',
        name: 'dpi',
        label: 'Разрешение (DPI)',
        type: 'number',
        required: false,
        min: 72,
        max: 1200,
        defaultValue: 300,
        order: 2
      },
      {
        id: 'orientation',
        name: 'orientation',
        label: 'Ориентация',
        type: 'select',
        required: false,
        options: [
          { value: 'landscape', label: 'Альбомная' },
          { value: 'portrait', label: 'Портретная' },
          { value: 'square', label: 'Квадратная' }
        ],
        order: 3
      },
      {
        id: 'bit_depth',
        name: 'bit_depth',
        label: 'Глубина цвета',
        type: 'select',
        required: false,
        options: [
          { value: '8', label: '8 бит' },
          { value: '16', label: '16 бит' },
          { value: '32', label: '32 бит' }
        ],
        order: 4
      },
      {
        id: 'has_alpha',
        name: 'has_alpha',
        label: 'Прозрачность (Alpha)',
        type: 'boolean',
        required: false,
        defaultValue: false,
        order: 5
      }
    ]
  },
  {
    id: 4,
    name: 'approval_data',
    label: 'Данные согласования',
    description: 'Информация о процессе согласования',
    icon: 'ClipboardDocumentCheckIcon',
    color: 'green',
    isRequired: false,
    documentTypes: ['image', 'video', 'document', 'audio'],
    createdAt: '2024-04-15T11:30:00Z',
    updatedAt: '2025-11-25T09:15:00Z',
    fields: [
      {
        id: 'approval_date',
        name: 'approval_date',
        label: 'Дата согласования',
        type: 'date',
        required: false,
        order: 1
      },
      {
        id: 'approved_by',
        name: 'approved_by',
        label: 'Кем согласовано',
        type: 'text',
        required: false,
        placeholder: 'ФИО ответственного',
        order: 2
      },
      {
        id: 'approval_level',
        name: 'approval_level',
        label: 'Уровень согласования',
        type: 'select',
        required: false,
        options: [
          { value: 'team_lead', label: 'Руководитель группы' },
          { value: 'department_head', label: 'Руководитель отдела' },
          { value: 'director', label: 'Директор' },
          { value: 'legal', label: 'Юридический отдел' },
          { value: 'executive', label: 'Высшее руководство' }
        ],
        order: 3
      },
      {
        id: 'approval_notes',
        name: 'approval_notes',
        label: 'Комментарии согласования',
        type: 'textarea',
        required: false,
        placeholder: 'Дополнительные комментарии по согласованию',
        order: 4
      },
      {
        id: 'needs_revision',
        name: 'needs_revision',
        label: 'Требуется доработка',
        type: 'boolean',
        required: false,
        defaultValue: false,
        order: 5
      }
    ]
  },
  {
    id: 5,
    name: 'brand_guidelines',
    label: 'Брендбук',
    description: 'Соответствие брендовым стандартам',
    icon: 'SwatchIcon',
    color: 'pink',
    isRequired: false,
    documentTypes: ['image', 'video'],
    createdAt: '2024-05-20T08:00:00Z',
    updatedAt: '2025-08-30T12:00:00Z',
    fields: [
      {
        id: 'brand_name',
        name: 'brand_name',
        label: 'Бренд',
        type: 'select',
        required: true,
        options: [
          { value: 'main', label: 'Основной бренд' },
          { value: 'sub_brand_a', label: 'Суб-бренд А' },
          { value: 'sub_brand_b', label: 'Суб-бренд Б' },
          { value: 'partner', label: 'Партнёрский бренд' }
        ],
        order: 1
      },
      {
        id: 'brand_compliant',
        name: 'brand_compliant',
        label: 'Соответствует брендбуку',
        type: 'boolean',
        required: false,
        defaultValue: false,
        order: 2
      },
      {
        id: 'logo_version',
        name: 'logo_version',
        label: 'Версия логотипа',
        type: 'select',
        required: false,
        options: [
          { value: 'primary', label: 'Основной' },
          { value: 'secondary', label: 'Вторичный' },
          { value: 'monochrome', label: 'Монохромный' },
          { value: 'reversed', label: 'Инверсный' }
        ],
        order: 3
      },
      {
        id: 'brand_colors_used',
        name: 'brand_colors_used',
        label: 'Использованы фирменные цвета',
        type: 'boolean',
        required: false,
        order: 4
      },
      {
        id: 'brand_fonts_used',
        name: 'brand_fonts_used',
        label: 'Использованы фирменные шрифты',
        type: 'boolean',
        required: false,
        order: 5
      }
    ]
  }
]

// ============================================================
// MOCK ASSET METADATA (pre-filled for some assets)
// ============================================================

export const ASSET_METADATA: Map<number, AssetMetadata[]> = new Map([
  [1, [
    {
      assetId: 1,
      typeId: 1, // campaign_data
      values: [
        { fieldId: 'campaign_name', value: 'Весенняя коллекция 2025', updatedAt: '2025-11-20T10:00:00Z', updatedBy: 'Иванов А.А.' },
        { fieldId: 'campaign_type', value: 'seasonal', updatedAt: '2025-11-20T10:00:00Z', updatedBy: 'Иванов А.А.' },
        { fieldId: 'launch_date', value: '2025-03-01', updatedAt: '2025-11-20T10:00:00Z', updatedBy: 'Иванов А.А.' },
        { fieldId: 'is_active', value: true, updatedAt: '2025-11-20T10:00:00Z', updatedBy: 'Иванов А.А.' }
      ],
      isComplete: false,
      completeness: 57
    },
    {
      assetId: 1,
      typeId: 2, // legal_info
      values: [
        { fieldId: 'copyright_holder', value: 'ООО "Компания"', updatedAt: '2025-11-19T14:30:00Z', updatedBy: 'Петров Б.В.' },
        { fieldId: 'license_type', value: 'internal', updatedAt: '2025-11-19T14:30:00Z', updatedBy: 'Петров Б.В.' },
        { fieldId: 'model_release', value: true, updatedAt: '2025-11-19T14:30:00Z', updatedBy: 'Петров Б.В.' }
      ],
      isComplete: false,
      completeness: 38
    }
  ]],
  [5, [
    {
      assetId: 5,
      typeId: 4, // approval_data
      values: [
        { fieldId: 'approval_date', value: '2025-11-25', updatedAt: '2025-11-25T09:15:00Z', updatedBy: 'Директор' },
        { fieldId: 'approved_by', value: 'Сидоров В.Г.', updatedAt: '2025-11-25T09:15:00Z', updatedBy: 'Директор' },
        { fieldId: 'approval_level', value: 'director', updatedAt: '2025-11-25T09:15:00Z', updatedBy: 'Директор' }
      ],
      isComplete: false,
      completeness: 60
    }
  ]]
])

// ============================================================
// HELPER FUNCTIONS
// ============================================================

/**
 * Get all metadata types
 */
export function getAllMetadataTypes(): MetadataType[] {
  return [...METADATA_TYPES]
}

/**
 * Get metadata type by ID
 */
export function getMetadataTypeById(id: number): MetadataType | undefined {
  return METADATA_TYPES.find(t => t.id === id)
}

/**
 * Get metadata types applicable to a document type
 */
export function getMetadataTypesForDocumentType(documentType: string): MetadataType[] {
  return METADATA_TYPES.filter(t => t.documentTypes.includes(documentType))
}

/**
 * Get asset metadata
 */
export function getAssetMetadata(assetId: number): AssetMetadata[] {
  return ASSET_METADATA.get(assetId) || []
}

/**
 * Save asset metadata value
 */
export function saveAssetMetadataValue(
  assetId: number,
  typeId: number,
  fieldId: string,
  value: string | number | boolean | null,
  updatedBy: string = 'Текущий пользователь'
): AssetMetadata {
  let assetMetadataList = ASSET_METADATA.get(assetId)
  
  if (!assetMetadataList) {
    assetMetadataList = []
    ASSET_METADATA.set(assetId, assetMetadataList)
  }
  
  let typeMetadata = assetMetadataList.find(m => m.typeId === typeId)
  
  if (!typeMetadata) {
    typeMetadata = {
      assetId,
      typeId,
      values: [],
      isComplete: false,
      completeness: 0
    }
    assetMetadataList.push(typeMetadata)
  }
  
  const existingValue = typeMetadata.values.find(v => v.fieldId === fieldId)
  const now = new Date().toISOString()
  
  if (existingValue) {
    existingValue.value = value
    existingValue.updatedAt = now
    existingValue.updatedBy = updatedBy
  } else {
    typeMetadata.values.push({
      fieldId,
      value,
      updatedAt: now,
      updatedBy
    })
  }
  
  // Recalculate completeness
  const metadataType = getMetadataTypeById(typeId)
  if (metadataType) {
    const requiredFields = metadataType.fields.filter(f => f.required)
    const filledRequired = requiredFields.filter(f => {
      const val = typeMetadata!.values.find(v => v.fieldId === f.id)
      return val && val.value !== null && val.value !== ''
    })
    typeMetadata.completeness = requiredFields.length > 0 
      ? Math.round((filledRequired.length / requiredFields.length) * 100)
      : 100
    typeMetadata.isComplete = typeMetadata.completeness === 100
  }
  
  return typeMetadata
}

/**
 * Bulk save asset metadata
 */
export function bulkSaveAssetMetadata(
  assetId: number,
  typeId: number,
  values: { fieldId: string; value: string | number | boolean | null }[],
  updatedBy: string = 'Текущий пользователь'
): AssetMetadata {
  let result: AssetMetadata | undefined
  
  for (const { fieldId, value } of values) {
    result = saveAssetMetadataValue(assetId, typeId, fieldId, value, updatedBy)
  }
  
  return result!
}

/**
 * Get field value from asset metadata
 */
export function getFieldValue(
  assetId: number,
  typeId: number,
  fieldId: string
): string | number | boolean | null {
  const assetMetadata = getAssetMetadata(assetId)
  const typeMetadata = assetMetadata.find(m => m.typeId === typeId)
  if (!typeMetadata) return null
  
  const fieldValue = typeMetadata.values.find(v => v.fieldId === fieldId)
  return fieldValue?.value ?? null
}

