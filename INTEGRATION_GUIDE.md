# Prime-EDMS Integration Guide

## Architecture Overview

### Backend (Mayan EDMS)
- **Port:** 8080 (Docker container mapping)
- **API:** REST API v4 with token authentication
- **Auth:** `/api/v4/auth/token/obtain/`
- **User info:** `/api/v4/user_management/users/current/`
- **Auto admin:** `/autoadmin-api/credentials/`
- **Database:** PostgreSQL with Redis cache
- **Queue:** RabbitMQ with Celery workers

### Frontend (Vue 3 SPA)
- **Port:** 5173 (development), production build for deployment
- **Framework:** Vue 3 + TypeScript + Tailwind CSS
- **State:** Pinia stores with localStorage persistence
- **API client:** Axios with interceptors
- **Build:** Vite with hot reload
- **Proxy:** All API requests proxied to backend on port 80

## Authentication Flow

1. **First Run:** Mayan EDMS generates random admin password via autoadmin system
2. **API Endpoint:** Frontend fetches credentials from `/autoadmin-api/credentials/`
3. **Auto-fill:** Login form automatically populated with generated credentials
4. **Token Auth:** Frontend obtains JWT token via `/api/v4/auth/token/obtain/`
5. **User Info:** Frontend fetches user details from `/api/v4/user_management/users/current/`
6. **Session:** Token stored in localStorage and sent with all API requests

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

| Endpoint | Method | Purpose | Authentication |
|----------|--------|---------|----------------|
| `/autoadmin-api/credentials/` | GET | Get auto-generated admin credentials | None (first setup only) |
| `/api/v4/auth/token/obtain/` | POST | Obtain authentication token | None |
| `/api/v4/user_management/users/current/` | GET | Get current user information | Token required |
| `/api/v4/documents/documents/` | GET/POST | DAM document operations | Token required |

## Auto Admin System

### How It Works
1. **Model:** `mayan.apps.autoadmin.models.AutoAdminSingleton`
2. **Generation:** Random password created on first run via `AutoAdminSingleton.objects.create_autoadmin()`
3. **Storage:** Credentials stored in database for lifetime of container
4. **API Access:** Available via `/autoadmin-api/credentials/` endpoint
5. **Cleanup:** Credentials cleared when password is manually changed

### Security Considerations
- Endpoint only accessible without authentication
- Only returns credentials if they exist
- Should be disabled in production environments
- Credentials cleared after first successful login

## Frontend Architecture

### Auth Service (`frontend/src/services/authService.ts`)
```typescript
// Always use real API
const USE_REAL_API = true

// Get auto-generated credentials
export async function getAutoAdminCredentials()

// Token management functions
export function getToken()
export function setToken(token: string)
export function clearToken()
```

### Auth Store (`frontend/src/stores/authStore.ts`)
```typescript
// Pinia store with persistence
export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const permissions = ref<string[]>([])

  // Actions
  async function login(email: string, password: string)
  async function logout()
  async function checkAuth()
})
```

### Login Page (`frontend/src/pages/LoginPage.vue`)
```vue
<script setup lang="ts">
// Auto-fill credentials on mount
onMounted(async () => {
  const credentials = await getAutoAdminCredentials()
  if (credentials) {
    email.value = credentials.email
    password.value = credentials.password
    showCredentials.value = true
  }
})
</script>
```

## Vite Configuration

### Proxy Setup (`frontend/vite.config.ts`)
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': { target: 'http://localhost:80' },
    '/autoadmin-api': { target: 'http://localhost:80' },
    '/static': { target: 'http://localhost:80' },
    '/media': { target: 'http://localhost:80' }
  }
}
```

## Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Check if Docker containers are running: `docker-compose ps`
   - Verify ports: backend on 80, frontend on 5173
   - Check Vite proxy configuration

2. **Auto admin credentials not available**
   - Ensure this is the first run of the container
   - Check if autoadmin app is properly configured
   - Verify database migrations ran successfully

3. **Token authentication fails**
   - Verify credentials are correct
   - Check Mayan EDMS authentication settings
   - Ensure token endpoint is accessible

4. **CORS issues**
   - Check Django CORS settings in Mayan EDMS
   - Verify Vite proxy configuration
   - Ensure backend allows requests from localhost:5173

### Debug Commands

```bash
# Check backend health
curl http://localhost:8080/api/v4/

# Get auto admin credentials
curl http://localhost:8080/autoadmin-api/credentials/

# Test token authentication
curl -X POST http://localhost:8080/api/v4/auth/token/obtain/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'

# Check frontend proxy
curl http://localhost:5173/autoadmin-api/credentials/
```

### Logs

```bash
# Backend logs
docker-compose logs app

# Frontend logs (in browser console)
# Open http://localhost:5173 and check DevTools
```

## Deployment

### Production Build
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

### Environment Variables
```bash
# Backend
MAYAN_DATABASE_PASSWORD=your_password
DAM_GIGACHAT_CREDENTIALS=your_credentials
# ... other Mayan EDMS settings

# Frontend (in production)
VITE_API_URL=http://your-backend:80
```

## Security

- **Development:** Auto-generated credentials for easy setup
- **Production:** Disable auto admin credentials endpoint
- **Tokens:** JWT tokens with expiration
- **HTTPS:** Enable in production environment
- **CORS:** Restrict to allowed origins

## API Response Formats

### Auto Admin Credentials
```json
{
  "username": "admin",
  "email": "autoadmin@example.com",
  "password": "KWF9yc2CGK",
  "is_auto_generated": true
}
```

### Token Authentication
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Information
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "autoadmin@example.com",
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "permissions": ["admin.access", "documents.view"],
    "role": "admin"
  },
  "permissions": ["admin.access", "documents.view"]
}
```

---

**Status:** ✅ Integration Complete
**Last Updated:** December 2025
