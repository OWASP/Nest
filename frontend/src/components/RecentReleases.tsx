import { faCalendar, faFolderOpen, faTag } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
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
  const router = useRouter()

  return (
    <SecondaryCard icon={faTag} title="Recent Releases">
      {data && data.length > 0 ? (
        <div
          className={`grid ${
            showSingleColumn
              ? 'grid-cols-1'
              : 'gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
          }`}
        >
          {data.map((item, index) => (
            <div
              key={index}
              className="mb-4 w-full rounded-xl bg-gray-200 p-4 shadow-sm dark:bg-gray-700"
            >
              <div className="flex w-full flex-col justify-between">
                <div className="flex w-full items-center">
                  {showAvatar && (
                    <Tooltip
                      content={item?.author?.name || item?.author?.login}
                      placement="bottom"
                      showArrow
                      id={`avatar-tooltip-${index}`}
                    >
                      <Link href={`/members/${item?.author?.login}`} className="shrink-0">
                        <Image
                          src={item?.author?.avatarUrl || ''}
                          alt={item?.author?.name || 'author'}
                          width={24}
                          height={24}
                          className="mr-2 h-6 w-6 rounded-full"
                        />
                      </Link>
                    </Tooltip>
                  )}
                  <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                    <Link
                      href={item?.url || '/'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:underline"
                    >
                      <TruncatedText text={item?.name} />
                    </Link>
                  </h3>
                </div>

                <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
                  <div className="flex items-center">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(item.publishedAt)}</span>
                  </div>

                  {item.repositoryName && (
                    <div className="item-center flex">
                      <FontAwesomeIcon icon={faFolderOpen} className="ml-4 mr-2 h-4 w-4" />
                      <button
                        className="cursor-pointer text-gray-600 hover:underline dark:text-gray-400"
                        onClick={() =>
                          router.push(
                            `/organizations/${item.organizationName}/repositories/${item.repositoryName || ''}`
                          )
                        }
                      >
                        {item.repositoryName}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-600 dark:text-gray-400">No recent releases.</p>
      )}
    </SecondaryCard>
  )
}

export default RecentReleases
