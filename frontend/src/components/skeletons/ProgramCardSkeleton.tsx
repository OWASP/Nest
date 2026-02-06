import React from 'react'

interface ProgramCardSkeletonProps {
  className?: string
}

const ProgramCardSkeleton: React.FC<ProgramCardSkeletonProps> = ({ className = '' }) => {
  return (
    <div 
      className={`group block h-72 w-full max-w-sm rounded-lg border border-gray-400 bg-white p-6 text-left text-inherit transition-transform duration-300 hover:scale-[1.02] hover:brightness-105 md:h-80 md:w-80 lg:h-80 lg:w-96 dark:border-gray-600 dark:bg-gray-800 ${className}`}
      role="status"
      aria-label="Loading program card"
    >
      {/* Header Section */}
      <div className="mb-4 flex items-center justify-between">
        {/* Status Badge Skeleton */}
        <div className="h-6 w-16 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
        
        {/* Actions Menu Skeleton */}
        <div className="h-8 w-8 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>

      {/* Title Section */}
      <div className="mb-4">
        <div className="mr-1 line-clamp-2 h-12 overflow-hidden break-words text-wrap">
          <div className="h-6 w-full rounded bg-gray-300 dark:bg-gray-600 animate-pulse mb-2" />
          <div className="h-6 w-3/4 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
      </div>

      {/* Organization and Date Section */}
      <div className="mb-4 space-y-2">
        <div className="flex items-center space-x-2">
          <div className="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-4 w-32 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-4 w-24 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
      </div>

      {/* Description Section */}
      <div className="mb-4 flex-1">
        <div className="line-clamp-8 break-words overflow-hidden text-wrap space-y-2">
          <div className="h-3 w-full rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-3 w-full rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-3 w-5/6 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-3 w-4/5 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
      </div>

      {/* Footer Section */}
      <div className="flex items-center justify-between">
        {/* Mentors/Mentees Count */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
            <div className="h-4 w-8 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
          </div>
          <div className="flex items-center space-x-1">
            <div className="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
            <div className="h-4 w-8 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
          </div>
        </div>

        {/* Modules Count */}
        <div className="flex items-center space-x-1">
          <div className="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-4 w-12 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
      </div>

      {/* Progress Bar Skeleton */}
      <div className="mt-4">
        <div className="h-2 w-full rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>
    </div>
  )
}

export default ProgramCardSkeleton
