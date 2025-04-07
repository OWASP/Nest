import { faChevronRight, faUser } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Image from 'next/image'
import { UserCardProps } from 'types/card'

const UserCard = ({ avatar, name, company, email, location, button, className }: UserCardProps) => {
  return (
    <Button
      onPress={button.onclick}
      className={`group flex flex-col items-center rounded-lg p-6 ${className}`}
    >
      <div className="flex w-full flex-col items-center space-y-4">
        <div className="relative h-20 w-20 overflow-hidden rounded-full ring-2 ring-gray-100 group-hover:ring-blue-400 dark:ring-gray-700">
          {avatar ? (
            <Image fill src={`${avatar}&s=160`} alt={name || 'user'} objectFit="cover" />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-gray-200 dark:bg-gray-700">
              <FontAwesomeIcon
                icon={faUser}
                className="h-12 w-12 text-gray-400 dark:text-gray-500"
              />
            </div>
          )}
        </div>

        <div className="text-center">
          <h3 className="max-w-[250px] truncate text-lg font-semibold text-gray-900 dark:text-white sm:text-xl">
            {name}
          </h3>
          <p className="mt-1 max-w-[250px] truncate text-sm text-gray-600 dark:text-gray-400 sm:text-base">
            {company || location || email}
          </p>
        </div>
      </div>

      <div className="mt-auto inline-flex items-center text-sm font-medium text-blue-400">
        View Profile
        <FontAwesomeIcon
          icon={faChevronRight}
          className="ml-2 h-4 w-4 transform transition-transform group-hover:translate-x-1"
        />
      </div>
    </Button>
  )
}

export default UserCard
