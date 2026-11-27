import type { ReactNode } from 'react'
import { FaCircleInfo } from 'react-icons/fa6'
import AnchorTitle from 'components/AnchorTitle'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'

interface SummaryProps {
  summary?: string
  userSummary?: ReactNode
  className?: string
}

const Summary = ({ summary, userSummary, className = '' }: SummaryProps) => {
  return (
    <>
      {summary && (
        <SecondaryCard
          icon={FaCircleInfo}
          title={<AnchorTitle title="Summary" />}
          className={className}
        >
          <Markdown content={summary} />
        </SecondaryCard>
      )}

      {userSummary && <SecondaryCard className={className}>{userSummary}</SecondaryCard>}
    </>
  )
}

export default Summary
