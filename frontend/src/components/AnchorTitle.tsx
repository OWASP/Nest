import { faLink } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'

interface AnchorTitleProps {
  href: string
  title: string
}

const AnchorTitle: React.FC<AnchorTitleProps> = ({ href, title }) => {
  const id = href.replace('#', '')

  const handleClick = (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
    const element = document.getElementById(id)
    if (element) {
      event.preventDefault()
      const headingHeight = element.querySelector('h2')?.offsetHeight || 0
      const yOffset = -headingHeight - 50
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset
      window.scrollTo({ top: y, behavior: 'smooth' })
    }
  }

  return (
    <div id={id} className="relative">
      <div className="items-top group relative flex">
        <h2 className="mb-4 text-2xl font-semibold">{title}</h2>
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
