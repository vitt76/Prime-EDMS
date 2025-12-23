# FRONTEND_AUDIT_V1.md

**Дата аудита:** 2025-12-09  
**Версия:** 1.0  
**Статус:** Полный аудит кодовой базы фронтенда

---

## 1. Обзор архитектуры

### 1.1. Стек технологий

| Компонент | Технология | Версия | Назначение |
|-----------|-----------|--------|------------|
| **Фреймворк** | Vue 3 | 3.4.21 | Основной UI-фреймворк с Composition API |
| **Сборщик** | Vite | 5.4.11 | Dev server и production build |
| **Язык** | TypeScript | 5.3.3 | Типизация и статический анализ |
| **State Management** | Pinia | 2.1.7 | Централизованное управление состоянием |
| **Роутинг** | Vue Router | 4.2.5 | SPA-навигация |
| **HTTP Client** | Axios | 1.6.5 | API-запросы с interceptors |
| **UI Framework** | Tailwind CSS | 3.4.1 | Utility-first CSS framework |
| **UI Components** | Headless UI | 1.7.16 | Unstyled accessible components |
| **Icons** | Heroicons | 2.1.1 | SVG-иконки |
| **Charts** | Chart.js | 4.4.1 | Визуализация данных |
| **Testing** | Vitest | 4.0.14 | Unit-тесты |
| **E2E Testing** | Playwright | 1.41.2 | End-to-end тесты |
| **Storybook** | 8.4.5 | Документация компонентов |

### 1.2. Структура папок

```
frontend/src/
├── components/          # Vue-компоненты
│   ├── admin/          # Админ-панель компоненты
│   ├── asset/          # Компоненты для работы с активами
│   ├── collections/    # Коллекции и папки
│   ├── Common/         # Переиспользуемые UI-компоненты
│   ├── DAM/            # DAM-специфичные компоненты
│   ├── Distribution/    # Распространение и публикации
│   ├── Layout/         # Layout-компоненты (Header, Sidebar)
│   ├── modals/         # Модальные окна
│   └── workflow/       # Workflow-компоненты
├── composables/        # Vue Composition API hooks
├── layouts/            # Layout-обертки (AdminLayout)
├── pages/              # Страницы приложения (route components)
├── router/             # Конфигурация роутинга
├── services/           # Бизнес-логика и API-интеграция
│   └── adapters/      # Адаптеры для трансформации данных
├── stores/             # Pinia stores
├── types/              # TypeScript типы и интерфейсы
├── utils/              # Утилиты и хелперы
├── styles/             # Глобальные стили
└── mocks/              # Mock-данные для разработки
```

### 1.3. Схема взаимодействия с API

**Паттерн:** Repository/Adapter с централизованным HTTP-клиентом

**Архитектура:**
1. **`apiService.ts`** — единый Axios-инстанс с interceptors:
   - Request interceptor: добавляет `Authorization: Token <token>`, CSRF-токен
   - Response interceptor: обработка 401/403/404, retry логика (3 попытки для 5xx/network errors)
   - Кеширование GET-запросов через `cacheService`
   - Логирование запросов/ответов в dev-режиме

2. **Сервисы** (`services/*.ts`):
   - `authService.ts` — аутентификация (Token-based, DRF)
   - `assetService.ts` — работа с документами/активами
   - `uploadService.ts` — загрузка файлов (simple/chunked)
   - `editorService.ts` — редактирование изображений
   - `distributionService.ts` — публикации и share links
   - `adminService.ts` — админ-функции
   - И другие...

3. **Адаптеры** (`services/adapters/`):
   - `mayanAdapter.ts` — трансформация ответов Mayan EDMS API в фронтенд-типы
   - Преобразование `BackendOptimizedDocument` → `Asset`
   - Нормализация пагинации, метаданных, тегов

4. **Stores (Pinia)**:
   - Используют сервисы для получения данных
   - Управляют локальным состоянием (pagination, filters, selection)
   - Персистентность через `pinia-plugin-persistedstate`

**API Endpoints:**
- Базовый URL: `VITE_API_URL` (env) или `http://localhost:8080`
- Версионирование: `/api/v4/`
- Headless endpoints: `/api/v4/headless/` (BFF-адаптер)

---

## 2. Карта модулей (Module Map)

### 2.1. Authentication Module

**Описание:** Управление аутентификацией пользователей, токенами, 2FA (заглушка).

**Ключевые компоненты:**
- `pages/LoginPage.vue` — форма входа
- `pages/Login2FAPage.vue` — 2FA-верификация (не реализовано на backend)
- `pages/auth/ForgotPasswordPage.vue` — восстановление пароля
- `pages/auth/ResetPasswordPage.vue` — сброс пароля

**State Management:**
- `stores/authStore.ts` — основной store:
  - `user: User | null` — текущий пользователь
  - `token: string | null` — DRF Token
  - `permissions: string[]` — права доступа
  - `isAuthenticated: computed` — статус аутентификации
  - Actions: `login()`, `logout()`, `initialize()`, `checkAuth()`

**Сценарии использования:**
1. **Вход в систему:**
   - Пользователь вводит username/password → `authStore.login()`
   - `authService.obtainToken()` → POST `/api/v4/auth/token/obtain/` (form-urlencoded)
   - Сохранение токена в localStorage
   - `authService.getCurrentUser()` → GET `/api/v4/users/current/`
   - Обновление `authStore.user` и `authStore.permissions`

2. **Инициализация при загрузке:**
   - `main.ts` вызывает `authStore.initialize()` после mount
   - Проверка токена в localStorage
   - Валидация через `/api/v4/users/current/`
   - Восстановление сессии при валидном токене

3. **Выход:**
   - `authStore.logout()` → очистка localStorage, редирект на `/login`

4. **Смена пароля:**
   - `authService.changePassword()` → POST `/api/v4/headless/password/change/`
   - Требует `VITE_BFF_ENABLED=true`

**API Endpoints:**
- `POST /api/v4/auth/token/obtain/` — получение токена
- `GET /api/v4/users/current/` — текущий пользователь
- `GET /api/v4/headless/auth/me/` — расширенная информация (fallback)
- `POST /api/v4/headless/password/change/` — смена пароля (BFF)

---

### 2.2. Media Library (DAM) Module

**Описание:** Основной модуль для работы с цифровыми активами (документами, изображениями, видео).

**Ключевые компоненты:**
- `pages/DAMPage.vue` — главная страница DAM (обертка над `GalleryView`)
- `pages/DAMGalleryPage.vue` — галерея активов с фильтрами
- `pages/AssetDetailPage.vue` — детальная страница актива
- `pages/AdvancedSearchPage.vue` — расширенный поиск
- `components/DAM/GalleryView.vue` — основной компонент галереи
- `components/DAM/AssetCard.vue` — карточка актива в сетке
- `components/DAM/FiltersPanel.vue` — панель фильтров
- `components/DAM/SearchBar.vue` — поисковая строка
- `components/DAM/BulkActionsBar.vue` — панель массовых операций
- `components/DAM/UploadWizard.vue` — мастер загрузки файлов

**State Management:**
- `stores/assetStore.ts` — основной store:
  - `assets: Asset[]` — список активов текущей страницы
  - `currentAsset: Asset | null` — выбранный актив
  - `selectedAssets: Set<number>` — выбранные активы (multi-select)
  - `filters: AssetFilters` — активные фильтры
  - `sort: AssetSort` — сортировка
  - `pagination: { currentPage, pageSize, totalPages, totalCount }`
  - Actions: `fetchAssets()`, `getAssetDetail()`, `deleteAsset()`, `uploadFile()`, `setFilters()`, `setSort()`

**Сценарии использования:**
1. **Просмотр галереи:**
   - При монтировании `DAMPage` → `assetStore.fetchAssets({ page: 1 })`
   - GET `/api/v4/documents/optimized/` (или `/api/v4/documents/` fallback)
   - Отображение в `GalleryView` с пагинацией

2. **Поиск и фильтрация:**
   - Пользователь вводит запрос → `assetStore.setSearchQuery()`
   - Применение фильтров (тип, теги, дата) → `assetStore.applyFilters()`
   - Перезапрос API с query-параметрами

3. **Просмотр деталей:**
   - Клик на карточку → `router.push('/dam/assets/:id')`
   - `AssetDetailPage` → `assetStore.getAssetDetail(id)`
   - GET `/api/v4/document-detail/{id}/` (или `/api/v4/documents/{id}/` fallback)
   - Дополнительные запросы: метаданные, теги, версии

4. **Загрузка файла:**
   - Открытие `UploadWizard` → выбор файла
   - `uploadService.uploadFile()`:
     - Файлы < 50MB: simple upload (create document → upload file)
     - Файлы >= 50MB: chunked upload (init → append chunks → complete)
   - Прогресс через `onProgress` callback

5. **Массовые операции:**
   - Выбор активов (checkbox) → `assetStore.selectAsset()`
   - `BulkActionsBar` → удаление, перемещение, добавление тегов

6. **Редактирование изображения:**
   - Кнопка "Редактировать" в `AssetDetailPage` (только для изображений)
   - Открытие `MediaEditorModal` → редактирование → сохранение новой версии

**API Endpoints:**
- `GET /api/v4/documents/optimized/` — оптимизированный список (с N+1 fixes)
- `GET /api/v4/documents/` — стандартный список (fallback)
- `GET /api/v4/document-detail/{id}/` — детали с AI-анализом (DAM endpoint)
- `GET /api/v4/documents/{id}/` — стандартные детали (fallback)
- `GET /api/v4/documents/{id}/files/` — список файлов документа
- `GET /api/v4/documents/{id}/metadata/` — метаданные
- `GET /api/v4/documents/{id}/tags/` — теги
- `POST /api/v4/documents/` — создание документа
- `POST /api/v4/documents/{id}/files/` — загрузка файла
- `DELETE /api/v4/documents/{id}/` — удаление
- `PATCH /api/v4/documents/{id}/` — обновление метаданных

---

### 2.3. Image Editor Module

**Описание:** Редактор изображений с трансформациями (поворот, отражение, обрезка, фильтры).

**Ключевые компоненты:**
- `components/asset/MediaEditorModal.vue` — модальное окно редактора
- `stores/editorStore.ts` — состояние редактора (history, transformations)

**State Management:**
- `stores/editorStore.ts`:
  - `currentState: EditorState` — текущее состояние (transform, filters, crop)
  - `history: EditorState[]` — история изменений (undo/redo)
  - `canUndo: computed`, `canRedo: computed`
  - Actions: `rotateLeft()`, `rotateRight()`, `flipHorizontal()`, `flipVertical()`, `applyFilter()`, `crop()`, `undo()`, `redo()`

**Сценарии использования:**
1. **Открытие редактора:**
   - В `AssetDetailPage` кнопка "Редактировать" (только для изображений: `isImage` computed)
   - `showMediaEditor = true` → открытие `MediaEditorModal`
   - Загрузка изображения через `URL.createObjectURL()` или прямой URL
   - Установка `img.crossOrigin='anonymous'` для предотвращения "tainted canvas"

2. **Редактирование:**
   - Пользователь применяет трансформации → обновление `editorStore.currentState`
   - Предпросмотр в реальном времени через CSS transforms
   - История сохраняется для undo/redo

3. **Сохранение:**
   - Кнопка "Сохранить" → `editorService.saveEditedImage()`
   - Конвертация canvas в Blob
   - POST `/api/v4/headless/documents/{id}/versions/new_from_edit/` (multipart/form-data)
   - Создание новой версии документа

4. **Создание копии:**
   - "Сохранить как копию" → `editorService.createAssetFromImage()`
   - Создание нового документа → загрузка файла

**API Endpoints:**
- `POST /api/v4/headless/documents/{id}/versions/new_from_edit/` — сохранение отредактированного изображения
- `POST /api/v4/documents/` — создание нового документа (для копии)
- `POST /api/v4/documents/{id}/files/` — загрузка файла (для копии)

**Технические детали:**
- Использование `blob:` URLs для локального отображения
- `crossOrigin='anonymous'` для canvas-операций
- CSS transforms для предпросмотра (не изменяет исходное изображение до сохранения)

---

### 2.4. Distribution Module

**Описание:** Управление публикациями, share links, распространением контента.

**Ключевые компоненты:**
- `pages/SharingPage.vue` — список share links
- `pages/SharingDetailPage.vue` — детали share link
- `pages/PublicationDetailPage.vue` — детали публикации
- `components/Distribution/CreatePublicationModal.vue` — создание публикации
- `components/Distribution/EditPublicationModal.vue` — редактирование

**State Management:**
- `stores/distributionStore.ts`:
  - `publications: Publication[]` — список публикаций
  - `sharedLinks: SharedLink[]` — список share links
  - `campaigns: DistributionCampaign[]` — кампании (не реализовано)
  - Actions: `fetchPublications()`, `createPublication()`, `fetchSharedLinks()`, `createShareLink()`

**Сценарии использования:**
1. **Просмотр share links:**
   - `SharingPage` → `distributionStore.fetchSharedLinks()`
   - GET `/api/v4/distribution/share_links/`
   - Отображение списка с фильтрацией (active/expired/revoked)

2. **Создание share link:**
   - Выбор актива → "Поделиться" → модальное окно
   - Выбор rendition (original/low_res/high_res)
   - `distributionService.createShareLink()` → POST `/api/v4/distribution/share_links/`
   - Генерация публичной ссылки

3. **Управление публикациями:**
   - Создание → `createPublication()` → POST `/api/v4/distribution/publications/`
   - Публикация → `publishPublication()` → POST `/api/v4/distribution/publications/{id}/publish/`

**API Endpoints:**
- `GET /api/v4/distribution/share_links/` — список share links
- `GET /api/v4/distribution/share_links/{id}/` — детали
- `POST /api/v4/distribution/share_links/` — создание
- `PATCH /api/v4/distribution/share_links/{id}/` — обновление
- `DELETE /api/v4/distribution/share_links/{id}/` — удаление
- `GET /api/v4/distribution/publications/` — список публикаций
- `POST /api/v4/distribution/publications/` — создание
- `POST /api/v4/distribution/publications/{id}/publish/` — публикация

---

### 2.5. Collections Module

**Описание:** Управление коллекциями (папками, избранным, недавними).

**Ключевые компоненты:**
- `pages/collections/FavoritesPage.vue` — избранное
- `pages/collections/MyUploadsPage.vue` — мои загрузки
- `pages/collections/RecentPage.vue` — недавние
- `pages/collections/SharedWithMePage.vue` — доступные мне
- `components/collections/CollectionTree.vue` — дерево коллекций
- `components/collections/CreateCollectionModal.vue` — создание коллекции

**State Management:**
- `stores/collectionsStore.ts` — коллекции (не реализовано полностью)
- `stores/favoritesStore.ts` — избранное:
  - `favorites: Asset[]` — список избранных
  - Actions: `fetchFavorites()`, `toggleFavorite()`

**Сценарии использования:**
1. **Избранное:**
   - `FavoritesPage` → `favoritesStore.fetchFavorites()`
   - GET `/api/v4/headless/favorites/` (BFF endpoint)
   - Добавление/удаление → `toggleFavorite()` → POST `/api/v4/headless/favorites/{id}/toggle/`

2. **Мои загрузки:**
   - `MyUploadsPage` → GET `/api/v4/headless/documents/my_uploads/`
   - Фильтрация по текущему пользователю

**API Endpoints:**
- `GET /api/v4/headless/favorites/` — список избранного
- `POST /api/v4/headless/favorites/{id}/toggle/` — переключение избранного
- `GET /api/v4/headless/documents/my_uploads/` — мои загрузки

---

### 2.6. Admin Panel Module

**Описание:** Административная панель для управления пользователями, ролями, метаданными, workflows.

**Ключевые компоненты:**
- `layouts/AdminLayout.vue` — layout для админ-панели
- `pages/admin/AdminDashboard.vue` — дашборд
- `pages/admin/AdminUsers.vue` — управление пользователями
- `pages/admin/AdminRoles.vue` — управление ролями
- `pages/admin/AdminMetadata.vue` — метаданные
- `pages/admin/AdminWorkflows.vue` — workflows
- `components/admin/CreateUserModal.vue` — создание пользователя
- `components/admin/EditUserModal.vue` — редактирование
- `components/admin/BulkRoleModal.vue` — массовое назначение ролей

**State Management:**
- `stores/adminStore.ts`:
  - `users: User[]` — список пользователей
  - `roles: Role[]` — список ролей
  - `metadataTypes: MetadataType[]` — типы метаданных
  - Actions: `fetchUsers()`, `createUser()`, `updateUser()`, `deleteUser()`, `fetchRoles()`, `assignRole()`

**Сценарии использования:**
1. **Управление пользователями:**
   - `AdminUsers` → `adminStore.fetchUsers()`
   - GET `/api/v4/users/`
   - Создание → `createUser()` → POST `/api/v4/users/`
   - Редактирование → `updateUser()` → PATCH `/api/v4/users/{id}/`
   - Массовое назначение ролей → `BulkRoleModal`

2. **Управление ролями:**
   - `AdminRoles` → `adminStore.fetchRoles()`
   - GET `/api/v4/roles/`

3. **Workflows:**
   - `AdminWorkflows` → визуализация через `WorkflowCanvas`
   - Редактирование nodes/transitions через `NodeEditor`, `TransitionEditor`

**API Endpoints:**
- `GET /api/v4/users/` — список пользователей
- `POST /api/v4/users/` — создание
- `PATCH /api/v4/users/{id}/` — обновление
- `DELETE /api/v4/users/{id}/` — удаление
- `GET /api/v4/roles/` — список ролей
- `GET /api/v4/metadata/types/` — типы метаданных
- `GET /api/v4/workflows/` — workflows

**Права доступа:**
- Проверка через `router.beforeEach`:
  - `to.meta.requiresAdmin` → проверка `is_staff` или `is_superuser` или permissions
  - Редирект на `/forbidden` при отсутствии прав

---

### 2.7. Settings Module

**Описание:** Настройки пользователя (профиль, пароль, API keys).

**Ключевые компоненты:**
- `pages/SettingsPage.vue` — главная страница настроек

**State Management:**
- Использует `authStore` для данных пользователя

**Сценарии использования:**
1. **Смена пароля:**
   - Форма в `SettingsPage` → `authService.changePassword()`
   - POST `/api/v4/headless/password/change/` (BFF endpoint)
   - Валидация: `current_password`, `new_password`, `new_password_confirm`

2. **Обновление профиля:**
   - `authService.updateProfile()` → PATCH `/api/v4/headless/profile/`
   - Обновление `first_name`, `last_name`, `email`

**API Endpoints:**
- `GET /api/v4/headless/profile/` — профиль пользователя
- `PATCH /api/v4/headless/profile/` — обновление профиля
- `POST /api/v4/headless/password/change/` — смена пароля

---

## 3. Реестр компонентов (Component Registry)

### 3.1. Бизнес-компоненты

#### `AssetCard.vue`
**Функционал:** Карточка актива в галерее с превью, метаданными, действиями.

**Props:**
- `asset: Asset` — данные актива
- `selected?: boolean` — выбран ли актив
- `showActions?: boolean` — показывать ли действия

**Events:**
- `@click` — клик на карточку (переход на детальную страницу)
- `@select` — выбор актива (для multi-select)
- `@favorite` — добавление в избранное
- `@download` — скачивание
- `@share` — поделиться

**Dependencies:**
- `assetStore` — для `toggleFavorite()`, `selectAsset()`
- `favoritesStore` — проверка избранного

---

#### `MediaEditorModal.vue`
**Функционал:** Модальное окно редактора изображений с трансформациями, фильтрами, обрезкой.

**Props:**
- `isOpen: boolean` — открыто ли модальное окно
- `asset: Asset | null` — актив для редактирования

**Events:**
- `@close` — закрытие модального окна
- `@save` — сохранение отредактированного изображения

**Dependencies:**
- `editorStore` — состояние редактора (history, transformations)
- `editorService` — `saveEditedImage()`, `createAssetFromImage()`
- `assetStore` — обновление актива после сохранения

**Особенности:**
- Использует `blob:` URLs для локального отображения
- `img.crossOrigin='anonymous'` для canvas-операций
- CSS transforms для предпросмотра (не изменяет исходное изображение)

---

#### `GalleryView.vue`
**Функционал:** Основной компонент галереи активов с сеткой, пагинацией, фильтрами.

**Props:**
- Нет (использует `assetStore` напрямую)

**Events:**
- `@open-upload` — открытие мастера загрузки

**Dependencies:**
- `assetStore` — `fetchAssets()`, `assets`, `pagination`, `filters`
- `favoritesStore` — синхронизация избранного
- `uiStore` — управление модальными окнами

**Особенности:**
- Виртуализация через `VirtualScroller` для больших списков
- Infinite scroll через `loadMore()`
- Реактивность на изменения фильтров/поиска

---

#### `UploadWizard.vue`
**Функционал:** Мастер загрузки файлов с drag-and-drop, прогрессом, валидацией.

**Props:**
- `isOpen: boolean` — открыто ли модальное окно

**Events:**
- `@close` — закрытие
- `@success` — успешная загрузка

**Dependencies:**
- `uploadService` — `uploadFile()` (simple/chunked)
- `assetStore` — обновление списка после загрузки
- `documentTypeService` — валидация метаданных (если BFF enabled)

**Особенности:**
- Автоматический выбор стратегии (simple/chunked) по размеру файла
- Прогресс-бар с ETA и скоростью
- Валидация типов файлов, размера

---

#### `AssetDetailPage.vue`
**Функционал:** Детальная страница актива с превью, метаданными, версиями, комментариями.

**Props:**
- Нет (использует `route.params.id`)

**Events:**
- Нет

**Dependencies:**
- `assetStore` — `getAssetDetail()`, `currentAsset`
- `editorStore` — для `MediaEditorModal`
- `favoritesStore` — переключение избранного

**Особенности:**
- Условный рендеринг кнопки "Редактировать" только для изображений (`isImage` computed)
- Загрузка метаданных, тегов, версий отдельными запросами
- AI-инсайты через `AIInsightsWidget`

---

#### `AdminUsers.vue`
**Функционал:** Управление пользователями с таблицей, фильтрами, массовыми операциями.

**Props:**
- Нет

**Events:**
- Нет

**Dependencies:**
- `adminStore` — `fetchUsers()`, `createUser()`, `updateUser()`, `deleteUser()`
- `authStore` — проверка прав доступа

**Особенности:**
- Массовое назначение ролей через `BulkRoleModal`
- Фильтрация по статусу, роли, поиск

---

### 3.2. UI-компоненты (Common)

#### `Button.vue`
**Функционал:** Переиспользуемая кнопка с вариантами стилей, размеров, состояний.

**Props:**
- `variant?: 'primary' | 'secondary' | 'danger' | 'ghost'`
- `size?: 'sm' | 'md' | 'lg'`
- `disabled?: boolean`
- `loading?: boolean`

**Events:**
- `@click` — клик

---

#### `Modal.vue`
**Функционал:** Модальное окно с backdrop, анимациями, фокус-трапом.

**Props:**
- `isOpen: boolean`
- `title?: string`
- `size?: 'sm' | 'md' | 'lg' | 'xl'`

**Events:**
- `@close` — закрытие

**Dependencies:**
- `useFocusTrap` composable — управление фокусом

---

#### `DataTable.vue`
**Функционал:** Таблица данных с сортировкой, пагинацией, выбором строк.

**Props:**
- `columns: Column[]` — определение колонок
- `data: any[]` — данные
- `selectable?: boolean` — возможность выбора

**Events:**
- `@sort` — сортировка
- `@select` — выбор строки

---

## 4. API Интеграция

### 4.1. Список всех API-вызовов

#### Authentication
- `POST /api/v4/auth/token/obtain/` — получение токена
- `GET /api/v4/users/current/` — текущий пользователь
- `GET /api/v4/headless/auth/me/` — расширенная информация (fallback)
- `POST /api/v4/headless/password/change/` — смена пароля (BFF)
- `GET /api/v4/headless/profile/` — профиль
- `PATCH /api/v4/headless/profile/` — обновление профиля

#### Documents/Assets
- `GET /api/v4/documents/optimized/` — оптимизированный список (с N+1 fixes)
- `GET /api/v4/documents/` — стандартный список (fallback)
- `GET /api/v4/document-detail/{id}/` — детали с AI-анализом (DAM endpoint)
- `GET /api/v4/documents/{id}/` — стандартные детали (fallback)
- `GET /api/v4/documents/{id}/files/` — список файлов
- `GET /api/v4/documents/{id}/metadata/` — метаданные
- `GET /api/v4/documents/{id}/tags/` — теги
- `GET /api/v4/documents/{id}/processing_status/` — статус обработки (AI)
- `POST /api/v4/documents/` — создание документа
- `POST /api/v4/documents/{id}/files/` — загрузка файла
- `PATCH /api/v4/documents/{id}/` — обновление метаданных
- `DELETE /api/v4/documents/{id}/` — удаление

#### Image Editor
- `POST /api/v4/headless/documents/{id}/versions/new_from_edit/` — сохранение отредактированного изображения
- `POST /api/v4/headless/image-editor/sessions/` — создание сессии редактора
- `PATCH /api/v4/headless/image-editor/sessions/{id}/` — обновление состояния
- `GET /api/v4/headless/image-editor/sessions/{id}/preview/` — превью
- `POST /api/v4/headless/image-editor/sessions/{id}/commit/` — коммит изменений
- `GET /api/v4/headless/image-editor/watermarks/` — список водяных знаков

#### Upload
- `POST /api/v4/uploads/init/` — инициализация chunked upload
- `POST /api/v4/uploads/append/` — загрузка chunk
- `POST /api/v4/uploads/complete/` — завершение chunked upload

#### Distribution
- `GET /api/v4/distribution/share_links/` — список share links
- `GET /api/v4/distribution/share_links/{id}/` — детали
- `POST /api/v4/distribution/share_links/` — создание
- `PATCH /api/v4/distribution/share_links/{id}/` — обновление
- `DELETE /api/v4/distribution/share_links/{id}/` — удаление
- `GET /api/v4/distribution/publications/` — список публикаций
- `POST /api/v4/distribution/publications/` — создание
- `PATCH /api/v4/distribution/publications/{id}/` — обновление
- `POST /api/v4/distribution/publications/{id}/publish/` — публикация

#### Collections/Favorites
- `GET /api/v4/headless/favorites/` — список избранного
- `POST /api/v4/headless/favorites/{id}/toggle/` — переключение избранного
- `GET /api/v4/headless/documents/my_uploads/` — мои загрузки
- `GET /api/v4/headless/dashboard/activity/` — активность дашборда
- `GET /api/v4/headless/activity/feed/` — полная лента активности

#### Admin
- `GET /api/v4/users/` — список пользователей
- `POST /api/v4/users/` — создание
- `PATCH /api/v4/users/{id}/` — обновление
- `DELETE /api/v4/users/{id}/` — удаление
- `GET /api/v4/roles/` — список ролей
- `GET /api/v4/metadata/types/` — типы метаданных
- `GET /api/v4/workflows/` — workflows

#### Configuration
- `GET /api/v4/headless/config/document_types/` — конфигурация типов документов (BFF)
- `GET /api/v4/document_types/` — список типов документов

### 4.2. Выявленные несовпадения контрактов

1. **Оптимизированный список документов:**
   - Backend возвращает `BackendOptimizedDocument` с вложенными объектами
   - Frontend использует `mayanAdapter.adaptBackendAsset()` для трансформации в `Asset`
   - Маппинг полей: `label` → `label`, `datetime_created` → `date_added`, `file_latest` → `file_details`

2. **Пагинация:**
   - Backend: `{ count, next, previous, results }`
   - Frontend: `adaptBackendPaginatedResponse()` нормализует в `{ count, results, total_pages }`

3. **Метаданные:**
   - Backend: массив объектов `{ metadata_type: { name, label }, value }`
   - Frontend: преобразование в `Record<string, string>` через `metaMap`

4. **Теги:**
   - Backend: массив объектов `{ label, name, tag }`
   - Frontend: извлечение `label` или `name` в массив строк

5. **Share Links:**
   - Backend: `APIShareLink` с полями `rendition`, `expires_at`
   - Frontend: `adaptShareLink()` трансформирует в `SharedLink` с `status`, `expiresAt`

---

## 5. Технический долг и Рекомендации

### 5.1. Обнаруженные TODO/FIXME

**Критичные:**
1. `MediaEditorModal.vue:1715` — fallback на `document_type_id = 1` вместо разрешения типа документа
2. `uploadService.ts:713` — отсутствует вызов abort endpoint для cleanup частичной загрузки
3. `notificationStore.ts:78,83` — WebSocket-подключение не реализовано

**Средние:**
4. `GalleryView.vue:429,486` — открытие preview modal и more actions menu не реализовано
5. `DAMGalleryPage.vue:656,685,690` — share modal, bulk download, bulk share не реализованы
6. `SettingsPage.vue:398` — навигация на API keys page не реализована
7. `DistributionPage.vue:246,268,271,280,288` — preview modal, toast notifications не реализованы
8. `CreatePublicationModal.vue:364,402` — asset selector modal, error toast не реализованы
9. `BulkMoveModal.vue:161` — создание коллекции через API не реализовано
10. `App.vue:119,138,158` — toggle filters panel, notifications center, create folder modal не реализованы

**Низкие:**
11. `FolderTreeNode.vue:185` — context menu не реализован
12. `aiAnalysisService.ts:140,152` — tag acceptance/rejection не реализовано на backend

### 5.2. Плохая типизация

1. **`authService.ts`:**
   - `mapMayanUser(data: any): User` — параметр `any`, нужно типизировать `MayanUserResponse`

2. **`assetStore.ts`:**
   - `lastRawResponse: ref<any>` — должен быть `BackendPaginatedResponse<BackendOptimizedDocument>`
   - `fetchDocumentMetadata(id: number): Promise<any[] | null>` — нужно типизировать `DocumentMetadata[]`

3. **`editorService.ts`:**
   - `updateImageEditorSessionState(sessionId: number, state: any)` — `state` должен быть типизирован

4. **`router/index.ts`:**
   - `generateBreadcrumbs(to: any)` — `to` должен быть `RouteLocationNormalized`

5. **`distributionStore.ts`:**
   - Использование mock-данных в dev-режиме без типизации

### 5.3. Дублирование кода

1. **Обработка ошибок API:**
   - Повторяющаяся логика в `assetStore.handleApiError()`, `uploadService`, других сервисах
   - **Рекомендация:** Вынести в `utils/apiErrorHandler.ts`

2. **Валидация форм:**
   - Дублирование валидации пароля, email в разных компонентах
   - **Рекомендация:** Создать `composables/useFormValidation.ts`

3. **Форматирование дат:**
   - Использование `new Date().toISOString()` в разных местах
   - **Рекомендация:** Использовать `utils/formatters.ts` (уже существует, но не везде используется)

4. **Проверка прав доступа:**
   - Дублирование логики `hasPermission()`, `hasRole()` в компонентах
   - **Рекомендация:** Использовать `authStore.hasPermission()`, `authStore.hasRole()` везде

### 5.4. Архитектурные нарушения

1. **Прямые вызовы axios в stores:**
   - `assetStore.ts` использует `axios.get()` напрямую вместо `apiService`
   - **Рекомендация:** Все API-вызовы через `apiService` для единообразия interceptors

2. **Смешивание бизнес-логики и UI:**
   - `AssetDetailPage.vue` содержит логику загрузки метаданных/тегов
   - **Рекомендация:** Вынести в `assetStore.getAssetDetail()` (частично уже сделано)

3. **Отсутствие error boundaries:**
   - Только глобальный `ErrorBoundary` в `App.vue`
   - **Рекомендация:** Добавить error boundaries для критичных модулей (DAM, Admin)

4. **Хардкод значений:**
   - `MediaEditorModal.vue:1715` — `document_type_id = 1`
   - `uploadService.ts:34` — `CHUNKED_UPLOAD_THRESHOLD = 50MB` (можно вынести в env)

### 5.5. Рекомендации по рефакторингу

#### Приоритет 1 (Критично)
1. **Типизация API-ответов:**
   - Создать типы для всех Mayan EDMS API-ответов в `types/api.ts`
   - Убрать все `any` из сервисов и stores

2. **Централизация обработки ошибок:**
   - Создать `utils/apiErrorHandler.ts` с единой логикой
   - Использовать во всех сервисах

3. **Исправление fallback на document_type_id:**
   - Реализовать разрешение типа документа через `documentTypeService`
   - Убрать хардкод `document_type_id = 1`

#### Приоритет 2 (Важно)
4. **Рефакторинг assetStore:**
   - Убрать прямые вызовы `axios`, использовать `apiService`
   - Вынести логику загрузки метаданных/тегов в отдельные методы

5. **Реализация WebSocket:**
   - Подключить `websocketService` в `notificationStore`
   - Реализовать real-time уведомления

6. **Улучшение типизации:**
   - Типизировать все `any` в `editorService`, `distributionStore`
   - Добавить типы для `EditorState`, `Publication`, `SharedLink`

#### Приоритет 3 (Желательно)
7. **Оптимизация производительности:**
   - Добавить виртуализацию для больших списков (уже есть `VirtualScroller`, но не везде используется)
   - Оптимизировать re-renders через `shallowRef` для больших массивов

8. **Улучшение UX:**
   - Реализовать toast notifications (сейчас только TODO)
   - Добавить skeleton loaders для всех списков

9. **Тестирование:**
   - Увеличить покрытие unit-тестами (сейчас только базовые тесты)
   - Добавить E2E-тесты для критичных flows (upload, edit, share)

---

## 6. Заключение

### 6.1. Текущее состояние

**Сильные стороны:**
- Четкая архитектура с разделением на модули (services, stores, components)
- Использование TypeScript для типизации
- Централизованный API-клиент с interceptors
- Хорошая структура папок
- Использование Pinia для state management
- Адаптеры для трансформации данных backend → frontend

**Слабые стороны:**
- Множество TODO/FIXME, указывающих на незавершенный функционал
- Плохая типизация в некоторых местах (`any` типы)
- Дублирование кода (обработка ошибок, валидация)
- Прямые вызовы axios в stores вместо apiService
- Отсутствие WebSocket-подключения для real-time уведомлений

### 6.2. Метрики

- **Компонентов:** ~50+ Vue-компонентов
- **Stores:** 15 Pinia stores
- **Сервисов:** 15+ сервисов
- **API Endpoints:** ~40+ endpoints
- **TODO/FIXME:** 20+ комментариев
- **Покрытие тестами:** Низкое (только базовые unit-тесты)

### 6.3. Рекомендации по приоритетам

1. **Немедленно:**
   - Исправить fallback на `document_type_id = 1`
   - Типизировать все `any` в критичных модулях (auth, assets)
   - Централизовать обработку ошибок API

2. **В ближайшее время:**
   - Рефакторинг `assetStore` (убрать прямые вызовы axios)
   - Реализовать WebSocket для уведомлений
   - Увеличить покрытие тестами

3. **В будущем:**
   - Реализовать все TODO/FIXME
   - Оптимизация производительности
   - Улучшение UX (toast notifications, skeleton loaders)

---

**Документ составлен:** 2025-12-09  
**Автор аудита:** Senior Frontend Architect  
**Версия:** 1.0

