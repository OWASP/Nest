import React, { useEffect, useCallback } from 'react'
import { FaLink } from 'react-icons/fa6'
import { scrollToAnchor, scrollToAnchorWithHistory } from 'utils/scrollToAnchor'
import slugify from 'utils/slugify'

interface AnchorTitleProps {
  title: string
}

const AnchorTitle: React.FC<AnchorTitleProps> = ({ title }) => {
  const id = slugify(title)
  const href = `#${id}`

  const scrollToElement = useCallback(() => {
    scrollToAnchor(id)
  }, [id])

  const handleClick = (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
    event.preventDefault()
    scrollToAnchorWithHistory(id)
  }

  useEffect(() => {
    const hash = globalThis.location.hash.replace('#', '')
    if (hash === id) {
      requestAnimationFrame(() => scrollToElement())
    }
  }, [id, scrollToElement])

  useEffect(() => {
    const handlePopState = () => {
      const hash = globalThis.location.hash.replace('#', '')
      if (hash === id) {
        requestAnimationFrame(() => scrollToElement())
      }
    }
    globalThis.addEventListener('popstate', handlePopState)
    return () => globalThis.removeEventListener('popstate', handlePopState)
  }, [id, scrollToElement])

  return (
    <div id={id} className="relative">
      <div className="group relative flex items-center">
        <div className="flex items-center text-2xl font-semibold" data-anchor-title="true">
          {title}
        </div>
        <a
          href={href}
          className="inherit-color ml-2 opacity-0 transition-opacity duration-200 group-hover:opacity-100"
          onClick={handleClick}
          aria-label={`Link to ${title} section`}
        >
          <FaLink className="custom-icon h-7 w-5" />
        </a>
      </div>
    </div>
  )
}

export default AnchorTitle
