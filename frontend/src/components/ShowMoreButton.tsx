import { Button } from '@heroui/button'
import { useState } from 'react'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'

const ShowMoreButton = ({ onToggle }: { onToggle: () => void }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const handleToggle = () => {
    setIsExpanded(!isExpanded)
    onToggle()
  }

  return (
    <div className="mt-4 flex justify-start">
      <Button
        type="button"
        disableAnimation
        onPress={handleToggle}
        className="flex items-center bg-transparent px-2 text-blue-400 hover:underline focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500"
      >
        {isExpanded ? (
          <>
            Show less <FaChevronUp aria-hidden="true" className="ml-2 text-sm" />
          </>
        ) : (
          <>
            Show more <FaChevronDown aria-hidden="true" className="ml-2 text-sm" />
          </>
        )}
      </Button>
    </div>
  )
}

export default ShowMoreButton
