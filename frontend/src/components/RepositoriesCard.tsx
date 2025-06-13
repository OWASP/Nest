import {
  faCodeFork,
  faStar,
  faUsers,
  faExclamationCircle,
  faChevronDown,
  faChevronUp,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import type { RepositoriesCardProps, RepositoryCardProps } from 'types/project'
import InfoItem from 'components/InfoItem'
import { TruncatedText } from 'components/TruncatedText'

const RepositoriesCard: React.FC<RepositoriesCardProps> = ({ repositories }) => {
  const [showAllRepositories, setShowAllRepositories] = useState(false)

  const displayedRepositories = showAllRepositories ? repositories : repositories.slice(0, 4)

  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {displayedRepositories.map((repository, index) => {
          return <RepositoryItem key={index} details={repository} />
        })}
      </div>
      {repositories.length > 4 && (
        <div className="mt-6 flex items-center justify-center text-center">
          <button
            onClick={() => setShowAllRepositories(!showAllRepositories)}
            className="mt-4 flex items-center justify-center text-blue-400 hover:underline"
          >
            {showAllRepositories ? (
              <>
                Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
              </>
            ) : (
              <>
                Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
              </>
            )}
          </button>
        </div>
      )}
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
        <InfoItem icon={faStar} pluralizedName="Stars" unit="Stars" value={details.starsCount} />
        <InfoItem
          icon={faCodeFork}
          pluralizedName="Forks"
          unit="Forks"
          value={details.forksCount}
        />
        <InfoItem
          icon={faUsers}
          pluralizedName="Contributors"
          unit="Contributors"
          value={details.contributorsCount}
        />
        <InfoItem
          icon={faExclamationCircle}
          pluralizedName="Issues"
          unit="Issues"
          value={details.openIssuesCount}
        />
      </div>
    </div>
  )
}

export default RepositoriesCard
