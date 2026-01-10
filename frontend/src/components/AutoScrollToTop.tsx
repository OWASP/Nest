'use client'

import { usePathname } from 'next/navigation'
import { FC, useEffect } from 'react'

const AutoScrollToTop: FC = () => {
  const pathname = usePathname()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  return null
}

export default AutoScrollToTop
