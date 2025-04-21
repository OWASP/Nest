import { faCalendar, faFolderOpen, faCircleExclamation } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import React from 'react'
import { ProjectIssuesType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from './AnchorTitle'
import ItemCardList from './ItemCardList'

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
        <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
          <div className="flex items-center">
            <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>
          {item?.repositoryName && (
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
      )}
    />
  )
}

export default RecentIssues
