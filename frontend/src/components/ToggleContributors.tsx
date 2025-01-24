import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
const TopContributors = ({
  contributors,
  label = 'Top Contributors',
  maxInitialDisplay = 6,
  className = '',
}) => {
  const navigate = useNavigate()
  const [showAllContributors, setShowAllContributors] = useState(false)

  const toggleContributors = () => setShowAllContributors(!showAllContributors)

  const displayContributors = showAllContributors
    ? contributors
    : contributors.slice(0, maxInitialDisplay)

  return (
    <div className={`mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 ${className}`}>
      <h2 className="mb-4 text-2xl font-semibold">{label}</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
        {displayContributors.map((contributor, index) => (
          <div
            key={index}
            onClick={() => navigate(`/community/users/${contributor.login}`)}
            className="flex cursor-pointer items-center space-x-3 rounded-lg p-3 hover:bg-gray-200 dark:hover:bg-gray-700"
          >
            <img
              src={contributor.avatar_url}
              alt={contributor.name || contributor.login}
              className="mr-3 h-10 w-10 rounded-full"
            />
            <div>
              <p className="font-semibold text-blue-600 hover:underline dark:text-sky-400">
                {contributor.name || contributor.login}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {contributor.contributions_count} contributions
              </p>
            </div>
          </div>
        ))}
      </div>
      {contributors.length > maxInitialDisplay && (
        <button
          onClick={toggleContributors}
          className="mt-4 flex items-center text-[#1d7bd7] hover:underline dark:text-sky-600"
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
        </button>
      )}
    </div>
  )
}

export default TopContributors
