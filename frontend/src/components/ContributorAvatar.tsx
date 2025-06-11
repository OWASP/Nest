import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { memo } from 'react'
import { TopContributors } from 'types/contributor'

type ContributorProps = {
  contributor: TopContributors
  uniqueKey: string
}

const isAlgoliaContributor = (contributor: TopContributors): contributor is TopContributors => {
  return (
    typeof contributor === 'object' &&
    contributor !== null &&
    'avatar_url' in contributor &&
    'contributions_count' in contributor
  )
}

const ContributorAvatar = memo(({ contributor, uniqueKey }: ContributorProps) => {
  const isAlgolia = isAlgoliaContributor(contributor)

  const avatarUrl = isAlgolia ? contributor.avatarUrl : (contributor as TopContributors).avatarUrl

  const contributionsCount = isAlgolia
    ? contributor.contributionsCount
    : (contributor as TopContributors).contributionsCount

  const { login, name } = contributor
  const displayName = name || login

  const repositoryInfo =
    !isAlgolia && (contributor as TopContributors).projectName
      ? ` in ${(contributor as TopContributors).projectName}`
      : ''

  return (
    <Tooltip
      id={`avatar-tooltip-${login}-${uniqueKey}`}
      content={`${contributionsCount} contributions${repositoryInfo} by ${displayName}`}
      delay={100}
      closeDelay={100}
      showArrow
      placement="bottom"
    >
      <Link href={`/members/${login}`} target="_blank" rel="noopener noreferrer">
        <Image
          height={30}
          width={30}
          className="rounded-full grayscale transition-all duration-300 hover:scale-110 hover:grayscale-0"
          src={`${avatarUrl}${isAlgolia ? '&s=60' : ''}`}
          alt={`${displayName}'s avatar`}
        />
      </Link>
    </Tooltip>
  )
})

ContributorAvatar.displayName = 'ContributorAvatar'
export default ContributorAvatar
