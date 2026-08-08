import { type RefObject, useEffect, useState } from 'react'

export type ProfileSelection = {
  text: string
  rect: DOMRect
}

export const useProfileSelection = (
  containerRef: RefObject<HTMLElement | null>,
  enabled: boolean
): ProfileSelection | null => {
  const [selection, setSelection] = useState<ProfileSelection | null>(null)

  useEffect(() => {
    if (!enabled) {
      setSelection(null)
      return
    }

    const handleSelectionChange = () => {
      const container = containerRef.current
      const active = window.getSelection()

      if (!container || !active || active.rangeCount === 0 || active.isCollapsed) {
        setSelection(null)
        return
      }

      const range = active.getRangeAt(0)
      if (!container.contains(range.startContainer) || !container.contains(range.endContainer)) {
        setSelection(null)
        return
      }

      const text = active.toString().trim()
      if (!text) {
        setSelection(null)
        return
      }

      setSelection({ text, rect: range.getBoundingClientRect() })
    }

    document.addEventListener('selectionchange', handleSelectionChange)
    return () => document.removeEventListener('selectionchange', handleSelectionChange)
  }, [containerRef, enabled])

  return selection
}
