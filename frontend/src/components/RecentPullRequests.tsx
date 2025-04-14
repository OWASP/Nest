import { faCalendar, faCodePullRequest, faFileCode } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import React from 'react'
import { PullRequestsType } from 'types/home'
import { ItemCardPullRequests } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import ItemCardList from './ItemCardList'

interface RecentPullRequestsProps {
  data: ItemCardPullRequests[] | PullRequestsType[]
  showAvatar?: boolean
}

const RecentPullRequests: React.FC<RecentPullRequestsProps> = ({ data, showAvatar = true }) => {
  return (
    <ItemCardList
      title="Recent Pull Requests"
      data={data}
      showAvatar={showAvatar}
      icon={faCodePullRequest}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
          <div className="mr-4 flex items-center">
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

export default RecentPullRequests
