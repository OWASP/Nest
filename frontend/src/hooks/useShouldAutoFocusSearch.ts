'use client'

import { useEffect, useState } from 'react'

export const useShouldAutoFocusSearch = (): boolean => {
  const [shouldAutoFocus, setShouldAutoFocus] = useState(false)

  useEffect(() => {
    if (typeof globalThis.matchMedia !== 'function') {
      setShouldAutoFocus(false)
      return
    }

    const smallScreen = globalThis.matchMedia('(max-width: 767px)')
    const coarsePointer = globalThis.matchMedia('(pointer: coarse)')

    const update = () => {
      const isMobileOrTouch = smallScreen.matches || coarsePointer.matches
      setShouldAutoFocus(!isMobileOrTouch)
    }

    update()
    smallScreen.addEventListener('change', update)
    coarsePointer.addEventListener('change', update)

    return () => {
      smallScreen.removeEventListener('change', update)
      coarsePointer.removeEventListener('change', update)
    }
  }, [])

  return shouldAutoFocus
}