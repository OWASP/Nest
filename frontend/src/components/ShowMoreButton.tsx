import { Button } from '@heroui/button'
import { FaChevronDown, FaChevronUp } from 'react-icons/fa'

type ShowMoreButtonProps = {
  expanded: boolean
  onToggle: () => void
}

const ShowMoreButton = ({ expanded, onToggle }: ShowMoreButtonProps) => {
  return (
    <div className="mt-4 flex justify-start">
      <Button
        type="button"
        disableAnimation
        onPress={onToggle}
        className="flex items-center bg-transparent px-2 py-1 text-blue-400 hover:underline focus-visible:rounded focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
      >
        {expanded ? (
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
