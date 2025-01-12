import { millify } from 'millify'
import { Tooltip } from 'react-tooltip'
import { IconType, tooltipStyle } from 'lib/constants'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { IconKeys, Icons } from './data'

export default function DisplayIcon({
  item,
  icons,
  idx,
}: {
  item: string
  icons: IconType
  idx: number
}) {
  // className for the container
  const containerClassName = [
    'flex flex-col items-center justify-center gap-1 border-b border-l border-t border-border px-4 pb-1 sm:border-t-0',
    idx === 0 || (idx === -1 && Object.keys(icons).length === 1)
      ? 'rounded-bl-none sm:rounded-bl-md'
      : '',
    idx === -1 ? 'border-r sm:border-r-0' : '',
    item === 'idx_updated_at' || item === 'idx_stars_count' ? 'rotate-container' : '',
    item === 'idx_forks_count' || item === 'idx_contributors_count' ? 'flip-container' : '',
  ]
    .filter(Boolean)
    .join(' ')

  // className for the FontAwesome icon
  const iconClassName = [
    'text-gray-600 dark:text-gray-300',
    item === 'idx_updated_at' || item === 'idx_stars_count' ? 'icon-rotate' : '',
    item === 'idx_forks_count' || item === 'idx_contributors_count' ? 'icon-flip' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return icons[item] ? (
    <div
      data-tooltip-id={`icon-tooltip-${item}`}
      data-tooltip-content={`${Icons[item as keyof typeof Icons]?.label}`}
      className={containerClassName}
    >
      {/* Display formatted number if the value is a number */}
      <span className="text-gray-600 dark:text-gray-300">
        {typeof icons[item] === 'number'
          ? millify(icons[item], { precision: 1 }) // Format large numbers using 'millify' library
          : icons[item]}
      </span>
      <span>
        <FontAwesomeIconWrapper
          className={iconClassName}
          icon={Icons[item as IconKeys]?.icon} // Display corresponding icon
        />
      </span>
      {/* Tooltip for showing more info when hovering */}
      <Tooltip id={`icon-tooltip-${item}`} style={tooltipStyle} />
    </div>
  ) : null
}
