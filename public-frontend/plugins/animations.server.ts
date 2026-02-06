/**
 * Server-side stub for animation directives.
 *
 * The real directives (v-animate-on-scroll, v-stagger) are registered in
 * animations.client.ts and rely on IntersectionObserver (browser-only).
 * During SSR Vue's server-renderer calls getSSRProps() on every directive
 * it encounters in templates.  Without this stub the render crashes with:
 *   "Cannot read properties of undefined (reading 'getSSRProps')"
 */

export default defineNuxtPlugin((nuxtApp) => {
  // Register SSR-safe stubs that simply return empty props.
  nuxtApp.vueApp.directive('animate-on-scroll', {
    getSSRProps() {
      return {}
    }
  })

  nuxtApp.vueApp.directive('stagger', {
    getSSRProps() {
      return {}
    }
  })
})
