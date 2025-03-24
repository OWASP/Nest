import { useRef, useEffect, useCallback } from 'react'

export const TruncatedText = ({ text, className = '' }: { text: string; className?: string }) => {
  const textRef = useRef<HTMLSpanElement>(null)

  const checkTruncation = useCallback(() => {
    const element = textRef.current
    if (element) {
      element.title = text
    }
  }, [text])

  useEffect(() => {
    checkTruncation()

    const observer = new ResizeObserver(() => checkTruncation())
    if (textRef.current) {
      observer.observe(textRef.current)
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
      className={`block overflow-hidden truncate text-ellipsis whitespace-nowrap ${className}`}
    >
      {text}
    </span>
  )
}
