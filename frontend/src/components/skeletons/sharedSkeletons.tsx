import { Skeleton } from '@heroui/skeleton'
import type { ReactNode } from 'react'

export const ItemCardSkeleton = ({ titleWidth }: { titleWidth: string }) => (
  <div className="mb-4 rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900">
    <Skeleton className={`mb-2 h-5 ${titleWidth}`} aria-hidden="true" />
    <div className="mt-2 flex flex-wrap items-center text-sm">
      <div className="mr-4 flex items-center">
        <Skeleton className="mr-2 h-4 w-4" aria-hidden="true" />
        <Skeleton className="h-4 w-20" aria-hidden="true" />
      </div>
      <div className="flex flex-1 items-center overflow-hidden">
        <Skeleton className="mr-2 h-5 w-4" aria-hidden="true" />
        <Skeleton className="h-4 w-24" aria-hidden="true" />
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
      <Skeleton className="h-5 w-5" aria-hidden="true" />
      <Skeleton className={`h-6 ${titleSkeletonWidth}`} aria-hidden="true" />
    </h2>
    <div className="space-y-3">
      {Array.from({ length: itemCount }, (_, i) => (
        <ItemCardSkeleton key={`${itemKeyPrefix}-${i}`} titleWidth={titleWidth} />
      ))}
    </div>
  </div>
)

export const PageWrapper = ({
  children,
  ariaBusy = true,
}: {
  children: ReactNode
  ariaBusy?: boolean
}) => (
  <div
    className="min-h-screen bg-white p-8 text-gray-800 dark:bg-[#212529] dark:text-gray-300"
    aria-busy={ariaBusy}
  >
    <div className="mx-auto max-w-6xl">{children}</div>
  </div>
)

export const TitleSection = ({
  skeletonClassName = 'h-10 w-64 rounded',
}: {
  skeletonClassName?: string
}) => (
  <div className="mt-4 flex flex-row items-center">
    <div className="flex w-full items-center justify-between">
      <Skeleton className={skeletonClassName} aria-hidden="true" />
    </div>
  </div>
)

export const TwoColumnSection = ({
  sections,
}: {
  sections: Array<{
    keyPrefix: string
    titleWidth: string
    itemTitleWidth: string
    minHeight?: string
  }>
}) => (
  <div className="gap-4 lg:grid lg:grid-cols-2">
    {sections.map(({ keyPrefix, titleWidth, itemTitleWidth, minHeight }) => (
      <SectionSkeleton
        key={keyPrefix}
        titleWidth={itemTitleWidth}
        itemCount={5}
        itemKeyPrefix={keyPrefix}
        titleSkeletonWidth={titleWidth}
        minHeight={minHeight}
      />
    ))}
  </div>
)

export const SectionHeader = ({
  titleSkeletonWidth,
  rounded = false,
}: {
  titleSkeletonWidth: string
  rounded?: boolean
}) => (
  <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
    <Skeleton className={`h-5 w-5 ${rounded ? 'rounded' : ''}`} aria-hidden="true" />
    <Skeleton
      className={`h-6 ${titleSkeletonWidth} ${rounded ? 'rounded' : ''}`}
      aria-hidden="true"
    />
  </h2>
)

export const CardSection = ({
  children,
  className = '',
  minHeight,
  colSpan,
}: {
  children: ReactNode
  className?: string
  minHeight?: string
  colSpan?: string
}) => (
  <div
    className={`mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 ${minHeight || ''} ${colSpan || ''} ${className}`}
  >
    {children}
  </div>
)
