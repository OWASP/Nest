import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { TopContributorsTypeGraphql } from 'types/contributor'
import { capitalize } from 'utils/capitalize'
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
  const router = useRouter()
  const [showAllContributors, setShowAllContributors] = useState(false)

  const toggleContributors = () => setShowAllContributors(!showAllContributors)

  const displayContributors = showAllContributors
    ? contributors
    : contributors.slice(0, maxInitialDisplay)

  if (contributors.length === 0) {
    return
  }
  return (
    <SecondaryCard icon={icon} title={label}>
      <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-3">
        {displayContributors.map((item, index) => (
          <button
            key={index}
            onClick={() => router.push(`/members/${item.login}`)}
            className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
          >
            <div className="flex w-full flex-col justify-between">
              <div className="flex w-full items-center gap-2">
                <Image
                  src={`${item?.avatarUrl}&s=60`}
                  width={24}
                  height={24}
                  alt={item?.name || ''}
                  className="rounded-full"
                />
                <h3 className="overflow-hidden text-ellipsis whitespace-nowrap font-semibold text-blue-400">
                  {capitalize(item.name) || capitalize(item.login)}
                </h3>
              </div>
              <div className="ml-0.5 w-full">
                <div className="mt-2 flex flex-shrink-0 items-center text-sm text-gray-600 dark:text-gray-400">
                  <span className="overflow-hidden text-ellipsis whitespace-nowrap">
                    {type === 'contributor'
                      ? `${item.contributionsCount ?? 0} contributions`
                      : item.projectName}
                  </span>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
      {contributors.length > maxInitialDisplay && (
        <Button
          disableAnimation
          onPress={toggleContributors}
          className="mt-4 flex items-center bg-transparent px-0 text-blue-400 hover:underline"
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
