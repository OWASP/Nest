import type { ReactNode } from 'react'
import { FaCircleInfo } from 'react-icons/fa6'
import AnchorTitle from 'components/AnchorTitle'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'

interface CardDetailsSummaryProps {
  summary?: string
  userSummary?: ReactNode
}

const CardDetailsSummary = ({ summary, userSummary }: CardDetailsSummaryProps) => {
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

export default CardDetailsSummary
