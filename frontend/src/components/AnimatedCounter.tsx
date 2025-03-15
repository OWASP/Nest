import millify from 'millify'
import { useEffect, useRef, useState } from 'react'

interface AnimatedCounterProps {
  className?: string
  duration: number
  end: number
}

export default function AnimatedCounter({ end, duration, className }: AnimatedCounterProps) {
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
      }
    }

    requestAnimationFrame(animate)
  }, [end, duration])

  return <span className={className}>{millify(count)}</span>
}
