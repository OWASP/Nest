import { faMedal } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import type { Badge } from 'types/badge'

interface BadgeCountProps {
  badges: Badge[]
  className?: string
}

const BadgeCount: React.FC<BadgeCountProps> = ({ badges, className }) => {
  if (!badges || badges.length === 0) {
    return null
  }

  return (
    <div className={`flex items-center gap-1 ${className || ''}`}>
      <FontAwesomeIcon icon={faMedal} className="h-4 w-4 text-yellow-500" />
      <span className="text-sm font-medium text-gray-600 dark:text-gray-300">{badges.length}</span>
    </div>
  )
}

export default BadgeCount
