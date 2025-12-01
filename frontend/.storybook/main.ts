import type { StorybookConfig } from '@storybook/vue3-vite'
import { mergeConfig } from 'vite'
import path from 'path'

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx|mdx)', '../src/**/*.stories.ts'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-links'
  ],
  framework: {
    name: '@storybook/vue3-vite',
    options: {}
  },
  core: {
    builder: '@storybook/builder-vite'
  },
  async viteFinal(config) {
    return mergeConfig(config, {
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '../src')
        }
      }
    })
  },
  docs: {
    autodocs: 'tag'
  }
}

export default config
