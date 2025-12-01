# API Services Documentation

## Overview

API сервисы для интеграции с Django REST API backend. Все сервисы используют единый базовый `apiService` с interceptors, кешированием и обработкой ошибок.

## Services

### apiService (Base HTTP Client)

Базовый HTTP клиент на основе Axios с расширенными возможностями.

**Features:**
- ✅ CSRF token handling
- ✅ JWT authentication
- ✅ Request/Response logging (dev mode)
- ✅ Auto-retry on network errors (до 3 попыток)
- ✅ Response caching (in-memory, 5 min TTL)
- ✅ Structured error handling
- ✅ 401/403 error handling

**Usage:**
```typescript
import { apiService } from '@/services/apiService'

// GET request
const data = await apiService.get<MyType>('/endpoint', config, useCache)

// POST request
const result = await apiService.post<MyType>('/endpoint', requestData)

// PUT request
const updated = await apiService.put<MyType>('/endpoint/1', updateData)

// DELETE request
await apiService.delete('/endpoint/1')
```

### assetService (DAM Assets)

Сервис для работы с активами DAM системы.

**Methods:**

#### getAssets(params?)
Получить пагинированный список активов.

```typescript
import { assetService } from '@/services/assetService'

const response = await assetService.getAssets({
  page: 1,
  page_size: 50,
  sort: '-date_added',
  type: 'image',
  tags: 'campaign'
})

// Response: PaginatedResponse<Asset>
// {
//   count: 100,
//   next: '/api/v4/dam/assets/?page=2',
//   previous: null,
//   results: Asset[]
// }
```

#### getAsset(id)
Получить детальную информацию об активе.

```typescript
const asset = await assetService.getAsset(123)

// Response: AssetDetailResponse
// {
//   id: 123,
//   label: 'photo.jpg',
//   file_details: {...},
//   ai_analysis: {...},
//   comments: [...],
//   version_history: [...]
// }
```

#### searchAssets(query)
Поиск активов с фильтрами и facets.

```typescript
const results = await assetService.searchAssets({
  q: 'landscape photography',
  filters: {
    type: ['image'],
    tags: ['campaign', 'hero'],
    date_range: ['2025-01-01', '2025-12-31']
  },
  sort: 'relevance',
  limit: 50,
  offset: 0
})

// Response: SearchResponse
// {
//   count: 156,
//   results: Asset[],
//   facets: {
//     type: { image: 145, video: 11 },
//     tags: { campaign: 89, hero: 76 }
//   }
// }
```

#### bulkOperation(operation)
Массовые операции над активами.

```typescript
const result = await assetService.bulkOperation({
  ids: [1, 2, 3, 4, 5],
  action: 'add_tags',
  data: { tags: ['new-tag', 'campaign-2025'] }
})

// Available actions:
// - 'add_tags' - Добавить теги
// - 'remove_tags' - Удалить теги
// - 'move' - Переместить в коллекцию
// - 'delete' - Удалить
// - 'export' - Экспортировать

// Response: BulkOperationResponse
// {
//   success: true,
//   updated: 5,
//   failed: 0,
//   errors: []
// }
```

#### updateAsset(id, data)
Обновить метаданные актива.

```typescript
const updated = await assetService.updateAsset(123, {
  label: 'New Label',
  tags: ['updated', 'tag']
})
```

#### deleteAsset(id)
Удалить актив.

```typescript
await assetService.deleteAsset(123)
```

### cacheService (In-Memory Cache)

Сервис кеширования с TTL поддержкой.

**Usage:**
```typescript
import { cacheService } from '@/services/cacheService'

// Set cache (default TTL: 5 minutes)
cacheService.set('key', data)

// Set cache with custom TTL (in milliseconds)
cacheService.set('key', data, 10 * 60 * 1000) // 10 minutes

// Get from cache
const cached = cacheService.get<MyType>('key')

// Check if exists
if (cacheService.has('key')) {
  // ...
}

// Delete specific key
cacheService.delete('key')

// Clear all cache
cacheService.clear()
```

## Error Handling

Все ошибки обрабатываются через структурированный формат `ApiError`:

```typescript
import type { ApiError } from '@/types/api'
import { formatApiError, isNetworkError, isAuthError } from '@/utils/errors'

try {
  const asset = await assetService.getAsset(123)
} catch (error) {
  if (isNetworkError(error)) {
    // Обработка сетевой ошибки
    console.error('Network error:', formatApiError(error))
  } else if (isAuthError(error)) {
    // Обработка ошибки авторизации
    console.error('Auth error:', formatApiError(error))
  } else {
    // Другая ошибка
    console.error('Error:', formatApiError(error))
  }
}
```

## Caching Strategy

- **GET requests**: Автоматически кешируются (TTL: 5 минут)
- **POST/PUT/DELETE**: Автоматически инвалидируют кеш
- **Manual cache control**: `apiService.clearCache()` или `assetService.clearCache()`

## Retry Logic

Автоматический retry для:
- Network errors (нет ответа от сервера)
- 5xx server errors

**Retry strategy:**
- Максимум 3 попытки
- Exponential backoff: 1s, 2s, 4s
- Только для GET и безопасных операций

## Request Logging

В development режиме все запросы логируются в консоль:
- Request method, URL, params, data
- Response data
- Errors

В production логирование отключено.

## TypeScript Support

Все методы полностью типизированы:

```typescript
import type { Asset, PaginatedResponse, SearchResponse } from '@/types/api'

// Type-safe responses
const assets: PaginatedResponse<Asset> = await assetService.getAssets()
const search: SearchResponse = await assetService.searchAssets({ q: 'test' })
```

## Examples

### Получить первую страницу активов
```typescript
const { results, count, next } = await assetService.getAssets({
  page: 1,
  page_size: 50,
  sort: '-date_added'
})
```

### Поиск с фильтрами
```typescript
const searchResults = await assetService.searchAssets({
  q: 'campaign hero',
  filters: {
    type: ['image'],
    tags: ['hero', 'social'],
    date_range: ['2025-01-01', '2025-12-31']
  }
})
```

### Массовое добавление тегов
```typescript
const result = await assetService.bulkOperation({
  ids: [1, 2, 3, 4, 5],
  action: 'add_tags',
  data: { tags: ['campaign-2025', 'approved'] }
})

if (result.success) {
  console.log(`Updated ${result.updated} assets`)
  if (result.failed > 0) {
    console.warn(`${result.failed} assets failed`)
  }
}
```

## Testing

Все сервисы покрыты unit тестами. Запуск:

```bash
npm run test
npm run test:coverage
```

См. `src/services/__tests__/` для примеров использования.

