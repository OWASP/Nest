import { millify } from 'millify'
import { IconType } from 'types/icon'
import { IconKeys, Icons } from 'utils/data'
import { TooltipRecipe } from 'utils/theme'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { Tooltip } from 'components/ui/tooltip'

export default function DisplayIcon({ item, icons }: { item: string; icons: IconType }) {

  const brandColors: Record<string, string> = {
    discord: 'text-[#7289DA] hover:text-[#5b6eae]',
    instagram: 'text-[#E4405F] hover:text-[#c13548]',
    linkedin: 'text-[#0077B5] hover:text-[#005582]',
    youtube: 'text-[#FF0000] hover:text-[#cc0000]',
  }

  const isSocialMedia = Object.keys(brandColors).includes(item.toLowerCase())


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
    isSocialMedia ? brandColors[item.toLowerCase()] : 'text-gray-600 dark:text-gray-300',
    'transition-transform transform hover:scale-110',
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
