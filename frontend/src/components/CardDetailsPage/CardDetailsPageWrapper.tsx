import React from 'react'

interface CardDetailsPageWrapperProps {
  children: React.ReactNode
}

const CardDetailsPageWrapper: React.FC<CardDetailsPageWrapperProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">{children}</div>
    </div>
  )
}

export default CardDetailsPageWrapper
