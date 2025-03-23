import { useRef, useState, useEffect, useCallback } from 'react'

export const TruncatedText = ({ text, className = '' }: { text: string; className?: string }) => {
  const textRef = useRef<HTMLSpanElement>(null)
  const [isTruncated, setIsTruncated] = useState(false)

  const checkTruncation = useCallback(() => {
    const element = textRef.current
    if (element) {
      setIsTruncated(element.scrollWidth > element.offsetWidth)
    }
  }, [])

  useEffect(() => {
    checkTruncation()

    const observer = new ResizeObserver(() => checkTruncation())
    if (textRef.current) {
      observer.observe(textRef.current) // Watch for size changes
    }

    window.addEventListener('resize', checkTruncation)

    return () => {
      observer.disconnect()
      window.removeEventListener('resize', checkTruncation)
    }
  }, [text, checkTruncation])

  return (
    <span
      ref={textRef}
      title={isTruncated ? text : undefined}
      className={`block overflow-hidden truncate text-ellipsis whitespace-nowrap ${className}`}
    >
      {text}
    </span>
  )
}
