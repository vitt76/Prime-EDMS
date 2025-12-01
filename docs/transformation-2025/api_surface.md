# Поверхность API Prime EDMS и интеграционные хуки

> Этот документ — единый контракт между backend и новым SPA. В нём перечислены все актуальные REST‑эндпоинты, фоновые пайплайны (Celery/сигналы) и точки расширения Mayan/Prime EDMS. Базовые URL приведены относительно корня инсталляции (`https://host/`). Все ответы — JSON, если явно не указано HTML.

---

## 1. Глобальные правила

- **Аутентификация**: DRF включает `SessionAuthentication`, `TokenAuthentication`, Basic. Middleware Stronghold закрывает все URL, кроме whitelisted. Неавторизованные запросы получают `302 /authentication/login/?next=...`.
- **Token API**: `POST /api/v4/auth/token/obtain/` принимает `{"username":"", "password":""}` и возвращает `{"token": "..."}`. Управление токенами пока отсутствует (см. раздел 9).
- **Заголовки**: для REST используйте `Authorization: Token <key>` или cookie‑сессию.
- **Тип данных**: `application/json`. Загрузка файлов — multipart (DRF parsers).
- **Пагинация**: `MayanPageNumberPagination`, параметры `?page`, `?page_size` (верхний предел управляется Smart Settings).
- **ACL**: все QuerySet’ы оборачиваются `AccessControlList.objects.restrict_queryset(permission_document_view, ...)`. Даже пользователь с глобальными правами получит 403, если нет ACL.
- **Ошибки**: 400 — валидация, 401/302 — аутентификация, 403 — ACL, 404 — объект отсутствует. Stronghold возвращает HTML‑страницу, поэтому фронту важно проверять `Content-Type`.

---

## 2. Аутентификация и сессии

| Действие | Путь | Примечание |
| --- | --- | --- |
| Логин (форма) | `POST /authentication/login/` | Для cookie‑сессий. |
| Логаут | `POST /authentication/logout/` | Завершает сессию. |
| Получить DRF token | `POST /api/v4/auth/token/obtain/` | Возвращает `{"token": "..."} `. |
| Управление токенами | `GET/POST /api/v4/auth/tokens/`, `DELETE /api/v4/auth/tokens/<key>/` | Пользователь видит только свои токены, суперпользователь — все; повторное `POST` вращает ключ. |

---

## 3. Документы и файлы (`/api/v4/documents/...`)

| Возможность | Эндпоинт | Комментарий |
| --- | --- | --- |
| Список/создание документов | `GET/POST /documents/` | Фильтры `?q`, `?document_type_id`, `?ordering`. |
| Деталь/редактирование | `GET/PATCH/DELETE /documents/<id>/` | `PATCH` обновляет свойства. |
| Смена типа | `POST /documents/<id>/change_type/` | Требует `permission_document_properties_edit`. |
| Загрузка файлов | `POST /document_files/` | Привязка к документу. |
| Просмотр файла | `GET /document_files/<id>/` и `/document_files/<id>/download/` | Возвращает метаданные/файл. |
| Версии | `/document_versions/`, `/document_versions/<id>/export/` | Управление версиями. |
| Корзина | `/trashed_documents/`, `/trashed_documents/<id>/restore/` | Удалённые документы. |
| Избранное / недавно | `/favorites/`, `/recently_accessed/`, `/recently_created/` | Персональные списки. |

**Пробелы**: нет bulk‑операций (массовое изменение типа, тегов, метаданных) и облегчённого upload без источников. Требуются новые endpoints (см. раздел 12).

---

## 4. Типы документов и метаданные

| Возможность | Эндпоинт | Комментарий |
| --- | --- | --- |
| CRUD типов метаданных | `/api/v4/metadata/metadata_types/` | Управление справочником. |
| Привязка метаданных к типу документов | `/api/v4/metadata/document_types/<doc_type_id>/metadata_types/` | Настройка обязательности, значений по умолчанию. |
| Значения у документа | `/api/v4/metadata/documents/<doc_id>/metadata/` | `GET/POST/PATCH`. |

**Пробел**: нет массового обновления значений. Нужен endpoint `POST /metadata/bulk_update/`.

---

## 5. Теги и кабинеты

- **Теги** (`mayan.apps.tags`):
  - `/api/v4/tags/tags/` — CRUD.
  - `/api/v4/tags/tags/<id>/attach/` — `{ "document_ids": [...] }`.
  - `/api/v4/tags/tags/<id>/documents/` — связанные документы.
- **Кабинеты** (`mayan.apps.cabinets`):
  - `/api/v4/cabinets/cabinets/` — дерево (поддерживает `parent`).
  - `/api/v4/cabinets/cabinets/<id>/documents/` — управление членством.

**Пробел**: нет API для перемещения веток кабинетов (нужен `PATCH /cabinets/<id>/move/`).

---

## 6. Поиск, индексы, рабочие области

- `/api/v4/dynamic_search/search/` — глобальный поиск (`q`, `app_label`, `model_name`, `backend`).
- `/api/v4/indexes/index_templates/` — шаблоны индексов. Нет REST для дерева index instances (нужен `/api/v4/indexes/index_instances/`).
- `/api/v4/documents/recently_accessed/` и другие — поддерживают quick filters.

---

## 7. Пользователи, группы, ACL

| Возможность | Эндпоинт |
| --- | --- |
| CRUD пользователей | `/api/v4/user_management/users/` |
| CRUD групп | `/api/v4/user_management/groups/` |
| Группы пользователя / пользователи группы | вложенные `/users/<id>/groups/`, `/groups/<id>/users/` |
| Объектные ACL | `/api/v4/acls/access_controls/` |
| Глобальные разрешения ролей | `/api/v4/permissions/permissions/by_role/` |

**Пробелы**:
1. Нужен endpoint `GET /api/v4/documents/<id>/effective_permissions/`.
2. Отсутствует REST‑управление API‑токенами (см. раздел 2).

---

## 8. Smart Settings и системные сервисы

Сейчас Smart Settings доступны только через HTML UI `/settings/namespaces/...` или `config.yml`. Для SPA потребуется:

- `GET /api/v4/system/settings/?namespace=common` — чтение значений.
- `PATCH /api/v4/system/settings/<FULL_NAME>/` — запись с валидацией.
- Аудит изменений (лог событий).

Системные данные:

- `/api/v4/events/events/` — журнал (фильтры по `target_content_type`, `verb`, `user_id`).
- `/api/v4/task_manager/task_types/` и `/api/v4/task_manager/tasks/` — Celery задачи / состояние очередей.
- `/api/v4/sources/sources/` — список источников загрузки документов.

---

## 9. DAM (Digital Asset Management)

Все DAM‑эндпоинты живут под `/digital-assets/api/`, включены только если приложение `mayan.apps.dam` активировано.

| Путь | Назначение |
| --- | --- |
| `/documents/` | Лента документов с данными AI (`DAMDocumentListSerializer`). Фильтры `q`, `page`. |
| `/document-detail/<document_id>/` | Возвращает HTML‑фрагмент (`dam/ajax_document_dam.html`) — можно игнорировать в SPA. |
| `/ai-analysis/` | `ModelViewSet` для `DocumentAIAnalysis`. |
| `/ai-analysis/analyze/` | Запуск анализа (`{"document_id": ...}`), enqueues `analyze_document_with_ai`. |
| `/ai-analysis/<pk>/reanalyze/`, `/bulk_analyze/` | Повтор/массовый запуск. |
| `/analysis-status/` | Лёгкий статус по `document_id`. |
| `/metadata-presets/` | Управление пресетами извлечения. |
| `/dashboard-stats/` | Сводная статистика DAM. |

### Пайплайн
1. `post_save` сигнала `DocumentFile` → `trigger_ai_analysis`.
2. Celery задача `analyze_document_with_ai(document_id)` (очередь `documents`).
3. Результаты записываются в `DocumentAIAnalysis`, документ обновляет метаданные/теги.

---

## 10. Distribution (публикации и шэр‑ссылки)

Пути начинаются с `/distribution/` (см. `mayan.apps.distribution.urls.api_urls`).

| Сущность | Основные эндпоинты |
| --- | --- |
| Получатели | `/distribution/recipients/` |
| Списки получателей | `/distribution/recipient_lists/` (поддержка `recipients_id_list`, `internal_users_id_list`). |
| Пресеты рендеринга | `/distribution/rendition_presets/` |
| Публикации | `/distribution/publications/` |
| Элементы публикации | `/distribution/publication_items/` |
| Шэр‑ссылки | `/distribution/share_links/` |
| Рендеры | `/distribution/generated_renditions/` |
| Логи доступа | `/distribution/access_logs/` |
| Генерация | `POST /distribution/publications/<id>/generate_renditions/` |

Публичные URL: `/distribution/portal/publications/<token>/` (HTML) и прямые ссылки `/<uuid>/` (обслуживаются `RenditionDownloadView`, файлы лежат в S3 `distribution__renditions`).

---

## 11. Фоновые очереди и хуки

- **Celery**: очередь `documents` (DAM, bulk операций), `converter` (рендеры), `distribution` (отправка ссылок). Конфигурация в `mayan/apps/task_manager/workers.py`.
- **DocumentFile hooks** (`HooksModelMixin`):
  ```python
  DocumentFile.register_pre_create_hook(func, order=None)
  DocumentFile.register_post_save_hook(func, order=None)
  ```
  Можно подключать вебхуки/аудит до/после загрузки файла.
- **Distribution**: `generate_rendition_task` читает `DocumentFile`, прогоняет через `converter_pipeline_extension`, сохраняет в S3 (`storage_distribution_renditions`), обновляет статус `GeneratedRendition`.

---

## 12. Пробелы, требующие реализации

| Зона | Что нужно сделать |
| --- | --- |
| Bulk‑операции над документами | Ввести `/api/v4/documents/bulk/` с типами операций (`change_type`, `add_tags`, `delete`). |
| Bulk‑метаданные | Endpoint для массового обновления значений (`/metadata/bulk_update/`). |
| Smart Settings REST | `GET /system/settings/`, `PATCH /system/settings/<name>/`, аудит изменений. |
| Дерево индексов | `GET /api/v4/indexes/index_instances/` (возвращает иерархию узлов). |
| Effective permissions | `GET /documents/<id>/effective_permissions/` для быстрого UI. |

Эти требования подробно описаны в `docs/spa_api_requirements.md` и будут специфицированы (Шаг 4 плана) перед реализацией.

---

## 13. Практические советы для SPA

1. **Контроль сессии**: проверяйте `Content-Type:text/html` + статус `302/401`. При появлении Stronghold страницы редиректите на форму логина.
2. **Базовый путь**: храните `basePath` в конфиге, чтобы поддержать будущий `MAYAN_URL_BASE_PATH`.
3. **Асинхронные процессы**: для DAM/Distribution показывайте оптимистичный UI, но подтверждайте статус через `/analysis-status/` и `/generated_renditions/`.
4. **S3**: никогда не собирайте URL вручную — используйте `download_url`, который возвращает API (он уже подписан).
5. **Локализация**: backend возвращает переведённые строки (через `ugettext`). SPA может отображать их напрямую или использовать в качестве ключей.

---

Документ обязан оставаться синхронизированным с кодом. Любые изменения REST или фоновых хуков сопровождаем обновлением этого файла и Swagger (`/api/swagger`).
