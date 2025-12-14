import millify from 'millify'
import { useEffect, useRef, useState } from 'react'

interface AnimatedCounterProps {
  className?: string
  duration: number
  end: number
}

export default function AnimatedCounter({ end, duration, className }: AnimatedCounterProps) {
  const [count, setCount] = useState(0)
  const countRef = useRef(0)
  const startTime = useRef(0)

  useEffect(() => {
    startTime.current = Date.now()
    countRef.current = 0
    setCount(0)

    let frameId: number

    const animate = () => {
      const now = Date.now()
      const progress = Math.min(
        (now - startTime.current) / (duration * 1000),
        1
      )

      const currentCount = Math.floor(progress * end)

      if (currentCount !== countRef.current) {
        countRef.current = currentCount
        setCount(currentCount)
      }

      if (progress < 1) {
        frameId = requestAnimationFrame(animate)
      }
    }

    frameId = requestAnimationFrame(animate)

    return () => cancelAnimationFrame(frameId)
  }, [end, duration])

  return <span className={className}>{millify(count)}</span>
}
