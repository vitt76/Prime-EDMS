export interface AnalyticsEvent {
  event: string
  category?: string
  label?: string
  value?: number
  [key: string]: any
}

export class AnalyticsService {
  private gaId: string | null

  constructor(gaId: string) {
    this.gaId = gaId
  }

  track(event: AnalyticsEvent) {
    if (this.gaId && typeof window !== 'undefined' && (window as any).gtag) {
      ;(window as any).gtag('event', event.event, {
        event_category: event.category,
        event_label: event.label,
        value: event.value,
        ...event
      })
    }

    if (typeof window !== 'undefined') {
      $fetch('/api/v4/public/analytics/events/', {
        method: 'POST',
        body: {
          ...event,
          timestamp: new Date().toISOString(),
          url: window.location.href,
          referrer: document.referrer
        }
      }).catch(() => undefined)
    }
  }

  trackPageView(page: string) {
    this.track({
      event: 'page_view',
      page
    })
  }

  trackCTAClick(buttonText: string, section: string) {
    this.track({
      event: 'cta_click',
      category: 'engagement',
      label: buttonText,
      section
    })
  }

  trackFormSubmit(formType: string, success: boolean) {
    this.track({
      event: 'form_submit',
      category: 'conversion',
      label: formType,
      success
    })
  }

  trackPricingView(plan: string) {
    this.track({
      event: 'pricing_view',
      category: 'intent',
      label: plan
    })
  }
}

export const createAnalyticsService = (gaId: string) => new AnalyticsService(gaId)
