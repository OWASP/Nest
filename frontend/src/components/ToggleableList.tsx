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
        <div className="flex items-center">
          <div className="flex items-center space-x-2">
            {icon && <FontAwesomeIcon icon={icon} className="mr-2 h-5 w-5" />}
          </div>
          <span>{label}</span>
        </div>
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
        <div className="mt-4 flex justify-start">
          <Button
            disableAnimation
            onPress={toggleShowAll}
            className="bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-md px-4 py-2 font-medium transition-colors"
          >
            {showAll ? (
              <>
                Show less <FontAwesomeIcon icon={faChevronUp} className="ml-2 text-sm" />
              </>
            ) : (
              <>
                Show more <FontAwesomeIcon icon={faChevronDown} className="ml-2 text-sm" />
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  )
}

export default ToggleableList
