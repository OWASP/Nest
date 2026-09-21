'use client'

import { Button } from '@heroui/button'
import { useState } from 'react'
import { FaStar } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'

export const MAX_RATING = 5

const STARS = Array.from({ length: MAX_RATING }, (_, index) => index + 1)

const SIZE_CLASSES = {
  sm: 'h-3.5 w-3.5',
  md: 'h-5 w-5',
  lg: 'h-7 w-7',
} as const

const starColor = (isFilled: boolean) =>
  isFilled ? 'text-yellow-500' : 'text-gray-300 dark:text-gray-600'

type StarRatingProps = {
  value: number
  onChange?: (rating: number) => void
  isDisabled?: boolean
  label?: string
  size?: keyof typeof SIZE_CLASSES
}

const StarRating = ({
  value,
  onChange,
  isDisabled = false,
  label = 'Rating',
  size = 'md',
}: StarRatingProps) => {
  const [previewed, setPreviewed] = useState(0)
  const sizeClass = SIZE_CLASSES[size]

  if (!onChange) {
    return (
      <span
        className="flex items-center gap-0.5"
        role="img"
        aria-label={`${label}: ${value} out of ${MAX_RATING} stars`}
      >
        {STARS.map((star) => (
          <IconWrapper
            key={star}
            aria-hidden="true"
            className={`${sizeClass} ${starColor(star <= Math.round(value))}`}
            icon={FaStar}
          />
        ))}
      </span>
    )
  }

  const displayed = previewed || value

  return (
    <div className="flex items-center gap-1" role="group" aria-label={label}>
      {STARS.map((star) => (
        <span
          key={star}
          onMouseEnter={() => !isDisabled && setPreviewed(star)}
          onMouseLeave={() => setPreviewed(0)}
          onFocus={() => !isDisabled && setPreviewed(star)}
          onBlur={() => setPreviewed(0)}
        >
          <Button
            aria-label={`${star} ${star === 1 ? 'star' : 'stars'}`}
            aria-pressed={star === value}
            className="h-auto min-w-0 bg-transparent p-0.5 transition-transform hover:scale-110"
            disableAnimation
            isDisabled={isDisabled}
            isIconOnly
            onPress={() => onChange(star)}
            type="button"
          >
            <IconWrapper
              aria-hidden="true"
              className={`${sizeClass} ${starColor(star <= displayed)}`}
              icon={FaStar}
            />
          </Button>
        </span>
      ))}
    </div>
  )
}

export default StarRating
