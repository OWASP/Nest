import {
  faChevronRight,
  faFolderOpen,
  faMedal,
  faUser,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { Tooltip } from '@heroui/tooltip'
import millify from 'millify'
import Image from 'next/image'
import type { UserCardProps } from 'types/card'

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
  return (
    <Button
      onPress={button.onclick}
      className={`group flex flex-col items-center rounded-lg px-6 py-6 ${className}`}
    >
      <div className="flex w-full flex-col items-center gap-3">
        <div className="relative h-20 w-20 shrink-0 overflow-hidden rounded-full ring-2 ring-gray-100 transition-all group-hover:ring-blue-400 dark:ring-gray-700">
          {avatar ? (
            <Image
              fill
              src={`${avatar}&s=160`}
              alt={name ? `${name}'s profile picture` : 'User profile picture'}
              style={{ objectFit: 'cover' }}
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-gray-200 dark:bg-gray-700">
              <FontAwesomeIcon
                icon={faUser}
                className="h-12 w-12 text-gray-400 dark:text-gray-500"
              />
            </div>
          )}
        </div>

        <div className="w-full max-w-[250px] min-w-0 text-center">
          <Tooltip content={name} delay={100} closeDelay={100} showArrow placement="top">
            <h3 className="w-full truncate text-lg font-semibold text-gray-900 sm:text-xl dark:text-white">
              {name}
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
                <FontAwesomeIcon icon={faUsers} className="h-3.5 w-3.5" />
                <span>{millify(followersCount, { precision: 1 })}</span>
              </div>
            )}
            {repositoriesCount > 0 && (
              <div className="flex items-center gap-1 text-xs text-gray-600 sm:text-sm dark:text-gray-400">
                <FontAwesomeIcon icon={faFolderOpen} className="h-3.5 w-3.5" />
                <span>{millify(repositoriesCount, { precision: 1 })}</span>
              </div>
            )}
            {badgeCount > 0 && (
              <div className="flex items-center gap-1 text-xs text-gray-600 sm:text-sm dark:text-gray-400">
                <FontAwesomeIcon icon={faMedal} className="h-3.5 w-3.5" aria-label="badges" />
                <span>{millify(badgeCount, { precision: 1 })}</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center justify-center text-sm font-medium text-blue-400">
        {button.label}
        <FontAwesomeIcon
          icon={faChevronRight}
          className="ml-2 h-4 w-4 transform transition-transform group-hover:translate-x-1"
        />
      </div>
    </Button>
  )
}

export default UserCard
