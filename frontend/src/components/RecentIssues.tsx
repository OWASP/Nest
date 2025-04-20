import { faCalendar, faFolderOpen, faCircleExclamation } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import React from 'react'
import { ProjectIssuesType } from 'types/project'
import { formatDate } from 'utils/dateFormatter'
import ItemCardList from './ItemCardList'

interface RecentIssuesProps {
  data: ProjectIssuesType[]
  showAvatar?: boolean
}

const RecentIssues: React.FC<RecentIssuesProps> = ({ data, showAvatar = true }) => {
  const router = useRouter()

  const renderMetaInfo = (item: ProjectIssuesType) => {
    const details = [
      {
        condition: true,
        icon: faCalendar,
        content: formatDate(item.createdAt),
      },
      {
        condition: !!item.repositoryName,
        icon: faFolderOpen,
        content: item.repositoryName,
        onClick: () =>
          router.push(
            `/organizations/${item.organizationName}/repositories/${item.repositoryName}`
          ),
      },
    ]

    return (
      <div className="mt-2 flex flex-col flex-wrap gap-y-1 text-sm text-gray-600 dark:text-gray-400 md:flex-row md:items-center">
        {details
          .filter((d) => d.condition)
          .map((d, idx) => (
            <div key={idx} className="flex items-center mr-4">
              <FontAwesomeIcon icon={d.icon} className="mr-2 h-4 w-4" />
              {d.onClick ? (
                <button
                  onClick={d.onClick}
                  className="cursor-pointer text-gray-600 hover:underline dark:text-gray-400"
                >
                  {d.content}
                </button>
              ) : (
                <span>{d.content}</span>
              )}
            </div>
          ))}
      </div>
    )
  }

  return (
    <ItemCardList
      title="Recent Issues"
      data={data}
      showAvatar={showAvatar}
      icon={faCircleExclamation}
      renderDetails={(item) => renderMetaInfo(item)}
    />
  )
}

export default RecentIssues
