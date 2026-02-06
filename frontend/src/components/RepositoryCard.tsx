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
  const handleClick = () => {
    router.push(`/organizations/${details.organization?.login}/repositories/${details.key}`)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }

  return (
    <div className="flex h-46 w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <div className="flex items-start justify-between gap-2">
        <button
          type="button"
          onClick={handleClick}
          onKeyDown={handleKeyDown}
          className="min-w-0 flex-1 cursor-pointer text-start font-semibold text-blue-300 hover:underline focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500"
        >
          <TruncatedText text={details?.name} />
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
