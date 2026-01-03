import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import type { IconType } from 'react-icons'
import { IconWrapper } from 'wrappers/IconWrapper'
import ShowMoreButton from 'components/ShowMoreButton'

const ToggleableList = <T,>({
  items,
  label,
  icon,
  limit = 10,
  isDisabled = false,
  renderItem,
}: {
  items: T[]
  label?: React.ReactNode
  limit?: number
  icon?: IconType
  isDisabled?: boolean
  renderItem: (item: T, index: number, items: T[]) => React.ReactNode
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
            {icon && <IconWrapper icon={icon} className="mr-2 h-5 w-5" />}
          </div>
          <span>{label}</span>
        </div>
      </h2>
      <div className="flex flex-wrap gap-2">
      {(showAll ? items : items.slice(0, limit)).map(renderItem)}
      </div>
      {items.length > limit && <ShowMoreButton onToggle={toggleShowAll} />}
    </div>
  )
}

export default ToggleableList
