import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import './styles/index.css'
import { hasToken } from './services/authService'

// ============================================================================
// Sync persisted auth state with real token presence
// This prevents "ghost" authenticated state from previous sessions
// ============================================================================
function syncAuthState() {
  const hasRealToken = hasToken()
  const hasMockAuth = localStorage.getItem('dev_authenticated') === 'true'
  
  // If no real token and no mock flag, clear any persisted auth state
  if (!hasRealToken && !hasMockAuth) {
    // Clear Pinia persisted auth state
    const persistedAuth = localStorage.getItem('auth')
    if (persistedAuth) {
      try {
        const authData = JSON.parse(persistedAuth)
        if (authData.isAuthenticated) {
          console.warn('[Main] Clearing stale persisted auth state (no token found)')
          localStorage.removeItem('auth')
        }
      } catch (e) {
        // Ignore parse errors
      }
    }
  }
}

// Sync auth state before app initialization
syncAuthState()

const app = createApp(App)

// Setup Pinia with persistence
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

// Mount app first
app.mount('#app')

// Initialize auth store AFTER mount - this is important for proper Pinia initialization
import { useAuthStore } from './stores/authStore'
const authStore = useAuthStore()
authStore.checkAuth()


