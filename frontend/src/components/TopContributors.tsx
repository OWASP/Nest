import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'
import { TopContributorsTypeGraphql } from 'types/contributor'
import { capitalize } from 'utils/capitalize'
import { getMemberUrl, getProjectUrl } from 'utils/urlFormatter'
import SecondaryCard from './SecondaryCard'

const TopContributors = ({
  contributors,
  label = 'Top Contributors',
  maxInitialDisplay = 6,
  type,
  icon,
}: {
  contributors: TopContributorsTypeGraphql[]
  label?: string
  maxInitialDisplay?: number
  type: string
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
  const isContributor = type === 'contributor'

  return (
    <SecondaryCard icon={icon} title={label}>
      <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-3">
        {displayContributors.map((item, index) => (
          <div key={index} className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
            <div className="flex w-full flex-col justify-between">
              <div className="flex w-full items-center gap-2">
                <Image
                  src={`${item?.avatarUrl}&s=60`}
                  width={24}
                  height={24}
                  alt={item?.name || ''}
                  className="rounded-full"
                />
                <Link
                  className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap font-semibold text-blue-400 hover:underline"
                  href={getMemberUrl(item?.login)}
                >
                  {capitalize(item.name) || capitalize(item.login)}
                </Link>
              </div>
              <div className="ml-0.5 w-full">
                <div className="mt-2 flex flex-shrink-0 items-center text-sm text-gray-600 dark:text-gray-400">
                  {isContributor ? (
                    <span className="overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 dark:text-gray-400">
                      {' '}
                      {`${item.contributionsCount ?? 0} contributions`}
                    </span>
                  ) : (
                    <Link
                      className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 hover:underline dark:text-gray-400"
                      href={getProjectUrl(item?.projectUrl)}
                    >
                      {' '}
                      {item.projectName}
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      {contributors.length > maxInitialDisplay && (
        <Button
          disableAnimation
          onPress={toggleContributors}
          className="mt-4 flex items-center bg-transparent text-blue-400 hover:underline"
        >
          {showAllContributors ? (
            <>
              Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
            </>
          ) : (
            <>
              Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
            </>
          )}
        </Button>
      )}
    </SecondaryCard>
  )
}

export default TopContributors
