/**
 * Примеры использования API сервисов
 * Этот файл не импортируется в production, только для документации
 */

import { assetService } from './assetService'
import type { Asset, SearchQuery, BulkOperationRequest } from '@/types/api'

// Пример 1: Получить первую страницу активов
export async function exampleGetAssets() {
  const response = await assetService.getAssets({
    page: 1,
    page_size: 50,
    sort: '-date_added'
  })

  console.log(`Найдено активов: ${response.count}`)
  console.log(`Текущая страница: ${response.results.length} элементов`)
  if (response.next) {
    console.log('Есть следующая страница')
  }
}

// Пример 2: Поиск активов с фильтрами
export async function exampleSearchAssets() {
  const query: SearchQuery = {
    q: 'landscape photography',
    filters: {
      type: ['image'],
      tags: ['campaign', 'hero'],
      date_range: ['2025-01-01', '2025-12-31']
    },
    sort: 'relevance',
    limit: 50
  }

  const results = await assetService.searchAssets(query)

  console.log(`Найдено: ${results.count} результатов`)
  console.log('Facets:', results.facets)
  // facets: { type: { image: 145 }, tags: { campaign: 89 } }
}

// Пример 3: Получить детальную информацию об активе
export async function exampleGetAssetDetail(assetId: number) {
  const asset = await assetService.getAsset(assetId)

  console.log(`Asset: ${asset.label}`)
  console.log(`File: ${asset.file_details.filename}`)
  console.log(`Size: ${asset.file_details.size} bytes`)

  if (asset.ai_analysis) {
    console.log('AI Tags:', asset.ai_analysis.tags)
    console.log('Objects detected:', asset.ai_analysis.objects_detected)
  }

  if (asset.comments && asset.comments.length > 0) {
    console.log(`Comments: ${asset.comments.length}`)
  }
}

// Пример 4: Массовые операции
export async function exampleBulkOperations() {
  // Добавить теги к нескольким активам
  const addTagsResult = await assetService.bulkOperation({
    ids: [1, 2, 3, 4, 5],
    action: 'add_tags',
    data: { tags: ['campaign-2025', 'approved'] }
  })

  if (addTagsResult.success) {
    console.log(`✅ Обновлено: ${addTagsResult.updated}`)
    if (addTagsResult.failed > 0) {
      console.warn(`⚠️ Ошибок: ${addTagsResult.failed}`)
      if (addTagsResult.errors) {
        addTagsResult.errors.forEach((err) => {
          console.error(`Asset ${err.id}: ${err.error}`)
        })
      }
    }
  }

  // Удалить активы
  const deleteResult = await assetService.bulkOperation({
    ids: [10, 11, 12],
    action: 'delete'
  })

  console.log(`Удалено: ${deleteResult.updated}`)
}

// Пример 5: Обновить метаданные актива
export async function exampleUpdateAsset(assetId: number) {
  const updated = await assetService.updateAsset(assetId, {
    label: 'New Label',
    tags: ['updated', 'tag']
  })

  console.log(`Asset ${updated.id} updated: ${updated.label}`)
}

// Пример 6: Обработка ошибок
export async function exampleErrorHandling() {
  try {
    const asset = await assetService.getAsset(999)
    console.log(asset)
  } catch (error) {
    // Импортируем утилиты для обработки ошибок
    const { formatApiError, isNetworkError, isAuthError } = await import(
      '@/utils/errors'
    )

    if (isNetworkError(error)) {
      console.error('Сетевая ошибка:', formatApiError(error))
      // Показать пользователю: "Проверьте подключение к интернету"
    } else if (isAuthError(error)) {
      console.error('Ошибка авторизации:', formatApiError(error))
      // Перенаправить на страницу входа
    } else {
      console.error('Ошибка:', formatApiError(error))
      // Показать общее сообщение об ошибке
    }
  }
}

// Пример 7: Пагинация
export async function examplePagination() {
  let page = 1
  let hasMore = true
  const allAssets: Asset[] = []

  while (hasMore) {
    const response = await assetService.getAssets({
      page,
      page_size: 50
    })

    allAssets.push(...response.results)

    if (response.next) {
      page++
    } else {
      hasMore = false
    }
  }

  console.log(`Загружено всего: ${allAssets.length} активов`)
}

