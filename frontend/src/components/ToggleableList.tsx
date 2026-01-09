import { useEffect, useRef, useState } from 'react'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
import ShowMoreButton from 'components/ShowMoreButton'

type ToggleableListProps<T> = {
  items: T[]
  label?: React.ReactNode
  icon?: IconType
  limit?: number
  isDisabled?: boolean
  keyExtractor?: (item: T, index: number) => string | number
  renderItem: (item: T, index: number, visibleCount: number) => React.ReactNode
}

const ToggleableList = <T,>({
  items,
  label,
  icon,
  limit = 10,
  isDisabled = false,
  keyExtractor,
  renderItem,
}: ToggleableListProps<T>) => {
  const [showAll, setShowAll] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)

  const safeLimit = Number.isFinite(limit) && limit > 0 ? limit : items.length
  const visibleItems = showAll ? items : items.slice(0, safeLimit)
  const visibleCount = visibleItems.length

  useEffect(() => {
    if (containerRef.current) {
      if (isDisabled) {
        containerRef.current.setAttribute('inert', '')
      } else {
        containerRef.current.removeAttribute('inert')
      }
    }
  }, [isDisabled])

  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      {label && (
        <h2 className="mb-4 text-2xl font-semibold">
          <span className="flex items-center">
            {icon && <IconWrapper icon={icon} className="mr-2 h-5 w-5" />}
            <span>{label}</span>
          </span>
        </h2>
      )}

      <div
        ref={containerRef}
        className="flex flex-wrap gap-2"
        aria-disabled={isDisabled}
      >
        {visibleItems.map((item, index) => (
          <div
            key={keyExtractor ? keyExtractor(item, index) : `${index}`}
            className={isDisabled ? 'pointer-events-none opacity-60' : undefined}
          >
            {renderItem(item, index, visibleCount)}
          </div>
        ))}
      </div>

      {items.length > safeLimit && !isDisabled && (
        <ShowMoreButton
          expanded={showAll}
          onToggle={() => setShowAll((v) => !v)}
        />
      )}
    </div>
  )
}

export default ToggleableList
