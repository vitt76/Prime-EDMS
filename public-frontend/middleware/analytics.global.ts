export default defineNuxtRouteMiddleware((to, from) => {
  if (process.client && to.path !== from.path) {
    const { $analytics } = useNuxtApp()
    nextTick(() => {
      $analytics?.trackPageView(to.path)
    })
  }
})
