import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup/vitest.setup.ts',
    include: ['tests/unit/**/*.spec.ts', 'src/**/*.spec.ts'],
    exclude: [
      'node_modules/',
      'tests/e2e/**', // Исключаем E2E тесты (они для Playwright)
      '*.config.*',
      'dist/',
      '**/*.d.ts',
      '**/*.stories.*',
      'storybook-static/',
      '.storybook/'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '*.config.*',
        'dist/',
        '**/*.d.ts',
        '**/*.stories.*',
        'storybook-static/',
        '.storybook/'
      ]
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})


