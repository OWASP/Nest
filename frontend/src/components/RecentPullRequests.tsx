import { useRouter } from 'next/navigation'
import React, { JSX } from 'react'
import { FaCalendar, FaCodePullRequest, FaFolderOpen } from 'react-icons/fa6'
import type { PullRequest } from 'types/pullRequest'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import ItemCardList from 'components/ItemCardList'
import { TruncatedText } from 'components/TruncatedText'

interface RecentPullRequestsProps {
  data: PullRequest[]
  showAvatar?: boolean
  showBadge?: boolean
  showSingleColumn?: boolean
  bare?: boolean
}

const getBadgeClass = (pr: PullRequest) => {
  if (pr.mergedAt) {
    return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
  }
  if (pr.state === 'open') {
    return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  }
  return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
}

const getPullRequestBadge = (pr: PullRequest): JSX.Element => (
  <span className={`ml-2 shrink-0 rounded-full px-2 py-1 text-xs font-medium ${getBadgeClass(pr)}`}>
    {pr.mergedAt ? 'merged' : (pr.state ?? 'unknown')}
  </span>
)

const RecentPullRequests: React.FC<RecentPullRequestsProps> = ({
  data,
  showAvatar = true,
  showBadge = false,
  showSingleColumn = true,
  bare = false,
}) => {
  const router = useRouter()

  return (
    <ItemCardList
      title={
        !bare ? (
          <div className="flex items-center gap-2">
            <AnchorTitle title="Recent Pull Requests" />
          </div>
        ) : undefined
      }
      data={data}
      icon={FaCodePullRequest}
      showAvatar={showAvatar}
      showSingleColumn={showSingleColumn}
      bare={bare}
      renderBadge={
        showBadge ? (item) => getPullRequestBadge(item as unknown as PullRequest) : undefined
      }
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
