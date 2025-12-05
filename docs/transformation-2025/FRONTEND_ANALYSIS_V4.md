# Анализ Фронтенда V4 — Vue 3 DAM System

**Дата анализа:** 04 декабря 2025
**Версия:** 4.0 (КРИТИЧЕСКИЙ ПЕРЕСМОТР — Ожидание Реализации BFF)
**Автор:** Senior Frontend Architect & Technical Writer
**Статус:** 🟡 **ОЖИДАНИЕ РЕАЛИЗАЦИИ BFF**

---

## 📋 Содержание

1. [Критический Статус](#1-критический-статус)
2. [Заблокированные Потоки](#2-заблокированные-потоки)
3. [План Рефакторинга URL](#3-план-рефакторинга-url)
4. [Детальные Спецификации Изменений](#4-детальные-спецификации-изменений)
5. [Интеграция с Headless API](#5-интеграция-с-headless-api)
6. [Timeline Рефакторинга](#6-timeline-рефакторинга)

---

## 1. Критический Статус

### 🟡 СТАТУС: Ожидание Реализации BFF

**Предыдущий статус (V3):** "100% Integration Complete — Production Ready"

**Реальный статус (V4):** 🟡 **ЧАСТИЧНО РАБОТАЕТ** — Критические self-service функции заблокированы из-за отсутствия backend endpoints.

### Резюме Проблем

| Функционал | Текущее Состояние | Блокер | Требуемое Действие |
|------------|-------------------|--------|-------------------|
| **Аутентификация** | ✅ Работает | — | Нет изменений |
| **Галерея ассетов** | ✅ Работает | — | Нет изменений |
| **Загрузка файлов** | ✅ Работает | — | Нет изменений |
| **Смена пароля** | 🔴 НЕ РАБОТАЕТ | 404 на endpoint | Ждем `/headless/password/change/` |
| **Динамические формы** | 🔴 НЕ РАБОТАЕТ | Нет config API | Ждем `/headless/config/` |
| **Лента активности** | 🔴 НЕ РАБОТАЕТ | Нет user-specific API | Ждем `/headless/activity/` |
| **Скачивание** | ✅ Работает | — | Нет изменений |
| **Поиск** | ✅ Работает | — | Нет изменений |

---

## 2. Заблокированные Потоки

### 2.1 Критический Сбой: Смена Пароля (F2)

**Текущая Реализация:**

```typescript
// src/services/settingsService.ts — ТЕКУЩИЙ КОД (НЕ РАБОТАЕТ)
export async function changePassword(
  currentPassword: string,
  newPassword: string
): Promise<void> {
  await apiService.post('/api/v4/users/current/password/', {
    current_password: currentPassword,
    new_password: newPassword
  })
}
```

**Результат Тестирования:**
```
POST http://127.0.0.1:8080/api/v4/users/current/password/
Status: 404 Not Found
Content-Type: text/html
Response: HTML страница "Page not found"
```

**Влияние:**
- ❌ Пользователи не могут менять пароли
- ❌ Форма в SettingsPage.vue не работает
- ❌ Нарушение требований безопасности (регулярная смена паролей)

**Требуемые Изменения (после развертывания BFF):**

```typescript
// src/services/settingsService.ts — БУДУЩИЙ КОД
export async function changePassword(
  currentPassword: string,
  newPassword: string,
  newPasswordConfirm: string
): Promise<void> {
  // Используем новый headless endpoint
  await apiService.post('/api/v4/headless/password/change/', {
    current_password: currentPassword,
    new_password: newPassword,
    new_password_confirm: newPasswordConfirm
  })
}
```

### 2.2 Критический Сбой: Динамические Формы Загрузки (F3-Config)

**Текущая Реализация:**

```typescript
// src/services/uploadService.ts — ТЕКУЩИЙ КОД (ХАРДКОД)
export async function uploadFile(
  file: File,
  options: UploadOptions
): Promise<UploadResult> {
  // ПРОБЛЕМА: document_type_id хардкодится
  // Мы не знаем, какие метаданные обязательны
  const documentTypeId = options.documentTypeId || 1  // ❌ ХАРДКОД
  
  // ПРОБЛЕМА: Не валидируем метаданные перед отправкой
  // Сервер может отклонить из-за отсутствия required fields
  const response = await initUpload({
    filename: file.name,
    document_type_id: documentTypeId,
    // metadata: ???  // Какие поля обязательны?
  })
}
```

**Влияние:**
- ❌ Загрузка может провалиться из-за отсутствия required metadata
- ❌ Пользователь не видит, какие поля заполнять
- ❌ UX страдает от неясных ошибок

**Требуемые Изменения (после развертывания BFF):**

```typescript
// src/services/documentTypeService.ts — НОВЫЙ СЕРВИС
export interface DocumentTypeConfig {
  id: number
  label: string
  required_metadata: MetadataFieldConfig[]
  optional_metadata: MetadataFieldConfig[]
  workflows: WorkflowConfig[]
}

export interface MetadataFieldConfig {
  id: number
  name: string
  label: string
  type: 'text' | 'number' | 'date' | 'select'
  required: boolean
  validation_regex: string | null
  default_value: string | null
  options: string[] | null
}

export async function getDocumentTypeConfig(
  documentTypeId: number
): Promise<DocumentTypeConfig> {
  const response = await apiService.get<DocumentTypeConfig>(
    `/api/v4/headless/config/document_types/${documentTypeId}/`
  )
  return response.data
}

export async function getAllDocumentTypes(): Promise<DocumentTypeConfig[]> {
  const response = await apiService.get<DocumentTypeConfig[]>(
    '/api/v4/headless/config/document_types/'
  )
  return response.data
}
```

```typescript
// src/services/uploadService.ts — ОБНОВЛЕННЫЙ КОД
export async function uploadFile(
  file: File,
  options: UploadOptions
): Promise<UploadResult> {
  // Шаг 1: Получаем конфигурацию типа документа
  const docTypeConfig = await getDocumentTypeConfig(options.documentTypeId)
  
  // Шаг 2: Валидируем metadata против required fields
  const missingFields = docTypeConfig.required_metadata.filter(
    field => !options.metadata?.[field.name]
  )
  
  if (missingFields.length > 0) {
    throw new ValidationError(
      `Отсутствуют обязательные поля: ${missingFields.map(f => f.label).join(', ')}`
    )
  }
  
  // Шаг 3: Продолжаем загрузку
  // ...
}
```

### 2.3 Критический Сбой: Лента Активности (F8)

**Текущая Реализация:**

```typescript
// src/services/activityService.ts — ТЕКУЩИЙ КОД (ВРЕМЕННОЕ РЕШЕНИЕ)
export async function getActivityFeed(): Promise<ActivityItem[]> {
  // ПРОБЛЕМА: Используем sessionStorage для demo
  // Реальный API отсутствует
  const stored = sessionStorage.getItem('dam_activity_log')
  return stored ? JSON.parse(stored) : []
}

export function logActivity(action: ActivityAction): void {
  // Локальное логирование в sessionStorage
  const log = getActivityFeed()
  log.unshift({
    id: Date.now(),
    timestamp: new Date().toISOString(),
    action: action.type,
    target: action.target,
    user: getCurrentUser()
  })
  sessionStorage.setItem('dam_activity_log', JSON.stringify(log.slice(0, 50)))
}
```

**Влияние:**
- ❌ Активность не персистится между сессиями
- ❌ Пользователь не видит действия других
- ❌ Dashboard показывает только локальные данные

**Требуемые Изменения (после развертывания BFF):**

```typescript
// src/services/activityService.ts — ОБНОВЛЕННЫЙ КОД
export interface ActivityItem {
  id: number
  timestamp: string
  actor: {
    id: number
    username: string
    full_name: string
  }
  verb: string
  verb_code: string
  target: {
    id: number
    type: string
    label: string
    url: string | null
  } | null
  description: string
}

export interface ActivityFeedResponse {
  count: number
  page: number
  page_size: number
  results: ActivityItem[]
}

export async function getActivityFeed(
  options: {
    filter?: 'my_actions' | 'my_documents' | 'all'
    page?: number
    page_size?: number
  } = {}
): Promise<ActivityFeedResponse> {
  const params = new URLSearchParams()
  if (options.filter) params.append('filter', options.filter)
  if (options.page) params.append('page', options.page.toString())
  if (options.page_size) params.append('page_size', options.page_size.toString())
  
  const response = await apiService.get<ActivityFeedResponse>(
    `/api/v4/headless/activity/feed/?${params.toString()}`
  )
  return response.data
}
```

---

## 3. План Рефакторинга URL

### 3.1 Карта Изменений Сервисов

| Файл | Текущий Endpoint | Новый Endpoint | Статус |
|------|------------------|----------------|--------|
| `src/services/settingsService.ts` | `POST /api/v4/users/current/password/` | `POST /api/v4/headless/password/change/` | 🔴 Ждет BFF |
| `src/services/uploadService.ts` | — | `GET /api/v4/headless/config/document_types/` | 🔴 Ждет BFF |
| `src/services/activityService.ts` | sessionStorage | `GET /api/v4/headless/activity/feed/` | 🔴 Ждет BFF |
| `src/services/authService.ts` | `POST /api/v4/auth/token/obtain/` | Без изменений | ✅ Работает |
| `src/services/assetService.ts` | `GET /api/v4/documents/optimized/` | Без изменений | ✅ Работает |

### 3.2 Список Файлов для Рефакторинга

```
src/services/
├── settingsService.ts        🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
├── uploadService.ts          🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
├── activityService.ts        🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ (новый)
├── documentTypeService.ts    🆕 НОВЫЙ ФАЙЛ
├── authService.ts            ✅ БЕЗ ИЗМЕНЕНИЙ
├── assetService.ts           ✅ БЕЗ ИЗМЕНЕНИЙ
├── collectionsService.ts     ✅ БЕЗ ИЗМЕНЕНИЙ
└── adminService.ts           ✅ БЕЗ ИЗМЕНЕНИЙ

src/stores/
├── settingsStore.ts          🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
├── uploadWorkflowStore.ts    🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
├── dashboardStore.ts         🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
├── authStore.ts              ✅ БЕЗ ИЗМЕНЕНИЙ
├── assetStore.ts             ✅ БЕЗ ИЗМЕНЕНИЙ
└── galleryStore.ts           ✅ БЕЗ ИЗМЕНЕНИЙ

src/pages/
├── SettingsPage.vue          🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
├── UploadPage.vue            🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
├── DashboardPage.vue         🔴 ТРЕБУЕТ ИЗМЕНЕНИЙ
└── остальные                 ✅ БЕЗ ИЗМЕНЕНИЙ
```

---

## 4. Детальные Спецификации Изменений

### 4.1 settingsService.ts

**Текущий код:**

```typescript
// src/services/settingsService.ts
import { apiService } from './apiService'

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export async function changePassword(data: ChangePasswordRequest): Promise<void> {
  // ❌ НЕ РАБОТАЕТ — endpoint не существует
  await apiService.post('/api/v4/users/current/password/', data)
}

export async function updateProfile(data: ProfileUpdateRequest): Promise<User> {
  const response = await apiService.patch('/api/v4/users/current/', data)
  return response.data
}
```

**Новый код (после развертывания BFF):**

```typescript
// src/services/settingsService.ts
import { apiService } from './apiService'

// ====== TYPES ======

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  new_password_confirm: string
}

export interface ChangePasswordResponse {
  message: string
  status: 'success'
}

export interface ChangePasswordError {
  error: string
  error_code: 
    | 'MISSING_FIELDS'
    | 'INVALID_CURRENT_PASSWORD'
    | 'PASSWORD_MISMATCH'
    | 'PASSWORD_VALIDATION_FAILED'
  details?: string[]
}

// ====== API CALLS ======

/**
 * Смена пароля текущего пользователя.
 * 
 * Использует новый headless API endpoint.
 * 
 * @param data - Данные для смены пароля
 * @throws {ApiError} При ошибке валидации или неверном пароле
 */
export async function changePassword(data: ChangePasswordRequest): Promise<ChangePasswordResponse> {
  const response = await apiService.post<ChangePasswordResponse>(
    '/api/v4/headless/password/change/',
    data
  )
  return response.data
}

/**
 * Обновление профиля пользователя.
 * 
 * НЕ включает смену пароля — используйте changePassword().
 */
export async function updateProfile(data: ProfileUpdateRequest): Promise<User> {
  const response = await apiService.patch('/api/v4/users/current/', data)
  return response.data
}
```

### 4.2 documentTypeService.ts (НОВЫЙ ФАЙЛ)

```typescript
// src/services/documentTypeService.ts
import { apiService } from './apiService'

// ====== TYPES ======

export interface MetadataFieldConfig {
  id: number
  name: string
  label: string
  type: 'text' | 'number' | 'date' | 'select' | 'textarea'
  required: boolean
  validation_regex: string | null
  default_value: string | null
  options: string[] | null
}

export interface WorkflowConfig {
  id: number
  label: string
  initial_state: string | null
}

export interface RetentionPolicy {
  enabled: boolean
  days: number
}

export interface Capabilities {
  ocr_enabled: boolean
  ai_analysis_enabled: boolean
  preview_enabled: boolean
}

export interface DocumentTypeConfig {
  id: number
  label: string
  description: string
  required_metadata: MetadataFieldConfig[]
  optional_metadata: MetadataFieldConfig[]
  workflows: WorkflowConfig[]
  retention_policy: RetentionPolicy
  capabilities: Capabilities
}

export interface DocumentTypeBasic {
  id: number
  label: string
  description: string
  url: string
}

// ====== API CALLS ======

/**
 * Получить список всех типов документов с базовой информацией.
 */
export async function getAllDocumentTypes(): Promise<DocumentTypeBasic[]> {
  const response = await apiService.get<DocumentTypeBasic[]>(
    '/api/v4/headless/config/document_types/'
  )
  return response.data
}

/**
 * Получить полную конфигурацию типа документа.
 * 
 * Используется для построения динамических форм загрузки.
 * 
 * @param documentTypeId - ID типа документа
 * @returns Полная конфигурация с метаданными, workflows, capabilities
 */
export async function getDocumentTypeConfig(
  documentTypeId: number
): Promise<DocumentTypeConfig> {
  const response = await apiService.get<DocumentTypeConfig>(
    `/api/v4/headless/config/document_types/${documentTypeId}/`
  )
  return response.data
}

/**
 * Валидация метаданных против конфигурации типа документа.
 * 
 * @param config - Конфигурация типа документа
 * @param metadata - Метаданные для валидации
 * @returns Список ошибок (пустой если валидация прошла)
 */
export function validateMetadata(
  config: DocumentTypeConfig,
  metadata: Record<string, string>
): string[] {
  const errors: string[] = []
  
  // Проверка обязательных полей
  for (const field of config.required_metadata) {
    const value = metadata[field.name]
    
    if (!value || value.trim() === '') {
      errors.push(`Поле "${field.label}" обязательно для заполнения`)
      continue
    }
    
    // Проверка regex если задан
    if (field.validation_regex) {
      const regex = new RegExp(field.validation_regex)
      if (!regex.test(value)) {
        errors.push(`Поле "${field.label}" имеет неверный формат`)
      }
    }
  }
  
  return errors
}
```

### 4.3 activityService.ts (ОБНОВЛЕНИЕ)

```typescript
// src/services/activityService.ts
import { apiService } from './apiService'

// ====== TYPES ======

export interface ActivityActor {
  id: number
  username: string
  full_name: string
}

export interface ActivityTarget {
  id: number
  type: string
  label: string
  url: string | null
}

export interface ActivityItem {
  id: number
  timestamp: string
  actor: ActivityActor
  verb: string
  verb_code: string
  target: ActivityTarget | null
  description: string
}

export interface ActivityFeedResponse {
  count: number
  page: number
  page_size: number
  results: ActivityItem[]
}

export type ActivityFilter = 'my_actions' | 'my_documents' | 'all'

export interface ActivityFeedOptions {
  filter?: ActivityFilter
  page?: number
  page_size?: number
}

// ====== API CALLS ======

/**
 * Получить персонализированную ленту активности.
 * 
 * В отличие от /api/v4/events/, этот endpoint возвращает:
 * - Только события текущего пользователя (filter=my_actions)
 * - События с документами пользователя (filter=my_documents)
 * - Человекочитаемые описания на русском языке
 * 
 * @param options - Параметры фильтрации и пагинации
 */
export async function getActivityFeed(
  options: ActivityFeedOptions = {}
): Promise<ActivityFeedResponse> {
  const params = new URLSearchParams()
  
  if (options.filter) {
    params.append('filter', options.filter)
  }
  if (options.page) {
    params.append('page', options.page.toString())
  }
  if (options.page_size) {
    params.append('page_size', options.page_size.toString())
  }
  
  const queryString = params.toString()
  const url = queryString 
    ? `/api/v4/headless/activity/feed/?${queryString}`
    : '/api/v4/headless/activity/feed/'
  
  const response = await apiService.get<ActivityFeedResponse>(url)
  return response.data
}

/**
 * Получить последние N действий пользователя.
 * 
 * Удобный метод для Dashboard виджетов.
 */
export async function getRecentActivity(limit: number = 10): Promise<ActivityItem[]> {
  const response = await getActivityFeed({
    filter: 'my_actions',
    page: 1,
    page_size: limit
  })
  return response.results
}
```

### 4.4 SettingsPage.vue (ОБНОВЛЕНИЕ)

```vue
<!-- src/pages/SettingsPage.vue -->
<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useNotification } from '@/composables/useNotification'
import { changePassword, type ChangePasswordRequest } from '@/services/settingsService'
import type { ChangePasswordError } from '@/services/settingsService'

const { showSuccess, showError } = useNotification()

// ====== PASSWORD CHANGE FORM ======

const passwordForm = reactive<ChangePasswordRequest>({
  current_password: '',
  new_password: '',
  new_password_confirm: ''
})

const isSubmitting = ref(false)
const passwordErrors = ref<string[]>([])

async function handlePasswordChange() {
  // Клиентская валидация
  passwordErrors.value = []
  
  if (!passwordForm.current_password) {
    passwordErrors.value.push('Введите текущий пароль')
  }
  if (!passwordForm.new_password) {
    passwordErrors.value.push('Введите новый пароль')
  }
  if (passwordForm.new_password !== passwordForm.new_password_confirm) {
    passwordErrors.value.push('Пароли не совпадают')
  }
  if (passwordForm.new_password.length < 8) {
    passwordErrors.value.push('Пароль должен содержать минимум 8 символов')
  }
  
  if (passwordErrors.value.length > 0) {
    return
  }
  
  // Отправка на сервер
  isSubmitting.value = true
  
  try {
    await changePassword(passwordForm)
    
    showSuccess('Пароль успешно изменен')
    
    // Очищаем форму
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.new_password_confirm = ''
    
  } catch (error: any) {
    const apiError = error.response?.data as ChangePasswordError | undefined
    
    if (apiError?.error_code === 'INVALID_CURRENT_PASSWORD') {
      passwordErrors.value = ['Неверный текущий пароль']
    } else if (apiError?.error_code === 'PASSWORD_MISMATCH') {
      passwordErrors.value = ['Новые пароли не совпадают']
    } else if (apiError?.error_code === 'PASSWORD_VALIDATION_FAILED') {
      passwordErrors.value = apiError.details || ['Пароль не соответствует требованиям']
    } else {
      showError('Не удалось изменить пароль. Попробуйте позже.')
    }
    
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="settings-page">
    <h1>Настройки</h1>
    
    <section class="settings-section">
      <h2>Смена пароля</h2>
      
      <form @submit.prevent="handlePasswordChange" class="password-form">
        <!-- Текущий пароль -->
        <div class="form-group">
          <label for="current_password">Текущий пароль</label>
          <input
            id="current_password"
            type="password"
            v-model="passwordForm.current_password"
            :disabled="isSubmitting"
            autocomplete="current-password"
          />
        </div>
        
        <!-- Новый пароль -->
        <div class="form-group">
          <label for="new_password">Новый пароль</label>
          <input
            id="new_password"
            type="password"
            v-model="passwordForm.new_password"
            :disabled="isSubmitting"
            autocomplete="new-password"
          />
          <small>Минимум 8 символов, не только цифры</small>
        </div>
        
        <!-- Подтверждение нового пароля -->
        <div class="form-group">
          <label for="new_password_confirm">Подтвердите новый пароль</label>
          <input
            id="new_password_confirm"
            type="password"
            v-model="passwordForm.new_password_confirm"
            :disabled="isSubmitting"
            autocomplete="new-password"
          />
        </div>
        
        <!-- Ошибки валидации -->
        <div v-if="passwordErrors.length > 0" class="form-errors">
          <ul>
            <li v-for="error in passwordErrors" :key="error">{{ error }}</li>
          </ul>
        </div>
        
        <!-- Кнопка отправки -->
        <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
          <span v-if="isSubmitting">Сохранение...</span>
          <span v-else>Изменить пароль</span>
        </button>
      </form>
    </section>
  </div>
</template>
```

---

## 5. Интеграция с Headless API

### 5.1 Конфигурация Axios

```typescript
// src/services/apiService.ts
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const apiService = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// ====== REQUEST INTERCEPTOR ======

apiService.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    
    // Добавляем токен авторизации
    if (authStore.token) {
      config.headers.Authorization = `Token ${authStore.token}`
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// ====== RESPONSE INTERCEPTOR ======

apiService.interceptors.response.use(
  (response) => response,
  (error) => {
    const authStore = useAuthStore()
    
    // 401 — сессия истекла
    if (error.response?.status === 401) {
      authStore.logout()
      window.location.href = '/login'
    }
    
    // 404 — endpoint не найден
    if (error.response?.status === 404) {
      console.error(`Endpoint not found: ${error.config?.url}`)
      // Для headless endpoints показываем понятное сообщение
      if (error.config?.url?.includes('/headless/')) {
        error.message = 'Функция временно недоступна. BFF слой не развернут.'
      }
    }
    
    return Promise.reject(error)
  }
)

export { apiService }
```

### 5.2 Feature Flags для BFF

```typescript
// src/config/features.ts

export const FEATURES = {
  // BFF endpoints доступны
  BFF_PASSWORD_CHANGE: import.meta.env.VITE_BFF_ENABLED === 'true',
  BFF_CONFIG_API: import.meta.env.VITE_BFF_ENABLED === 'true',
  BFF_ACTIVITY_FEED: import.meta.env.VITE_BFF_ENABLED === 'true',
  
  // Fallback на старое поведение
  LEGACY_PASSWORD_CHANGE: false,  // Нет fallback — endpoint не существует
  LEGACY_ACTIVITY_FEED: true,     // sessionStorage fallback
}

// Проверка доступности BFF
export function isBFFAvailable(): boolean {
  return FEATURES.BFF_PASSWORD_CHANGE && 
         FEATURES.BFF_CONFIG_API && 
         FEATURES.BFF_ACTIVITY_FEED
}
```

```env
# .env.development
VITE_API_URL=http://localhost:8080
VITE_BFF_ENABLED=false  # Включить после развертывания headless_api

# .env.production (после развертывания BFF)
VITE_API_URL=https://api.your-domain.com
VITE_BFF_ENABLED=true
```

---

## 6. Timeline Рефакторинга

### 6.1 Зависимости

```
Backend (Дмитрий)                    Frontend (Виталий)
─────────────────────────────────    ─────────────────────────────────
Неделя 1-2:                          Неделя 1-2:
├── HeadlessPasswordView             ├── Подготовка settingsService.ts
├── Unit tests                       ├── Подготовка SettingsPage.vue
└── Deploy to staging                └── Feature flag конфигурация

        ▼ CHECKPOINT: Password API Ready ▼

Неделя 3:                            Неделя 3:
├── HeadlessConfigView               ├── Создание documentTypeService.ts
├── Unit tests                       ├── Интеграция с uploadService.ts
└── Deploy to staging                └── Тестирование динамических форм

        ▼ CHECKPOINT: Config API Ready ▼

Неделя 4:                            Неделя 4:
├── HeadlessActivityFeedView         ├── Обновление activityService.ts
├── Unit tests                       ├── Обновление dashboardStore.ts
└── Deploy to staging                └── Тестирование Activity Feed

        ▼ CHECKPOINT: Activity API Ready ▼

Неделя 5-6:                          Неделя 5-6:
├── E2E тестирование                 ├── E2E тестирование
├── Security audit                   ├── Performance optimization
└── Production deploy                └── Production deploy

        ▼ PRODUCTION READY ▼
```

### 6.2 Чек-лист Готовности Фронтенда

**До развертывания BFF:**
- [ ] Код settingsService.ts подготовлен (закомментирован новый endpoint)
- [ ] Код documentTypeService.ts создан (закомментирован)
- [ ] Код activityService.ts подготовлен (fallback на sessionStorage)
- [ ] Feature flags настроены
- [ ] Unit tests написаны (mocked)

**После развертывания BFF:**
- [ ] VITE_BFF_ENABLED=true
- [ ] Раскомментировать новые endpoints
- [ ] E2E тесты прошли
- [ ] Смена пароля работает
- [ ] Динамические формы работают
- [ ] Activity feed показывает реальные данные

---

## 📋 Связанная Документация

- **[TRANSFORMATION_PLAN_V4.md](TRANSFORMATION_PLAN_V4.md)** — План трансформации с BFF стратегией
- **[BACKEND_ANALYSIS_V4.md](BACKEND_ANALYSIS_V4.md)** — Архитектура headless_api
- **[TEST_EXECUTION_REPORT.md](TEST_EXECUTION_REPORT.md)** — Доказательства API сбоев

---

**Версия документа:** 4.0 (Ожидание Реализации BFF)
**Создан:** 04 декабря 2025
**Автор:** Senior Frontend Architect & Technical Writer

---

*🟡 СТАТУС: Фронтенд готов к интеграции с BFF. Ожидание развертывания headless_api micro-app.*


