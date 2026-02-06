declare global {
  interface Window {
    $crisp: any[]
    CRISP_WEBSITE_ID: string
  }
}

export default defineNuxtPlugin(() => {
  if (process.client) {
    window.$crisp = []
    window.CRISP_WEBSITE_ID = 'YOUR_CRISP_WEBSITE_ID'

    const script = document.createElement('script')
    script.src = 'https://client.crisp.chat/l.js'
    script.async = true
    document.head.appendChild(script)
  }
})
