import type { IconProp } from '@fortawesome/fontawesome-svg-core'
import upperFirst from 'lodash/upperFirst'
import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'
import type { Contributor } from 'types/contributor'
import { getMemberUrl } from 'utils/urlFormatter'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'
import ShowMoreButton from 'components/ShowMoreButton'

const TopContributorsList = ({
  contributors,
  label = 'Top Contributors',
  maxInitialDisplay = 12,
  icon,
}: {
  contributors: Contributor[]
  label?: string
  maxInitialDisplay?: number
  icon?: IconProp
}) => {
  const [showAllContributors, setShowAllContributors] = useState(false)

  const toggleContributors = () => setShowAllContributors(!showAllContributors)

  const displayContributors = showAllContributors
    ? contributors
    : contributors.slice(0, maxInitialDisplay)

  if (contributors.length === 0) {
    return
  }

  return (
    <SecondaryCard
      icon={icon}
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title={label} className="flex items-center" />
        </div>
      }
    >
      <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-4">
        {displayContributors.map((item) => (
          <div
            key={item.login}
            className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
          >
            <div className="flex w-full items-center gap-2">
              <Image
                alt={item?.name ? `${item.name}'s avatar` : 'Contributor avatar'}
                className="rounded-full"
                height={24}
                src={`${item?.avatarUrl}&s=60`}
                title={item?.name || item?.login}
                width={24}
              />
              <Link
                className="cursor-pointer overflow-hidden font-semibold text-ellipsis whitespace-nowrap text-blue-400 hover:underline"
                href={getMemberUrl(item?.login)}
                title={item?.name || item?.login}
              >
                {upperFirst(item.name) || upperFirst(item.login)}
              </Link>
            </div>
          </div>
        ))}
      </div>
      {contributors.length > maxInitialDisplay && <ShowMoreButton onToggle={toggleContributors} />}
    </SecondaryCard>
  )
}

export default TopContributorsList
