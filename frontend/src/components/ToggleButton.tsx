import { Button } from '@heroui/button'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'

interface ToggleButtonProps {
  isExpanded: boolean
  onToggle: () => void
  showMoreText?: string
  showLessText?: string
}

const ToggleButton = ({
  isExpanded,
  onToggle,
  showMoreText = "Show more",
  showLessText = "Show less",
}: ToggleButtonProps) => (
  <div className="mt-4 flex justify-start">
    <Button
      type="button"
      disableAnimation
      onPress={onToggle}
      className="bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 border border-blue-200 dark:border-blue-800 rounded-md px-4 py-2 font-medium transition-colors"
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
export default ToggleButton