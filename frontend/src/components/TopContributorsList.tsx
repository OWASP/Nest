import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'
import type { Contributor } from 'types/contributor'
import { capitalize } from 'utils/capitalize'
import { getMemberUrl } from 'utils/urlFormatter'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

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
      <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-4">
        {displayContributors.map((item, index) => (
          <div key={index} className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
            <div className="flex w-full items-center gap-2">
              <Image
                alt={item?.name || ''}
                className="rounded-full"
                height={24}
                src={`${item?.avatarUrl}&s=60`}
                title={item?.name || item?.login}
                width={24}
              />
              <Link
                className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap font-semibold text-blue-400 hover:underline"
                href={getMemberUrl(item?.login)}
                title={item?.name || item?.login}
              >
                {capitalize(item.name) || capitalize(item.login)}
              </Link>
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

export default TopContributorsList
