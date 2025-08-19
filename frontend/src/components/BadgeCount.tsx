import { faMedal } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import React from 'react'
import type { Badge } from 'types/badge'
import Badges from 'components/Badges'

interface BadgeCountProps {
  badges: Badge[]
  className?: string
}

const BadgeCount: React.FC<BadgeCountProps> = ({ badges, className }) => {
  if (!badges || badges.length === 0) {
    return null
  }

  return (
    <Tooltip
      content={<Badges badges={badges} />}
      delay={150}
      closeDelay={100}
      showArrow
      placement="top"
    >
      <div className={`flex cursor-pointer items-center gap-1 ${className || ''}`}>
        <FontAwesomeIcon icon={faMedal} className="h-4 w-4 text-yellow-500" />
        <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
          {badges.length}
        </span>
      </div>
    </Tooltip>
  )
}

export default BadgeCount
