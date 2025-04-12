import { faCalendar, faFileCode, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import { ProjectIssuesType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import { pluralize } from 'utils/pluralize'
import AnchorTitle from './AnchorTitle'
import ItemCardList from './ItemCardList'

interface RecentIssuesProps {
  data: ProjectIssuesType[]
  showAvatar?: boolean
}

const RecentIssues: React.FC<RecentIssuesProps> = ({ data, showAvatar = true }) => {
  return (
    <ItemCardList
      title={
        <div className="flex items-center gap-2">
          <FontAwesomeIcon
            icon={faTriangleExclamation}
            className="relative -top-[8px] h-5 w-5"
            style={{ verticalAlign: 'middle' }}
          />
          <AnchorTitle
            href="#recent-issues"
            title="Recent Issues"
            className="flex items-center leading-none"
          />
        </div>
      }
      data={data}
      showAvatar={showAvatar}
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
