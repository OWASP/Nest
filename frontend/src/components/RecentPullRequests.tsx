import { faCalendar, faCodePullRequest, faUser } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import { PullRequestsType } from 'types/home'
import { ItemCardPullRequests } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from './AnchorTitle'
import ItemCardList from './ItemCardList'

interface RecentPullRequestsProps {
  data: ItemCardPullRequests[] | PullRequestsType[]
  showAvatar?: boolean
  showAuthor?: boolean
}

const RecentPullRequests: React.FC<RecentPullRequestsProps> = ({
  data,
  showAvatar = true,
  showAuthor = false,
}) => {
  return (
    <ItemCardList
      title={
        <div className="flex items-center gap-2">
          <FontAwesomeIcon
            icon={faCodePullRequest}
            className="relative -top-[8px] h-5 w-5"
            style={{ verticalAlign: 'middle' }}
          />
          <AnchorTitle
            href="#recent-pull-requests"
            title="Recent Pull Requests"
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

          {showAuthor &&
            (item?.author?.name || item?.author?.login ? (
              <div className="flex items-center">
                <FontAwesomeIcon icon={faUser} className="mr-2 h-4 w-4" />
                <span>{item.author.name || item.author.login}</span>
              </div>
            ) : null)}
        </div>
      )}
    />
  )
}

export default RecentPullRequests
