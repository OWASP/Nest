import { faStar as faRegularStar } from '@fortawesome/free-regular-svg-icons'
import { faStar as faSolidStar } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'

const StarRepoButton = () => {
  const [isHovered, setIsHovered] = useState(false)
  return (
    <a
      href={'https://github.com/OWASP/Nest'}
      target="_blank"
      className="group relative hidden h-10 w-full cursor-pointer items-center justify-center gap-1 overflow-hidden whitespace-pre rounded-md border border-b bg-[#87a1bc] px-4 py-2 text-sm font-medium text-black transition-all duration-300 ease-out hover:bg-transparent hover:ring-2 hover:ring-[#87a1bc] hover:ring-offset-2 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-slate-900 md:flex"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span className="absolute right-0 -mt-12 h-32 w-8 translate-x-12 rotate-12 bg-white opacity-10 transition-all duration-1000 ease-out group-hover:-translate-x-40"></span>
      <FontAwesomeIcon
        icon={isHovered ? faSolidStar : faRegularStar}
        className={isHovered ? 'text-yellow-400' : 'text-current'}
      />
      <div className="flex items-center">
        <span className="ml-1 text-black dark:text-white">Star</span>
      </div>
      <div className="flex items-center gap-1 text-sm md:flex"></div>
    </a>
  )
}

export default StarRepoButton
