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
      onClick={scrollToTop}
      aria-label="Scroll to top"
      className={`duration-400 fixed bottom-4 right-4 z-50 flex h-11 w-11 items-center justify-center rounded-full bg-owasp-blue bg-opacity-70 text-white shadow-lg transition-all hover:scale-105 hover:bg-opacity-100 active:scale-100 dark:bg-opacity-30 dark:text-slate-300 hover:dark:bg-opacity-50 ${isVisible ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'} `}
    >
      <FontAwesomeIcon icon={faArrowUp} className="text-xl" />
    </button>
  )
}
