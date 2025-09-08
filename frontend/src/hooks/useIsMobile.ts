import { useEffect, useState } from 'react'

export const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    // Tailwind md breakpoint starts at 768px (min-width:768px),
    // so mobile should be max-width:767px
    const mediaQuery = window.matchMedia('(max-width: 767px)')

    const updateMatch = (e: MediaQueryListEvent | MediaQueryList) => {
      setIsMobile(e.matches)
    }

    updateMatch(mediaQuery)

    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', updateMatch)
      return () => mediaQuery.removeEventListener('change', updateMatch)
    } else {
      // Safari browser < 14 fallback
      mediaQuery.addListener(updateMatch)
      return () => mediaQuery.removeListener(updateMatch)
    }
  }, [])

  return isMobile
}
