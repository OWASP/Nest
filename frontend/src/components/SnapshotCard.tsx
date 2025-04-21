import { faChevronRight, faCalendar } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Image from 'next/image'
import Link from 'next/link'
import { SnapshotCardProps } from 'types/card'
import { formatDate } from 'utils/dateFormatter'
import { capitalize } from 'utils/capitalize'
import { pluralize } from 'utils/pluralize'
import { getMemberUrl } from 'utils/urlFormatter'

const SnapshotCard = ({ title, button, startAt, endAt, topContributors }: SnapshotCardProps) => {
  return (
    <Button
      onClick={button.onclick}
      className="group flex w-full flex-col items-start rounded-lg bg-white p-6 text-left shadow-lg transition-transform duration-500 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
    >
      {/* Title */}
      <div className="text-center w-full">
        <h3 className="max-w-[250px] text-balance text-lg font-semibold text-gray-900 group-hover:text-blue-400 dark:text-white sm:text-xl">
          <p>{title}</p>
        </h3>
      </div>

      {/* Date Range */}
      <div className="my-2 flex flex-wrap items-center gap-2 text-gray-600 dark:text-gray-300">
        <div className="flex items-center">
          <FontAwesomeIcon icon={faCalendar} className="mr-1 h-4 w-4" />
          <span>
            {formatDate(startAt)} - {formatDate(endAt)}
          </span>
        </div>
      </div>

      {/* Top Contributors */}
      {topContributors && topContributors.length > 0 && (
        <div className="mt-2 flex w-full flex-wrap gap-3">
          {topContributors.slice(0, 3).map((contributor, index) => (
            <div
              key={index}
              className="flex items-center gap-2 rounded bg-gray-100 px-3 py-1 text-sm dark:bg-gray-700"
            >
              <Image
                src={`${contributor.avatarUrl}&s=40`}
                alt={contributor.name || contributor.login}
                width={20}
                height={20}
                className="rounded-full"
              />
              <Link
                href={getMemberUrl(contributor.login)}
                className="text-blue-500 hover:underline"
              >
                {capitalize(contributor.name || contributor.login)}
              </Link>
              <span className="text-gray-500 dark:text-gray-300">
                ({contributor.contributionsCount}{' '}
                {pluralize(contributor.contributionsCount, 'contribution')})
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Footer CTA */}
      <div className="mt-auto inline-flex items-center text-sm font-medium text-blue-400">
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
