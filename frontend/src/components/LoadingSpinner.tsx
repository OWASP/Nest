import React from 'react'

interface LoadingSpinnerProps {
  imageUrl: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ imageUrl }) => {
  const dark = imageUrl.replace('white', 'black')
  return (
    <div
      className="animate-spin relative h-16 w-16 rounded-full border-4 border-[#98AFC7] dark:border-white"
      style={{
        borderTopColor: 'transparent',
      }}
    >
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="animate-fade-in-out">
          <img
            src={imageUrl}
            alt="Loading indicator"
            className="hidden rounded-full dark:block"
            width={60}
            height={60}
          />
          <img
            src={dark}
            alt="Loading indicator"
            className="rounded-full dark:hidden"
            width={60}
            height={60}
          />
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
