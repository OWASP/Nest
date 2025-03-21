import { useRef, useState, useEffect, useCallback } from 'react'
import { Tooltip } from 'components/ui/tooltip'

export const TruncatedText = ({
  text,
  className = '',
  disabledTooltip = false,
}: {
  text: string
  className?: string
  disabledTooltip?: boolean
}) => {
  const textRef = useRef<HTMLSpanElement>(null)
  const [isTruncated, setIsTruncated] = useState(false)

   const checkTruncation = useCallback(() => {
    const element = textRef.current
    if (element) {
      setIsTruncated(element.scrollWidth > element.clientWidth)
    }
  }, [])



  useEffect(() => {
    checkTruncation()

    window.addEventListener('resize', checkTruncation) // Recalculate on resize
    return () => window.removeEventListener('resize', checkTruncation)
  }, [text, checkTruncation])

  return (
    <Tooltip content={text} disabled={!isTruncated || disabledTooltip}>
      <span
        ref={textRef}
        title={isTruncated && !disabledTooltip ? text : undefined}
        data-testid="truncated-text"
        className={`block overflow-hidden truncate text-ellipsis whitespace-nowrap ${className}`}
      >
        {text}
      </span>
    </Tooltip>
  )
}
