import { Skeleton } from '@heroui/skeleton'

const OrganizationDetailsPageSkeleton = () => {
  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        {/* Title */}
        <div className="mt-4 flex flex-row items-center">
          <div className="flex w-full items-center justify-between">
            <Skeleton className="h-10 w-64 rounded" />
          </div>
        </div>

        {/* Description - empty for organization */}
        <div className="mb-7"></div>

        {/* Main Grid - Organization Details and Statistics */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          {/* Organization Details - Takes 5 columns */}
          <div className="mb-8 min-h-[235px] gap-3 rounded-lg bg-gray-100 p-6 shadow-md md:col-span-5 dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-48 rounded" />
            </h2>
            <div>
              {Array.from({ length: 4 }, (_, i) => (
                <div key={`detail-${i}`} className="pb-1">
                  <Skeleton className="h-5 w-full max-w-md rounded" />
                </div>
              ))}
            </div>
          </div>

          {/* Statistics - Takes 2 columns */}
          <div className="mb-8 gap-2 rounded-lg bg-gray-100 p-6 shadow-md md:col-span-2 dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-24 rounded" />
            </h2>
            <div>
              {Array.from({ length: 5 }, (_, i) => (
                <div key={`stat-${i}`} className="pb-1">
                  <Skeleton className="h-4 w-full rounded" />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Contributors */}
        <div className="mb-8 min-h-[350px] rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-6 w-40 rounded" />
          </h2>
          <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 12 }, (_, i) => (
              <div
                key={`contributor-${i}`}
                className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
              >
                <div className="flex w-full items-center gap-2">
                  <Skeleton className="h-6 w-6 rounded-full" />
                  <Skeleton className="h-5 w-full rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Two Column Layout - Recent Issues and Milestones */}
        <div className="grid-cols-2 gap-4 lg:grid">
          {/* Recent Issues */}
          <div className="mb-8 min-h-[600px] rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-36 rounded" />
            </h2>
            <div className="space-y-3">
              {Array.from({ length: 5 }, (_, i) => (
                <div
                  key={`issue-${i}`}
                  className="mb-4 rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900"
                >
                  <Skeleton className="mb-2 h-5 w-full rounded" />
                  <div className="mt-2 flex flex-wrap items-center text-sm">
                    <div className="mr-4 flex items-center">
                      <Skeleton className="mr-2 h-4 w-4 rounded" />
                      <Skeleton className="h-4 w-24 rounded" />
                    </div>
                    <div className="flex flex-1 items-center overflow-hidden">
                      <Skeleton className="mr-2 h-5 w-4 rounded" />
                      <Skeleton className="h-4 w-full rounded" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Milestones */}
          <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-44 rounded" />
            </h2>
            <div className="space-y-3">
              {Array.from({ length: 2 }, (_, i) => (
                <div
                  key={`milestone-${i}`}
                  className="mb-4 rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900"
                >
                  <Skeleton className="mb-2 h-5 w-full rounded" />
                  <div className="mt-2 flex flex-wrap items-center text-sm">
                    <div className="mr-4 flex items-center">
                      <Skeleton className="mr-2 h-4 w-4 rounded" />
                      <Skeleton className="h-4 w-24 rounded" />
                    </div>
                    <div className="mr-4 flex items-center">
                      <Skeleton className="mr-2 h-4 w-4 rounded" />
                      <Skeleton className="h-4 w-20 rounded" />
                    </div>
                    <div className="mr-4 flex items-center">
                      <Skeleton className="mr-2 h-4 w-4 rounded" />
                      <Skeleton className="h-4 w-16 rounded" />
                    </div>
                    <div className="flex flex-1 items-center overflow-hidden">
                      <Skeleton className="mr-2 h-5 w-4 rounded" />
                      <Skeleton className="h-4 w-full rounded" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Two Column Layout - Pull Requests and Releases */}
        <div className="grid-cols-2 gap-4 lg:grid">
          {/* Recent Pull Requests */}
          <div className="mb-8 min-h-[600px] rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-52 rounded" />
            </h2>
            <div className="space-y-3">
              {Array.from({ length: 5 }, (_, i) => (
                <div
                  key={`pr-${i}`}
                  className="mb-4 rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900"
                >
                  <Skeleton className="mb-2 h-5 w-full rounded" />
                  <div className="mt-2 flex flex-wrap items-center text-sm">
                    <div className="mr-4 flex items-center">
                      <Skeleton className="mr-2 h-4 w-4 rounded" />
                      <Skeleton className="h-4 w-24 rounded" />
                    </div>
                    <div className="mr-4 flex flex-1 items-center overflow-hidden">
                      <Skeleton className="mr-2 h-5 w-4 rounded" />
                      <Skeleton className="h-4 w-full rounded" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Releases */}
          <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5 rounded" />
              <Skeleton className="h-6 w-40 rounded" />
            </h2>
            <div className="grid grid-cols-1">
              {Array.from({ length: 5 }, (_, i) => (
                <div key={`release-${i}`} className="mb-3">
                  <Skeleton className="mb-2 h-5 w-32 rounded" />
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center">
                      <Skeleton className="mr-2 h-4 w-4 rounded" />
                      <Skeleton className="h-4 w-24 rounded" />
                    </div>
                    <div className="flex items-center">
                      <Skeleton className="mr-2 h-5 w-5 rounded-full" />
                      <Skeleton className="h-4 w-20 rounded" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Repositories */}
        <div className="mb-8 min-h-[322px] rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
            <Skeleton className="h-5 w-5 rounded" />
            <Skeleton className="h-6 w-32 rounded" />
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 4 }, (_, i) => (
              <div
                key={`repo-${i}`}
                className="flex h-46 w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs dark:border-gray-700 dark:bg-gray-800"
              >
                <Skeleton className="h-5 w-3/4 rounded" />
                <div className="flex flex-col gap-2 text-sm">
                  <Skeleton className="h-4 w-full rounded" />
                  <Skeleton className="h-4 w-full rounded" />
                  <Skeleton className="h-4 w-full rounded" />
                  <Skeleton className="h-4 w-full rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default OrganizationDetailsPageSkeleton
