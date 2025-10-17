import React from 'react'
import { faCircleInfo } from '@fortawesome/free-solid-svg-icons'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'
import type { JSX } from 'react'

interface SummarySectionProps {
  summary?: string | null
  userSummary?: JSX.Element
}

const SummarySection: React.FC<SummarySectionProps> = ({ summary, userSummary }) => {
  if (!summary && !userSummary) return null

  return (
    <div className="mb-6 space-y-4">
      {summary && (
        <SecondaryCard icon={faCircleInfo} title={<AnchorTitle title="Summary" />}>
          <p>{summary}</p>
        </SecondaryCard>
      )}

      {userSummary && <SecondaryCard>{userSummary}</SecondaryCard>}
    </div>
  )
}

export default SummarySection;
