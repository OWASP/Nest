import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'

interface TitleWithIconProps {
  href: string
  icon: IconProp
  title: string
}

const TitleWithIcon: React.FC<TitleWithIconProps> = ({ href, icon, title }) => {
  const id = href.replace('#', '')

  const handleClick = (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => {
    const element = document.getElementById(id)
    if (element) {
      event.preventDefault()
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <div id={id} className="relative scroll-mt-20">
      <div className="items-top group relative flex">
        <h2 className="mb-4 text-2xl font-semibold">{title}</h2>
        <a
          href={href}
          className="inherit-color ml-2 opacity-0 transition-opacity duration-200 group-hover:opacity-100"
          onClick={handleClick}
        >
          <FontAwesomeIcon icon={icon} className="h-7 w-5" />
        </a>
      </div>
    </div>
  )
}

export default TitleWithIcon
