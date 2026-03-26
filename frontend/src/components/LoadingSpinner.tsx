import Image from 'next/image'
import React from 'react'

interface LoadingSpinnerProps {
  imageUrl?: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ imageUrl }) => {
  const defaultImage = '/img/spinner_white.png'
  const image = imageUrl || defaultImage
  const dark = image.replace('white', 'blue')

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      {/* Wrapper: positions the spinner ring and logo independently */}
      <div className="relative h-16 w-16">
        {/* Spinning ring only — logo is NOT inside this div */}
        <div
          className="animate-custom-spin absolute inset-0 rounded-full border-4 border-[#98AFC7] dark:border-white"
          style={{ borderTopColor: 'transparent' }}
          aria-hidden="true"
        />
        {/* Static logo — sibling of the spinner, not a child */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-fade-in-out">
            <Image
              src={image}
              alt="Loading indicator"
              className="hidden rounded-full dark:block"
              width={40}
              height={40}
            />
            <Image
              src={dark}
              alt="Loading indicator"
              className="rounded-full dark:hidden"
              width={40}
              height={40}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
