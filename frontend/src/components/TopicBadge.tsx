import { Tooltip } from 'react-tooltip'
import { tooltipStyle } from '../lib/constants'

const TopicBadge = ({ topic, tooltipLabel }: { topic: string; tooltipLabel?: string }) => {
  return (
    <div
      data-tooltip-id={`lang-tooltip-${topic}`}
      data-tooltip-content={tooltipLabel}
      className=" p-1 px-2 text-xs font-bold rounded-md bg-[#6C757D] text-white "
    >
      {topic}

      <Tooltip id={`lang-tooltip-${topic}`} style={tooltipStyle} />
    </div>
  )
}

export default TopicBadge
