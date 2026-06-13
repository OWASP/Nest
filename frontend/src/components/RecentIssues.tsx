import Image from 'next/image'
import { useRouter } from 'next/navigation'
import React from 'react'
import { FaCalendar, FaFolderOpen, FaCircleExclamation } from 'react-icons/fa6'
import type { Issue } from 'types/issue'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import ItemCardList from 'components/ItemCardList'
import { TruncatedText } from 'components/TruncatedText'

interface RecentIssuesProps {
  data: Issue[]
  showAvatar?: boolean
  variant?: 'sidebar' | 'full'
}

const RecentIssues: React.FC<RecentIssuesProps> = ({
  data,
  showAvatar = true,
  variant = 'sidebar',
}) => {
  const router = useRouter()

  if (variant === 'full') {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {data.map((issue) => (
          <a
            key={issue.objectID || issue.url}
            href={issue.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
          >
            <div className="flex items-start gap-3">
              <div className="min-w-0 flex-1">
                <h3 className="truncate text-lg font-semibold text-gray-800 dark:text-gray-100">
                  {issue.title}
                </h3>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                  {showAvatar && issue.author && (
                    <span className="flex items-center gap-1">
                      <Image
                        src={issue.author.avatarUrl}
                        alt={issue.author.login}
                        width={16}
                        height={16}
                        className="h-4 w-4 rounded-full"
                      />
                      {issue.author.name || issue.author.login}
                    </span>
                  )}
                  {issue.repositoryName && (
                    <span>
                      {issue.organizationName
                        ? `${issue.organizationName}/${issue.repositoryName}`
                        : issue.repositoryName}
                    </span>
                  )}
                  <span>{formatDate(issue.createdAt)}</span>
                </div>
              </div>
              <span
                className={`shrink-0 rounded-full px-2 py-1 text-xs font-medium ${
                  issue.state === 'open'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}
              >
                {issue.state ?? 'unknown'}
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
          <AnchorTitle title="Recent Issues" />
        </div>
      }
      data={data}
      showAvatar={showAvatar}
      icon={FaCircleExclamation}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
          <div className="mr-4 flex items-center">
            <FaCalendar className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>
          {item?.repositoryName && (
            <div className="flex flex-1 items-center overflow-hidden">
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

export default RecentIssues
