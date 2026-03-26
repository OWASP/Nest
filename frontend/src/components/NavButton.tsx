import Link from 'next/link'
import { useState } from 'react'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
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
}: NavButtonProps & { defaultIcon: IconType; hoverIcon: IconType }) => {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <Link
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
      'group relative flex h-10 cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-md border border-gray-300 bg-white px-4 text-sm font-medium text-gray-800 transition-all duration-200 hover:bg-gray-100 hover:border-gray-400 hover:shadow-sm focus-visible:ring-1 focus-visible:ring-blue-500 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 md:flex dark:border-slate-700 dark:bg-slate-900 dark:text-white dark:hover:bg-slate-800 dark:hover:border-slate-500 dark:hover:shadow-md dark:hover:shadow-blue-500/20',
      className
    )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <IconWrapper
        icon={isHovered ? hoverIcon : defaultIcon}
        className={cn({
          'scale-110 text-yellow-400': isHovered,
        })}
        style={{ color: isHovered ? hoverIconColor : defaultIconColor }}
      />
      <span className="relative inline-block after:absolute after:left-0 after:bottom-0 after:h-[.9px] after:w-0 after:bg-gray-800 after:transition-all after:duration-300 group-hover:after:w-full dark:after:bg-white">
        {text}
      </span>
    </Link>
  )
}

export default NavButton
