import { Tooltip } from '@heroui/tooltip'
import { IconWrapper } from 'wrappers/IconWrapper'
import { BADGE_CLASS_MAP } from 'utils/data'

type BadgeProps = {
  name: string
  cssClass: string | undefined
  showTooltip?: boolean
}

const DEFAULT_ICON = BADGE_CLASS_MAP['medal']

const resolveIcon = (cssClass: string | undefined) => {
  if (!cssClass) {
    return DEFAULT_ICON
  }

  return BADGE_CLASS_MAP[cssClass] ?? DEFAULT_ICON
}

const Badges = ({ name, cssClass, showTooltip = true }: BadgeProps) => {
  const icon = resolveIcon(cssClass)

  return (
    <div className="inline-flex items-center">
      <Tooltip content={name} isDisabled={!showTooltip}>
        <IconWrapper icon={icon} className="h-4 w-4" />
      </Tooltip>
    </div>
  )
}

export default Badges
