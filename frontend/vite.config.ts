import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
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
      // Main REST API v4
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        cookieDomainRewrite: 'localhost',
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Log requests in dev
            console.log(`[Proxy] ${proxyReq.method} ${proxyReq.path}`)
          })
        }
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
        changeOrigin: true,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Log media requests in dev
            if (import.meta.env.DEV) {
              console.log(`[Proxy Media] ${proxyReq.method} ${proxyReq.path}`)
            }
          })
        }
      }
    }
  },
  build: {
    target: 'es2015',
    outDir: 'dist'
  }
})


