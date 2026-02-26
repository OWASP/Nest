'use client'

import { usePathname } from 'next/navigation'
import { useEffect } from 'react'

export default function AutoScrollToTop() {
  const pathname = usePathname()

  useEffect(() => {
    // window.scrollTo(0, 0)
    if ('scrollRestoration' in history) {
      history.scrollRestoration = 'auto'
    }
  }, [pathname])

  return null
}
