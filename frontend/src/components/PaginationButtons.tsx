import { FaChevronDown, FaChevronUp } from 'react-icons/fa6'

interface PaginationButtonsProps {
  onShowMore: () => void
  onShowLess: () => void
  showMore: boolean
  showLess: boolean
  isLoading: boolean
}

const PaginationButtons = ({
  onShowMore,
  onShowLess,
  showMore,
  showLess,
  isLoading,
}: PaginationButtonsProps) => {
  if (!showMore && !showLess) return null

  return (
    <div className="mt-4 flex justify-start gap-4">
      {showMore && (
        <button
          disabled={isLoading}
          onClick={onShowMore}
          type="button"
          className={`flex items-center bg-transparent px-2 py-1 text-sm text-blue-400 ${isLoading ? 'cursor-not-allowed opacity-50' : 'hover:underline'}`}
        >
          {isLoading ? 'Loading...' : 'Show more'}{' '}
          <FaChevronDown aria-hidden="true" className="ml-2 text-sm" />
        </button>
      )}
      {showLess && (
        <button
          disabled={isLoading}
          onClick={onShowLess}
          type="button"
          className={`flex items-center bg-transparent px-2 py-1 text-sm text-blue-400 hover:underline ${isLoading ? 'cursor-not-allowed opacity-50' : ''}`}
        >
          Show less <FaChevronUp aria-hidden="true" className="ml-2 text-sm" />
        </button>
      )}
    </div>
  )
}

export default PaginationButtons
