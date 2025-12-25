const API_BASE =
  (import.meta as any)?.env?.VITE_API_BASE_URL ||
  (import.meta as any)?.env?.VITE_API_URL ||
  'http://localhost:8000'

const PLACEHOLDER = '/placeholder-document.svg'

function makeAbsolute(url: string | undefined | null): string | undefined {
  if (!url) return undefined
  if (url.startsWith('data:image')) return url
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  // relative path -> prepend backend base
  return `${API_BASE}${url.startsWith('/') ? '' : '/'}${url}`
}

export function resolveAssetImageUrl(asset: any): string {
  if (!asset) return PLACEHOLDER

  // Приоритет 1: Активная версия (если есть)
  const versionActiveId =
    asset?.version_active_id ||
    asset?.version_active?.id

  // Приоритет 2: Текущий файл (из активной версии или последний).
  // Сюда включаем:
  // - version_active_file_id (если пришёл с детального DAM-эндпоинта),
  // - выбранный/текущий файл из UI,
  // - document_file_id (для кампаний и других связок),
  // - file_latest_id (для оптимизированных списков),
  // - прочие fallback-и.
  const preferredFileId =
    asset?.version_active_file_id ||
    asset?.selected_file_id ||
    asset?.current_file_id ||
    asset?.document_file_id ||
    asset?.file_latest_id ||
    asset?.file_id ||
    asset?.file?.id

  // Приоритет 3: Другие версии (fallback)
  const versionId =
    asset?.version_id ||
    asset?.version?.id ||
    'latest'

  // Приоритет 1: Готовые URL из бэкенда (thumbnail_url, preview_url)
  // Эти URL уже правильно сформированы и работают
  const backendPreview = asset?.thumbnail_url || asset?.preview_url

  // Приоритет 2: Fallback на общий download_url (готовый URL от бэкенда)
  // Используем только готовые URL, чтобы избежать 404 ошибок
  const downloadUrl = asset?.download_url

  // Примечание: НЕ формируем URL вручную, так как:
  // 1. file_id может быть неправильным или файл может быть удален
  // 2. Бэкенд уже предоставляет готовые валидные URL
  // 3. Ручное формирование URL приводит к 404 ошибкам

  const url =
    backendPreview ||
    downloadUrl

  return makeAbsolute(url) || PLACEHOLDER
}

