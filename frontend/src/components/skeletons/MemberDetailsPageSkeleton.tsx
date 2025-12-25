import { Skeleton } from '@heroui/skeleton'
import React from 'react'
import {
  CardSection,
  PageWrapper,
  SectionHeader,
  TitleSection,
  TwoColumnSection,
} from 'components/skeletons/sharedSkeletons'

const MemberDetailsPageSkeleton: React.FC = () => {
  return (
    <PageWrapper>
      <TitleSection skeletonClassName="h-10 w-64" />

      {/* User Summary Card - bg-gray-100 like SecondaryCard */}
      <div className="mt-6 mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
        <div className="mt-4 flex flex-col items-center lg:flex-row">
          {/* Avatar */}
          <Skeleton
            className="mb-4 h-[200px] w-[200px] shrink-0 rounded-full lg:mr-6 lg:mb-0"
            aria-hidden="true"
          />

          {/* User Info and Heatmap */}
          <div className="w-full text-center lg:text-left">
            <div className="pl-0 lg:pl-4">
              {/* Username with badge */}
              <div className="mb-1 flex items-center justify-center gap-3 text-center text-sm lg:justify-start lg:text-left">
                <Skeleton className="h-6 w-40" aria-hidden="true" />
              </div>
              {/* Bio */}
              <Skeleton className="mb-1 h-4 w-full max-w-xl" aria-hidden="true" />
            </div>

            {/* Heatmap - Only on desktop */}
            <div className="mt-4 hidden w-full lg:block">
              <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800">
                <Skeleton className="h-32 w-full" aria-hidden="true" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid - User Details and Statistics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
        {/* User Details Card */}
        <CardSection minHeight="min-h-[210px]" className="gap-2" colSpan="md:col-span-5">
          <SectionHeader titleSkeletonWidth="w-36" />
          <div>
            {[1, 2, 3, 4].map((i) => (
              <div key={`detail-${i}`} className="pb-1">
                <div className="flex flex-row gap-1">
                  <Skeleton className="h-5 w-20" aria-hidden="true" />
                  <Skeleton className="h-5 w-32" aria-hidden="true" />
                </div>
              </div>
            ))}
          </div>
        </CardSection>

        {/* Statistics Card */}
        <CardSection className="gap-2" colSpan="md:col-span-2">
          <SectionHeader titleSkeletonWidth="w-24" />
          <div>
            {[1, 2, 3, 4].map((i) => (
              <div key={`stat-${i}`}>
                <div className="pb-1">
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-4" aria-hidden="true" />
                    <Skeleton className="h-4 w-16" aria-hidden="true" />
                    <Skeleton className="h-4 w-20" aria-hidden="true" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardSection>
      </div>

      {/* Two Column Layout - Issues and Milestones */}
      <TwoColumnSection
        sections={[
          {
            keyPrefix: 'issue',
            titleWidth: 'w-32',
            itemTitleWidth: 'w-4/5',
            minHeight: 'min-h-[600px]',
          },
          {
            keyPrefix: 'milestone',
            titleWidth: 'w-40',
            itemTitleWidth: 'w-4/5',
            minHeight: 'min-h-[600px]',
          },
        ]}
      />

      {/* Two Column Layout - Pull Requests and Releases */}
      <TwoColumnSection
        sections={[
          {
            keyPrefix: 'pr',
            titleWidth: 'w-48',
            itemTitleWidth: 'w-3/4',
            minHeight: 'min-h-[600px]',
          },
          {
            keyPrefix: 'release',
            titleWidth: 'w-48',
            itemTitleWidth: 'w-3/4',
            minHeight: 'min-h-[600px]',
          },
        ]}
      />

      {/* Repositories Section */}
      <CardSection>
        <SectionHeader titleSkeletonWidth="w-32" />
        <div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={`repo-${i}`}
                className="flex h-48 w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
              >
                <Skeleton className="h-5 w-3/4" aria-hidden="true" />
                <div className="flex flex-col gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-4" aria-hidden="true" />
                    <Skeleton className="h-4 w-10" aria-hidden="true" />
                    <Skeleton className="h-4 w-10" aria-hidden="true" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-4" aria-hidden="true" />
                    <Skeleton className="h-4 w-10" aria-hidden="true" />
                    <Skeleton className="h-4 w-12" aria-hidden="true" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-4" aria-hidden="true" />
                    <Skeleton className="h-4 w-16" aria-hidden="true" />
                    <Skeleton className="h-4 w-20" aria-hidden="true" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-4 w-4" aria-hidden="true" />
                    <Skeleton className="h-4 w-10" aria-hidden="true" />
                    <Skeleton className="h-4 w-10" aria-hidden="true" />
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex justify-start">
            <Skeleton className="h-10 w-24 rounded-md" aria-hidden="true" />
          </div>
        </div>
      </CardSection>
    </PageWrapper>
  )
}

export default MemberDetailsPageSkeleton
