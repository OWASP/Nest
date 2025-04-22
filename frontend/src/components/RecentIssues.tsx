import { faCalendar, faFolderOpen, faCircleExclamation } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import React from 'react'
import { ProjectIssuesType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from './AnchorTitle'
import ItemCardList from './ItemCardList'
import { TruncatedText } from './TruncatedText'

interface RecentIssuesProps {
  data: ProjectIssuesType[]
  showAvatar?: boolean
}

const RecentIssues: React.FC<RecentIssuesProps> = ({ data, showAvatar = true }) => {
  const router = useRouter()

  return (
    <ItemCardList
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle
            href="#recent-issues"
            title="Recent Issues"
            className="flex items-center leading-none"
          />
        </div>
      }
      data={data}
      showAvatar={showAvatar}
      icon={faCircleExclamation}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
          <div className="mr-4 flex items-center">
            <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>
          {item?.repositoryName && (
            <div className="flex flex-1 items-center overflow-hidden">
              <FontAwesomeIcon icon={faFolderOpen} className="mr-2 h-5 w-4" />
              <button
                className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 hover:underline dark:text-gray-400"
                onClick={() =>
                  router.push(
                    `/organizations/${item.organizationName}/repositories/${item.repositoryName || ''}`
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
