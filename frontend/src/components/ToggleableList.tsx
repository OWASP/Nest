import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import { useRouter } from 'next/navigation'
import { useState, useRef, useEffect } from 'react'

const ToggleableList = ({
  items,
  label,
  limit = 10,
}: {
  items: string[]
  label: string
  limit?: number
}) => {
  const [showAll, setShowAll] = useState(false)
  const [height, setHeight] = useState<number | 'auto'>(0)
  const extraRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  const toggleShowAll = () => {
    if (showAll) {
      setHeight(extraRef.current?.scrollHeight || 0)
      requestAnimationFrame(() => {
        setHeight(0)
      })
    } else {
      const fullHeight = extraRef.current?.scrollHeight || 0
      setHeight(fullHeight)
    }
    setShowAll(!showAll)
  }

  useEffect(() => {
    if (showAll) {
      const timeout = setTimeout(() => setHeight('auto'), 500)
      return () => clearTimeout(timeout)
    }
  }, [showAll])

  const handleButtonClick = ({ item }: { item: string }) => {
    router.push(`/projects?q=${encodeURIComponent(item)}`)
  }
  const visibleItems = items.slice(0, limit)
  const extraItems = items.slice(limit)
  return (
    <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
      <h2 className="mb-4 text-2xl font-semibold">{label}</h2>

      <div className="flex flex-wrap gap-2">
        {visibleItems.map((item, index) => (
          <button
            key={index}
            className="rounded-lg border border-gray-400 px-3 py-1 text-sm transition-all duration-200 ease-in-out hover:scale-105 hover:bg-gray-200 hover:underline dark:border-gray-300 dark:hover:bg-gray-700"
            onClick={() => handleButtonClick({ item })}
          >
            {item}
          </button>
        ))}
      </div>

      <div
        className={`overflow-hidden transition-all duration-500 ease-in-out`}
        style={{
          maxHeight: typeof height === 'number' ? `${height}px` : 'none',
        }}
      >
        <div
          ref={extraRef}
          className={`flex flex-wrap gap-2 ${
            showAll ? 'translate-y-0 opacity-100' : '-translate-y-2 opacity-0'
          } transition-all duration-500 ease-in-out`}
        >
          {extraItems.map((item, index) => (
            <button
              key={index}
              className="mt-2 rounded-lg border border-gray-400 px-3 py-1 text-sm transition-all duration-300 ease-in-out hover:scale-105 hover:bg-gray-200 hover:underline dark:border-gray-300 dark:hover:bg-gray-700"
              onClick={() => handleButtonClick({ item })}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {items.length > limit && (
        <Button
          disableAnimation
          onPress={toggleShowAll}
          className="mt-4 flex items-center bg-transparent text-blue-400 hover:underline"
        >
          {showAll ? (
            <>
              Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
            </>
          ) : (
            <>
              Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
            </>
          )}
        </Button>
      )}
    </div>
  )
}

export default ToggleableList
