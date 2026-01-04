import { useState } from 'react'
import type React from 'react'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
import ShowMoreButton from 'components/ShowMoreButton'

type ToggleableListProps<T> = {
  items: T[]
  label?: React.ReactNode
  icon?: IconType
  limit?: number
  isDisabled?: boolean
  renderItem: (item: T, index: number, items: T[]) => React.ReactNode
}

const ToggleableList = <T,>({
  items,
  label,
  icon,
  limit = 10,
  isDisabled = false,
  renderItem,
}: ToggleableListProps<T>) => {
  const [showAll, setShowAll] = useState(false)

  const visibleItems = showAll ? items : items.slice(0, limit)

  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      {label && (
        <h2 className="mb-4 text-2xl font-semibold">
          <div className="flex items-center">
            {icon && (
              <div className="flex flex-row items-center gap-2">
                <IconWrapper icon={icon} className="mr-2 h-5 w-5" />
              </div>
            )}
            <span>{label}</span>
          </div>
        </h2>
      )}

      <div className="flex flex-wrap gap-2">
        {visibleItems.map((item, index) => renderItem(item, index, items))}
      </div>

      {items.length > limit && (
        <ShowMoreButton onToggle={() => setShowAll(!showAll)} />
      )}
    </div>
  )
}

export default ToggleableList
