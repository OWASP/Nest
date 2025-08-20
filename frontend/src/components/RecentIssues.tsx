import { faCircleExclamation } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import type { Issue } from 'types/issue'
import AnchorTitle from 'components/AnchorTitle'
import ItemCardList from 'components/ItemCardList'
import { IssueMetadata } from 'components/IssueMetadata' // ← new reusable component

interface RecentIssuesProps {
  data: Issue[]
  showAvatar?: boolean
}

const RecentIssues: React.FC<RecentIssuesProps> = ({ data, showAvatar = true }) => {
  return (
    <ItemCardList
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title="Recent Issues" className="flex items-center leading-none" />
          <FontAwesomeIcon icon={faCircleExclamation} className="h-5 w-5 text-red-500" />
        </div>
      }
      data={data}
      showAvatar={showAvatar}
      icon={faCircleExclamation}
      renderDetails={(item) => <IssueMetadata issue={item} />}
    />
  )
}

export default RecentIssues