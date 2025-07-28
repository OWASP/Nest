import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'

const ShowMoreButton = ({
  isExpanded,
  onToggle,
  showMoreText = 'Show more',
  showLessText = 'Show less',
}: {
  isExpanded: boolean
  onToggle: () => void
  showMoreText?: string
  showLessText?: string
}) => (
  <div className="mt-4 flex justify-start">
    <Button
      type="button"
      disableAnimation
      onPress={onToggle}
      className="flex items-center bg-transparent text-blue-400"
    >
      {isExpanded ? (
        <>
          {showLessText} <FontAwesomeIcon icon={faChevronUp} className="ml-2 text-sm" />
        </>
      ) : (
        <>
          {showMoreText} <FontAwesomeIcon icon={faChevronDown} className="ml-2 text-sm" />
        </>
      )}
    </Button>
  </div>
)

export default ShowMoreButton
