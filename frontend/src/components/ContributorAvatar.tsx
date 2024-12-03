import { Tooltip } from 'react-tooltip'
import { tooltipStyle, topContributorsType } from '../lib/constants'

const ContributorAvatar = ({ contributor }: { contributor: topContributorsType }) => {
  return (
    <a
      data-tooltip-id={`avatar-tooltip-${contributor.login}`}
      data-tooltip-content={`${contributor.contributions_count} contributions by ${contributor.name}`}
      href={`https://github.com/${contributor.login}`}
      target="_blank"
    >
      <img
        className="grayscale rounded-full hover:grayscale-0 w-[30px] h-[30px] "
        src={contributor.avatar_url}
      />
      <Tooltip id={`avatar-tooltip-${contributor.login}`} style={tooltipStyle} />
    </a>
  )
}

export default ContributorAvatar
