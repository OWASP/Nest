import {
  IconName,
  IconLookup,
  findIconDefinition,
  library,
} from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'

library.add(fas)

type BadgeProps = {
  name: string
  cssClass: string
  showTooltip?: boolean
}

const Badges = ({ name, cssClass, showTooltip = true }: BadgeProps) => {
  const safeCssClass = (cssClass ?? 'fa-medal') as string
  // Remove one or more 'fa-' prefixes, normalize underscores to dashes
  const iconName = String(safeCssClass)
    .trim()
    .replace(/^(?:fa-)+/, '')
    .replace(/_/g, '-') as IconName

  // Check if the icon exists in the FA library
  const lookup: IconLookup = { prefix: 'fas', iconName }
  let iconFound = false
  try {
    findIconDefinition(lookup)
    iconFound = true
  } catch {
    iconFound = false
  }

  if (!iconFound) {
    // Fallback to a default icon if the specified icon doesn't exist
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
