import { Tooltip } from '@heroui/tooltip'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { BADGE_CLASS_MAP } from 'utils/data'

const BADGE_SIZE = 16
const DEFAULT_ICON = BADGE_CLASS_MAP['medal']

type BadgeProps = {
  name: string
  cssClass: string | undefined
  showTooltip?: boolean
}

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
        <div
          className="flex items-center justify-center"
          style={{ width: BADGE_SIZE, height: BADGE_SIZE }}
        >
          <FontAwesomeIconWrapper
            icon={icon}
            data-testid="badge-icon"
            style={{ width: BADGE_SIZE, height: BADGE_SIZE }}
            fixedWidth
          />
        </div>
      </Tooltip>
    </div>
  )
}

export default Badges
