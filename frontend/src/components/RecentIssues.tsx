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
}

const RecentIssues: React.FC<RecentIssuesProps> = ({ data, showAvatar = true }) => {
  const router = useRouter()

  return (
    <ItemCardList
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title="Recent Issues" className="flex items-center leading-none" />
        </div>
      }
      data={data}
      showAvatar={showAvatar}
      icon={FaCircleExclamation}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
          <div className="mr-4 flex items-center">
            <FaCalendar className="mr-2 h-4 w-4" />
            <span>{formatDate(new Date(item.createdAt).getTime() / 1000)}</span>
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
