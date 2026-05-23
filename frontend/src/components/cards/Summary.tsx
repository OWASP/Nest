import type { ReactNode } from 'react'
import { FaCircleInfo } from 'react-icons/fa6'
import AnchorTitle from 'components/AnchorTitle'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'

interface SummaryProps {
  summary?: string
  userSummary?: ReactNode
}

const Summary = ({ summary, userSummary }: SummaryProps) => {
  return (
    <>
      {summary && (
        <SecondaryCard icon={FaCircleInfo} title={<AnchorTitle title="Summary" />}>
          <Markdown content={summary} />
        </SecondaryCard>
      )}

      {userSummary && <SecondaryCard>{userSummary}</SecondaryCard>}
    </>
  )
}

export default Summary
