import { createApiService } from '~/services/apiService'

export function useApi() {
  const config = useRuntimeConfig()
  const apiService = createApiService(config.public.apiBase)

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
