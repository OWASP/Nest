import { findIconDefinition } from '@fortawesome/fontawesome-svg-core'
import { Tooltip } from '@heroui/tooltip'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { BADGE_CLASS_MAP } from 'utils/data'

type BadgeProps = {
  name: string
  cssClass: string
  showTooltip?: boolean
}

const DEFAULT = BADGE_CLASS_MAP['medal']

const Badges = ({ name, cssClass, showTooltip = true }: BadgeProps) => {
  const cls = typeof cssClass === 'string' ? BADGE_CLASS_MAP[cssClass] : undefined
  const icon = cls ?? DEFAULT
  const iconName = icon.split(' ').pop()?.replace('fa-', '') || 'medal'
  const def = findIconDefinition({ prefix: 'fas', iconName: iconName as any })
  const iconClass = def ? icon : DEFAULT

  return (
    <div className="inline-flex items-center">
      <Tooltip content={name} isDisabled={!showTooltip}>
        <FontAwesomeIconWrapper icon={iconClass} className="h-4 w-4" />
      </Tooltip>
    </div>
  )
}

export default Badges
