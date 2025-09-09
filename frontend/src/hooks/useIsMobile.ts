import { useEffect, useState } from 'react'
import { desktopViewMinWidth } from 'utils/constants'

export const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // check whether the browser supports matchMedia API
    if (typeof window.matchMedia !== 'function') return

    const mediaQuery = window.matchMedia(`(max-width: ${desktopViewMinWidth - 1}px)`)

    const handleChange = (e: MediaQueryListEvent | MediaQueryList) => {
      setIsMobile(e.matches)
    }

    handleChange(mediaQuery)

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    } else {
      // Safari browser < 14 fallback
      mediaQuery.addListener(handleChange)
      return () => mediaQuery.removeListener(handleChange)
    }
  }, [])

  return isMobile
}
