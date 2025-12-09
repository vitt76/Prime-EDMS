# Backend Analysis V5 — Prime-EDMS / DAM System (Django / Mayan)

**Дата анализа:** 08 декабря 2025  
**Версия:** 5.0 (Фактическое состояние кода — устранение архитектурного дрейфа)  
**Автор:** Lead Software Architect  
**Статус:** 🔴 Требуются дополнения (self-service API на фронте ещё не подключён)

---

## 1. Что действительно развернуто (доказано кодом)

- **INSTALLED_APPS:** `mayan.apps.headless_api` подключен в `mayan/settings/base.py` (стр. ~101).
- **Аутентификация:** DRF `TokenAuthentication` + `SessionAuthentication` (нет Knox / SimpleJWT). См. `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`.
- **URL включение:** headless endpoints подключены в `mayan/apps/rest_api/urls.py` под префиксом `/api/v4/headless/` (AcceptHeaderVersioning). Отдельный `mayan/apps/headless_api/urls.py` зеркалирует маршруты, но фактический вход — через REST API router.

---

## 2. Реальная поверхность API (headless + связанные оптимизированные сериализаторы)

| Endpoint | View | Auth | Назначение | Примечания |
|----------|------|------|------------|------------|
| `POST /api/v4/headless/password/change/` | `HeadlessPasswordChangeView` | Token/Session | Смена пароля | Проверка `current_password`, Django validators, **не инвалидирует токен** |
| `GET /api/v4/headless/config/document_types/` | `HeadlessDocumentTypeConfigView` | Token/Session | Базовый список типов | Возвращает `id/label/description/url` |
| `GET /api/v4/headless/config/document_types/{id}/` | `HeadlessDocumentTypeConfigView` | Token/Session | Полная конфигурация типа | `required_metadata/optional_metadata/workflows/retention/capabilities` |
| `GET /api/v4/headless/activity/feed/` | `HeadlessActivityFeedView` | Token/Session | Персональная лента | filter=`my_actions|my_documents|all`, пагинация |
| `GET /api/v4/headless/dashboard/activity/` | `DashboardActivityView` | Token/Session | Упрощённая лента для дашборда | Возвращает последние N событий (по умолчанию 20) |
| `GET /api/v4/headless/favorites/` | `HeadlessFavoriteListView` | Token/Session | Избранное пользователя | Пагинация, использует `OptimizedDocumentListSerializer` |
| `POST /api/v4/headless/favorites/{document_id}/` | `HeadlessFavoriteToggleView` | Token/Session | Добавить/убрать из избранного | Проверка ACL (view) |
| `GET /api/v4/headless/documents/my_uploads/` | `HeadlessMyUploadsView` | Token/Session | «Мои загрузки» | По событиям `documents.document_create`/`document_file_created`, ACL фильтр |
| `POST /api/v4/headless/documents/{id}/versions/new_from_edit/` | `HeadlessEditView` | Token/Session | Создание новой версии из отредактированного изображения | Принимает `file` (multipart), опционально `format`, `comment`, `action_id`; конвертация через Pillow |

### Связанные сериализаторы (documents)
- `OptimizedDocumentListSerializer`: содержит `document_type_id` (read-only) и `document_type_label`, file_latest*, thumbnail/preview/download URLs (кэшируемые).
- `OptimizedDocumentSerializer` (detail): **имеет `document_type_id` write_only**, `document_type` (id/label), `file_latest`, `version_active`, `tags`, `metadata`, `ai_analysis`. Подтверждает возможность передачи `document_type_id` при создании/обновлении.
- `HeadlessDocumentVersionSerializer`: возвращает id версии, `thumbnail_url`, `download_url` для новых версий из редактора.

### Дополнительные headless сериализаторы
- `ActivityFeedSerializer` (dashboard): плоская лента событий с map verb → icon.
- `FavoriteDocumentEntrySerializer`: оборачивает документ через `OptimizedDocumentListSerializer`.

---

## 3. Подробности реализации ключевых view

### HeadlessEditView (`mayan/apps/headless_api/views/version_views.py`)
- Маршрут: `/api/v4/headless/documents/{document_id}/versions/new_from_edit/`.
- Auth: Session + Token, Permission: `permission_document_version_create` (ACL check).
- Логика:
  - Читает `file` из multipart, опционально `format` (конвертация через Pillow), `comment`, `action_id` (default `DocumentFileActionUseNewPages.backend_id`).
  - Создаёт новую `DocumentFile` через `document.file_new(...)`.
  - Возвращает `{document_id, file_id, version_id, version}` (cериализовано `HeadlessDocumentVersionSerializer`).
  - HTML view `ImageEditorSaveView` в `mayan/apps/image_editor/views.py` помечен как **DEPRECATED** и переадресует на headless API.

### HeadlessDocumentTypeConfigView
- Даёт полный конфиг: required/optional metadata (lookup → select options), workflows (если есть), retention, capabilities (`ocr_enabled`, `ai_analysis_enabled`, `preview_enabled`).
- Возвращает 404 при отсутствии doc type; 500 с `error_code: INTERNAL_ERROR` при исключениях.

### HeadlessActivityFeedView
- Параметры: `filter` (my_actions | my_documents | all), `page`, `page_size`.
- Ограничивает выдачу 500 последних действий; сериализация включает `actor`, `verb` (с переводом), `target` с ссылкой (`/api/v4/documents/{id}/` и пр.).

### Favorites
- `GET /headless/favorites/` пагинирует избранное текущего пользователя, применяет ACL `permission_document_view`.
- `POST /headless/favorites/{document_id}/` — toggle; для несуперпользователей проверяет ACL.

### My Uploads
- Использует события (`Action`) с verb `documents.document_create`/`document_file_created`, actor = текущий пользователь, target_content_type = Document; приводит target_object_id к int.
- Результат сериализуется `OptimizedDocumentListSerializer` + ACL фильтр.

---

## 4. Что отсутствует / устарело в документации V4

- **JWT/Knox** — отсутствуют. Единственные активные классы аутентификации: DRF Token + Session.
- **HeadlessPasswordView** есть, но BFF-обёртки не нужны для смены пароля (уже REST), однако фронт всё ещё должен вызвать headless endpoint, не core `/users/current/password/`.
- **Config API** реализован (headless), фронт читает только при `VITE_BFF_ENABLED=true`; при false возвращает пустой список/ошибку и не валидирует метаданные.
- **Activity Feed** реализована (headless). В фронте используется только упрощённый dashboard endpoint; персональная feed пока не подключена.

---

## 5. Известные проблемы / долги

| Область | Статус | Детали |
|---------|--------|--------|
| Смена пароля | ✅ Endpoint есть (`/headless/password/change/`), но требуется корректный токен | Фронтенд использует вызов через authService только при `VITE_BFF_ENABLED=true`; иначе ломается |
| Динамическая конфигурация типов | ✅ Endpoint есть (list/detail) | Фронт запрашивает только при `VITE_BFF_ENABLED=true`; при false метаданные не валидируются |
| Лента активности | ✅ Реализована (feed + dashboard) | В фронте используется только dashboard endpoint; персональная feed не подключена |
| My Uploads | ✅ Реализовано через события | Нужна привязка фронтенда (коллекции «Мои загрузки») |
| Favorites | ✅ Реализовано | Проверить интеграцию коллекций на фронте |
| Auth | ✅ Token/Session | Нет JWT; редирект/очистка токена реализованы на фронте |

---

## 6. Итог для V5

1) **API Surface (headless) подтверждён**: password/change, config/document_types (list/detail), activity/feed, dashboard/activity, favorites (list/toggle), documents/my_uploads, documents/{id}/versions/new_from_edit.  
2) **OptimizedDocumentSerializer** реально содержит `document_type_id` (write_only) и `document_type` (read).  
3) **Аутентификация** — только DRF Token + Session; никаких Knox/SimpleJWT.  
4) **Документация V4** устарела: headless endpoints существуют; фронт подключён частично и gated через `VITE_BFF_ENABLED`.  
5) **Дальнейшие действия:** синхронизировать фронт (services/stores) на headless endpoints, добавить e2e smoke для `/headless/documents/{id}/versions/new_from_edit/`, `/headless/activity/feed/`, `/headless/config/document_types/{id}/`, убрать использование deprecated HTML `ImageEditorSaveView`.

---

**Версия документа:** 5.0 (Синхронизация с реальным кодом)  
**Дата:** 08 декабря 2025  
**Автор:** Lead Software Architect

