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
}

const RecentPullRequests: React.FC<RecentPullRequestsProps> = ({ data, showAvatar = true }) => {
  const router = useRouter()

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
          {item.state && (
            <div className="mr-4 flex items-center">
              <span
                className="inline-flex items-center rounded-lg px-2 py-0.5 text-xs font-medium text-white"
                style={{
                  backgroundColor:
                    item.state.toLowerCase() === 'closed' && item.mergedAt
                      ? '#8657E5'
                      : item.state.toLowerCase() === 'closed'
                        ? '#DA3633'
                        : '#238636',
                }}
              >
                {item.state.toLowerCase() === 'closed' && item.mergedAt
                  ? 'Merged'
                  : item.state.toLowerCase() === 'closed'
                    ? 'Closed'
                    : 'Open'}
              </span>
            </div>
          )}
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
