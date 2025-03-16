import { useRef, useState, useEffect } from 'react'
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

  useEffect(() => {
    const element = textRef.current
    if (element) {
      setIsTruncated(element.scrollWidth > element.clientWidth)
    }
  }, [text])

  return (
    <Tooltip content={text} disabled={!isTruncated || disabledTooltip}>
      <span
        ref={textRef}
        className={`block overflow-hidden truncate text-ellipsis whitespace-nowrap ${className}`}
      >
        {text}
      </span>
    </Tooltip>
  )
}
