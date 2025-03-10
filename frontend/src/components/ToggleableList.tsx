import { Button } from '@chakra-ui/react'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useExpandableList } from 'hooks/useExpandableList'

const ToggleableList = ({
  items,
  label,
  limit = 10,
}: {
  items: string[]
  label: string
  limit?: number
}) => {
  const { visibleItems, showAll, animatingOut, toggleShowAll } = useExpandableList(items, limit)

  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      <h2 className="mb-4 text-2xl font-semibold">{label}</h2>
      <div className="flex flex-wrap gap-2">
        {visibleItems.map((item, index) => (
          <span
            key={index}
            className={`rounded-lg border border-gray-400 px-2 py-1 text-sm transition-all duration-700 ease-in-out dark:border-gray-300 ${
              index >= limit
                ? showAll
                  ? 'animate-fadeIn'
                  : animatingOut
                    ? 'animate-fadeOut'
                    : 'hidden'
                : ''
            }`}
          >
            {item}
          </span>
        ))}
      </div>
      {items.length > limit && (
        <Button
          onClick={toggleShowAll}
          disabled={animatingOut}
          className="mt-4 flex items-center text-[#1d7bd7] transition-all duration-300 hover:underline dark:text-sky-600"
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

export default ToggleableList
