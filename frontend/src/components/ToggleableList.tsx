import { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { useRouter } from 'next/navigation'
import React, { useState } from 'react'

const ToggleableList = ({
  items,
  label,
  icon,
  limit = 10,
}: {
  items: string[]
  label: React.ReactNode
  limit?: number
  icon?: IconDefinition
}) => {
  const [showAll, setShowAll] = useState(false)
  const router = useRouter()

  const toggleShowAll = () => setShowAll(!showAll)
  const handleButtonClick = ({ item }: { item: string }) => {
    router.push(`/projects?q=${encodeURIComponent(item)}`)
  }
  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      <h2 className="mb-4 text-2xl font-semibold">
        {icon && <FontAwesomeIcon icon={icon} className="mr-2 h-5 w-5" />}
        {label}
      </h2>
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
          disableAnimation
          onPress={toggleShowAll}
          className="mt-4 flex items-center bg-transparent text-blue-400 hover:underline"
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
