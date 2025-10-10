import { faArchive } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import type React from 'react'

interface ArchivedBadgeProps {
  className?: string
  showIcon?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const ArchivedBadge: React.FC<ArchivedBadgeProps> = ({
  className = '',
  showIcon = true,
  size = 'md',
}) => {
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'text-sm px-3 py-1',
    lg: 'px-4 py-2 text-base',
  }

  return (
    <span
      className={` ${sizeClasses[size]} ${className} inline-flex items-center gap-1.5 rounded-full border border-yellow-600 bg-yellow-50 font-medium text-yellow-800 dark:border-yellow-500 dark:bg-yellow-900/30 dark:text-yellow-400   `}
      title="This repository has been archived and is read-only"
    >
      {showIcon && <FontAwesomeIcon icon={faArchive} className="h-3 w-3" />}
      Archived
    </span>
  )
}

export default ArchivedBadge
