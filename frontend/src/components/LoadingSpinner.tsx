'use client'

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
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
      
      {/* ✅ STATIC LOGO (NO ANIMATION) */}
      <div className="animate-fade-in-out">
        <Image
          src={image}
          alt="OWASP"
          className="hidden rounded-full dark:block"
          width={60}
          height={60}
        />
        <Image
          src={dark}
          alt="OWASP"
          className="rounded-full dark:hidden"
          width={60}
          height={60}
        />
      </div>

      {/* ✅ SPINNER ONLY (ROTATES) */}
      <div
        className="h-16 w-16 animate-custom-spin rounded-full border-4 border-[#98AFC7] dark:border-white"
        style={{ borderTopColor: 'transparent' }}
        role="status"
        aria-label="Loading"
      />
    </div>
  )
}

export default LoadingSpinner