import { faLink } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React, { useEffect, useCallback } from 'react'
import slugify from 'utils/slugify'

interface AnchorTitleProps {
  className?: string
  title: string
}

const AnchorTitle: React.FC<AnchorTitleProps> = ({ title }) => {
  const id = slugify(title)
  const href = `#${id}`

  const scrollToElement = useCallback(() => {
    const element = document.getElementById(id)
    if (element) {
      const headingHeight =
        (element.querySelector('div#anchor-title') as HTMLElement)?.offsetHeight || 0
      const yOffset = -headingHeight - 50
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset
      window.scrollTo({ top: y, behavior: 'smooth' })
    }
  }, [id])

  const handleClick = (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
    event.preventDefault()
    scrollToElement()
    window.history.pushState(null, '', href)
  }

  useEffect(() => {
    const hash = window.location.hash.replace('#', '')
    if (hash === id) {
      requestAnimationFrame(() => scrollToElement())
    }
  }, [id, scrollToElement])

  useEffect(() => {
    const handlePopState = () => {
      const hash = window.location.hash.replace('#', '')
      if (hash === id) {
        requestAnimationFrame(() => scrollToElement())
      }
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [id, scrollToElement])

  return (
    <div id={id} className="relative">
      <div className="group relative flex items-center">
        <div className="flex items-center text-2xl font-semibold" id="anchor-title">
          {title}
        </div>
        <a
          href={href}
          className="inherit-color ml-2 opacity-0 transition-opacity duration-200 group-hover:opacity-100"
          onClick={handleClick}
        >
          <FontAwesomeIcon icon={faLink} className="custom-icon h-7 w-5" />
        </a>
      </div>
    </div>
  )
}

export default AnchorTitle
