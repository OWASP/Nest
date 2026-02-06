import { Tooltip } from '@heroui/tooltip'
import { millify } from 'millify'
import { IconWrapper } from 'wrappers/IconWrapper'
import type { Icon } from 'types/icon'
import { IconKeys, ICONS } from 'utils/data'

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

  // className for the icon
  const iconClassName = [
    'text-gray-800 dark:text-gray-300',
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
      content={`${ICONS[item as IconKeys]?.label}`}
      delay={150}
      closeDelay={100}
      showArrow
      placement="top"
    >
      <div className={containerClassName}>
        {/* Display formatted number if the value is a number */}
        <span className="text-gray-800 dark:text-gray-300">
          {typeof icons[item] === 'number' ? millify(icons[item], { precision: 1 }) : icons[item]}
        </span>
        <span>
          <IconWrapper className={iconClassName} icon={ICONS[item as IconKeys]?.icon} />
        </span>
      </div>
    </Tooltip>
  ) : null
}
