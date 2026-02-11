import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import { FaExclamationCircle } from 'react-icons/fa'
import { FaCodeFork, FaStar } from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import type { RepositoryCardListProps, RepositoryCardProps } from 'types/project'
import InfoItem from 'components/InfoItem'
import ShowMoreButton from 'components/ShowMoreButton'
import StatusBadge from 'components/StatusBadge'
import { TruncatedText } from 'components/TruncatedText'
import { useCardState } from 'hooks/useCardState'

const RepositoryCard: React.FC<RepositoryCardListProps> = ({
  maxInitialDisplay = 4,
  repositories,
}) => {
  const [showAllRepositories, setShowAllRepositories] = useState(false)

  const toggleRepositories = () => setShowAllRepositories(!showAllRepositories)

  const displayedRepositories = showAllRepositories
    ? repositories
    : repositories.slice(0, maxInitialDisplay)
  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {displayedRepositories.map((repository) => {
          return (
            <RepositoryItem
              key={`${repository.organization?.login ?? 'unknown'}-${repository.key}`}
              details={repository}
            />
          )
        })}
      </div>
      {repositories.length > maxInitialDisplay && <ShowMoreButton onToggle={toggleRepositories} />}
    </div>
  )
}

const RepositoryItem = ({ details }: { details: RepositoryCardProps }) => {
  const router = useRouter()
  const cardKey = `${details.organization?.login ?? 'unknown'}-${details.key}`
  const { handleCardClick, isCardActive, isCardVisited } = useCardState(cardKey)

  const handleClick = () => {
    handleCardClick(cardKey)
    router.push(`/organizations/${details.organization?.login}/repositories/${details.key}`)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }

  const cardClasses = `
    flex h-46 w-full flex-col gap-3 rounded-lg border-1 p-4 shadow-xs ease-in-out transition-all duration-150 ease-in-out cursor-pointer
    ${isCardActive 
      ? 'border-blue-400 bg-blue-50 shadow-md scale-[1.02] dark:border-blue-300 dark:bg-blue-900/20' 
      : isCardVisited 
        ? 'border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-800/50' 
        : 'border-gray-200 dark:border-gray-700 dark:bg-gray-800'
    }
    hover:border-gray-300 hover:bg-gray-50 hover:shadow-md hover:scale-[1.01] dark:hover:border-gray-600 dark:hover:bg-gray-800/50
  `

  return (
    <div className={cardClasses}>
      <div className="flex items-start justify-between gap-2">
        <button
          type="button"
          onClick={handleClick}
          onKeyDown={handleKeyDown}
          className={`
            min-w-0 flex-1 cursor-pointer text-start font-semibold transition-all duration-200 ease-in-out focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500
            ${isCardVisited 
              ? 'text-blue-600 dark:text-blue-400' 
              : 'text-blue-400 hover:text-blue-600 hover:underline dark:text-blue-400 dark:hover:text-blue-300'
            }
          `}
        >
          <TruncatedText text={details?.name} />
          {isCardVisited && (
            <span className="ml-2 inline-flex h-2 w-2 rounded-full bg-green-500" title="Visited" />
          )}
        </button>
        {details.isArchived && (
          <div className="flex-shrink-0">
            <StatusBadge status="archived" size="sm" showIcon={false} />
          </div>
        )}
      </div>

      <div className="flex flex-col gap-2 text-sm">
        <InfoItem icon={FaStar} pluralizedName="Stars" unit="Star" value={details.starsCount} />
        <InfoItem icon={FaCodeFork} pluralizedName="Forks" unit="Fork" value={details.forksCount} />
        <InfoItem
          icon={HiUserGroup}
          pluralizedName="Contributors"
          unit="Contributor"
          value={details.contributorsCount}
        />
        <InfoItem
          icon={FaExclamationCircle}
          pluralizedName="Issues"
          unit="Issue"
          value={details.openIssuesCount}
        />
      </div>
    </div>
  )
}

export default RepositoryCard
