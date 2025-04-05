import { faCalendar, faFileCode } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import { ProjectReleaseType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from './AnchorTitle'
import SecondaryCard from './SecondaryCard'

interface RecentReleasesProps {
  data: ProjectReleaseType[]
  showAvatar?: boolean
  showSingleColumn?: boolean
}

const RecentReleases: React.FC<RecentReleasesProps> = ({
  data,
  showAvatar = true,
  showSingleColumn = false,
}) => {
  return (
    <SecondaryCard
      icon={faFileCode}
      title={<AnchorTitle href="#recent-releases" title="Recent Releases" />}
    >
      {data && data.length > 0 ? (
        <div
          className={`grid ${showSingleColumn ? 'grid-cols-1' : 'grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}
        >
          {data.map((item, index) => (
            <div key={index} className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
              <div className="flex w-full flex-col justify-between">
                <div className="flex w-full items-center">
                  {showAvatar && (
                    <a
                      className="flex-shrink-0 text-blue-400 hover:underline"
                      href={`/community/users/${item?.author?.login}`}
                    >
                      <img
                        src={item?.author?.avatarUrl}
                        alt={item?.author?.name}
                        className="mr-2 h-6 w-6 rounded-full"
                      />
                    </a>
                  )}
                  <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                    <a
                      className="text-blue-400 hover:underline"
                      href={item?.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {item.name}
                    </a>
                  </h3>
                </div>
                <div className="ml-0.5 w-full">
                  <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(item.publishedAt)}</span>
                    <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
                    <span>{item.repositoryName}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p>No recent releases.</p>
      )}
    </SecondaryCard>
  )
}

export default RecentReleases
