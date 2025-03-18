import { Button } from '@chakra-ui/react'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState, JSX } from 'react'
import { capitalize } from 'utils/capitalize'

import { useNavigate } from 'react-router-dom'
import { TopContributorsTypeGraphql } from 'types/contributor'
const TopContributors = ({
  contributors,
  label = 'Top Contributors',
  maxInitialDisplay = 6,
  className = '',
  renderDetails
}: {
  contributors: TopContributorsTypeGraphql[]
  label?: string
  maxInitialDisplay?: number
  className?: string
  renderDetails: (item: { contributionsCount: number; projectName?: string }) => JSX.Element
}) => {
  const navigate = useNavigate()
  const [showAllContributors, setShowAllContributors] = useState(false)

  const toggleContributors = () => setShowAllContributors(!showAllContributors)

  const displayContributors = showAllContributors
    ? contributors
    : contributors.slice(0, maxInitialDisplay)

  if (contributors.length === 0) {
    return
  }
  return (
    <div className={`mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 ${className}`}>
      <h2 className="mb-4 text-2xl font-semibold">{label}</h2>
      <div className="grid gap-x-5 sm:grid-cols-2 md:grid-cols-3">
        {displayContributors.map((item, index) => (  
          <button
            key={index}
            data-testid="top-contributor"
            onClick={() => navigate(`/community/users/${item.login}`)}
            className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
          >
            <div className="flex w-full flex-col justify-between">
              <div className="flex w-full items-center gap-2">
                <img src={item?.avatarUrl} alt={item?.name} className="h-6 w-6 rounded-full" />
                <h3 className="overflow-hidden text-ellipsis whitespace-nowrap font-semibold text-blue-500">
                  {capitalize(item.name) || capitalize(item.login)}
                </h3>
              </div>
              <div className="ml-0.5 w-full">{renderDetails(item)}</div>
            </div>
          </button>
        ))}
      </div>
      {contributors.length > maxInitialDisplay && (
        <Button
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
        </Button>
      )}
    </div>
  )
}

export default TopContributors
