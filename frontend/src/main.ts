import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import './styles/index.css'
import { hasToken } from './services/authService'

// ============================================================================
// Phase A1.3: App Initialization with Auth State Sync
// ============================================================================

/**
 * Sync persisted auth state with real token presence.
 * This prevents "ghost" authenticated state from previous sessions
 * where the token was cleared but Pinia state persisted.
 */
function syncAuthState(): void {
  const hasRealToken = hasToken()
  const hasMockAuth = localStorage.getItem('dev_authenticated') === 'true'
  
  // If no real token and no mock flag, clear any persisted auth state
  if (!hasRealToken && !hasMockAuth) {
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

// ============================================================================
// Bootstrap Application
// ============================================================================

// Step 1: Sync auth state BEFORE app initialization
syncAuthState()

// Step 2: Create Vue app
const app = createApp(App)

// Step 3: Setup Pinia with persistence
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

// Step 4: Mount app
app.mount('#app')

// Step 5: Initialize auth store AFTER mount (important for proper Pinia initialization)
// This validates the token and restores user session if valid
import { useAuthStore } from './stores/authStore'

const authStore = useAuthStore()
authStore.initialize().then((isAuthenticated) => {
  console.log('[Main] Auth initialized, authenticated:', isAuthenticated)
})


