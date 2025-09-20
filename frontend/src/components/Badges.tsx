import {
  IconName,
  IconLookup,
  findIconDefinition,
  library,
} from '@fortawesome/fontawesome-svg-core'
import { fab } from '@fortawesome/free-brands-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'

library.add(fas, far, fab)
type BadgeProps = {
  name: string
  cssClass: string
  showTooltip?: boolean
}

const Badges = ({ name, cssClass, showTooltip = true }: BadgeProps) => {
  if (cssClass == null) {
    return (
      <div className="inline-flex items-center">
        {showTooltip ? (
          <Tooltip content={name}>
            <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4" />
          </Tooltip>
        ) : (
          <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4" />
        )}
      </div>
    )
  }
  if (typeof cssClass !== 'string') {
    return (
      <div className="inline-flex items-center">
        {showTooltip ? (
          <Tooltip content={`${name} (icon not found)`} className="bg-gray-800">
            <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4 text-gray-400" />
          </Tooltip>
        ) : (
          <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4 text-gray-400" />
        )}
      </div>
    )
  }

  // Empty string should gracefully fall back to medal without error text
  if (cssClass === '') {
    return (
      <div className="inline-flex items-center">
        {showTooltip ? (
          <Tooltip content={name}>
            <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4" />
          </Tooltip>
        ) : (
          <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4" />
        )}
      </div>
    )
  }

  const trimmed = String(cssClass).trim()
  if (trimmed.length === 0) {
    return (
      <div className="inline-flex items-center">
        {showTooltip ? (
          <Tooltip content={`${name} (icon not found)`} className="bg-gray-800">
            <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4 text-gray-400" />
          </Tooltip>
        ) : (
          <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4 text-gray-400" />
        )}
      </div>
    )
  }

  const tokens = trimmed.split(/\s+/)
  const styleToken = tokens.find((t) => /^fa-(solid|regular|brands)$/i.test(t))
  const stylePrefix: IconLookup['prefix'] =
    styleToken?.toLowerCase() === 'fa-regular'
      ? 'far'
      : styleToken?.toLowerCase() === 'fa-brands'
        ? 'fab'
        : 'fas'

  // Allow either a plain icon token (e.g., "crown") or an fa- prefixed token (e.g., "fa-crown")
  const plainIconToken = tokens
    .slice()
    .reverse()
    .find((t) => /^[a-z0-9-]+$/i.test(t))

  const faIconToken = tokens
    .slice()
    .reverse()
    .find((t) => /^fa-[a-z0-9-]+$/i.test(t) && !/^fa-(solid|regular|brands)$/i.test(t))

  const chosenToken = plainIconToken || faIconToken || 'fa-medal'
  const iconName = chosenToken.replace(/^fa-/, '') as IconName

  // Check if the icon exists in the FA library for the derived style
  const lookup: IconLookup = { prefix: stylePrefix, iconName }
  let iconFound = false
  try {
    findIconDefinition(lookup)
    iconFound = true
  } catch {
    iconFound = false
  }

  if (!iconFound) {
    return (
      <div className="inline-flex items-center">
        {showTooltip ? (
          <Tooltip content={`${name} (icon not found)`} className="bg-gray-800">
            <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4 text-gray-400" />
          </Tooltip>
        ) : (
          <FontAwesomeIcon icon={['fas', 'medal']} className="h-4 w-4 text-gray-400" />
        )}
      </div>
    )
  }

  return (
    <div className="inline-flex items-center">
      {showTooltip ? (
        <Tooltip content={name}>
          <FontAwesomeIcon icon={['fas', iconName]} className="h-4 w-4" />
        </Tooltip>
      ) : (
        <FontAwesomeIcon icon={['fas', iconName]} className="h-4 w-4" />
      )}
    </div>
  )
}

export default Badges
