import { IconName, library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'

library.add(fas)

type BadgeProps = {
  name: string
  weight: number
  description: string
  cssClass: string
  showTooltip?: boolean
}

const Badges = ({ name, cssClass, showTooltip = true }: BadgeProps) => {
  // Extract icon name from cssClass (remove 'fa-' prefix)
  // Handle edge cases where cssClass might be null, undefined, or not a string
  const safeCssClass = cssClass || 'fa-medal'
  const iconName = String(safeCssClass).replace(/^fa-/, '') as IconName

  // Check if the icon exists in FontAwesome
  const iconExists = fas[iconName]

  if (!iconExists) {
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
