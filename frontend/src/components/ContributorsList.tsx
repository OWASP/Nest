import upperFirst from 'lodash/upperFirst'
import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'
import type { IconType } from 'react-icons'
import { twMerge } from 'tailwind-merge'
import type { Contributor } from 'types/contributor'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'
import ShowMoreButton from 'components/ShowMoreButton'

interface ContributorsListProps {
  contributors: Contributor[]
  title?: string
  maxInitialDisplay?: number
  icon?: IconType
  getUrl: (login: string) => string
  className?: string
  gridClassName?: string
}

const ContributorsList = ({
  contributors,
  title: label = 'Contributors',
  maxInitialDisplay = 12,
  icon,
  getUrl,
  className,
  gridClassName,
}: ContributorsListProps) => {
  const [showAllContributors, setShowAllContributors] = useState(false)

  const toggleContributors = () => setShowAllContributors(!showAllContributors)

  const displayContributors = showAllContributors
    ? contributors
    : contributors.slice(0, maxInitialDisplay)

  if (contributors.length === 0) {
    return null
  }

  return (
    <SecondaryCard
      icon={icon}
      title={
        <div className="flex items-center gap-2">
          <AnchorTitle title={label} />
        </div>
      }
      className={className}
    >
      <div
        className={twMerge(
          'grid gap-4',
          !gridClassName && 'sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-4',
          gridClassName
        )}
      >
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
                src={`${item?.avatarUrl}${item?.avatarUrl?.includes('?') ? '&' : '?'}s=60`}
                title={item?.name || item?.login}
                width={24}
              />
              <Link
                className="cursor-pointer overflow-hidden font-semibold text-ellipsis whitespace-nowrap text-blue-400 hover:underline"
                href={getUrl(item?.login)}
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

export default ContributorsList
