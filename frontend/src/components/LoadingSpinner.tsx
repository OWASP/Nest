import Image from 'next/image'
import React from 'react'

interface LoadingSpinnerProps {
  imageUrl?: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ imageUrl }) => {
  const defaultImage = '/img/owasp_icon_white_sm.png'
  const image = imageUrl || defaultImage
  const dark = image.replace('white', 'black')

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div
        className="animate-custom-spin relative h-16 w-16 rounded-full border-4 border-[#98AFC7] dark:border-white"
        style={{ borderTopColor: 'transparent' }}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-fade-in-out">
            <Image
              src={image}
              alt="Loading indicator"
              className="hidden rounded-full dark:block"
              width={60}
              height={60}
            />
            <Image
              src={dark}
              alt="Loading indicator"
              className="rounded-full dark:hidden"
              width={60}
              height={60}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
