import { Box, Flex } from '@chakra-ui/react'
import type React from 'react'
import { CardSkeletonProps } from 'types/skeleton'
import { Skeleton, SkeletonCircle, SkeletonText } from 'components/ui/skeleton'

const CardSkeleton: React.FC<CardSkeletonProps> = ({
  showLevel = true,
  showIcons = 4,
  showProjectName = true,
  showSummary = true,
  showLink = true,
  showContributors = true,
  showSocial = true,
  showActionButton = true,
}) => {
  const NUM_CONTRIBUTORS = 8

  return (
    <div data-testid="skeleton-loader" className="flex w-full justify-center">
      <Box className="mb-6 w-full rounded-lg border border-border bg-card p-6 transition-colors duration-300 ease-linear hover:bg-accent/10 md:max-w-6xl">
        <Flex direction="column" className="flex flex-col sm:flex-row" gap={6}>
          {/* Header Section */}
          <Flex className="flex w-full flex-col items-start justify-between gap-4 sm:flex-row">
            <Flex className="items-center gap-4">
              {showLevel && <SkeletonCircle className="h-10 w-10" />}
              <Flex direction="column" gap={2}>
                {showProjectName && <Skeleton className="h-8 w-[180px] sm:w-[250px]" />}
              </Flex>
            </Flex>

            {showIcons && (
              <Flex className="flex min-w-[30%] flex-grow flex-row items-center justify-end gap-2 overflow-auto">
                {Array.from({ length: showIcons }).map((_, i) => (
                  <Skeleton key={i} className="h-8 w-16" />
                ))}
                <Skeleton />
              </Flex>
            )}
          </Flex>

          {/* Link Section */}
          {showLink && <SkeletonText className="w-[180px] md:w-[350px]" noOfLines={1} />}

          {/* Description Section */}
          {showSummary && <SkeletonText className="space-y-3" noOfLines={4} />}

          {/* Footer Section */}
          <Flex className="items-center justify-between gap-4 pt-3">
            <div className="flex flex-col justify-start gap-2">
              {showContributors && (
                <Flex className="items-center space-x-2">
                  {[...Array(NUM_CONTRIBUTORS)].map((_, i) => (
                    <SkeletonCircle
                      key={i}
                      className="h-[30px] w-[30px] border-2 border-background"
                    />
                  ))}
                </Flex>
              )}
              {showSocial && (
                <Flex className="space-x-2">
                  <SkeletonCircle className="h-5 w-5" />
                  <SkeletonCircle className="h-5 w-5" />
                  <SkeletonCircle className="h-5 w-5" />
                  <SkeletonCircle className="h-5 w-5" />
                  <SkeletonCircle className="h-5 w-5" />
                  <SkeletonCircle className="h-5 w-5" />
                </Flex>
              )}
            </div>

            <Flex gap={4} className="ml-auto items-center">
              {showActionButton && <Skeleton className="h-9 w-[100px]" />}
            </Flex>
          </Flex>
        </Flex>
      </Box>
    </div>
  )
}

export default CardSkeleton
