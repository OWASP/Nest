import { millify } from 'millify'
import { IconType } from 'types/icon'
import { IconKeys, Icons } from 'utils/data'
import { TooltipRecipe } from 'utils/theme'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { Tooltip } from 'components/ui/tooltip'
import { useState } from 'react'

export default function DisplayIcon({ item, icons }: { item: string; icons: IconType }) {
  const [hovered, setHovered] = useState(false)

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

  const iconClassName = `transition-colors duration-200 ${
    hovered ? Icons[item as IconKeys]?.colorClass || 'text-gray-600' : 'text-gray-600 dark:text-gray-300'
  }`

  return icons[item] ? (
    <Tooltip
      content={`${Icons[item as keyof typeof Icons]?.label}`}
      recipe={TooltipRecipe}
      openDelay={150}
      closeDelay={100}
      showArrow
      positioning={{ placement: 'bottom' }}
    >
      <div
        className={containerClassName}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <span className="text-gray-600 dark:text-gray-300">
          {typeof icons[item] === 'number' ? millify(icons[item], { precision: 1 }) : icons[item]}
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
