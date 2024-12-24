import { Tooltip } from 'react-tooltip'

import { tooltipStyle, topContributorsType } from '@src/lib/constants'

const ContributorAvatar = ({ contributor }: { contributor: topContributorsType }) => {
  return (
    <a
      data-tooltip-id={`avatar-tooltip-${contributor.login}`}
      data-tooltip-content={`${contributor.contributions_count} contributions by ${contributor.name}`}
      href={`https://github.com/${contributor.login}`}
      target="_blank"
    >
      <img
        className="h-[30px] w-[30px] rounded-full grayscale hover:grayscale-0"
        src={contributor.avatar_url}
      />
      <Tooltip id={`avatar-tooltip-${contributor.login}`} style={tooltipStyle} />
    </a>
  )
}

export default ContributorAvatar
