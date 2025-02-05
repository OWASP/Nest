import { millify } from 'millify'
import { IconType } from 'types/icon'
import { IconKeys, Icons } from 'utils/data'
import { TooltipRecipe } from 'utils/theme'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { Tooltip } from 'components/ui/tooltip'

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
    item === 'updated_at' || item === 'stars_count' ? 'rotate-container' : '',
    item === 'forks_count' || item === 'contributors_count' ? 'flip-container' : '',
  ]
    .filter(Boolean)
    .join(' ')

  // className for the FontAwesome icon
  const iconClassName = [
    'text-gray-600 dark:text-gray-300',
    item === 'updated_at' || item === 'stars_count' ? 'icon-rotate' : '',
    item === 'forks_count' || item === 'contributors_count' ? 'icon-flip' : '',
  ]
    .filter(Boolean)
    .join(' ')

  return icons[item] ? (
    <Tooltip
      content={`${Icons[item as keyof typeof Icons]?.label}`}
      recipe={TooltipRecipe}
      openDelay={150}
      closeDelay={100}
      showArrow
      positioning={{ placement: 'top' }}
    >
      <div className={containerClassName}>
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
      </div>
    </Tooltip>
  ) : null
}
