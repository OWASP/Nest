import { Skeleton } from '@heroui/skeleton'

export const ItemCardSkeleton = ({ titleWidth }: { titleWidth: string }) => (
  <div className="mb-4 rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900">
    <Skeleton className={`mb-2 h-5 ${titleWidth}`} />
    <div className="mt-2 flex flex-wrap items-center text-sm">
      <div className="mr-4 flex items-center">
        <Skeleton className="mr-2 h-4 w-4" />
        <Skeleton className="h-4 w-20" />
      </div>
      <div className="flex flex-1 items-center overflow-hidden">
        <Skeleton className="mr-2 h-5 w-4" />
        <Skeleton className="h-4 w-24" />
      </div>
    </div>
  </div>
)

export const SectionSkeleton = ({
  titleWidth,
  itemCount,
  itemKeyPrefix,
  titleSkeletonWidth,
  minHeight,
}: {
  titleWidth: string
  itemCount: number
  itemKeyPrefix: string
  titleSkeletonWidth: string
  minHeight?: string
}) => (
  <div className={`mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 ${minHeight || ''}`}>
    <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
      <Skeleton className="h-5 w-5" />
      <Skeleton className={`h-6 ${titleSkeletonWidth}`} />
    </h2>
    <div className="space-y-3">
      {Array.from({ length: itemCount }, (_, i) => (
        <ItemCardSkeleton key={`${itemKeyPrefix}-${i}`} titleWidth={titleWidth} />
      ))}
    </div>
  </div>
)
