import { Tooltip } from '@heroui/tooltip'
import { millify } from 'millify'
import { IconType } from 'types/icon'
import { IconKeys, Icons } from 'utils/data'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'

export default function DisplayIcon({ item, icons }: { item: string; icons: IconType }) {
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

  const iconClassName = [
    'transition-transform duration-200',
    'hover:scale-110',
    getBrandColorClass(item),
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
      placement="bottom"
    >
      <div className={containerClassName}>
        <span className="text-gray-600 dark:text-gray-300">
          {typeof icons[item] === 'number'
            ? millify(icons[item], { precision: 1 })
            : icons[item]}
        </span>
        <span>
          <FontAwesomeIconWrapper
            className={iconClassName}
            icon={Icons[item as IconKeys]?.icon}
          />
        </span>
      </div>
    </Tooltip>
  ) : null
}

function getBrandColorClass(item: string): string {
  const brandColors: Record<string, string> = {
    discord: 'hover:text-[#5865F2]',
    instagram: 'hover:text-[#E4405F]',
    linkedin: 'hover:text-[#0077B5]',
    youtube: 'hover:text-[#FF0000]',
  }

  return brandColors[item.toLowerCase()] || 'text-gray-600 dark:text-gray-300'
}
