import { faCalendar, faFileCode } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Image from 'next/image'
import Link from 'next/link'
import React from 'react'
import { ProjectReleaseType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import SecondaryCard from './SecondaryCard'
import { TruncatedText } from './TruncatedText'

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
    <SecondaryCard icon={faFileCode} title="Recent Releases">
      {data && data.length > 0 ? (
        <div
          className={`grid ${showSingleColumn ? 'grid-cols-1' : 'gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}
        >
          {data.map((item, index) => (
            <div key={index} className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
              <div className="flex w-full flex-col justify-between">
                <div className="flex w-full items-center">
                  {showAvatar && (
                    <Link
                      className="flex-shrink-0 text-blue-400 hover:underline"
                      href={`/community/members/${item?.author?.login}`}
                    >
                      <Image
                        alt={item?.author?.name || 'author'}
                        className="mr-2 h-6 w-6 rounded-full"
                        height={24}
                        src={item?.author?.avatarUrl || ''}
                        width={24}
                      />
                    </Link>
                  )}
                  <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                    <Link
                      className="text-blue-400 hover:underline"
                      href={item?.url || '/'}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <TruncatedText text={item?.name} />
                    </Link>
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
