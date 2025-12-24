import type React from 'react'
import type { IconType } from 'react-icons'
import { FaArchive, FaBan } from 'react-icons/fa'

export type StatusType = 'archived' | 'inactive'

interface StatusConfig {
  text: string
  icon: IconType
  bgColor: string
  textColor: string
  borderColor: string
  darkBgColor: string
  darkTextColor: string
  darkBorderColor: string
  tooltip: string
  ariaLabel: string
}

interface StatusBadgeProps {
  status: StatusType
  className?: string
  showIcon?: boolean
  size?: 'sm' | 'md' | 'lg'
  customText?: string
  customIcon?: IconType
  customTooltip?: string
}

const statusConfig: Record<StatusType, StatusConfig> = {
  archived: {
    text: 'Archived',
    icon: FaArchive,
    bgColor: 'bg-yellow-50',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-600',
    darkBgColor: 'dark:bg-yellow-900/30',
    darkTextColor: 'dark:text-yellow-400',
    darkBorderColor: 'dark:border-yellow-500',
    tooltip: 'This entity has been archived and is read-only',
    ariaLabel: 'This entity has been archived and is read-only',
  },
  inactive: {
    text: 'Inactive',
    icon: FaBan,
    bgColor: 'bg-red-50',
    textColor: 'text-red-800',
    borderColor: 'border-red-600',
    darkBgColor: 'dark:bg-red-900/30',
    darkTextColor: 'dark:text-red-400',
    darkBorderColor: 'dark:border-red-500',
    tooltip: 'This entity is currently inactive',
    ariaLabel: 'This entity is currently inactive',
  },
}

const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  className = '',
  showIcon = true,
  size = 'md',
  customText,
  customIcon,
  customTooltip,
}) => {
  const config = statusConfig[status]
  const displayText = customText ?? config.text
  const DisplayIcon = customIcon ?? config.icon
  const displayTooltip = customTooltip ?? config.tooltip

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'text-sm px-3 py-1',
    lg: 'px-4 py-2 text-base',
  }

  return (
    <span
      className={`${sizeClasses[size]} ${className} inline-flex items-center gap-1.5 rounded-full border ${config.borderColor} ${config.bgColor} ${config.textColor} ${config.darkBorderColor} ${config.darkBgColor} ${config.darkTextColor} font-medium`}
      title={displayTooltip}
      aria-label={config.ariaLabel}
    >
      {showIcon && <DisplayIcon className="h-3 w-3" />}
      {displayText}
    </span>
  )
}

export default StatusBadge
