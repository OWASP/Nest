import { Box, Flex } from '@chakra-ui/react'
import type React from 'react'
import { UserCardSkeletonProps } from 'types/skeleton'
import { Skeleton, SkeletonCircle } from 'components/ui/skeleton'

const UserCardSkeleton: React.FC<UserCardSkeletonProps> = ({
  showAvatar = true,
  showName = true,
  showViewProfile = true,
}) => {
  return (
    <Box
      data-testid="skeleton-loader"
      className="group flex h-64 w-80 flex-col items-center rounded-lg bg-white p-6 text-left shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30"
    >
      <Flex direction="column" className="w-full items-center space-y-4">
        {showAvatar && (
          <Box className="relative h-20 w-20 overflow-hidden rounded-full ring-2 ring-gray-100 dark:ring-gray-700">
            <SkeletonCircle className="h-full w-full" />
          </Box>
        )}

        <Flex direction="column" className="w-full items-center space-y-2">
          {showName && <Skeleton className="h-7 w-40" />}
        </Flex>
      </Flex>

      {showViewProfile && (
        <Flex className="mt-auto items-center justify-center">
          <Skeleton className="h-5 w-24" />
        </Flex>
      )}
    </Box>
  )
}

export default UserCardSkeleton
