import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { memo } from 'react'
import { TopContributorsTypeAlgolia, TopContributorsTypeGraphql } from 'types/contributor'
type ContributorProps = {
  contributor: TopContributorsTypeAlgolia | TopContributorsTypeGraphql
  uniqueKey: string
}

const isAlgoliaContributor = (
  contributor: TopContributorsTypeAlgolia | TopContributorsTypeGraphql
): contributor is TopContributorsTypeAlgolia => {
  return (
    typeof contributor === 'object' &&
    contributor !== null &&
    'avatar_url' in contributor &&
    'contributions_count' in contributor
  )
}

const ContributorAvatar = memo(({ contributor, uniqueKey }: ContributorProps) => {
  const isAlgolia = isAlgoliaContributor(contributor)

  const avatarUrl = isAlgolia
    ? contributor.avatar_url
    : (contributor as TopContributorsTypeGraphql).avatarUrl

  const contributionsCount = isAlgolia
    ? contributor.contributions_count
    : (contributor as TopContributorsTypeGraphql).contributionsCount

  const { login, name } = contributor
  const displayName = name || login

  const repositoryInfo =
    !isAlgolia && (contributor as TopContributorsTypeGraphql).projectName
      ? ` in ${(contributor as TopContributorsTypeGraphql).projectName}`
      : ''

  return (
    <Tooltip
      id={`avatar-tooltip-${login}-${uniqueKey}`}
      content={`${contributionsCount} contributions${repositoryInfo} by ${displayName}`}
      delay={100}
      closeDelay={100}
      showArrow
      placement="top"
    >
      <Link href={`/community/users/${login}`} target="_blank" rel="noopener noreferrer">
        <Image
          height={30}
          width={30}
          className="rounded-full grayscale hover:grayscale-0"
          src={`${avatarUrl}${isAlgolia ? '&s=60' : ''}`}
          alt={`${displayName}'s avatar`}
        />
      </Link>
    </Tooltip>
  )
})

ContributorAvatar.displayName = 'ContributorAvatar'

export default ContributorAvatar
