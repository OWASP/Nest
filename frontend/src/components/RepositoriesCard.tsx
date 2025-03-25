import {
  faCodeFork,
  faStar,
  faUsers,
  faExclamationCircle,
  faChevronDown,
  faChevronUp,
  IconDefinition,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import millify from 'millify'
import type React from 'react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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
  const navigate = useNavigate()
  const handleClick = () => {
    navigate('/repositories/' + details?.key)
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
        <InfoItem
          icon={faStar}
          label="Stars"
          value={millify(details.starsCount, { precision: 1 })}
        />
        <InfoItem
          icon={faCodeFork}
          label="Forks"
          value={millify(details.forksCount, { precision: 1 })}
        />
        <InfoItem
          icon={faUsers}
          label="Contributors"
          value={millify(details.contributorsCount, { precision: 1 })}
        />
        <InfoItem
          icon={faExclamationCircle}
          label="Issues"
          value={millify(details.openIssuesCount, { precision: 1 })}
        />
      </div>
    </div>
  )
}

const InfoItem: React.FC<{ icon: IconDefinition; label: string; value: string }> = ({
  icon,
  label,
  value,
}) => (
  <div className="flex items-center justify-between">
    <span className="flex items-center">
      <FontAwesomeIcon icon={icon} className="mr-2 h-4 w-4" />
      {label}
    </span>
    <span className="font-medium">{value.toLocaleString()}</span>
  </div>
)

export default RepositoriesCard
