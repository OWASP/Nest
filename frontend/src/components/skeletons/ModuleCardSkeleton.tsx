import React from 'react'

interface ModuleCardSkeletonProps {
  className?: string
}

const ModuleCardSkeleton: React.FC<ModuleCardSkeletonProps> = ({ className = '' }) => {
  return (
    <div 
      className={`rounded-lg border border-gray-400 bg-white p-6 text-left text-inherit transition-transform duration-300 hover:scale-[1.02] hover:brightness-105 dark:border-gray-600 dark:bg-gray-800 ${className}`}
      role="status"
      aria-label="Loading module card"
    >
      {/* Header Section */}
      <div className="mb-4 flex items-center justify-between">
        {/* Drag Handle Skeleton */}
        <div className="h-6 w-6 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        
        {/* Actions Menu Skeleton */}
        <div className="h-8 w-8 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>

      {/* Title Section */}
      <div className="mb-4">
        <div className="h-6 w-full rounded bg-gray-300 dark:bg-gray-600 animate-pulse mb-2" />
        <div className="h-4 w-3/4 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>

      {/* Description Section */}
      <div className="mb-4 space-y-2">
        <div className="h-3 w-full rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        <div className="h-3 w-5/6 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        <div className="h-3 w-4/5 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>

      {/* Stats Section */}
      <div className="mb-4 grid grid-cols-2 gap-4">
        <div className="flex items-center space-x-2">
          <div className="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-4 w-8 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-4 w-4 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-4 w-8 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
      </div>

      {/* Progress Section */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="h-4 w-16 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
          <div className="h-4 w-8 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
        <div className="h-2 w-full rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>

      {/* Footer Section */}
      <div className="flex items-center justify-between">
        <div className="h-4 w-20 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        <div className="h-4 w-16 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>
    </div>
  )
}

export default ModuleCardSkeleton
