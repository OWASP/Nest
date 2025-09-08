import { useEffect, useState } from 'react'
import { desktopViewMinWidth } from 'utils/constants'

export const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {

    // check whether the browser supports matchMedia API
    if (typeof window.matchMedia !== 'function') return
    
    const mediaQuery = window.matchMedia(`(max-width: ${desktopViewMinWidth - 1}px)`)

    const updateMatch = (e: MediaQueryListEvent | MediaQueryList) => {
      setIsMobile(e.matches)
    }

    updateMatch(mediaQuery)

    if (typeof mediaQuery.addEventListener === 'function') { // check for modern browser so it doesn't throw an error
      mediaQuery.addEventListener('change', updateMatch)
      return () => mediaQuery.removeEventListener('change', updateMatch)
    } else if(typeof mediaQuery.addListener === 'function') { // check for old browser
      mediaQuery.addListener(updateMatch)
      return () => mediaQuery.removeListener(updateMatch)
    } else return;
  }, [])

  return isMobile
}
