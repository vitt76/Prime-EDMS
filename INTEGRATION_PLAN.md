# План интеграции Vue 3 фронтенда с Mayan EDMS бэкендом

## 📋 Обзор проекта

**Prime-EDMS** - это DAM (Digital Asset Management) система на базе Mayan EDMS с современным Vue 3 SPA фронтендом.

### Архитектура системы

| Компонент | Технология | Порт | Описание |
|-----------|------------|------|----------|
| **Фронтенд** | Vue 3 + TypeScript + Tailwind CSS | 5173 | Современный SPA с компонентами DAM |
| **Бэкенд** | Mayan EDMS (Django) | 8080 | REST API с token authentication |
| **База данных** | PostgreSQL | 5433 | Основное хранилище данных |
| **Кэш** | Redis | 6380 | Кеширование и сессии |
| **Очереди** | RabbitMQ | 5672 | Celery задачи |

## 🎯 Цели интеграции

1. **Автоматическая авторизация** - сохранение механизма генерации паролей при пересборке контейнера
2. **Seamless UX** - автоматическое заполнение формы логина учетными данными
3. **API Integration** - корректная работа фронтенда с REST API бэкенда
4. **Production Ready** - система готова к развертыванию

## 🔧 Этапы интеграции

### Этап 1: Backend API расширения

#### 1.1 Создать API endpoint для получения учетных данных autoadmin

**Файл:** `mayan/apps/autoadmin/api_views.py`

```python
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import AutoAdminSingleton


class AutoAdminCredentialsAPIView(APIView):
    """
    Get auto-generated admin credentials for first-time setup.
    Only available when auto admin properties exist.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            autoadmin_properties = AutoAdminSingleton.objects.get()
            if autoadmin_properties.account and autoadmin_properties.password:
                return Response({
                    'username': autoadmin_properties.account.username,
                    'email': autoadmin_properties.account.email,
                    'password': autoadmin_properties.password,
                    'is_auto_generated': True
                })
        except AutoAdminSingleton.DoesNotExist:
            pass

        return Response({
            'message': 'No auto-generated credentials available',
            'is_auto_generated': False
        })
```

**Файл:** `mayan/apps/autoadmin/urls.py` (добавление URL)

```python
from django.conf.urls import url
from .api_views import AutoAdminCredentialsAPIView

api_urls = [
    # ... existing URLs ...
    url(
        regex=r'^credentials/$',
        view=AutoAdminCredentialsAPIView.as_view(),
        name='autoadmin-credentials'
    )
]
```

### Этап 2: Frontend модификации

#### 2.1 Исправить authService.ts

**Изменения:**
- Убрать флаг `USE_REAL_API`
- Всегда использовать реальное API
- Добавить метод для получения autoadmin учетных данных

```typescript
// Удалить эту строку:
// const USE_REAL_API = import.meta.env.VITE_USE_REAL_API === 'true' || !import.meta.env.DEV

// Всегда использовать реальное API в production
const USE_REAL_API = true

/**
 * Get auto-generated admin credentials (only available on first setup)
 */
export async function getAutoAdminCredentials(): Promise<{
  username: string
  email: string
  password: string
  is_auto_generated: boolean
} | null> {
  try {
    const response = await axios.get('/api/v4/autoadmin/credentials/')
    return response.data.is_auto_generated ? response.data : null
  } catch (error) {
    console.warn('[Auth] Could not fetch auto admin credentials:', error)
    return null
  }
}
```

#### 2.2 Модифицировать LoginPage.vue

**Изменения:**
- Добавить автоматическое заполнение формы при первом запуске
- Показывать подсказку о автоматически сгенерированных учетных данных

```vue
<template>
  <div class="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-50 px-4">
    <Card class="w-full max-w-md">
      <h1 class="text-3xl font-semibold mb-6 text-center">Login</h1>

      <!-- Предупреждение об автоматически сгенерированных учетных данных -->
      <div v-if="showCredentials" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p class="text-sm text-blue-800">
          🔐 Автоматически сгенерированные учетные данные загружены
        </p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <Input
          v-model="email"
          type="email"
          label="Email"
          placeholder="Enter your email"
          required
        />
        <Input
          v-model="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          required
        />
        <Button type="submit" variant="primary" class="w-full" :loading="loading">
          Sign In
        </Button>
      </form>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { getAutoAdminCredentials } from '@/services/authService'
import Card from '@/components/Common/Card.vue'
import Input from '@/components/Common/Input.vue'
import Button from '@/components/Common/Button.vue'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const loading = ref(false)
const showCredentials = ref(false)

// Автоматически заполнить учетные данные при первом запуске
onMounted(async () => {
  const credentials = await getAutoAdminCredentials()
  if (credentials) {
    email.value = credentials.email
    password.value = credentials.password
    showCredentials.value = true
  }
})

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(email.value, password.value)

    // Перенаправление после успешного входа
    const returnTo = router.currentRoute.value.query.returnTo as string || '/'
    router.push(returnTo)
  } catch (error) {
    console.error('Login failed:', error)
    // TODO: Show error message to user
  } finally {
    loading.value = false
  }
}
</script>
```

#### 2.3 Обновить Vite конфигурацию

**Файл:** `frontend/vite.config.ts`

```typescript
server: {
  port: 5173,
  host: '0.0.0.0',
  proxy: {
    // Main REST API v4 - указываем правильный порт Mayan EDMS
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      cookieDomainRewrite: 'localhost'
    },
    // DAM-specific API endpoints
    '/digital-assets': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      cookieDomainRewrite: 'localhost'
    },
    // Distribution API endpoints
    '/distribution': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      cookieDomainRewrite: 'localhost'
    },
    // Django authentication
    '/authentication': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      secure: false,
      cookieDomainRewrite: 'localhost'
    },
    // Static files (CSS, JS from Django)
    '/static': {
      target: 'http://localhost:8080',
      changeOrigin: true
    },
    // Media files (uploaded documents)
    '/media': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}
```

### Этап 3: Скрипты запуска и тестирования

#### 3.1 Скрипт запуска интегрированной системы

**Файл:** `start-integrated-system.sh`

```bash
#!/bin/bash

echo "🚀 Starting Prime-EDMS Integrated System"
echo "========================================"

# Запуск Docker containers
echo "📦 Starting Docker services..."
docker-compose up -d

# Ожидание готовности бэкенда
echo "⏳ Waiting for backend to be ready..."
until curl -f http://localhost:8080/api/v4/ > /dev/null 2>&1; do
  echo "Backend not ready, waiting..."
  sleep 5
done

echo "✅ Backend is ready!"

# Получение учетных данных autoadmin
echo "🔑 Fetching auto-generated credentials..."
CREDENTIALS=$(curl -s http://localhost:8080/api/v4/autoadmin/credentials/)
if echo "$CREDENTIALS" | grep -q '"is_auto_generated":true'; then
  USERNAME=$(echo "$CREDENTIALS" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
  PASSWORD=$(echo "$CREDENTIALS" | grep -o '"password":"[^"]*"' | cut -d'"' -f4)
  echo "📝 Auto-generated credentials:"
  echo "   Username: $USERNAME"
  echo "   Password: $PASSWORD"
  echo ""
fi

# Запуск фронтенда
echo "🎨 Starting frontend..."
cd frontend
npm run dev
```

#### 3.2 Скрипт тестирования интеграции

**Файл:** `test-integration.sh`

```bash
#!/bin/bash

echo "🧪 Testing Prime-EDMS Integration"
echo "=================================="

BASE_URL="http://localhost:8080"

# Тест 1: Проверка доступности API
echo "1. Testing API availability..."
if curl -f "$BASE_URL/api/v4/" > /dev/null 2>&1; then
  echo "✅ API is accessible"
else
  echo "❌ API is not accessible"
  exit 1
fi

# Тест 2: Получение учетных данных autoadmin
echo "2. Testing auto admin credentials endpoint..."
CREDENTIALS=$(curl -s "$BASE_URL/api/v4/autoadmin/credentials/")
if echo "$CREDENTIALS" | grep -q '"is_auto_generated"'; then
  echo "✅ Auto admin credentials endpoint works"
else
  echo "❌ Auto admin credentials endpoint failed"
  exit 1
fi

# Тест 3: Получение токена авторизации
echo "3. Testing token authentication..."
if echo "$CREDENTIALS" | grep -q '"is_auto_generated":true'; then
  USERNAME=$(echo "$CREDENTIALS" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
  EMAIL=$(echo "$CREDENTIALS" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
  PASSWORD=$(echo "$CREDENTIALS" | grep -o '"password":"[^"]*"' | cut -d'"' -f4)

  TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v4/auth/token/obtain/" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

  if echo "$TOKEN_RESPONSE" | grep -q '"token"'; then
    echo "✅ Token authentication works"
  else
    echo "❌ Token authentication failed"
    exit 1
  fi
else
  echo "⚠️ No auto-generated credentials available, skipping token test"
fi

# Тест 4: Проверка фронтенда
echo "4. Testing frontend availability..."
if curl -f http://localhost:5173 > /dev/null 2>&1; then
  echo "✅ Frontend is accessible"
else
  echo "❌ Frontend is not accessible"
  exit 1
fi

echo ""
echo "🎉 All integration tests passed!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8080"
```

## 📝 Обновление документации

### 4.1 Обновить README.md

```markdown
# Prime-EDMS Integrated System

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd prime-edms
   ```

2. **Start integrated system:**
   ```bash
   chmod +x start-integrated-system.sh
   ./start-integrated-system.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8080
   - Admin panel: http://localhost:8080/admin/

4. **Login credentials:**
   The system will automatically generate admin credentials on first run.
   Check the terminal output or visit the frontend for auto-filled login form.

## 🧪 Testing

Run integration tests:
```bash
chmod +x test-integration.sh
./test-integration.sh
```
```

### 4.2 Создать integration guide

**Файл:** `INTEGRATION_GUIDE.md`

```markdown
# Prime-EDMS Integration Guide

## Architecture Overview

### Backend (Mayan EDMS)
- **Port:** 8080
- **API:** REST API v4 with token authentication
- **Auth:** `/api/v4/auth/token/obtain/`
- **User info:** `/api/v4/user_management/users/current/`
- **Auto admin:** `/api/v4/autoadmin/credentials/`

### Frontend (Vue 3 SPA)
- **Port:** 5173
- **Framework:** Vue 3 + TypeScript + Tailwind CSS
- **State:** Pinia stores
- **API client:** Axios with interceptors

## Authentication Flow

1. **First Run:** Docker generates random admin password
2. **API Endpoint:** Frontend fetches credentials from `/api/v4/autoadmin/credentials/`
3. **Auto-fill:** Login form is automatically populated
4. **Token Auth:** Frontend obtains JWT token via `/api/v4/auth/token/obtain/`
5. **User Info:** Frontend fetches user details from `/api/v4/user_management/users/current/`

## Development Workflow

### Starting the System
```bash
# Start all services
./start-integrated-system.sh

# Or manually:
docker-compose up -d
cd frontend && npm run dev
```

### Testing Integration
```bash
./test-integration.sh
```

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v4/autoadmin/credentials/` | GET | Get auto-generated admin credentials |
| `/api/v4/auth/token/obtain/` | POST | Obtain authentication token |
| `/api/v4/user_management/users/current/` | GET | Get current user information |
| `/api/v4/documents/documents/` | GET/POST | DAM document operations |
```

## Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Check if Docker containers are running: `docker-compose ps`
   - Verify ports: backend on 8080, frontend on 5173
   - Check CORS settings in Mayan EDMS

2. **Auto admin credentials not available**
   - Ensure this is the first run of the container
   - Check if autoadmin app is properly configured
   - Verify database migrations ran successfully

3. **Token authentication fails**
   - Verify credentials are correct
   - Check Mayan EDMS authentication settings
   - Ensure token endpoint is accessible

### Debug Commands

```bash
# Check backend health
curl http://localhost:8080/api/v4/

# Get auto admin credentials
curl http://localhost:8080/api/v4/autoadmin/credentials/

# Test token authentication
curl -X POST http://localhost:8080/api/v4/auth/token/obtain/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```
```

## ✅ **Проверочный список интеграции**

### Backend
- [ ] API endpoint `/api/v4/autoadmin/credentials/` создан
- [ ] URL pattern добавлен в `mayan/apps/autoadmin/urls.py`
- [ ] Модель `AutoAdminSingleton` корректно работает
- [ ] Token authentication endpoint доступен

### Frontend
- [ ] `authService.ts` использует реальное API
- [ ] Метод `getAutoAdminCredentials()` реализован
- [ ] `LoginPage.vue` автоматически заполняет форму
- [ ] Vite proxy настроен на порт 8080
- [ ] Axios interceptors корректно работают

### Integration
- [ ] Скрипт `start-integrated-system.sh` работает
- [ ] Скрипт `test-integration.sh` проходит все тесты
- [ ] Документация обновлена
- [ ] README содержит инструкции по запуску

### Testing
- [ ] Интеграционные тесты проходят
- [ ] Авторизация работает корректно
- [ ] API endpoints отвечают правильно
- [ ] Frontend и backend общаются без ошибок

## 🚀 **Запуск интеграции**

```bash
# 1. Запустить систему
./start-integrated-system.sh

# 2. Проверить интеграцию
./test-integration.sh

# 3. Открыть фронтенд
# http://localhost:5173

# 4. Проверить автоматическое заполнение формы логина
```

## 🔐 **Безопасность**

- **Пароли:** Генерируются автоматически при первом запуске
- **Хранение:** Учетные данные доступны только через защищенный API
- **Доступ:** Endpoint `/api/v4/autoadmin/credentials/` доступен без авторизации только при первом запуске
- **Токены:** JWT токены используются для всех последующих запросов

---

**Статус:** Готово к реализации
**Ответственный:** Frontend/Backend Developer
**Оценка времени:** 4-6 часов



