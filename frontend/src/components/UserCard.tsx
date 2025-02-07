import { Button } from '@chakra-ui/react'
import { faChevronRight, faUser } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { UserCardProps } from 'types/card'

const UserCard = ({ avatar, name, company, button }: UserCardProps) => {
  return (
    <Button
      onClick={button.onclick}
      className="group flex h-64 w-80 flex-col items-center rounded-lg bg-white p-6 text-left shadow-lg transition-transform duration-500 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
    >
      <div className="flex w-full flex-col items-center space-y-4">
        <div className="relative h-20 w-20 overflow-hidden rounded-full ring-2 ring-gray-100 transition-all group-hover:ring-blue-500 dark:ring-gray-700">
          {avatar ? (
            <img src={`${avatar}&s=160`} alt={name} className="h-full w-full object-cover" />
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
          <h3 className="line-clamp-1 text-lg font-semibold text-gray-900 group-hover:text-blue-500 dark:text-white sm:text-xl">
            {name}
          </h3>
          <p className="mt-1 line-clamp-1 text-sm text-gray-600 dark:text-gray-400 sm:text-base">
            {company || ''}
          </p>
        </div>
      </div>

      <div className="mt-auto inline-flex items-center text-sm font-medium text-blue-500 dark:text-blue-400">
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
