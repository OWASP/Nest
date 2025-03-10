import { Button } from '@chakra-ui/react'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useExpandableList } from 'hooks/useExpandableList'
import { useNavigate } from 'react-router-dom'
import { TopContributorsTypeGraphql } from 'types/contributor'

const TopContributors = ({
  contributors,
  label = 'Top Contributors',
  maxInitialDisplay = 6,
  className = '',
}: {
  contributors: TopContributorsTypeGraphql[]
  label?: string
  maxInitialDisplay?: number
  className?: string
}) => {
  const navigate = useNavigate()
  const { visibleItems, showAll, animatingOut, toggleShowAll } = useExpandableList(
    contributors,
    maxInitialDisplay
  )

  if (contributors.length === 0) {
    return null
  }

  return (
    <div className={`mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 ${className}`}>
      <h2 className="mb-4 text-2xl font-semibold">{label}</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
        {visibleItems.map((contributor, index) => (
          <div
            key={index}
            className={`flex cursor-pointer items-center space-x-3 rounded-lg p-3 transition-all duration-700 ease-in-out hover:bg-gray-200 dark:hover:bg-gray-700 ${index >= maxInitialDisplay ? (showAll ? 'animate-fadeIn' : animatingOut ? 'animate-fadeOut' : 'hidden') : ''}`}
          >
            <img
              src={`${contributor?.avatarUrl}&s=60`}
              alt={contributor.name || contributor.login}
              className="mr-3 h-10 w-10 rounded-full"
            />
            <div>
              <button
                onClick={() => navigate(`/community/users/${contributor.login}`)}
                className="m-0 border-none bg-transparent p-0 font-semibold text-blue-600 hover:underline dark:text-sky-400"
                style={{ all: 'unset', cursor: 'pointer' }}
              >
                {contributor.name || contributor.login}
              </button>
              {contributor?.projectName ? (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  <a
                    href={contributor.projectUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline dark:text-sky-400"
                  >
                    {contributor.projectName}
                  </a>
                </p>
              ) : (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {contributor?.contributionsCount} contributions
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
      {contributors.length > maxInitialDisplay && (
        <Button
          onClick={toggleShowAll}
          disabled={animatingOut}
          className={`mt-4 flex items-center text-[#1d7bd7] transition-all duration-300 hover:underline dark:text-sky-600 ${animatingOut ? 'opacity-70' : 'opacity-100'}`}
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
        </Button>
      )}
    </div>
  )
}

export default TopContributors
