import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import ShowMoreButton from 'components/ShowMoreButton'

const ToggleableList = ({
  items,
  label,
  icon,
  limit = 10,
  isDisabled = false,
}: {
  items: string[]
  label: React.ReactNode
  limit?: number
  icon?: IconDefinition
  isDisabled?: boolean
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
          <div className="flex flex-row items-center gap-2">
            {icon && <FontAwesomeIcon icon={icon} className="mr-2 h-5 w-5" />}
          </div>
          <span>{label}</span>
        </div>
      </h2>
      <div className="flex flex-wrap gap-2">
        {(showAll ? items : items.slice(0, limit)).map((item) => (
          <button
            key={item}
            type="button"
            className="rounded-lg border border-gray-400 px-3 py-1 text-sm hover:bg-gray-200 dark:border-gray-300 dark:hover:bg-gray-700 focus:outline-none focus-visible:ring-1 focus-visible:ring-offset-1 transition"
            onClick={() => !isDisabled && handleButtonClick({ item })}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                if (!isDisabled) handleButtonClick({ item })
              }
            }}
            aria-label={`Search for projects with ${item}`}
            disabled={isDisabled}
          >
            {item}
          </button>
        ))}
      </div>
      {items.length > limit && <ShowMoreButton onToggle={toggleShowAll} />}
    </div>
  )
}

export default ToggleableList
