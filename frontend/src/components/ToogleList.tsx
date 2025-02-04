import { Button } from '@chakra-ui/react'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'

const ToggleableList = ({ items, label, limit = 10 }) => {
  const [showAll, setShowAll] = useState(false)

  const toggleShowAll = () => setShowAll(!showAll)

  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      <h2 className="mb-4 text-2xl font-semibold">{label}</h2>
      <div className="flex flex-wrap gap-2">
        {(showAll ? items : items.slice(0, limit)).map((item, index) => (
          <span
            key={index}
            className="rounded-lg border border-gray-400 px-2 py-1 text-sm dark:border-gray-300"
          >
            {item}
          </span>
        ))}
      </div>
      {items.length > limit && (
        <Button
          onClick={toggleShowAll}
          className="mt-4 flex items-center text-[#1d7bd7] hover:underline dark:text-sky-600"
        >
          {showAll ? (
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
