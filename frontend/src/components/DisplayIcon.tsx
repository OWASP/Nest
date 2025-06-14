import { Tooltip } from '@heroui/tooltip'
import { millify } from 'millify'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Icon } from 'types/icon'
import { IconKeys, Icons } from 'utils/data'

export default function DisplayIcon({ item, icons }: { item: string; icons: Icon }) {
  // className for the container
  const containerClassName = [
    'flex flex-row-reverse items-center justify-center gap-1 px-4 pb-1 -ml-2',
    item === 'stars_count' || item === 'starsCount' ? 'rotate-container' : '',
    item === 'forks_count' ||
    item === 'contributors_count' ||
    item === 'forksCount' ||
    item === 'contributionCount'
      ? 'flip-container'
      : '',
  ]
    .filter(Boolean)
    .join(' ')

  // className for the FontAwesome icon
  const iconClassName = [
    'text-gray-600 dark:text-gray-300',
    item === 'stars_count' || item === 'starsCount' ? 'icon-rotate' : '',
    item === 'forks_count' ||
    item === 'contributors_count' ||
    item === 'forksCount' ||
    item === 'contributionCount'
      ? 'icon-flip'
      : '',
  ]
    .filter(Boolean)
    .join(' ')

  return icons[item] ? (
    <Tooltip
      content={`${Icons[item as keyof typeof Icons]?.label}`}
      delay={150}
      closeDelay={100}
      showArrow
      placement="top"
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
