import { Skeleton } from '@heroui/skeleton'
import type React from 'react'
import type { UserCardSkeletonProps } from 'types/skeleton'

const UserCardSkeleton: React.FC<UserCardSkeletonProps> = ({
  showAvatar = true,
  showName = true,
  showViewProfile = true,
}) => {
  return (
    <div
      role="status"
      className="group flex h-64 w-80 flex-col items-center rounded-lg bg-white p-6 text-left shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30"
    >
      <div className="flex w-full flex-col items-center space-y-4">
        {showAvatar && (
          <div className="relative h-20 w-20 overflow-hidden rounded-full ring-2 ring-gray-100 dark:ring-gray-700">
            <Skeleton className="h-full w-full rounded-full" />
          </div>
        )}

        <div className="flex w-full flex-col items-center space-y-2">
          {showName && <Skeleton className="h-7 w-40" />}
        </div>
      </div>

      {showViewProfile && (
        <div className="mt-auto flex items-center justify-center">
          <Skeleton className="h-5 w-24" />
        </div>
      )}
    </div>
  )
}

export default UserCardSkeleton
