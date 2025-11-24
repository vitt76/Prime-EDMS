# Спецификации недостающих REST-эндпоинтов для SPA

Документ фиксирует дизайн новых API, необходимых для полного функционала SPA. Формат: URI, поддерживаемые методы, структура запроса/ответа, требования по ACL и взаимодействие с существующими задачами.

## 1. Bulk-операции над документами

- **URI**: `POST /api/v4/documents/bulk/`
- **Payload**:
  ```json
  {
    "operation": "change_type",  // change_type | add_tags | remove_tags | delete | restore | assign_metadata
    "document_ids": [1, 2, 3],
    "params": {
      "document_type_id": 7,
      "tag_ids": [4, 5],
      "metadata": [{"type_id": 9, "value": "2025-01-01"}]
    }
  }
  ```
- **Ответ**: `202 Accepted` + `{ "job_id": "<uuid>", "affected": 3 }`. Работа уходит в Celery (`queue='documents'`).
- **ACL**: проверяем `permission_document_view` + дополнительные (например, `permission_document_properties_edit` при `change_type`).

## 2. Bulk-обновление метаданных

- **URI**: `POST /api/v4/metadata/bulk_update/`
- **Payload**:
  ```json
  {
    "document_ids": [1,2],
    "metadata": [
      {"type_id": 5, "value": "ACME"},
      {"type_id": 6, "value": "2025-12-31"}
    ],
    "overwrite": true
  }
  ```
- **Ответ**: `200 OK` + список документов с применёнными изменениями или `202` + `job_id` (если по времени долго).
- **ACL**: `permission_metadata_document_edit`.

## 3. Управление API-токенами (реализовано)

- **URI**:
  - `GET /api/v4/auth/tokens/`
  - `POST /api/v4/auth/tokens/`
  - `DELETE /api/v4/auth/tokens/<key>/`
- **Ответ**:
  ```json
  {
    "key": "ea9bafd7...",
    "user_id": 1,
    "created": "2025-11-24T08:00:00Z"
  }
  ```
- **ACL**: владелец видит только свои записи; суперпользователь — все. Создавать токен для другого пользователя может только суперпользователь.

## 4. Smart Settings REST

- **URI**:
  - `GET /api/v4/system/settings/` (параметры `namespace`, `search`).
  - `PATCH /api/v4/system/settings/<namespace>/<setting_name>/`.
- **Ответ**:
  ```json
  {
    "name": "COMMON__STORAGE_BACKEND",
    "namespace": "COMMON",
    "value": "django.core.files.storage.FileSystemStorage",
    "description": "...",
    "modified_at": "2025-11-24T10:15:00Z"
  }
  ```
- **ACL**: `permission_settings_edit`. Все изменения логируются в Events (`namespace="system"`).

## 5. Дерево индексов

- **URI**: `GET /api/v4/indexes/index_instances/`
- **Параметры**: `?template_id=...`, `?parent_id=...`, `?depth=2`.
- **Ответ**:
  ```json
  {
    "id": 42,
    "label": "2025",
    "parent": null,
    "children": [
      {"id": 43, "label": "01", "children": []}
    ]
  }
  ```
- **ACL**: `permission_index_instance_view`. Используем `AccessControlList.restrict_queryset`.

## 6. Effective permissions документа

- **URI**: `GET /api/v4/documents/<id>/effective_permissions/`
- **Ответ**:
  ```json
  {
    "document_id": 10,
    "user_id": 5,
    "roles": ["manager"],
    "permissions": [
      "documents.view_document",
      "documents.download_document",
      "documents.change_document"
    ]
  }
  ```
- **ACL**: доступен владельцу документа, администраторам или пользователю, для которого выполняется запрос (`?user_id=`). Внутри используем ACL и глобальные роли.

## 7. Upload без источников (опционально)

- **URI**: `POST /api/v4/documents/<id>/upload/`
- **Payload**: multipart (`file`, `filename`, `mimetype`).
- **Логика**: создаёт `DocumentFile` с автоматическим источником “SPA Direct Upload”, прогоняет через converter pipeline, публикует сигнал `document_file_created`.

---

**Следующие шаги**: после согласования спецификаций обновляем Swagger, добавляем сериализаторы/viewsets и покрываем Celery задачами (см. TODO `Реализовать и протестировать новые методы`).*** End Patch

