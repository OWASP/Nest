import { faCalendar, faFolderOpen, faTag } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import React from 'react'
import type { Release } from 'types/release'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'
import { TruncatedText } from 'components/TruncatedText'

interface RecentReleasesProps {
  data: Release[]
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
    <SecondaryCard
      icon={faTag}
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title="Recent Releases" className="flex items-center leading-none" />
        </div>
      }
    >
      {data && data.length > 0 ? (
        <div
          className={`grid ${showSingleColumn ? 'grid-cols-1' : 'gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'}`}
        >
          {data.map((item, index) => (
            <div key={index} className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
              <div className="flex w-full flex-col justify-between">
                <div className="flex w-full items-center">
                  {showAvatar && (
                    <Tooltip
                      closeDelay={100}
                      content={item?.author?.name || item?.author?.login}
                      id={`avatar-tooltip-${index}`}
                      delay={100}
                      placement="bottom"
                      showArrow
                    >
                      <Link
                        className="flex-shrink-0 text-blue-400 hover:underline"
                        href={`/members/${item?.author?.login}`}
                      >
                        <Image
                          alt={item?.author?.name || 'author'}
                          className="mr-2 h-6 w-6 rounded-full"
                          height={24}
                          src={item?.author?.avatarUrl || ''}
                          width={24}
                        />
                      </Link>
                    </Tooltip>
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
                <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
                  <div className="mr-4 flex items-center">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(item.publishedAt)}</span>
                  </div>
                  <div className="flex flex-1 items-center overflow-hidden">
                    <FontAwesomeIcon icon={faFolderOpen} className="mr-2 h-5 w-4" />
                    <button
                      className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 hover:underline dark:text-gray-400"
                      onClick={() =>
                        router.push(
                          `/organizations/${item?.organizationName}/repositories/${item.repositoryName || ''}`
                        )
                      }
                    >
                      <TruncatedText text={item.repositoryName} />
                    </button>
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
