import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import { useState } from 'react'
import type { NavButtonProps } from 'types/button'
import { cn } from 'utils/utility'

const NavButton = ({
  href,
  defaultIcon,
  hoverIcon,
  defaultIconColor,
  hoverIconColor,
  text,
  className,
}: NavButtonProps) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <Link
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        'group relative flex h-10 w-full cursor-pointer items-center justify-center gap-2 overflow-hidden whitespace-pre rounded-md bg-[#87a1bc] px-4 py-2 text-sm font-medium text-black hover:ring-1 hover:ring-[#b0c7de] hover:ring-offset-0 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-900/90 dark:hover:ring-[#46576b] md:flex',
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <FontAwesomeIcon
        icon={isHovered ? hoverIcon : defaultIcon}
        className={cn({
          'scale-110 text-yellow-400': isHovered,
        })}
        style={{ color: isHovered ? hoverIconColor : defaultIconColor }}
      />
      <span>{text}</span>
    </Link>
  )
}

export default NavButton
