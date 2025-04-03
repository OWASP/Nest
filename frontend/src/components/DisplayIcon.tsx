import { useState } from 'react'
import { millify } from 'millify'
import { IconType } from 'types/icon'
import { IconKeys, Icons } from 'utils/data'
import { TooltipRecipe } from 'utils/theme'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { Tooltip } from 'components/ui/tooltip'

export default function DisplayIcon({ item, icons }: { item: string; icons: IconType }) {
  const [hovered, setHovered] = useState(false)
  const [isTooltipOpen, setIsTooltipOpen] = useState(false)

  const socialMediaIcons: IconKeys[] = ['linkedin', 'youtube', 'twitter', 'github']
  const isSocialMediaIcon = socialMediaIcons.includes(item as IconKeys)

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

  return icons[item] ? (
    <Tooltip
      content={`${Icons[item as keyof typeof Icons]?.label}`}
      recipe={TooltipRecipe}
      openDelay={150}
      closeDelay={100}
      showArrow
      positioning={{ placement: 'bottom' }}
      isOpen={isTooltipOpen}
      onOpenChange={setIsTooltipOpen}
    >
      <div
        className={containerClassName}
        onMouseEnter={() => {
          if (isSocialMediaIcon) setHovered(true);
          setIsTooltipOpen(true);
        }}
        onMouseLeave={() => {
          if (isSocialMediaIcon) setHovered(false);
          setIsTooltipOpen(false);
        }}
      >
        {/* Display formatted number if the value is a number */}
        <span className="text-gray-600 dark:text-gray-300">
          {typeof icons[item] === 'number'
            ? millify(icons[item], { precision: 1 })
            : icons[item]}
        </span>
        <span>
          <FontAwesomeIconWrapper
            className={`${
              isSocialMediaIcon
                ? hovered
                  ? Icons[item as IconKeys]?.color || 'text-gray-600'
                  : 'text-gray-400 dark:text-gray-500'
                : 'text-gray-600 dark:text-gray-300'
            } transition-colors duration-300`}
            icon={Icons[item as IconKeys]?.icon}
          />
        </span>
      </div>
    </Tooltip>
  ) : null
}
