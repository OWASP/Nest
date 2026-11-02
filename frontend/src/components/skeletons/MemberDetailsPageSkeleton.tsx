import { Skeleton } from '@heroui/skeleton'
import React from 'react'
import {
  CardSection,
  PageWrapper,
  SectionHeader,
  TwoColumnSection,
} from 'components/skeletons/sharedSkeletons'

const MemberDetailsPageSkeleton: React.FC = () => {
  return (
    <PageWrapper>
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-start">
          {/* Sidebar */}
          <aside className="w-full shrink-0 xl:w-[18rem]">
            <div className="h-fit space-y-6 md:space-y-8">
              <div className="flex flex-col items-start gap-0 text-left md:gap-6">
                <Skeleton className="aspect-square size-32 shrink-0 rounded-full border-2 border-white bg-white sm:size-40 xl:h-auto xl:w-full dark:border-gray-800 dark:bg-gray-600/60" />
                <div className="mt-6 mb-2 flex w-full flex-col gap-2 overflow-x-auto text-left">
                  <Skeleton className="h-8 w-3/4 rounded-lg" />
                  <Skeleton className="h-5 w-1/2 rounded-lg" />
                  <div className="mt-4 space-y-2">
                    <Skeleton className="h-4 w-full rounded-lg" />
                    <Skeleton className="h-4 w-5/6 rounded-lg" />
                    <Skeleton className="h-4 w-4/6 rounded-lg" />
                  </div>
                </div>
              </div>

              <div className="space-y-3 border-t border-gray-200 py-5 dark:border-gray-700">
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={`detail-${i}`} className="flex items-start gap-2">
                      <Skeleton className="h-5 w-16 rounded-lg" />
                      <Skeleton className="h-5 w-24 rounded-lg" />
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-3 border-t border-gray-200 py-5 dark:border-gray-700">
                <div className="space-y-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={`stat-${i}`} className="flex items-center gap-3">
                      <Skeleton className="h-8 w-8 rounded-full" />
                      <div className="flex w-full flex-col gap-1">
                        <Skeleton className="h-4 w-12 rounded-lg" />
                        <Skeleton className="h-3 w-20 rounded-lg" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          {/* Main content */}
          <div className="flex min-w-0 flex-1 flex-col gap-6">
            {/* Heatmap skeleton */}
            <div className="overflow-hidden rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
              <Skeleton className="h-40 w-full rounded-lg" />
            </div>

            {/* Repositories Section */}
            <CardSection className="mb-0! grow">
              <SectionHeader titleSkeletonWidth="w-32" />
              <div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div
                      key={`repo-${i}`}
                      className="flex h-48 w-full flex-1 flex-col gap-3 rounded-lg border border-gray-200 p-4 shadow-xs dark:border-gray-700 dark:bg-gray-800"
                    >
                      <Skeleton className="h-5 w-3/4 rounded-lg" aria-hidden="true" />
                      <div className="mt-2 flex flex-col gap-2 text-sm">
                        <div className="flex items-center gap-2">
                          <Skeleton className="h-4 w-4 rounded-full" aria-hidden="true" />
                          <Skeleton className="h-4 w-10 rounded-lg" aria-hidden="true" />
                          <Skeleton className="h-4 w-10 rounded-lg" aria-hidden="true" />
                        </div>
                        <div className="flex items-center gap-2">
                          <Skeleton className="h-4 w-4 rounded-full" aria-hidden="true" />
                          <Skeleton className="h-4 w-10 rounded-lg" aria-hidden="true" />
                          <Skeleton className="h-4 w-12 rounded-lg" aria-hidden="true" />
                        </div>
                        <div className="flex items-center gap-2">
                          <Skeleton className="h-4 w-4 rounded-full" aria-hidden="true" />
                          <Skeleton className="h-4 w-16 rounded-lg" aria-hidden="true" />
                        </div>
                        <div className="flex items-center gap-2">
                          <Skeleton className="h-4 w-4 rounded-full" aria-hidden="true" />
                          <Skeleton className="h-4 w-10 rounded-lg" aria-hidden="true" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardSection>

            {/* Two Column Layout - Issues and Pull Requests */}
            <TwoColumnSection
              sections={[
                {
                  keyPrefix: 'issue',
                  titleWidth: 'w-32',
                  itemTitleWidth: 'w-4/5',
                  minHeight: 'min-h-[400px]',
                },
                {
                  keyPrefix: 'pr',
                  titleWidth: 'w-48',
                  itemTitleWidth: 'w-3/4',
                  minHeight: 'min-h-[400px]',
                },
              ]}
            />

            {/* Two Column Layout - Milestones and Releases */}
            <TwoColumnSection
              sections={[
                {
                  keyPrefix: 'milestone',
                  titleWidth: 'w-40',
                  itemTitleWidth: 'w-4/5',
                  minHeight: 'min-h-[400px]',
                },
                {
                  keyPrefix: 'release',
                  titleWidth: 'w-48',
                  itemTitleWidth: 'w-3/4',
                  minHeight: 'min-h-[400px]',
                },
              ]}
            />
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}

export default MemberDetailsPageSkeleton
