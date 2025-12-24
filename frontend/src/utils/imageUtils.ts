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

  // Сначала пробуем активную версию
  const versionActivePreview =
    asset?.id && versionActiveId
      ? `/api/v4/documents/${asset.id}/versions/${versionActiveId}/pages/1/image/?width=1200`
      : undefined

  // Затем текущий файл (если активной версии нет)
  const filePreview =
    asset?.id && preferredFileId
      ? `/api/v4/documents/${asset.id}/files/${preferredFileId}/pages/1/image/?width=1200`
      : undefined

  // Fallback на другие версии
  const versionPreview =
    asset?.id && versionId && versionId !== 'latest'
      ? `/api/v4/documents/${asset.id}/versions/${versionId}/pages/1/image/?width=1200`
      : undefined

  // Последний fallback: latest версия
  const latestVersionPreview =
    asset?.id && versionId === 'latest'
      ? `/api/v4/documents/${asset.id}/versions/latest/pages/1/image/?width=1200`
      : undefined

  // Сначала пробуем превью по файлу (надёжнее, чем по версии: страницы
  // у файла создаются стабильнее, а versions/latest может отсутствовать).
  const url =
    filePreview ||
    versionActivePreview ||
    asset.thumbnail_url ||
    asset.preview_url ||
    versionPreview ||
    latestVersionPreview ||
    asset.download_url

  return makeAbsolute(url) || PLACEHOLDER
}

