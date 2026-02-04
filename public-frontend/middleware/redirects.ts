export default defineNuxtRouteMiddleware((to) => {
  const redirects: Record<string, string> = {
    '/old-pricing': '/pricing',
    '/news': '/blog',
    '/support': '/contact'
  }

  if (redirects[to.path]) {
    return navigateTo(redirects[to.path], { redirectCode: 301 })
  }
})
