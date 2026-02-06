import { Button } from '@heroui/button'
import { FaChevronRight, FaCalendar } from 'react-icons/fa6'
import type { SnapshotCardProps } from 'types/card'
import { formatDate } from 'utils/dateFormatter'

const SnapshotCard = ({ title, button, startAt, endAt }: SnapshotCardProps) => {
  return (
    <Button
      onClick={button.onclick}
      className="group flex h-40 w-full flex-col items-center rounded-lg bg-white p-6 text-left shadow-lg transition-transform duration-500 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
    >
      <div className="text-center">
        <h3 className="max-w-[250px] text-lg font-semibold text-balance text-gray-900 group-hover:text-blue-300 sm:text-xl dark:text-white">
          <p>{title}</p>
        </h3>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-gray-800 dark:text-gray-300">
        <div className="flex items-center">
          <FaCalendar className="mr-1 h-4 w-4" />
          <span>
            {formatDate(startAt)} - {formatDate(endAt)}
          </span>
        </div>
      </div>

      <div className="mt-auto inline-flex items-center text-sm font-medium text-blue-300">
        View Snapshot
        <FaChevronRight className="ml-2 h-4 w-4 transform transition-transform group-hover:translate-x-1" />
      </div>
    </Button>
  )
}

export default SnapshotCard
