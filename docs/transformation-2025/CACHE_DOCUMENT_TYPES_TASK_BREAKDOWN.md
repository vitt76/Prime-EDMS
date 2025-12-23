# Задача: Кеширование конфигурации типов документов

**Источник:** BACKEND_AUDIT_V1.md, раздел 5.7, пункт 3  
**Приоритет:** 2 (Важно)  
**TTL:** 1 час (3600 секунд)

## Проблема

`HeadlessDocumentTypeConfigView` каждый раз делает запросы к БД:

### Для списка всех типов (`GET /api/v4/headless/config/document_types/`):
- `DocumentType.objects.all()` - получение всех типов документов
- Для каждого типа вызывается `_build_basic_config()`, который обращается к полям модели

### Для детальной конфигурации (`GET /api/v4/headless/config/document_types/{id}/`):
- `DocumentType.objects.get(pk=document_type_id)` - получение конкретного типа
- `DocumentTypeMetadataType.objects.filter(document_type=doc_type).select_related('metadata_type')` - получение метаданных (уже оптимизировано через `select_related`)
- Для каждого метаданного вызывается `_build_metadata_config()`, который обращается к полям `MetadataType`
- `doc_type.workflows.all()` - получение связанных workflows (если доступно)
- Для каждого workflow вызывается `workflow.get_initial_state()` - дополнительный запрос к БД

**Проблема:** При частых обращениях к этим endpoints (особенно при загрузке форм на фронтенде) создается избыточная нагрузка на БД. Конфигурация типов документов меняется редко, поэтому идеально подходит для кеширования.

## Цель

Реализовать кеширование конфигурации типов документов с TTL 1 час, чтобы снизить нагрузку на БД и улучшить производительность API.

## Текущая конфигурация кеша

Согласно BACKEND_AUDIT_V1.md (раздел 1.3):
- **Backend:** `django.core.cache.backends.locmem.LocMemCache`
- **Timeout:** 300 секунд (5 минут) - для throttling counters
- **Max Entries:** 1000

**Примечание:** Для кеширования конфигурации типов документов будет использоваться тот же cache backend, но с TTL 3600 секунд (1 час). В production рекомендуется использовать Redis для распределенного кеширования.

## Структура данных для кеширования

### Список типов документов (`_get_all_configs()`):
```python
[
    {
        'id': int,
        'label': str,
        'description': str,
        'url': str  # '/api/v4/headless/config/document_types/{id}/'
    },
    ...
]
```

### Детальная конфигурация (`_get_single_config()`):
```python
{
    'id': int,
    'label': str,
    'description': str,
    'required_metadata': [
        {
            'id': int,
            'name': str,
            'label': str,
            'type': str,  # 'text', 'select', 'email', 'url', 'date'
            'required': bool,
            'default_value': str | None,
            'validation_regex': str | None,
            'options': list[str] | None  # для select полей
        },
        ...
    ],
    'optional_metadata': [...],  # та же структура
    'workflows': [
        {
            'id': int,
            'label': str,
            'initial_state': str | None
        },
        ...
    ],
    'retention_policy': {
        'enabled': bool,
        'days': int
    },
    'capabilities': {
        'ocr_enabled': bool,
        'ai_analysis_enabled': bool,
        'preview_enabled': bool
    }
}
```

**Важно:** Все данные уже сериализуемы в JSON (словари и списки), поэтому можно кешировать напрямую без дополнительной сериализации.

---

## Разбивка задачи на подзадачи

### 1. Анализ и проектирование

#### 1.1. Определить структуру кеш-ключей
- **Файл:** `mayan/apps/headless_api/views/config_views.py`
- **Задача:** 
  - Определить формат ключей для списка: `headless_doc_type_config_list` или `headless_doc_type_config_list_v1`
  - Определить формат ключей для детальной конфигурации: `headless_doc_type_config_{id}` или `headless_doc_type_config_{id}_v1`
  - Учесть версионирование кеша (для будущих изменений схемы ответа API)
  - Использовать единый префикс для всех ключей кеша headless_api
- **Время:** 15 минут
- **Зависимости:** Нет
- **Примечание:** Формат ключей должен быть уникальным и не конфликтовать с другими кешами в системе

#### 1.2. Определить стратегию инвалидации кеша
- **Файлы:** 
  - `mayan/apps/documents/models/document_type_models.py`
  - `mayan/apps/metadata/models/document_type_metadata_type_models.py`
  - `mayan/apps/document_states/models/workflow_models.py` (опционально)
- **Задача:**
  - Определить сигналы для отслеживания изменений:
    - `post_save` на `DocumentType` → инвалидировать список (`_list`) и конкретный тип (`_{id}`)
    - `post_delete` на `DocumentType` → инвалидировать список (конкретный тип уже удален)
    - `post_save`/`post_delete` на `DocumentTypeMetadataType` → инвалидировать конкретный тип (`_{document_type_id}`)
    - Изменения в workflows (если отслеживаемо) → инвалидировать все типы, связанные с workflow
  - Определить, нужны ли сигналы в `headless_api` или можно использовать существующие в `documents`
  - **Важно:** Workflows связаны через `hasattr(doc_type, 'workflows')` и `doc_type.workflows.all()`, но изменения в workflows могут не триггерить сигналы на DocumentType. Нужно проверить, как отслеживать изменения связей ManyToMany.
- **Время:** 30 минут
- **Зависимости:** 1.1

### 2. Реализация кеширования в View

#### 2.1. Добавить импорты и константы
- **Файл:** `mayan/apps/headless_api/views/config_views.py`
- **Задача:**
  - Добавить `from django.core.cache import cache`
  - Определить константы:
    - `DOC_TYPE_CONFIG_CACHE_TTL = 3600` (1 час)
    - `DOC_TYPE_CONFIG_CACHE_PREFIX = 'headless_doc_type_config'`
- **Время:** 10 минут
- **Зависимости:** 1.1

#### 2.2. Реализовать кеширование для списка типов
- **Файл:** `mayan/apps/headless_api/views/config_views.py`
- **Метод:** `_get_all_configs()`
- **Задача:**
  - Проверить кеш перед запросом к БД
  - Если кеш есть → вернуть из кеша
  - Если кеша нет → выполнить запрос, закешировать результат, вернуть
  - Обработать ошибки кеша (fallback на БД) - использовать try-except вокруг cache.get/set
  - **Важно:** Кешировать уже сериализованный JSON-ответ (список словарей), а не queryset
- **Код:**
  ```python
  def _get_all_configs(self):
      cache_key = f'{DOC_TYPE_CONFIG_CACHE_PREFIX}_list'
      
      try:
          cached_configs = cache.get(cache_key)
          if cached_configs is not None:
              logger.debug('Document types list cache HIT')
              return Response(cached_configs)
      except Exception as e:
          logger.warning(f'Cache get error: {e}, falling back to DB')
      
      logger.debug('Document types list cache MISS')
      try:
          doc_types = DocumentType.objects.all()
          configs = []
          for doc_type in doc_types:
              configs.append(self._build_basic_config(doc_type))
          
          try:
              cache.set(cache_key, configs, DOC_TYPE_CONFIG_CACHE_TTL)
          except Exception as e:
              logger.warning(f'Cache set error: {e}, continuing without cache')
          
          return Response(configs)
      except Exception as e:
          logger.error(f"Error getting document types list: {str(e)}")
          return Response(
              {'error': _('Error retrieving document types'), 'error_code': 'INTERNAL_ERROR'},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )
  ```
- **Время:** 20 минут
- **Зависимости:** 2.1

#### 2.3. Реализовать кеширование для детальной конфигурации
- **Файл:** `mayan/apps/headless_api/views/config_views.py`
- **Метод:** `_get_single_config(document_type_id)`
- **Задача:**
  - Проверить кеш перед запросом к БД
  - Если кеш есть → вернуть из кеша
  - Если кеша нет → выполнить запрос, закешировать результат, вернуть
  - Обработать ошибки кеша и 404 (fallback на БД)
  - **Важно:** Не кешировать 404 ответы (только успешные конфигурации)
  - **Важно:** Кешировать уже сериализованный JSON-ответ (словарь), включая все вложенные структуры (metadata, workflows)
- **Код:**
  ```python
  def _get_single_config(self, document_type_id):
      cache_key = f'{DOC_TYPE_CONFIG_CACHE_PREFIX}_{document_type_id}'
      
      try:
          cached_config = cache.get(cache_key)
          if cached_config is not None:
              logger.debug(f'Document type {document_type_id} config cache HIT')
              return Response(cached_config)
      except Exception as e:
          logger.warning(f'Cache get error: {e}, falling back to DB')
      
      logger.debug(f'Document type {document_type_id} config cache MISS')
      try:
          doc_type = DocumentType.objects.get(pk=document_type_id)
          config = self._build_full_config(doc_type)
          
          try:
              cache.set(cache_key, config, DOC_TYPE_CONFIG_CACHE_TTL)
          except Exception as e:
              logger.warning(f'Cache set error: {e}, continuing without cache')
          
          return Response(config)
      except ObjectDoesNotExist:
          # Не кешируем 404
          return Response(
              {'error': _('Document type not found'), 'error_code': 'NOT_FOUND'},
              status=status.HTTP_404_NOT_FOUND
          )
      except Exception as e:
          logger.error(f"Error getting document type config {document_type_id}: {str(e)}")
          return Response(
              {'error': _('Error retrieving document type configuration'), 'error_code': 'INTERNAL_ERROR'},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )
  ```
- **Время:** 20 минут
- **Зависимости:** 2.1

### 3. Реализация инвалидации кеша

#### 3.1. Создать модуль для инвалидации кеша
- **Файл:** `mayan/apps/headless_api/cache_utils.py` (новый)
- **Задача:**
  - Создать функции для инвалидации:
    - `invalidate_document_type_config_cache(document_type_id=None)` 
      - Если `document_type_id` указан → инвалидировать конкретный тип и список
      - Если `None` → инвалидировать только список
  - Использовать `cache.delete()` для удаления ключей
- **Код:**
  ```python
  from django.core.cache import cache
  
  DOC_TYPE_CONFIG_CACHE_PREFIX = 'headless_doc_type_config'
  
  def invalidate_document_type_config_cache(document_type_id=None):
      """Invalidate document type configuration cache."""
      if document_type_id:
          cache_key = f'{DOC_TYPE_CONFIG_CACHE_PREFIX}_{document_type_id}'
          cache.delete(cache_key)
          logger.debug(f'Invalidated cache for document type {document_type_id}')
      
      # Always invalidate list cache when any type changes
      list_cache_key = f'{DOC_TYPE_CONFIG_CACHE_PREFIX}_list'
      cache.delete(list_cache_key)
      logger.debug('Invalidated document types list cache')
  ```
- **Время:** 20 минут
- **Зависимости:** 2.1

#### 3.2. Добавить сигналы для инвалидации при изменении DocumentType
- **Файл:** `mayan/apps/headless_api/signals.py` (новый или существующий)
- **Задача:**
  - Подписаться на `post_save` и `post_delete` сигналы от `DocumentType`
  - Вызывать `invalidate_document_type_config_cache(document_type_id=instance.pk)`
- **Код:**
  ```python
  from django.db.models.signals import post_save, post_delete
  from django.dispatch import receiver
  from mayan.apps.documents.models import DocumentType
  from .cache_utils import invalidate_document_type_config_cache
  
  @receiver(post_save, sender=DocumentType)
  def invalidate_doc_type_cache_on_save(sender, instance, **kwargs):
      invalidate_document_type_config_cache(document_type_id=instance.pk)
  
  @receiver(post_delete, sender=DocumentType)
  def invalidate_doc_type_cache_on_delete(sender, instance, **kwargs):
      invalidate_document_type_config_cache(document_type_id=instance.pk)
  ```
- **Время:** 15 минут
- **Зависимости:** 3.1

#### 3.3. Добавить сигналы для инвалидации при изменении DocumentTypeMetadataType
- **Файл:** `mayan/apps/headless_api/signals.py`
- **Задача:**
  - Подписаться на `post_save` и `post_delete` сигналы от `DocumentTypeMetadataType`
  - Вызывать `invalidate_document_type_config_cache(document_type_id=instance.document_type.pk)`
- **Код:**
  ```python
  from mayan.apps.metadata.models import DocumentTypeMetadataType
  
  @receiver(post_save, sender=DocumentTypeMetadataType)
  @receiver(post_delete, sender=DocumentTypeMetadataType)
  def invalidate_doc_type_cache_on_metadata_change(sender, instance, **kwargs):
      invalidate_document_type_config_cache(document_type_id=instance.document_type.pk)
  ```
- **Время:** 15 минут
- **Зависимости:** 3.1

#### 3.4. Добавить инвалидацию при изменении workflows (опционально)
- **Файл:** `mayan/apps/headless_api/signals.py`
- **Задача:**
  - Определить, как отслеживать изменения в workflows
  - Если workflows связаны через ManyToMany → отслеживать изменения связи через `m2m_changed` сигнал
  - Вызывать инвалидацию для всех связанных типов документов
  - **Примечание:** В текущей реализации `_get_workflows()` использует `hasattr()` и `doc_type.workflows.all()`, что означает, что workflows могут быть связаны через related_name. Нужно проверить модель Workflow и найти связь с DocumentType.
  - **Альтернатива:** Если отслеживание изменений workflows сложно, можно полагаться на TTL (1 час) для автоматической инвалидации
- **Время:** 30-60 минут (если нужно, зависит от сложности связей)
- **Зависимости:** 3.1, 1.2

#### 3.5. Зарегистрировать сигналы в apps.py
- **Файл:** `mayan/apps/headless_api/apps.py`
- **Задача:**
  - Убедиться, что сигналы импортируются в методе `ready()`
  - Добавить импорт: `from . import signals  # noqa: F401`
- **Время:** 10 минут
- **Зависимости:** 3.2, 3.3

### 4. Тестирование

#### 4.1. Написать unit-тесты для кеширования
- **Файл:** `mayan/apps/headless_api/tests/test_config_views_cache.py` (новый)
- **Задача:**
  - Тест: кеш работает для списка типов
  - Тест: кеш работает для детальной конфигурации
  - Тест: кеш инвалидируется при изменении DocumentType
  - Тест: кеш инвалидируется при изменении DocumentTypeMetadataType
  - Тест: fallback на БД при ошибке кеша
- **Время:** 45 минут
- **Зависимости:** 2.2, 2.3, 3.2, 3.3

#### 4.2. Провести ручное тестирование
- **Задача:**
  - Проверить работу кеша через API endpoints
  - Проверить инвалидацию при изменении типов документов через админку
  - Проверить производительность (сравнить время ответа до/после)
- **Время:** 30 минут
- **Зависимости:** Все предыдущие задачи

### 5. Документация

#### 5.1. Обновить BACKEND_AUDIT_V1.md
- **Файл:** `docs/transformation-2025/BACKEND_AUDIT_V1.md`
- **Задача:**
  - Отметить задачу как выполненную (✅ **РЕШЕНО**)
  - Добавить описание реализации в раздел 5.7
  - Обновить дату последнего обновления
- **Время:** 15 минут
- **Зависимости:** Все предыдущие задачи

#### 5.2. Добавить docstrings в код
- **Файлы:** 
  - `mayan/apps/headless_api/views/config_views.py`
  - `mayan/apps/headless_api/cache_utils.py`
  - `mayan/apps/headless_api/signals.py`
- **Задача:**
  - Добавить docstrings с описанием кеширования
  - Указать TTL и стратегию инвалидации
- **Время:** 15 минут
- **Зависимости:** Все предыдущие задачи

---

## Итоговая оценка времени

| Подзадача | Время |
|-----------|-------|
| 1. Анализ и проектирование | 45 минут |
| 2. Реализация кеширования в View | 50 минут |
| 3. Реализация инвалидации кеша | 90 минут |
| 4. Тестирование | 75 минут |
| 5. Документация | 30 минут |
| **ИТОГО** | **~4.5 часа** |

---

## Риски и зависимости

### Риски:
1. **Производительность кеша:** LocMemCache может быть недостаточно для production (нужен Redis)
   - **Решение:** Использовать существующий Redis cache backend в production. LocMemCache подходит для development, но в production нужен распределенный кеш.
2. **Инвалидация workflows:** Может быть сложно отследить все изменения
   - **Решение:** Начать с базовых сигналов (DocumentType, DocumentTypeMetadataType), расширить при необходимости. Для workflows можно полагаться на TTL.
3. **Конкурентный доступ:** При одновременных изменениях может быть race condition
   - **Решение:** Использовать `cache.set()` с TTL (автоматическая инвалидация через час). TTL обеспечивает eventual consistency.
4. **Размер кеша:** При большом количестве типов документов список может быть большим
   - **Решение:** Мониторить размер кеша. При необходимости можно кешировать только часто используемые типы или использовать более агрессивную инвалидацию.
5. **Ошибки кеша:** При недоступности кеша (Redis down) система должна продолжать работать
   - **Решение:** Все операции с кешем обернуты в try-except с fallback на БД

### Зависимости:
- Django cache framework (уже настроен)
- Сигналы Django (стандартная функциональность)
- Модели `DocumentType`, `DocumentTypeMetadataType` (существующие)

---

## Критерии приемки

1. ✅ Список типов документов кешируется на 1 час
2. ✅ Детальная конфигурация типа кешируется на 1 час
3. ✅ Кеш инвалидируется при изменении DocumentType
4. ✅ Кеш инвалидируется при изменении DocumentTypeMetadataType
5. ✅ При ошибке кеша выполняется fallback на БД
6. ✅ Написаны unit-тесты с покрытием >80%
7. ✅ Документация обновлена
8. ✅ Производительность улучшена (время ответа снижено минимум на 50% при cache hit)

---

## Дополнительные улучшения (опционально)

1. **Версионирование кеша:** Добавить версию в ключ кеша для будущих изменений схемы
2. **Метрики:** Добавить логирование статистики cache hit/miss
3. **Настройка TTL через settings:** Вынести TTL в настройки для гибкости
4. **Кеширование на уровне middleware:** Рассмотреть кеширование на уровне DRF (если нужно)

