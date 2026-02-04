export default defineAppConfig({
  brand: {
    name: 'MADDAM',
    tagline: 'DAM система для управления медиафайлами',
    description: 'Облачное хранилище + AI-поиск + Аналитика для вашей команды'
  },
  theme: {
    primaryColor: '#4f46e5',
    accentColor: '#7c3aed'
  },
  social: {
    linkedin: 'https://linkedin.com/company/maddam',
    twitter: 'https://twitter.com/maddam_dam',
    github: 'https://github.com/maddam'
  },
  features: {
    analytics: true,
    darkMode: true,
    i18n: true
  },
  seo: {
    defaultOgImage: '/og-default.jpg',
    twitterHandle: '@maddam_dam'
  }
})
