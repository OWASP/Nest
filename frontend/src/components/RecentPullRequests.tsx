import Image from 'next/image'
import { useRouter } from 'next/navigation'
import React from 'react'
import { FaCalendar, FaCodePullRequest, FaFolderOpen } from 'react-icons/fa6'
import type { PullRequest } from 'types/pullRequest'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import ItemCardList from 'components/ItemCardList'
import { TruncatedText } from 'components/TruncatedText'

interface RecentPullRequestsProps {
  data: PullRequest[]
  showAvatar?: boolean
  variant?: 'sidebar' | 'full'
}

const RecentPullRequests: React.FC<RecentPullRequestsProps> = ({
  data,
  showAvatar = true,
  variant = 'sidebar',
}) => {
  const router = useRouter()

  if (variant === 'full') {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {data.map((pr) => (
          <a
            key={pr.id || pr.url}
            href={pr.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
          >
            <div className="flex items-start gap-3">
              <FaCodePullRequest className="mt-1 h-4 w-4 shrink-0 text-green-600 dark:text-green-400" />
              <div className="min-w-0 flex-1">
                <h3 className="truncate text-lg font-semibold text-gray-800 dark:text-gray-100">
                  {pr.title}
                </h3>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                  {pr.author && (
                    <span className="flex items-center gap-1">
                      <Image
                        src={pr.author.avatarUrl}
                        alt={pr.author.login}
                        width={16}
                        height={16}
                        className="h-4 w-4 rounded-full"
                      />
                      {pr.author.name || pr.author.login}
                    </span>
                  )}
                  {pr.repositoryName && (
                    <span>
                      {pr.organizationName}/{pr.repositoryName}
                    </span>
                  )}
                  <span>{formatDate(pr.createdAt)}</span>
                </div>
              </div>
              <span
                className={`shrink-0 rounded-full px-2 py-1 text-xs font-medium ${
                  pr.mergedAt
                    ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                    : pr.state === 'open'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}
              >
                {pr.mergedAt ? 'merged' : pr.state}
              </span>
            </div>
          </a>
        ))}
      </div>
    )
  }

  return (
    <ItemCardList
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title="Recent Pull Requests" />
        </div>
      }
      data={data}
      icon={FaCodePullRequest}
      showAvatar={showAvatar}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
          <div className="mr-4 flex items-center">
            <FaCalendar className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>

          {item?.repositoryName && (
            <div className="mr-4 flex flex-1 items-center overflow-hidden">
              <FaFolderOpen className="mr-2 h-5 w-4 shrink-0" />
              <button
                type="button"
                className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 hover:underline dark:text-gray-400"
                onClick={() =>
                  router.push(
                    `/organizations/${item.organizationName}/repositories/${item.repositoryName}`
                  )
                }
              >
                <TruncatedText text={item.repositoryName} />
              </button>
            </div>
          )}
        </div>
      )}
    />
  )
}

export default RecentPullRequests
