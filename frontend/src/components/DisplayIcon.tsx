import { memo } from 'react'
import { millify } from 'millify'
import { IconType } from 'types/icon'
import { IconKeys, Icons } from 'utils/data'
import { TooltipRecipe } from 'utils/theme'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { Tooltip } from 'components/ui/tooltip'

type DisplayIconProps = {
  item: string
  icons: IconType
}

const DisplayIcon: React.FC<DisplayIconProps> = memo(({ item, icons }) => {
  if (!icons[item]) return null

  const isRotating = item === 'stars_count' || item === 'starsCount'
  const isFlipping =
    ['forks_count', 'contributors_count', 'forksCount', 'contributionCount'].includes(item)

  // ClassNames
  const containerClassName = [
    'flex flex-row-reverse items-center justify-center gap-1 px-4 pb-1 -ml-2',
    isRotating ? 'rotate-container' : '',
    isFlipping ? 'flip-container' : '',
  ]
    .filter(Boolean)
    .join(' ')

  const iconClassName = [
    'text-gray-600 dark:text-gray-300',
    isRotating ? 'icon-rotate' : '',
    isFlipping ? 'icon-flip' : '',
  ]
    .filter(Boolean)
    .join(' ')

  const formattedValue =
    typeof icons[item] === 'number' ? millify(icons[item], { precision: 1 }) : icons[item]

  return (
    <Tooltip
    content={`${Icons[item as keyof typeof Icons]?.label}`}
    recipe={TooltipRecipe}
    openDelay={150}
    closeDelay={100}
    showArrow
    positioning={{ placement: 'top' }}
  >
      <div className={containerClassName}>
        <span className="text-gray-600 dark:text-gray-300">{formattedValue}</span>
        <FontAwesomeIconWrapper className={iconClassName} icon={Icons[item as IconKeys]?.icon} />
      </div>
     </Tooltip>
  ) : null
}
