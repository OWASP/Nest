import millify from 'millify'
import { useEffect, useRef, useState } from 'react'

interface AnimatedCounterProps {
  end: number
  duration: number
  className?: string
  'aria-label'?: string
  onEnd?: () => void
}

export default function AnimatedCounter({
  end,
  duration,
  className,
  onEnd,
  'aria-label': ariaLabel,
}: AnimatedCounterProps) {
  const [count, setCount] = useState(0)
  const countRef = useRef(count)
  const startTime = useRef(Date.now())

  useEffect(() => {
    const animate = () => {
      const now = Date.now()
      const progress = Math.min((now - startTime.current) / (duration * 1000), 1)
      const currentCount = Math.floor(progress * end)

      if (currentCount !== countRef.current) {
        setCount(currentCount)
        countRef.current = currentCount
      }

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        if (onEnd) onEnd()
      }
    }

    requestAnimationFrame(animate)
  }, [end, duration, onEnd])

  return (
    <span
      className={className}
      role="status"
      aria-label={ariaLabel || 'animated counter'}
    >
      {millify(count)}
    </span>
  )
}
