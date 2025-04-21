import { faCalendar, faCodePullRequest, faFolderOpen } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import React from 'react'
import { PullRequestsType } from 'types/home'
import { ItemCardPullRequests } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import ItemCardList from './ItemCardList'
import { TruncatedText } from './TruncatedText'

interface RecentPullRequestsProps {
  data: ItemCardPullRequests[] | PullRequestsType[]
  showAvatar?: boolean
}

const RecentPullRequests: React.FC<RecentPullRequestsProps> = ({ data, showAvatar = true }) => {
  const router = useRouter()

  return (
    <ItemCardList
      title="Recent Pull Requests"
      data={data}
      showAvatar={showAvatar}
      icon={faCodePullRequest}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
          <div className="mr-4 flex items-center">
            <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>

          {item?.repositoryName && (
            <div className="mr-4 flex flex-1 items-center overflow-hidden">
              <FontAwesomeIcon icon={faFolderOpen} className="mr-2 h-5 w-4" />
              <button
                className="cursor-pointer text-gray-600 hover:underline dark:text-gray-400"
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

export default RecentPullRequests
