import { Button } from '@chakra-ui/react'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const ToggleableList = ({
  items,
  label,
  limit = 10,
}: {
  items: string[]
  label: string
  limit?: number
}) => {
  const [showAll, setShowAll] = useState(false)
  const navigate = useNavigate()

  const toggleShowAll = () => setShowAll(!showAll)
  const handleButtonClick = ({ item }) => {
    navigate(`/projects?q=${encodeURIComponent(item)}`)
  }
  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      <h2 className="mb-4 text-2xl font-semibold">{label}</h2>
      <div className="flex flex-wrap gap-2">
        {(showAll ? items : items.slice(0, limit)).map((item, index) => (
          <button
            key={index}
            className="rounded-lg border border-gray-400 px-3 py-1 text-sm transition-all duration-200 ease-in-out hover:scale-105 hover:bg-gray-200 hover:underline dark:border-gray-300 dark:hover:bg-gray-700"
            onClick={() => handleButtonClick({ item })}
          >
            {item}
          </button>
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
