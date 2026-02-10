import { createApiService } from '~/services/apiService'

export function useApi() {
  const config = useRuntimeConfig()

  // On client: use empty baseURL — requests go through Nitro proxy (same origin, no CORS)
  // On server (SSR): use direct backend URL for server-to-server calls
  const baseURL = import.meta.server
    ? (config.apiBase as string || 'http://localhost:8080')
    : ''

  const apiService = createApiService(baseURL)

  return {
    getPage: apiService.getPage.bind(apiService),
    getPosts: apiService.getPosts.bind(apiService),
    getPost: apiService.getPost.bind(apiService),
    getPlans: apiService.getPlans.bind(apiService),
    getFaq: apiService.getFaq.bind(apiService),
    submitLead: apiService.submitLead.bind(apiService),
    subscribeNewsletter: apiService.subscribeNewsletter.bind(apiService),
    register: apiService.register.bind(apiService),
    verifyEmail: apiService.verifyEmail.bind(apiService)
  }
}
