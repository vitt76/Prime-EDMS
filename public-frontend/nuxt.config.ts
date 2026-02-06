export default defineNuxtConfig({
  devtools: { enabled: true },
  ssr: true,
  css: ['~/assets/css/tailwind.css'],
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n',
    '@nuxt/image',
    '@pinia/nuxt',
    '@nuxtjs/sitemap',
    '@nuxtjs/color-mode'
  ],

  // Runtime configuration
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8080',
      appUrl: process.env.NUXT_PUBLIC_APP_URL || 'http://localhost:5173',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
      environment: process.env.NUXT_PUBLIC_ENVIRONMENT || 'development',
      gaId: process.env.NUXT_PUBLIC_GA_ID || ''
    }
  },

  // App configuration
  app: {
    head: {
      htmlAttrs: {
        lang: 'ru'
      },
      title: 'MADDAM - DAM система для управления медиафайлами',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'format-detection', content: 'telephone=no' },
        { name: 'theme-color', content: '#4f46e5' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // Development server
  devServer: {
    port: 3000
  },

  // Vite configuration
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8080',
          changeOrigin: true
        }
      }
    },
    build: {
      // Optimize chunk sizes
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-vue': ['vue', 'vue-router', 'pinia'],
            'vendor-ui': ['@headlessui/vue'],
            'vendor-icons': ['@heroicons/vue/24/outline', '@heroicons/vue/24/solid'],
            'vendor-utils': ['zod', '@vueuse/core']
          }
        }
      }
    }
  },

  // Image optimization
  image: {
    provider: 'ipx',
    quality: 80,
    format: ['webp', 'avif', 'jpg'],
    screens: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280,
      '2xl': 1536
    },
    presets: {
      avatar: {
        modifiers: {
          format: 'webp',
          width: 80,
          height: 80,
          fit: 'cover'
        }
      },
      thumbnail: {
        modifiers: {
          format: 'webp',
          width: 400,
          height: 300,
          fit: 'cover'
        }
      },
      hero: {
        modifiers: {
          format: 'webp',
          width: 1200,
          height: 800,
          quality: 85
        }
      }
    }
  },

  // i18n configuration
  i18n: {
    strategy: 'prefix_except_default',
    defaultLocale: 'ru',
    locales: [
      { code: 'ru', iso: 'ru-RU', name: 'Русский', file: 'ru.json' },
      { code: 'en', iso: 'en-US', name: 'English', file: 'en.json' }
    ],
    langDir: 'locales/',
    baseUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root'
    }
  },

  // Color mode (dark mode)
  colorMode: {
    preference: 'system',
    fallback: 'light',
    classSuffix: ''
  },

  // Site URL (used by sitemap and other modules)
  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000'
  },

  // Sitemap configuration
  sitemap: {
    autoLastmod: true,
    exclude: ['/auth/**', '/api/**']
  },

  // Performance optimizations
  experimental: {
    payloadExtraction: true,
    renderJsonPayloads: true
  },

  // Route rules for caching
  routeRules: {
    // Homepage - revalidate every hour
    '/': { swr: 3600 },
    // Pricing - revalidate every 6 hours
    '/pricing': { swr: 21600 },
    // Blog index - revalidate every 30 minutes
    '/blog': { swr: 1800 },
    // Blog posts - revalidate every hour
    '/blog/**': { swr: 3600 },
    // Static pages - cache longer
    '/about': { swr: 86400 },
    '/contact': { swr: 86400 },
    '/terms': { swr: 86400 },
    '/privacy': { swr: 86400 },
    // Auth pages - no cache
    '/auth/**': { ssr: true, cache: false },
    // API routes - no prerender
    '/api/**': { cors: true }
  },

  // Nitro configuration
  nitro: {
    compressPublicAssets: true,
    prerender: {
      crawlLinks: true,
      routes: ['/', '/pricing', '/about', '/contact', '/blog']
    }
  },

  // TypeScript configuration
  typescript: {
    strict: true,
    typeCheck: false // Disable for faster dev builds
  }
})
