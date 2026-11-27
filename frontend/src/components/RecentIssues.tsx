import { useRouter } from 'next/navigation'
import React, { JSX } from 'react'
import { FaCalendar, FaCircleExclamation, FaFolderOpen } from 'react-icons/fa6'
import type { Issue } from 'types/issue'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import ItemCardList from 'components/ItemCardList'
import { TruncatedText } from 'components/TruncatedText'

interface RecentIssuesProps {
  data: Issue[]
  showAvatar?: boolean
  showBadge?: boolean
  showSingleColumn?: boolean
  bare?: boolean
}

const getIssueStateColor = (issue: Issue): string => {
  if (issue.state === 'open') {
    return 'bg-[#238636] text-white'
  }
  if (issue.isMerged) {
    return 'bg-[#8657E5] text-white'
  }
  return 'bg-[#DA3633] text-white'
}

const getIssueStateLabel = (issue: Issue): string => {
  if (issue.state === 'open') return 'open'
  if (issue.isMerged) return 'closed'
  return issue.state ?? 'unknown'
}

const getIssueBadge = (issue: Issue): JSX.Element => (
  <span
    className={`ml-2 shrink-0 rounded-full px-2 py-1 text-xs font-medium ${getIssueStateColor(issue)}`}
  >
    {getIssueStateLabel(issue)}
  </span>
)

const RecentIssues: React.FC<RecentIssuesProps> = ({
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
        bare ? undefined : (
          <div className="flex items-center gap-2">
            <AnchorTitle title="Recent Issues" />
          </div>
        )
      }
      data={data}
      showAvatar={showAvatar}
      icon={FaCircleExclamation}
      showSingleColumn={showSingleColumn}
      bare={bare}
      renderBadge={showBadge ? (item) => getIssueBadge(item as unknown as Issue) : undefined}
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
