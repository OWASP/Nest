// import { faHeart } from '@fortawesome/free-regular-svg-icons'
import { faHeart as faRegularHeart } from '@fortawesome/free-regular-svg-icons' // Outline Heart
import { faHeart as faSolidHeart } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'

const SponsorButton = () => {
  const [isHovered, setIsHovered] = useState(false)
  return (
    <a
      href={'https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest'}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex items-center space-x-2 divide-solid rounded-md border-2 border-solid bg-[#8faac6] px-4 py-2 font-medium text-[#253247] shadow-[0_1px_1px_-1px_rgba(0,0,0,0.05)] transition-all duration-300 hover:bg-[#98AFC7] hover:shadow-[0_1px_1px_-1px_rgba(0,0,0,0.05),0_1px_1px_0_rgba(0,0,0,0.1)] dark:bg-[#2D3B4F] dark:text-[#98AFC7] dark:shadow-[0_1px_1px_-1px_rgba(255,255,255,0.05)] dark:hover:bg-[#2D3B4F] dark:hover:shadow-[0_1px_1px_-1px_rgba(255,255,255,0.05),0px_1px_1px_0px_rgba(255,255,255,0.05)]"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <FontAwesomeIcon
        icon={isHovered ? faSolidHeart : faRegularHeart}
        className="heart-icon"
        color={isHovered ? '#d9156c' : '#b55f95'}
      />
      <span>Sponsor</span>
    </a>
  )
}

export default SponsorButton
