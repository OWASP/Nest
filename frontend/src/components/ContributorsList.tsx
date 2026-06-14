import upperFirst from 'lodash/upperFirst'
import Image from 'next/image'

import { useState } from 'react'
import type { IconType } from 'react-icons'
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
  variant?: 'compact' | 'card'
}

const ContributorsList = ({
  contributors,
  title: label = 'Contributors',
  maxInitialDisplay = 12,
  icon,
  getUrl,
  variant = 'compact',
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
    >
      <div
        className={
          variant === 'card'
            ? 'grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6'
            : 'grid gap-4 sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-4'
        }
      >
        {displayContributors.map((item) =>
          variant === 'card' ? (
            <a
              key={item.login}
              href={getUrl(item.login)}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
            >
              <Image
                src={`${item.avatarUrl}${item.avatarUrl.includes('?') ? '&' : '?'}s=128`}
                alt={item.login}
                width={64}
                height={64}
                className="h-16 w-16 rounded-full"
              />
              <span className="mt-2 text-center text-sm font-medium text-gray-800 dark:text-gray-100">
                {item.name || item.login}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">@{item.login}</span>
            </a>
          ) : (
            <a
              key={item.login}
              href={getUrl(item.login)}
              target="_blank"
              rel="noopener noreferrer"
              className="overflow-hidden rounded-lg bg-gray-200 p-4 transition-opacity hover:opacity-80 dark:bg-gray-700"
              data-testid="contributor-link"
              title={item?.name || item?.login}
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
                <span
                  className="cursor-pointer overflow-hidden font-semibold text-ellipsis whitespace-nowrap text-blue-400 group-hover:underline"
                  data-testid="contributor-name"
                >
                  {upperFirst(item.name) || upperFirst(item.login)}
                </span>
              </div>
            </a>
          )
        )}
      </div>
      {contributors.length > maxInitialDisplay && <ShowMoreButton onToggle={toggleContributors} />}
    </SecondaryCard>
  )
}

export default ContributorsList
