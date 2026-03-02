import { useEffect, useState } from 'react'
import { desktopViewMinWidth } from 'utils/constants'

export const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // Check whether the browser supports matchMedia API.
    if (typeof globalThis.matchMedia !== 'function') return

    const mediaQuery = globalThis.matchMedia(`(max-width: ${desktopViewMinWidth - 1}px)`)

    const handleChange = (e: MediaQueryListEvent | MediaQueryList) => {
      setIsMobile(e.matches)
    }

    handleChange(mediaQuery)

    mediaQuery.addEventListener('change', handleChange)
    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [])

  return isMobile
}
