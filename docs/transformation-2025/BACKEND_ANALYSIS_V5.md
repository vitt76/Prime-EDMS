# Backend Analysis V5 — Prime-EDMS / DAM System (Django / Mayan)

**Дата анализа:** 08 декабря 2025  
**Версия:** 5.0 (Фактическое состояние кода — устранение архитектурного дрейфа)  
**Автор:** Lead Software Architect  
**Статус:** 🔴 Требуются дополнения (self-service API на фронте ещё не подключён)

---

## 1. Что действительно развернуто (доказано кодом)

- **INSTALLED_APPS:** `mayan.apps.headless_api` подключен в `mayan/settings/base.py` (стр. ~101).
- **Аутентификация:** DRF `TokenAuthentication` + `SessionAuthentication` (нет Knox / SimpleJWT). См. `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`, `DEFAULT_PERMISSION_CLASSES=IsAuthenticated`, Stronghold закрывает HTML/REST без сессии/токена.
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
| `POST /api/v4/headless/documents/{id}/versions/new_from_edit/` | `HeadlessEditView` | 🔴 **НЕ ПРОБРОШЕН** | Реализован во view, но **нет** в `mayan/apps/rest_api/urls.py`; import в `headless_api/urls.py` указывает на `profile_views` → 404 | Требуется подключить через REST API маршруты |
| `GET /api/v4/headless/profile/` | `HeadlessProfileView` | Token/Session | Профиль текущего пользователя | Вернёт id/username/email/is_staff/is_superuser |

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
- **Сейчас не подключён в REST API:** в `mayan/apps/rest_api/urls.py` нет маршрута для `new_from_edit`, поэтому вызов `/api/v4/headless/documents/{id}/versions/new_from_edit/` вернёт 404.  
- В `mayan/apps/headless_api/urls.py` endpoint описан, но импорт ошибочный (`HeadlessEditView` тянется из `profile_views`, а не из `version_views`).  
- Логика (реализована во view):
  - Читает `file` из multipart, опционально `format` (конвертация через Pillow), `comment`, `action_id` (default `DocumentFileActionUseNewPages.backend_id`).
  - Проверяет ACL `permission_document_version_create`.
  - Создаёт новую `DocumentFile` через `document.file_new(...)`.
  - Возвращает `{document_id, file_id, version_id, version}` (cериализовано `HeadlessDocumentVersionSerializer`).
  - HTML view `ImageEditorSaveView` в `mayan/apps/image_editor/views.py` помечен как **DEPRECATED** и должна переадресовывать на headless API после починки маршрута.

### HeadlessPasswordChangeView (`mayan/apps/headless_api/views/password_views.py`)
- Auth: Session + Token, Permission: `IsAuthenticated`.
- Валидация: проверяет `current_password` через `check_password`, совпадение новых паролей, прогоняет Django `validate_password`; при ошибке — `400` с `error_code` (`MISSING_FIELDS`, `INVALID_CURRENT_PASSWORD`, `PASSWORD_MISMATCH`, `PASSWORD_VALIDATION_FAILED`).
- Без инвалидирования токена/сессии; при успехе логирует событие и возвращает 200.

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

### Profile
- `GET /headless/profile/` — короткий профиль текущего пользователя (id, username, first_name, last_name, email, is_staff, is_superuser).

### RBAC / Roles & Permissions (ядро Mayan)
- REST API для ролей и прав подключён через `permissions_api_urls` в `mayan/apps/rest_api/urls.py`.
- Доступные маршруты (`/api/v4/permissions/...`):
  - `GET /permissions/` — список всех stored permissions.
  - `GET/POST /roles/`, `GET /roles/{id}/` — CRUD ролей.
  - `GET /roles/{id}/groups/`, `POST /roles/{id}/groups/add/`, `POST /roles/{id}/groups/remove/` — управление связью ролей и групп.
  - `GET /roles/{id}/permissions/`, `POST /roles/{id}/permissions/add/`, `POST /roles/{id}/permissions/remove/` — управление правами роли.
- ACL остаются обязательными: даже с ролью без ACL документ недоступен.

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
| new_from_edit | 🔴 Реализован view, **не подключён** в `rest_api/urls.py`; неправильный импорт в `headless_api/urls.py` | Добавить url в REST API и исправить импорт на `version_views.HeadlessEditView` |
| Auth | ✅ Token/Session | Нет JWT; редирект/очистка токена реализованы на фронте |

---

## 6. Итог для V5

1) **API Surface (headless) подтверждён**: password/change, config/document_types (list/detail), activity/feed, dashboard/activity, favorites (list/toggle), documents/my_uploads, profile.  
2) **HeadlessEditView** реализован, но **не проброшен** в `rest_api/urls.py` (нужен маршрут) и в `headless_api/urls.py` импортируется неверно; фактически отдаёт 404 до исправления.  
3) **OptimizedDocumentSerializer** реально содержит `document_type_id` (write_only) и `document_type` (read).  
4) **Аутентификация** — только DRF Token + Session; никаких Knox/SimpleJWT.  
5) **Документация V4** устарела: headless endpoints существуют; фронт подключён частично и gated через `VITE_BFF_ENABLED`.  
6) **Дальнейшие действия:** пробросить `new_from_edit` в REST, исправить импорт, синхронизировать фронт (services/stores) на headless endpoints, добавить e2e smoke для `/headless/activity/feed/`, `/headless/config/document_types/{id}/`, `/headless/documents/{id}/versions/new_from_edit/` после подключения, убрать использование deprecated HTML `ImageEditorSaveView`.

---

**Версия документа:** 5.0 (Синхронизация с реальным кодом)  
**Дата:** 08 декабря 2025  
**Автор:** Lead Software Architect

