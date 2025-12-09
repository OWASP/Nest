import { Skeleton } from '@heroui/skeleton'
import type React from 'react'

interface SnapshotSkeletonProps {
  showTitle?: boolean
  showDateRange?: boolean
  showViewButton?: boolean
}

const SnapshotSkeleton: React.FC<SnapshotSkeletonProps> = ({
  showTitle = true,
  showDateRange = true,
  showViewButton = true,
}) => {
  return (
    <output className="group flex h-40 w-full flex-col items-center rounded-lg bg-white p-6 text-left shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
      <div className="text-center">{showTitle && <Skeleton className="h-7 w-64 rounded-md" />}</div>

      {showDateRange && (
        <div className="mt-2 flex items-center gap-2">
          <Skeleton className="h-4 w-4 rounded" />
          <Skeleton className="h-4 w-52 rounded-md" />
        </div>
      )}

      {showViewButton && (
        <div className="mt-4 flex items-center gap-2">
          <Skeleton className="h-3.5 w-28 rounded-md" />
          <Skeleton className="h-3.5 w-3.5 rounded" />
        </div>
      )}
    </output>
  )
}

export default SnapshotSkeleton
