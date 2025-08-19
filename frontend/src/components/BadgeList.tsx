import type { IconName, IconPrefix } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Image from 'next/image'
import React from 'react'
import type { Badge } from 'types/badge'

interface BadgeListProps {
  badges: Badge[]
  className?: string
}

const BadgeList: React.FC<BadgeListProps> = ({ badges, className }) => {
  if (!badges || badges.length === 0) {
    return null
  }

  const renderBadgeIcon = (badge: Badge) => {
    if (badge.cssClass?.startsWith('local:')) {
      const iconName = badge.cssClass.substring('local:'.length)
      return (
        <Image
          src={`/images/icons/${iconName}.svg`}
          alt={badge.name}
          width={16}
          height={16}
          className="h-4 w-4"
        />
      )
    } else if (badge.cssClass) {
      // Assuming Font Awesome classes like "fa-solid fa-star"
      // Normalize FA classnames like "fa-solid fa-star" to tuple ['fas', 'star']
      const classes = badge.cssClass.split(/\s+/).filter(Boolean)
      const styleClass =
        classes.find((c) => ['fa-solid', 'fa-regular', 'fa-brands', 'fas', 'far', 'fab'].includes(c)) ??
        'fa-solid'
      const prefixMap: Record<string, IconPrefix> = {
        'fa-solid': 'fas',
        'fa-regular': 'far',
        'fa-brands': 'fab',
        fas: 'fas',
        far: 'far',
        fab: 'fab',
      }
      const iconClass =
        classes.find(
          (c) =>
            c.startsWith('fa-') &&
            !['fa-solid', 'fa-regular', 'fa-brands'].includes(c) &&
            !['fas', 'far', 'fab'].includes(c),
        ) ?? ''
      const faPrefix = prefixMap[styleClass] ?? 'fas'
      const faIcon = (iconClass.replace(/^fa-/, '') || 'question') as IconName
      return (
        <FontAwesomeIcon
          icon={[faPrefix, faIcon]}
          className="h-4 w-4 text-gray-600 dark:text-gray-300"
        />
      )
    } else if (badge.iconPath) {
      return (
        <Image src={badge.iconPath} alt={badge.name} width={16} height={16} className="h-4 w-4" />
      )
    }
    return null
  }

  return (
    <div className={`flex flex-wrap items-center gap-2 ${className || ''}`}>
      {badges.map((badge, index) => (
        <div
          key={index}
          className="flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1 dark:bg-gray-700"
        >
          {renderBadgeIcon(badge)}
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{badge.name}</span>
        </div>
      ))}
    </div>
  )
}

export default BadgeList
