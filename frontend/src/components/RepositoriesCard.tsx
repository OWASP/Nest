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
import { useExpandableList } from 'hooks/useExpandableList'
import millify from 'millify'
import type React from 'react'
import { useNavigate } from 'react-router-dom'
import { RepositoriesCardProps } from 'types/project'

const RepositoriesCard: React.FC<RepositoriesCardProps> = ({ repositories }) => {
  const { visibleItems, showAll, animatingOut, toggleShowAll } = useExpandableList(repositories, 4)

  return (
    <div id="repositories" className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      <h2 className="mb-4 text-2xl font-semibold">Repositories</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {visibleItems.map((repository, index) => (
          <div
            key={index}
            className={`transition-all duration-700 ease-in-out ${
              index >= 4
                ? showAll
                  ? 'animate-fadeIn'
                  : animatingOut
                    ? 'animate-fadeOut'
                    : 'hidden'
                : ''
            }`}
          >
            <RepositoryItem details={repository} />
          </div>
        ))}
      </div>
      <section />

      {repositories.length > 4 && (
        <div className="mt-6 flex items-center justify-center text-center">
          <button
            onClick={toggleShowAll}
            disabled={animatingOut}
            className="mt-4 flex items-center justify-center text-[#1d7bd7] transition-all duration-300 hover:underline dark:text-sky-600"
          >
            {showAll || animatingOut ? (
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
    navigate(window.location.pathname + '/repositories/' + details?.key)
  }
  return (
    <div className="flex h-48 w-full flex-col justify-between rounded-lg border p-4 shadow-sm ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800">
      <button
        onClick={handleClick}
        className="font-semibold text-blue-600 hover:cursor-pointer hover:underline dark:text-sky-400"
      >
        {details?.name}
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
