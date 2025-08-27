import { Tooltip } from '@heroui/tooltip'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Badge as BadgeType } from 'types/badge'

type BadgesProps = {
  badges?: BadgeType[]
  max?: number
  compact?: boolean
  className?: string
}

const BadgeIcon = ({ badge }: { badge: BadgeType }) => {
  const title = badge.description || badge.name
  const cssClass = badge.cssClass || 'fa-solid fa-medal'

  return (
    <Tooltip content={title} placement="top" showArrow delay={100} closeDelay={100}>
      <span className="inline-flex h-4 w-4 items-center justify-center">
        <FontAwesomeIconWrapper icon={cssClass} className="h-4 w-4" />
      </span>
    </Tooltip>
  )
}

const Badges = ({ badges = [], max, compact = false, className = '' }: BadgesProps) => {
  if (!badges || badges.length === 0) return null

  const visibleBadges = typeof max === 'number' ? badges.slice(0, max) : badges
  const hiddenCount = badges.length - visibleBadges.length

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {visibleBadges.map((badge, idx) => (
        <BadgeIcon key={`${badge.name}-${idx}`} badge={badge} />
      ))}
      {hiddenCount > 0 && compact && (
        <span className="text-xs text-gray-500 dark:text-gray-400">+{hiddenCount}</span>
      )}
    </div>
  )
}

export default Badges
