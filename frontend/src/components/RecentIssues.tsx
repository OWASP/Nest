import { faCalendar, faFileCode, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import React from 'react'
import { ProjectIssuesType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
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
          <div className="flex items-center">
            <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>
          {item?.repositoryName && (
            <div className="item-center flex">
              <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
              <Link
                className="text-gray-600 hover:underline dark:text-gray-400"
                href={`/repositories/${item?.repositoryName ? item.repositoryName.toLowerCase() : ''}`}
              >
                <span>{item.repositoryName}</span>
              </Link>{' '}
            </div>
          )}
        </div>
      )}
    />
  )
}

export default RecentIssues
