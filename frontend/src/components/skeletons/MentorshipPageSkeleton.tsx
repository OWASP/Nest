import React from 'react'
import ProgramCardSkeleton from './ProgramCardSkeleton'
import ModuleCardSkeleton from './ModuleCardSkeleton'

interface MentorshipPageSkeletonProps {
  type: 'programs' | 'modules' | 'issues' | 'mentees'
  className?: string
}

const MentorshipPageSkeleton: React.FC<MentorshipPageSkeletonProps> = ({ 
  type, 
  className = '' 
}) => {
  const renderSkeletonContent = () => {
    switch (type) {
      case 'programs':
        return (
          <div className="mt-16 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 6 }, (_, index) => (
              <ProgramCardSkeleton key={`program-skeleton-${index}`} />
            ))}
          </div>
        )
      
      case 'modules':
        return (
          <div className="space-y-4">
            {Array.from({ length: 8 }, (_, index) => (
              <ModuleCardSkeleton key={`module-skeleton-${index}`} />
            ))}
          </div>
        )
      
      case 'issues':
        return (
          <div className="space-y-4">
            {Array.from({ length: 10 }, (_, index) => (
              <div 
                key={`issue-skeleton-${index}`}
                className="rounded-lg border border-gray-400 bg-white p-4 dark:border-gray-600 dark:bg-gray-800"
                role="status"
                aria-label="Loading issue card"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="h-5 w-3/4 rounded bg-gray-300 dark:bg-gray-600 animate-pulse mb-2" />
                    <div className="h-4 w-full rounded bg-gray-300 dark:bg-gray-600 animate-pulse mb-1" />
                    <div className="h-4 w-2/3 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  </div>
                  <div className="h-6 w-16 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse ml-4" />
                </div>
                <div className="flex items-center space-x-4">
                  <div className="h-4 w-20 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  <div className="h-4 w-16 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  <div className="h-4 w-24 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        )
      
      case 'mentees':
        return (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 12 }, (_, index) => (
              <div 
                key={`mentee-skeleton-${index}`}
                className="rounded-lg border border-gray-400 bg-white p-4 dark:border-gray-600 dark:bg-gray-800"
                role="status"
                aria-label="Loading mentee card"
              >
                <div className="flex items-center space-x-3 mb-3">
                  <div className="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  <div className="flex-1">
                    <div className="h-4 w-32 rounded bg-gray-300 dark:bg-gray-600 animate-pulse mb-1" />
                    <div className="h-3 w-24 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="h-3 w-full rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  <div className="h-3 w-5/6 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  <div className="h-3 w-4/5 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                </div>
                <div className="flex items-center justify-between mt-4">
                  <div className="h-4 w-16 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                  <div className="h-4 w-20 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        )
      
      default:
        return null
    }
  }

  return (
    <div className={`text-text flex min-h-screen w-full flex-col items-center justify-normal p-5 ${className}`}>
      {/* Search Bar Skeleton */}
      <div className="flex w-full items-center justify-center mb-8">
        <div className="w-full max-w-2xl">
          <div className="h-10 w-full rounded-lg bg-gray-300 dark:bg-gray-600 animate-pulse" />
        </div>
      </div>

      {/* Page Title Skeleton */}
      <div className="w-full mb-6">
        <div className="h-8 w-48 rounded bg-gray-300 dark:bg-gray-600 animate-pulse mb-2" />
        <div className="h-4 w-64 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>

      {/* Filter/Sort Skeleton */}
      <div className="flex w-full items-center justify-between mb-6">
        <div className="h-8 w-32 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
        <div className="h-8 w-24 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" />
      </div>

      {/* Main Content Skeleton */}
      {renderSkeletonContent()}

      {/* Pagination Skeleton */}
      <div className="flex w-full items-center justify-center mt-8">
        <div className="flex items-center space-x-2">
          {Array.from({ length: 5 }, (_, index) => (
            <div 
              key={`pagination-skeleton-${index}`}
              className="h-8 w-8 rounded bg-gray-300 dark:bg-gray-600 animate-pulse" 
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default MentorshipPageSkeleton
