import React, { useState } from 'react'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
import ShowMoreButton from 'components/ShowMoreButton'

type ToggleableListProps<T> = {
  items: T[]
  label?: React.ReactNode
  icon?: IconType
  limit?: number
  isDisabled?: boolean
  renderItem: (item: T, index: number, visibleCount: number) => React.ReactNode
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
  const visibleCount = visibleItems.length

  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      {label && (
        <h2 className="mb-4 text-2xl font-semibold">
          <div className="flex items-center">
            {icon && <IconWrapper icon={icon} className="mr-2 h-5 w-5" />}
            <span>{label}</span>
          </div>
        </h2>
      )}

      <div className="flex flex-wrap gap-2">
        {visibleItems.map((item, index) => (
          <div
            key={index}
            aria-disabled={isDisabled}
            className={isDisabled ? 'pointer-events-none opacity-60' : undefined}
          >
            {renderItem(item, index, visibleCount)}
          </div>
        ))}
      </div>

      {items.length > limit && !isDisabled && (
        <ShowMoreButton onToggle={() => setShowAll((v) => !v)} />
      )}
    </div>
  )
}

export default ToggleableList
