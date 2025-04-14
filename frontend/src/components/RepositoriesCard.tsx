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
import { useEffect, useRef, useState } from 'react'
import { RepositoriesCardProps, RepositoryCardProps } from 'types/project'
import InfoItem from './InfoItem'
import { TruncatedText } from './TruncatedText'

const RepositoriesCard: React.FC<RepositoriesCardProps> = ({ repositories }) => {
  const [showAllRepositories, setShowAllRepositories] = useState(false)
  const [height, setHeight] = useState<number | 'auto'>(0)
  const extraRef = useRef<HTMLDivElement>(null)

  const toggleShowAll = () => {
    if (showAllRepositories) {
      // closing animation
      setHeight(extraRef.current?.scrollHeight || 0)
      requestAnimationFrame(() => setHeight(0))
    } else {
      // opening animation
      const fullHeight = extraRef.current?.scrollHeight || 0
      setHeight(fullHeight)
    }
    setShowAllRepositories(!showAllRepositories)
  }

  useEffect(() => {
    if (showAllRepositories) {
      const timeout = setTimeout(() => setHeight('auto'), 500)
      return () => clearTimeout(timeout)
    }
  }, [showAllRepositories])

  const firstFour = repositories.slice(0, 4)
  const remaining = repositories.slice(4)

  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {firstFour.map((repository, index) => (
          <RepositoryItem key={index} details={repository} />
        ))}
      </div>

      {/* Animated container */}
      <div
        className="overflow-hidden transition-all duration-500 ease-in-out"
        style={{ maxHeight: typeof height === 'number' ? `${height}px` : 'none' }}
      >
        <div
          ref={extraRef}
          className={`mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 ${
            showAllRepositories ? 'translate-y-0 opacity-100' : '-translate-y-2 opacity-0'
          } transition-all duration-500 ease-in-out`}
        >
          {remaining.map((repository, index) => (
            <RepositoryItem key={index} details={repository} />
          ))}
        </div>
      </div>

      {repositories.length > 4 && (
        <div className="mt-6 flex items-center justify-center text-center">
          <button
            onClick={toggleShowAll}
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
    router.push('/repositories/' + details?.key)
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
        <InfoItem icon={faStar} unit="Star" value={details.starsCount} />
        <InfoItem icon={faCodeFork} unit="Fork" value={details.forksCount} />
        <InfoItem icon={faUsers} unit="Contributor" value={details.contributorsCount} />
        <InfoItem icon={faExclamationCircle} unit="Issue" value={details.openIssuesCount} />
      </div>
    </div>
  )
}

export default RepositoriesCard
