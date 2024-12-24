import { Tooltip } from 'react-tooltip'

import { tooltipStyle } from '@src/lib/constants'

const TopicBadge = ({
  topic,
  tooltipLabel,
  type,
}: {
  topic: string
  tooltipLabel?: string
  type: string
}) => {
  return (
    <div
      data-tooltip-id={`lang-tooltip-${topic}`}
      data-tooltip-content={tooltipLabel}
      className={`rounded-md bg-[#6C757D] p-1 px-2 text-xs font-bold text-white ${type == 'language' ? 'bg-[#868E96]' : 'bg-[#6C757D]'}`}
    >
      {topic}

      <Tooltip id={`lang-tooltip-${topic}`} style={tooltipStyle} />
    </div>
  )
}

export default TopicBadge
