'use client'

import { faArrowUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState, useEffect, useCallback } from 'react'

export default function ScrollToTop() {
  const [isVisible, setIsVisible] = useState(false)

  const handleScroll = useCallback(() => {
    const scrollThreshold = window.innerHeight * 0.3
    setIsVisible(window.scrollY > scrollThreshold)
  }, [])

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  useEffect(() => {
    let scrollTimeout: ReturnType<typeof setTimeout> | null = null
    const throttledScroll = () => {
      if (!scrollTimeout) {
        scrollTimeout = setTimeout(() => {
          handleScroll()
          scrollTimeout = null
        }, 100)
      }
    }

    window.addEventListener('scroll', throttledScroll)
    return () => window.removeEventListener('scroll', throttledScroll)
  }, [handleScroll])

  return (
    <button
      type="button"
      onClick={scrollToTop}
      aria-label="Scroll to top of page"
      aria-hidden={!isVisible}
      tabIndex={isVisible ? 0 : -1}
      className={`bg-owasp-blue/70 hover:bg-owasp-blue dark:bg-owasp-blue/30 hover:dark:bg-owasp-blue/50 fixed right-4 bottom-4 z-50 flex h-11 w-11 items-center justify-center rounded-full text-white shadow-lg transition-all duration-400 hover:scale-105 active:scale-100 dark:text-slate-300 ${isVisible ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'} `}
    >
      <FontAwesomeIcon icon={faArrowUp} className="text-xl" aria-hidden="true" />
    </button>
  )
}
