declare global {
  interface Window {
    $crisp: any[]
    CRISP_WEBSITE_ID: string
  }
}

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const crispId = (config.public as Record<string, any>).crispId

  // Only load Crisp when a real website ID is configured
  if (!crispId || crispId === 'YOUR_CRISP_WEBSITE_ID') {
    return
  }

  window.$crisp = []
  window.CRISP_WEBSITE_ID = crispId

  const script = document.createElement('script')
  script.src = 'https://client.crisp.chat/l.js'
  script.async = true
  document.head.appendChild(script)
})
