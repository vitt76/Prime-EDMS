export function useAbTest(testName: string, variants: string[]) {
  const variant = useCookie(`ab_test_${testName}`)

  if (!variant.value) {
    const randomIndex = Math.floor(Math.random() * variants.length)
    variant.value = variants[randomIndex]
  }

  const trackConversion = (conversionName: string) => {
    const { $analytics } = useNuxtApp()
    $analytics?.trackEvent('ab_test_conversion', {
      test_name: testName,
      variant: variant.value,
      conversion: conversionName
    })
  }

  return {
    variant: readonly(variant),
    trackConversion
  }
}
