import { useEffect, useRef, useState } from 'react'

interface AnimatedCounterProps {
  className?: string
  duration: number
  end: number | string
}

export default function AnimatedCounter({ end, duration, className }: AnimatedCounterProps) {
  const [count, setCount] = useState<string | number>(0)
  const countRef = useRef(0)
  const startTime = useRef(Date.now())

  useEffect(() => {
    let numericEnd = typeof end === 'string' ? parseFloat(end) : end

    const animate = () => {
      const now = Date.now()
      const progress = Math.min((now - startTime.current) / (duration * 1000), 1)
      const currentCount = Math.floor(progress * numericEnd)

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

  return <span className={className}>{count}</span>
}
