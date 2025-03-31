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
import InfoItem from './InfoItem'
import { useState } from 'react'
import { RepositoriesCardProps } from 'types/project'
import { TruncatedText } from './TruncatedText'

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
            className="mt-4 flex items-center justify-center text-[#1d7bd7] hover:underline dark:text-sky-600"
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

const RepositoryItem = ({ details }) => {
  const router = useRouter()
  const handleClick = () => {
    router.push('/repositories/' + details?.key)
  }
  return (
    <div className="h-46 flex w-full flex-col gap-3 rounded-lg border p-4 shadow-sm ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <button
        onClick={handleClick}
        className="text-start font-semibold text-blue-500 hover:underline dark:text-blue-400"
      >
        <TruncatedText text={details?.name} />
      </button>

      <div className="space-y-2 text-sm">
        <InfoItem icon={faStar} unit="Star" value={details.starsCount} />
        <InfoItem icon={faCodeFork} unit="Fork" value={details.forksCount} />
        <InfoItem icon={faUsers} unit="Contributor" value={details.contributorsCount} />
        <InfoItem icon={faExclamationCircle} unit="Issue" value={details.openIssuesCount} />
      </div>
    </div>
  )
}

export default RepositoriesCard
