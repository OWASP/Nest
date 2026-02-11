import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import millify from 'millify'
import Image from 'next/image'
import { FaChevronRight, FaFolderOpen, FaMedal, FaUser } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import type { UserCardProps } from 'types/card'
import { useCardState } from 'hooks/useCardState'

const UserCard = ({
  avatar,
  badgeCount,
  button,
  className,
  company,
  description,
  email,
  followersCount,
  location,
  login,
  name,
  repositoriesCount,
}: UserCardProps) => {
  const { handleCardClick, isCardActive, isCardVisited } = useCardState(login || name || 'unknown')

  const handleCardInteraction = () => {
    handleCardClick(login || name || 'unknown')
  }

  const cardClasses = `
    group flex flex-col items-center rounded-lg px-6 py-6 transition-all duration-150 ease-in-out cursor-pointer
    ${isCardActive 
      ? 'border-2 border-blue-400 bg-blue-50 shadow-lg scale-[1.02] dark:border-blue-300 dark:bg-blue-900/20' 
      : isCardVisited 
        ? 'border-2 border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-800/50' 
        : 'border-2 border-transparent bg-white dark:bg-gray-800'
    }
    hover:border-gray-300 hover:bg-gray-50 hover:shadow-md hover:scale-[1.01] dark:hover:border-gray-600 dark:hover:bg-gray-800/50
    ${className}
  `

  return (
    <Button
      onPress={() => {
        handleCardInteraction()
        button.onclick?.()
      }}
      className={cardClasses}
    >
      <div className="flex w-full flex-col items-center gap-3">
        <div className={`
          relative h-20 w-20 shrink-0 overflow-hidden rounded-full ring-2 transition-all duration-200 ease-in-out
          ${isCardActive 
            ? 'ring-blue-400 ring-4' 
            : isCardVisited 
              ? 'ring-gray-300 dark:ring-gray-600' 
              : 'ring-gray-100 dark:ring-gray-700'
          }
          group-hover:ring-blue-400
        `}>
          {avatar ? (
            <Image
              fill
              src={`${avatar}&s=160`}
              alt={name ? `${name}'s profile picture` : 'User profile picture'}
              style={{ objectFit: 'cover' }}
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-gray-200 dark:bg-gray-700">
              <FaUser className="h-12 w-12 text-gray-400 dark:text-gray-500" />
            </div>
          )}
        </div>

        <div className="w-full max-w-[250px] min-w-0 text-center">
          <Tooltip content={name} delay={100} closeDelay={100} showArrow placement="top">
            <h3 className={`
              w-full truncate text-lg font-semibold sm:text-xl transition-all duration-200 ease-in-out
              ${isCardVisited 
                ? 'text-blue-600 dark:text-blue-400' 
                : 'text-gray-900 dark:text-white'
              }
            `}>
              {name}
              {isCardVisited && (
                <span className="ml-2 inline-flex h-2 w-2 rounded-full bg-green-500" title="Visited" />
              )}
            </h3>
          </Tooltip>
          {(company || location || email || login) && (
            <p className="mt-1.5 truncate px-3 text-xs text-gray-600 sm:text-sm dark:text-gray-400">
              {company || location || email || login}
            </p>
          )}
          {description && (
            <p className="mt-1.5 truncate px-3 text-xs text-gray-600 sm:text-sm dark:text-gray-400">
              {description}
            </p>
          )}
        </div>

        {(followersCount > 0 || repositoriesCount > 0 || badgeCount > 0) && (
          <div className="flex flex-wrap justify-center gap-3 px-2">
            {followersCount > 0 && (
              <div className="flex items-center gap-1 text-xs text-gray-600 sm:text-sm dark:text-gray-400">
                <HiUserGroup className="h-4 w-4" />
                <span>{millify(followersCount, { precision: 1 })}</span>
              </div>
            )}
            {repositoriesCount > 0 && (
              <div className="flex items-center gap-1 text-xs text-gray-600 sm:text-sm dark:text-gray-400">
                <FaFolderOpen className="h-3.5 w-3.5" />
                <span>{millify(repositoriesCount, { precision: 1 })}</span>
              </div>
            )}
            {badgeCount > 0 && (
              <div className="flex items-center gap-1 text-xs text-gray-600 sm:text-sm dark:text-gray-400">
                <FaMedal className="h-3.5 w-3.5" aria-label="badges" />
                <span>{millify(badgeCount, { precision: 1 })}</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className={`
        flex items-center justify-center text-sm font-medium transition-all duration-200 ease-in-out
        ${isCardVisited 
          ? 'text-blue-600 dark:text-blue-400' 
          : 'text-blue-400'
        }
      `}>
        {button.label}
        <FaChevronRight className="ml-2 h-4 w-4 transform transition-transform group-hover:translate-x-1" />
      </div>
    </Button>
  )
}

export default UserCard
