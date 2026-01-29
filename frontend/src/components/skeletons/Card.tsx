import { Skeleton } from '@heroui/skeleton'
import type React from 'react'
import type { CardSkeletonProps } from 'types/skeleton'

const CardSkeleton: React.FC<CardSkeletonProps> = ({
  showLevel = true,
  showIcons = true,
  showProjectName = true,
  showSummary = true,
  showLink = true,
  showContributors = true,
  showSocial = true,
  showActionButton = true,
  numIcons = 3,
}) => {
  const NUM_CONTRIBUTORS = 8

  return (
    <div
      className="flex w-full justify-center">
      <div className="border-border bg-card hover:bg-accent/10 mb-6 w-full rounded-lg border-1 p-6 transition-colors duration-300 ease-linear md:max-w-6xl">
        <div className="flex flex-col gap-6">
          {/* Header Section */}
          <div className="flex w-full flex-col items-start justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-4">
              {showLevel && <Skeleton className="h-10 w-10 rounded-full" />}
              <div className="flex flex-col gap-1">
                {showProjectName && <Skeleton className="h-8 w-[180px] sm:w-[250px]" />}
              </div>
            </div>
          </div>

          {showIcons && (
            <div className="flex min-w-[30%] grow flex-row items-center justify-start gap-2 overflow-auto">
              {/* # NOSONAR As safe to use index as key - static skeleton items with fixed length */}
              {Array.from({ length: Math.max(0, Math.floor(numIcons)) }, (_, i) => `icon-${i}`).map((key) => (
                <Skeleton key={key} className="h-8 w-16" />
              ))}
              <Skeleton />
            </div>
          )}

          {/* Link Section */}
          {showLink && <Skeleton className="w-[180px] md:w-[350px]" />}

          {/* Description Section */}
          {showSummary && (
            <div className="flex flex-col gap-3">
              <Skeleton className="h-3 w-full gap-1" />
              <Skeleton className="h-3 w-full gap-1" />
              <Skeleton className="h-3 w-full gap-1" />
              <Skeleton className="h-3 w-full gap-1" />
            </div>
          )}

          {/* Footer Section */}
          <div className="flex items-center justify-between gap-4 pt-3">
            <div className="flex flex-col justify-start gap-2">
              {showContributors && (
                <div className="mt-3 flex w-full flex-wrap items-center gap-2">
                  {/* # NOSONAR As safe to use index as key - static skeleton items with fixed length */}
                  {new Array(NUM_CONTRIBUTORS).fill(Math.random()).map((_, i) => `contributor-${i}`).map((key) => (
                    <Skeleton key={key} className="border-background h-8 w-8 rounded-full border-2" />
                  ))}
                </div>
              )}
              {showSocial && (
                <div className="flex flex-row gap-2">
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <Skeleton className="h-8 w-8 rounded-full" />
                </div>
              )}
            </div>

            <div className="ml-auto flex items-center gap-1">
              {showActionButton && <Skeleton className="h-9 w-[100px]" />}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CardSkeleton
