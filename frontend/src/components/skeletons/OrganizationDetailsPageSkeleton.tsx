import { Skeleton } from '@heroui/skeleton'
import {
  CardSection,
  PageWrapper,
  SectionHeader,
  TitleSection,
  TwoColumnSection,
} from 'components/skeletons/sharedSkeletons'

const OrganizationDetailsPageSkeleton = () => {
  return (
    <PageWrapper>
      <TitleSection />

      {/* Description - empty for organization */}
      <div className="mb-7"></div>

      {/* Main Grid - Organization Details and Statistics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
        {/* Organization Details - Takes 5 columns */}
        <CardSection minHeight="min-h-[235px]" className="gap-3" colSpan="md:col-span-5">
          <SectionHeader titleSkeletonWidth="w-48" rounded />
          <div>
            {Array.from({ length: 4 }, (_, i) => (
              <div key={`detail-${i}`} className="pb-1">
                <Skeleton className="h-5 w-full max-w-md rounded" aria-hidden="true" />
              </div>
            ))}
          </div>
        </CardSection>

        {/* Statistics - Takes 2 columns */}
        <CardSection className="gap-2" colSpan="md:col-span-2">
          <SectionHeader titleSkeletonWidth="w-24" rounded />
          <div>
            {Array.from({ length: 5 }, (_, i) => (
              <div key={`stat-${i}`} className="pb-1">
                <Skeleton className="h-4 w-full rounded" aria-hidden="true" />
              </div>
            ))}
          </div>
        </CardSection>
      </div>

      {/* Top Contributors */}
      <CardSection minHeight="min-h-[350px]">
        <SectionHeader titleSkeletonWidth="w-40" rounded />
        <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 12 }, (_, i) => (
            <div
              key={`contributor-${i}`}
              className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
            >
              <div className="flex w-full items-center gap-2">
                <Skeleton className="h-6 w-6 rounded-full" aria-hidden="true" />
                <Skeleton className="h-5 w-full rounded" aria-hidden="true" />
              </div>
            </div>
          ))}
        </div>
      </CardSection>

      {/* Two Column Layout - Recent Issues and Milestones */}
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
            titleWidth: 'w-32',
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
          { keyPrefix: 'release', titleWidth: 'w-36', itemTitleWidth: 'w-2/3' },
        ]}
      />

      {/* Repositories */}
      <CardSection minHeight="min-h-[322px]">
        <SectionHeader titleSkeletonWidth="w-32" rounded />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 4 }, (_, i) => (
            <div
              key={`repo-${i}`}
              className="flex h-48 w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs dark:border-gray-700 dark:bg-gray-800"
            >
              <Skeleton className="h-5 w-3/4 rounded" aria-hidden="true" />
              <div className="flex flex-col gap-2 text-sm">
                <Skeleton className="h-4 w-full rounded" aria-hidden="true" />
                <Skeleton className="h-4 w-full rounded" aria-hidden="true" />
                <Skeleton className="h-4 w-full rounded" aria-hidden="true" />
                <Skeleton className="h-4 w-full rounded" aria-hidden="true" />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-start">
          <Skeleton className="h-10 w-24 rounded-md" aria-hidden="true" />
        </div>
      </CardSection>
    </PageWrapper>
  )
}

export default OrganizationDetailsPageSkeleton
