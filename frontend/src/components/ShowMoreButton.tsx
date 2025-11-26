import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { useState } from 'react'

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
        onKeyDown={(e: React.KeyboardEvent) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            handleToggle()
          }
        }}
        aria-expanded={isExpanded}
        aria-label={isExpanded ? 'Show less items' : 'Show more items'}
        className="flex items-center bg-transparent px-0 text-blue-400 focus:outline-none focus-visible:ring-1 focus-visible:ring-offset-1"
      >
        {isExpanded ? (
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
  )
}

export default ShowMoreButton
