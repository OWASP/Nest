import { Button } from '@heroui/button'
import { useEffect, useState } from 'react'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'

type ShowMoreButtonProps = {
  expanded?: boolean
  onToggle: () => void
}

const ShowMoreButton = ({ expanded, onToggle }: ShowMoreButtonProps) => {
  const [expandedState, setExpandedState] = useState(expanded ?? false)
  const isExpanded = expanded ?? expandedState

  useEffect(() => {
    if (expanded !== undefined) {
      setExpandedState(expanded)
    }
  }, [expanded])

  const handleToggle = () => {
    setExpandedState(!isExpanded)
    onToggle()
  }

  return (
    <div className="mt-4 flex justify-start">
      <Button
        type="button"
        aria-expanded={isExpanded}
        disableAnimation
        onPress={handleToggle}
        className="flex items-center bg-transparent px-2 py-1 text-blue-400 hover:underline focus-visible:rounded focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
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
