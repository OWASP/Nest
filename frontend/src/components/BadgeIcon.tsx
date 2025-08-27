import { Tooltip } from '@heroui/tooltip'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Badge } from 'types/badge'

interface BadgeIconProps {
  badge: Badge
  className?: string
}

const BadgeIcon: React.FC<BadgeIconProps> = ({ badge, className = '' }) => {
  const cssClass = badge.cssClass || 'fa-solid fa-medal' // Default to medal icon if no cssClass

  return (
    <Tooltip content={badge.name} placement="top" showArrow delay={100} closeDelay={100}>
      <span
        className={`inline-flex h-5 w-5 items-center justify-center text-gray-600 hover:text-gray-800 dark:text-gray-300 dark:hover:text-gray-100 ${className}`}
      >
        <FontAwesomeIconWrapper icon={cssClass} className="h-4 w-4" />
      </span>
    </Tooltip>
  )
}

export default BadgeIcon
