'use client'

import { usePathname } from 'next/navigation'
import { JSX, useEffect } from 'react'

export default function AutoScrollToTop(): JSX.Element | null {
  const pathname = usePathname()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  return null
}
