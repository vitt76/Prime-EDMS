/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    screens: {
      sm: '640px',   // Mobile
      md: '768px',   // Tablet
      lg: '1024px',  // Desktop
      xl: '1280px'   // Large desktop
    },
    extend: {
      colors: {
        // Primary colors (Light mode)
        primary: {
          0: '#0052CC',
          50: '#EBF5FF',
          100: '#C7E0FF',
          500: '#0052CC',
          600: '#0042A8'
        },
        // Neutral colors (Light mode)
        neutral: {
          0: '#FFFFFF',
          50: '#F9FAFB',
          100: '#F3F4F6',
          300: '#E1E4E8',
          600: '#4B5563',
          900: '#111827'
        },
        // Semantic colors
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#06B6D4',
        // Accent
        accent: {
          primary: '#00875A',
          secondary: '#4C8CFF'
        }
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'sans-serif'
        ],
        mono: ['Berkeley Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace']
      },
      fontSize: {
        xs: ['11px', { lineHeight: '1.5' }],
        sm: ['12px', { lineHeight: '1.5' }],
        base: ['14px', { lineHeight: '1.5' }],
        lg: ['16px', { lineHeight: '1.5' }],
        xl: ['18px', { lineHeight: '1.2' }],
        '2xl': ['20px', { lineHeight: '1.2' }],
        '3xl': ['24px', { lineHeight: '1.2' }],
        '4xl': ['32px', { lineHeight: '1.2' }]
      },
      spacing: {
        header: '64px',
        sidebar: '280px',
        'sidebar-collapsed': '64px'
      },
      maxWidth: {
        container: '1280px'
      },
      borderRadius: {
        base: '6px'
      },
      boxShadow: {
        xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
      },
      transitionDuration: {
        fast: '150ms',
        normal: '250ms',
        slow: '350ms',
        slower: '500ms'
      },
      transitionTimingFunction: {
        'ease-in': 'cubic-bezier(0.4, 0, 1, 1)',
        'ease-out': 'cubic-bezier(0, 0, 0.2, 1)',
        'ease-in-out': 'cubic-bezier(0.4, 0, 0.2, 1)'
      }
    }
  },
  plugins: [require('@tailwindcss/forms')]
}


