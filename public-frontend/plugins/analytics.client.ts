/**
 * Google Analytics Plugin
 * 
 * This plugin integrates Google Analytics 4 (GA4) with the Nuxt application.
 * It only runs on the client side (.client.ts suffix).
 */

import { createAnalyticsService } from '~/services/analyticsService'

declare global {
  interface Window {
    dataLayer: any[]
    gtag: (...args: any[]) => void
  }
}

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const gaId = config.public.gaId

  if (!gaId) {
    console.info('[Analytics] No GA ID configured, analytics disabled')
    return
  }

  window.dataLayer = window.dataLayer || []

  window.gtag = function gtag(...args: any[]) {
    window.dataLayer.push(args)
  }

  window.gtag('js', new Date())
  window.gtag('config', gaId, {
    page_path: window.location.pathname,
    send_page_view: false
  })

  useHead({
    script: [
      {
        src: `https://www.googletagmanager.com/gtag/js?id=${gaId}`,
        async: true
      }
    ]
  })

  const analyticsService = createAnalyticsService(gaId)

  nuxtApp.hook('page:finish', () => {
    analyticsService.track({
      event: 'page_view',
      page_title: document.title,
      page_location: window.location.href,
      page_path: window.location.pathname
    })
  })

  return {
    provide: {
      analytics: {
        trackEvent(eventName: string, eventParams?: Record<string, any>) {
          analyticsService.track({ event: eventName, ...(eventParams || {}) })
        },
        trackPageView(page: string) {
          analyticsService.trackPageView(page)
        },
        trackButtonClick(buttonName: string, location?: string) {
          analyticsService.track({
            event: 'button_click',
            button_name: buttonName,
            button_location: location || 'unknown'
          })
        },
        trackFormSubmit(formName: string, success: boolean) {
          analyticsService.trackFormSubmit(formName, success)
        },
        trackSignup(method: string = 'email') {
          analyticsService.track({
            event: 'sign_up',
            method
          })
        },
        trackLogin(method: string = 'email') {
          analyticsService.track({
            event: 'login',
            method
          })
        },
        trackContentView(contentType: string, contentId: string) {
          analyticsService.track({
            event: 'view_item',
            content_type: contentType,
            content_id: contentId
          })
        },
        trackOutboundLink(url: string, linkText?: string) {
          analyticsService.track({
            event: 'click',
            event_category: 'outbound',
            event_label: linkText || url,
            transport_type: 'beacon',
            outbound_url: url
          })
        },
        trackCTAClick(ctaName: string, ctaLocation: string) {
          analyticsService.trackCTAClick(ctaName, ctaLocation)
        },
        trackPlanSelect(planName: string, planPrice: number | null, billingPeriod: string) {
          analyticsService.track({
            event: 'select_item',
            item_name: planName,
            item_price: planPrice,
            billing_period: billingPeriod
          })
        },
        trackSearch(searchTerm: string) {
          analyticsService.track({
            event: 'search',
            search_term: searchTerm
          })
        },
        trackDemoPlay() {
          analyticsService.track({
            event: 'video_start',
            video_title: 'product_demo'
          })
        },
        setUserProperties(userId?: string, properties?: Record<string, any>) {
          if (window.gtag) {
            if (userId) {
              window.gtag('config', gaId, {
                user_id: userId
              })
            }
            if (properties) {
              window.gtag('set', 'user_properties', properties)
            }
          }
        }
      }
    }
  }
})
