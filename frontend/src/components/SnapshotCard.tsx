import { Button } from '@chakra-ui/react'
import { faChevronRight } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { SnapshotCardProps } from 'types/card'

const SnapshotCard = ({ title, button }: SnapshotCardProps) => {
  return (
    <Button
      onClick={button.onclick}
      className="group flex h-64 w-80 flex-col items-center rounded-lg bg-white p-6 text-left shadow-lg transition-transform duration-500 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
    >
      <div className="text-center">
        <h3 className="max-w-[250px] text-balance text-lg font-semibold text-gray-900 group-hover:text-blue-500 dark:text-white sm:text-xl">
          <p>{title}</p>
        </h3>
      </div>

      <div className="mt-auto inline-flex items-center text-sm font-medium text-blue-500 dark:text-blue-400">
        View Snapshot
        <FontAwesomeIcon
          icon={faChevronRight}
          className="ml-2 h-4 w-4 transform transition-transform group-hover:translate-x-1"
        />
      </div>
    </Button>
  )
}

export default SnapshotCard
