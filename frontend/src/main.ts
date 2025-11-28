import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import './styles/index.css'

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


