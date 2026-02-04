/**
 * Type declarations for the analytics plugin
 */

export interface AnalyticsPlugin {
  trackEvent(eventName: string, eventParams?: Record<string, any>): void
  trackPageView(page: string): void
  trackButtonClick(buttonName: string, location?: string): void
  trackFormSubmit(formName: string, success: boolean): void
  trackSignup(method?: string): void
  trackLogin(method?: string): void
  trackContentView(contentType: string, contentId: string): void
  trackOutboundLink(url: string, linkText?: string): void
  trackCTAClick(ctaName: string, ctaLocation: string): void
  trackPlanSelect(planName: string, planPrice: number | null, billingPeriod: string): void
  trackSearch(searchTerm: string): void
  trackDemoPlay(): void
  setUserProperties(userId?: string, properties?: Record<string, any>): void
}

declare module '#app' {
  interface NuxtApp {
    $analytics: AnalyticsPlugin
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $analytics: AnalyticsPlugin
  }
}

export {}
