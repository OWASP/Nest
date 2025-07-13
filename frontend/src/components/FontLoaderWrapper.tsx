'use client'

import { FC, useState, useEffect, ReactNode } from 'react'
import LoadingSpinner from 'components/LoadingSpinner'

const FontLoaderWrapper: FC<{ children: ReactNode }> = ({ children }) => {
  const [fontsLoaded, setFontsLoaded] = useState(false)
  useEffect(() => {
    document.fonts.ready.then(() => {
      setFontsLoaded(true)
    })
  }, [])
  if (!fontsLoaded) {
    return <LoadingSpinner />
  }
  return <>{children}</>
}

export default FontLoaderWrapper
