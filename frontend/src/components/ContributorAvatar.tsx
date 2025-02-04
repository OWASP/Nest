import { Link } from '@chakra-ui/react'
import { memo } from 'react'
import { topContributorsType } from 'types/contributor'
import { Tooltip } from 'components/ui/tooltip'

const ContributorAvatar = memo(({ contributor }: { contributor: topContributorsType }) => {
  const displayName = contributor.name || contributor.login

  return (
    <Tooltip
      id={`avatar-tooltip-${contributor.login}`}
      content={`${contributor.contributions_count} contributions by ${displayName}`}
      openDelay={100}
      closeDelay={100}
      showArrow
      positioning={{ placement: 'top' }}
    >
      <Link
        href={`/community/users/${contributor.login}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <img
          className="h-[30px] w-[30px] rounded-full grayscale hover:grayscale-0"
          src={`${contributor.avatar_url}&s=60`}
          alt={`${displayName}'s avatar`}
        />
      </Link>
    </Tooltip>
  )
})

export default ContributorAvatar
