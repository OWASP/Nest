import { Tooltip } from '@heroui/tooltip'
import { IconWrapper } from 'wrappers/IconWrapper'
import { BADGE_CLASS_MAP } from 'utils/data'

type BadgeProps = {
  name: string
  cssClass: string | undefined
  showTooltip?: boolean
}

const DEFAULT_ICON = BADGE_CLASS_MAP['medal']

const normalizeCssClass = (cssClass: string | undefined) => {
  if (!cssClass || cssClass.trim() === '') {
    return ''
  }
  // Convert backend snake_case format to frontend camelCase format
  return cssClass.trim().replaceAll(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

const resolveIcon = (cssClass: string | undefined) => {
  const normalizedClass = normalizeCssClass(cssClass)
  return BADGE_CLASS_MAP[normalizedClass] ?? DEFAULT_ICON
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
