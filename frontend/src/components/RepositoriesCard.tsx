import { faCodeFork, faStar, faUsers, faExclamationCircle } from '@fortawesome/free-solid-svg-icons'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import type { RepositoriesCardProps, RepositoryCardProps } from 'types/project'
import InfoItem from 'components/InfoItem'
import ShowMoreButton from 'components/ShowMoreButton'
import { TruncatedText } from 'components/TruncatedText'

const RepositoriesCard: React.FC<RepositoriesCardProps> = ({
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
        {displayedRepositories.map((repository, index) => {
          return <RepositoryItem key={index} details={repository} />
        })}
      </div>
      {repositories.length > maxInitialDisplay && <ShowMoreButton onToggle={toggleRepositories} />}
    </div>
  )
}

const RepositoryItem = ({ details }: { details: RepositoryCardProps }) => {
  const router = useRouter()
  const handleClick = () => {
    router.push(`/organizations/${details.organization.login}/repositories/${details.key}`)
  }

  return (
    <div className="h-46 flex w-full flex-col gap-3 rounded-lg border p-4 shadow-sm ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <button
        onClick={handleClick}
        className="text-start font-semibold text-blue-400 hover:underline"
      >
        <TruncatedText text={details?.name} />
      </button>

      <div className="space-y-2 text-sm">
        <InfoItem icon={faStar} pluralizedName="Stars" unit="Star" value={details.starsCount} />
        <InfoItem icon={faCodeFork} pluralizedName="Forks" unit="Fork" value={details.forksCount} />
        <InfoItem
          icon={faUsers}
          pluralizedName="Contributors"
          unit="Contributor"
          value={details.contributorsCount}
        />
        <InfoItem
          icon={faExclamationCircle}
          pluralizedName="Issues"
          unit="Issue"
          value={details.openIssuesCount}
        />
      </div>
    </div>
  )
}

export default RepositoriesCard
