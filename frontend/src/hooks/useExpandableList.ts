import { useState, useEffect } from 'react'

export const useExpandableList = <T>(items: T[], maxInitialDisplay: number) => {
  const [showAll, setShowAll] = useState(false)
  const [animatingOut, setAnimatingOut] = useState(false)
  const [visibleItems, setVisibleItems] = useState<T[]>(items.slice(0, maxInitialDisplay))

  useEffect(() => {
    if (showAll) {
      setVisibleItems(items)
      setAnimatingOut(false)
    } else if (animatingOut) {
      const timer = setTimeout(() => {
        setVisibleItems(items.slice(0, maxInitialDisplay))
        setAnimatingOut(false)
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [showAll, animatingOut, items, maxInitialDisplay])

  const toggleShowAll = () => {
    if (showAll) {
      setAnimatingOut(true)
      setTimeout(() => setShowAll(false), 50)
    } else {
      setShowAll(true)
    }
  }

  return { visibleItems, showAll, animatingOut, toggleShowAll }
}
