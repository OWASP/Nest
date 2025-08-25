import { Tooltip } from '@heroui/tooltip'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Badge as BadgeType } from 'types/badge'
import Badges from 'components/Badges'

type BadgesTooltipProps = {
  badges?: BadgeType[]
  className?: string
}

const BadgesTooltip = ({ badges = [], className = '' }: BadgesTooltipProps) => {
  if (!badges || badges.length === 0) return null

  return (
    <Tooltip
      content={<Badges badges={badges} max={6} compact />}
      placement="top"
      showArrow
      delay={100}
      closeDelay={100}
    >
      <span className={`inline-flex h-6 w-6 items-center justify-center ${className}`}>
        <FontAwesomeIconWrapper icon="fa-solid fa-award" className="h-4 w-4 text-gray-500" />
      </span>
    </Tooltip>
  )
}

export default BadgesTooltip
