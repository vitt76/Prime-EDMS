import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
// Backend URL - Docker exposes port 8080 which is accessible via localhost from Windows
const BACKEND_URL = 'http://localhost:8080'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      // Main REST API v4 → Django backend
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost',
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log(`[Vite Proxy] ${req.method} ${req.url} → ${BACKEND_URL}${req.url}`)
          })
        }
      },
      // DAM-specific API endpoints
      '/digital-assets': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost'
      },
      // Distribution API endpoints
      '/distribution': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost'
      },
      // Django authentication
      '/authentication': {
        target: BACKEND_URL,
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost'
      },
      // Static files (CSS, JS from Django)
      '/static': {
        target: BACKEND_URL,
        changeOrigin: true
      },
      // Media files (uploaded documents)
      '/media': {
        target: BACKEND_URL,
        changeOrigin: true
      }
    }
  },
  build: {
    target: 'es2015',
    outDir: 'dist'
  }
})


