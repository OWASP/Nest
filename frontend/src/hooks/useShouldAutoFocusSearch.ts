'use client'

import { useEffect, useState } from 'react'

const getAutoFocusValue = (): boolean => {
  if (typeof globalThis.matchMedia !== 'function') {
    return false
  }
  const smallScreen = globalThis.matchMedia('(max-width: 767px)')
  const coarsePointer = globalThis.matchMedia('(pointer: coarse)')
  return !(smallScreen.matches || coarsePointer.matches)
}

export const useShouldAutoFocusSearch = (): boolean => {
  const [shouldAutoFocus, setShouldAutoFocus] = useState(getAutoFocusValue)

  useEffect(() => {
    if (typeof globalThis.matchMedia !== 'function') {
      return
    }

    const smallScreen = globalThis.matchMedia('(max-width: 767px)')
    const coarsePointer = globalThis.matchMedia('(pointer: coarse)')

    const update = () => {
      const isMobileOrTouch = smallScreen.matches || coarsePointer.matches
      setShouldAutoFocus(!isMobileOrTouch)
    }

    smallScreen.addEventListener('change', update)
    coarsePointer.addEventListener('change', update)

    return () => {
      smallScreen.removeEventListener('change', update)
      coarsePointer.removeEventListener('change', update)
    }
  }, [])

  return shouldAutoFocus
}
