import { faCalendar, faFileCode, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import { ProjectIssuesType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import { pluralize } from 'utils/pluralize'
import ItemCardList from './ItemCardList'

interface RecentIssuesProps {
  data: ProjectIssuesType[]
  showAvatar?: boolean
}

const RecentIssues: React.FC<RecentIssuesProps> = ({ data, showAvatar = true }) => {
  return (
    <ItemCardList
      title="Recent Issues"
      data={data}
      showAvatar={showAvatar}
      icon={faTriangleExclamation}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
          <div className="mr-4 flex items-center">
            <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>
          {item?.commentsCount ? (
            <div className="flex items-center">
              <FontAwesomeIcon icon={faFileCode} className="mr-2 h-4 w-4" />
              <span>
                {item.commentsCount} {pluralize(item.commentsCount, 'comment')}
              </span>
            </div>
          ) : null}
        </div>
      )}
    />
  )
}

export default RecentIssues
