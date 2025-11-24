# Инвентаризация существующего REST API ядра Mayan

> Цель — зафиксировать, какие эндпоинты уже доступны для ядра DMS и какие гарантии (ACL, Stronghold, сериализаторы) с ними связаны. Этим документом будем руководствоваться при расширении `docs/api_surface.md`.

## Документы (`mayan.apps.documents`)

| Базовый путь | Методы | ViewSet / класс | ACL / Особенности |
| --- | --- | --- | --- |
| `/api/v4/documents/documents/` | GET, POST | `APIDocumentListView` (`document_api_views.py`) | Проверка `permission_document_view` / `permission_document_create`. Stronghold закрыт. |
| `/api/v4/documents/documents/<id>/` | GET, PATCH, DELETE | `APIDocumentDetailView` | Доступ через ACL. Поддерживает `PATCH` для свойств. |
| `/api/v4/documents/documents/<id>/change_type/` | POST | `APIDocumentChangeTypeView` | Требует `permission_document_properties_edit`. |
| `/api/v4/documents/files/` | GET, POST | `APIDocumentFileListView` | Добавление файлов к документу; требует `permission_document_file_new`. |
| `/api/v4/documents/files/<id>/download/` | GET | `APIDocumentFileDownloadView` | Возвращает файл; контролируется ACL + подписывание Storage. |
| `/api/v4/documents/versions/` | GET | `APIDocumentVersionListView` | Управление версиями документа. |
| `/api/v4/documents/trashed_documents/` | GET, DELETE | `APITrashedDocumentListView`/`DetailView` | Требует `permission_document_trash`/`restore`. |
| `/api/v4/documents/favorites/` | GET, POST, DELETE | `APIFavoriteDocumentListView` | Список избранного пользователя. |
| `/api/v4/documents/recently_accessed/` | GET | `APIRecentlyAccessedDocumentListView` | Только чтение, фильтруется по текущему пользователю. |

## Метаданные (`mayan.apps.metadata`)

| Путь | Методы | Описание |
| --- | --- | --- |
| `/api/v4/metadata/metadata_types/` | GET, POST | CRUD типов метаданных. |
| `/api/v4/metadata/metadata_types/<id>/documents/` | GET | Документы, использующие тип. |
| `/api/v4/metadata/document_types/<doc_type_id>/metadata_types/` | GET/POST | Привязка типов к документным типам. |
| `/api/v4/metadata/documents/<document_id>/metadata/` | GET/POST/PATCH | Значения метаданных для конкретного документа. |

## Теги (`mayan.apps.tags`)

| Путь | Методы | Комментарии |
| --- | --- | --- |
| `/api/v4/tags/tags/` | GET, POST | Создание и фильтрация тегов. |
| `/api/v4/tags/tags/<id>/documents/` | GET | Документы с тегом. |
| `/api/v4/tags/tags/<id>/attach/` | POST | Привязка тега к документу (требуется список `document_ids`). |

## Кабинеты (`mayan.apps.cabinets`)

| Путь | Методы | Комментарии |
| --- | --- | --- |
| `/api/v4/cabinets/cabinets/` | GET, POST | Дерево кабинетов. |
| `/api/v4/cabinets/cabinets/<id>/documents/` | GET, POST, DELETE | Управление членством документов. |

## Поиск и индексы

| Путь | Методы | Комментарии |
| --- | --- | --- |
| `/api/v4/dynamic_search/search/` | GET | Параметры `q`, `app_label`, `model_name`. |
| `/api/v4/indexes/index_templates/` | GET | Справочник шаблонов индексов. Нет удобного REST для получения дерева узлов. |

## Пользователи и группы (`mayan.apps.user_management`)

| Путь | Методы | Комментарии |
| --- | --- | --- |
| `/api/v4/user_management/users/` | GET, POST | CRUD пользователей. |
| `/api/v4/user_management/groups/` | GET, POST | CRUD групп. |
| `/api/v4/user_management/users/<id>/groups/` | GET, POST, DELETE | Управление принадлежностью к группам. |

## ACL и разрешения

| Путь | Методы | Комментарии |
| --- | --- | --- |
| `/api/v4/acls/access_controls/` | GET, POST | Управление объектными ACL. |
| `/api/v4/permissions/permissions/by_role/` | GET | Глобальные разрешения ролей. |

## Smart Settings / Конфигурация

На текущий момент удобного REST‑API нет. Единственный способ — HTML UI `/settings/namespaces/...` или прямое редактирование `config.yml`. Требуется новый read/write endpoint (см. шаг 4 плана).

## Аутентификация и токены

- `POST /authentication/login/` — сессионный логин (HTML).
- `POST /api/v4/auth/token/obtain/` — получение DRF token через JSON (см. `BrowseableObtainAuthToken`).
- Управление токенами отсутствует (только админ CLI) → нужно добавить `/api/v4/auth/tokens/`.

## Системные данные

- `/api/v4/events/events/` — аудит.
- `/api/v4/task_manager/task_types/` и `/api/v4/task_manager/tasks/` — Celery задания.
- `/api/v4/sources/sources/` — загрузчики документов (для UI Wizard); требует уточнения и описания.

---

**Вывод:** базовые CRUD операции для документов, файлов, тегов, кабинетов и пользователей уже существуют, но:

1. Отсутствует REST для Smart Settings, управления токенами, дерева индексов, массового обновления метаданных и bulk‑операций над документами.
2. Документация в `docs/api_surface.md` описывает только DAM/Distribution. Необходимо расширить её секциями по основному ядру, используя таблицы выше.

