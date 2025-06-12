import {
  faCalendar,
  faFolderOpen,
  faSignsPost,
  faCircleCheck,
  faCircleExclamation,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import React from 'react'
import type { Milestone } from 'types/milestone'
import { formatDate } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import ItemCardList from 'components/ItemCardList'
import { TruncatedText } from 'components/TruncatedText'

interface ProjectMilestonesProps {
  data: Milestone[]
  showAvatar?: boolean
  showSingleColumn?: boolean
}

const Milestones: React.FC<ProjectMilestonesProps> = ({
  data,
  showAvatar = true,
  showSingleColumn = true,
}) => {
  const router = useRouter()

  return (
    <ItemCardList
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title="Recent Milestones" className="flex items-center leading-none" />
        </div>
      }
      data={data}
      showAvatar={showAvatar}
      icon={faSignsPost}
      showSingleColumn={showSingleColumn}
      renderDetails={(item) => (
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
          <div className="mr-4 flex items-center">
            <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
            <span>{formatDate(item.createdAt)}</span>
          </div>
          <div className="mr-4 flex items-center">
            <FontAwesomeIcon icon={faCircleCheck} className="mr-2 h-4 w-4" />
            <span>{item.closedIssuesCount} closed</span>
          </div>
          <div className="mr-4 flex items-center">
            <FontAwesomeIcon icon={faCircleExclamation} className="mr-2 h-4 w-4" />
            <span>{item.openIssuesCount} open</span>
          </div>
          {item?.repositoryName && (
            <div className="flex flex-1 items-center">
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

export default Milestones
