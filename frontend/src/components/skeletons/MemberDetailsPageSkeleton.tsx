import { Skeleton } from '@heroui/skeleton'
import React from 'react'

const MemberDetailsPageSkeleton: React.FC = () => {
  return (
    <div className="min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        {/* Page Title - No description below */}
        <div className="mt-4 flex flex-row items-center">
          <div className="flex w-full items-center justify-between">
            <Skeleton className="h-10 w-64" />
          </div>
        </div>

        {/* User Summary Card - bg-gray-100 like SecondaryCard */}
        <div className="mt-6 mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <div className="mt-4 flex flex-col items-center lg:flex-row">
            {/* Avatar */}
            <Skeleton className="mb-4 h-[200px] w-[200px] shrink-0 rounded-full lg:mr-6 lg:mb-0" />

            {/* User Info and Heatmap */}
            <div className="w-full text-center lg:text-left">
              <div className="pl-0 lg:pl-4">
                {/* Username with badge */}
                <div className="mb-1 flex items-center justify-center gap-3 text-center text-sm lg:justify-start lg:text-left">
                  <Skeleton className="h-6 w-40" />
                </div>
                {/* Bio */}
                <Skeleton className="mb-1 h-4 w-full max-w-xl" />
              </div>

              {/* Heatmap - Only on desktop */}
              <div className="mt-4 hidden w-full lg:block">
                <div className="overflow-hidden rounded-lg bg-white dark:bg-gray-800">
                  <Skeleton className="h-32 w-full" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Grid - User Details and Statistics */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-7">
          {/* User Details Card */}
          <div className="mb-8 min-h-[210px] gap-2 rounded-lg bg-gray-100 p-6 shadow-md md:col-span-5 dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5" />
              <Skeleton className="h-6 w-36" />
            </h2>
            <div>
              {[1, 2, 3, 4].map((i) => (
                <div key={`detail-${i}`} className="pb-1">
                  <div className="flex flex-row gap-1">
                    <Skeleton className="h-5 w-20" />
                    <Skeleton className="h-5 w-32" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Statistics Card */}
          <div className="mb-8 gap-2 rounded-lg bg-gray-100 p-6 shadow-md md:col-span-2 dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5" />
              <Skeleton className="h-6 w-24" />
            </h2>
            <div>
              {[1, 2, 3, 4].map((i) => (
                <div key={`stat-${i}`}>
                  <div className="pb-1">
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-4 w-4" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-20" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Two Column Layout - Issues and Milestones */}
        <div className="grid-cols-2 gap-4 lg:grid">
          {/* Recent Issues */}
          <div className="mb-8 min-h-[600px] rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5" />
              <Skeleton className="h-6 w-32" />
            </h2>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={`issue-${i}`}
                  className="rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900"
                >
                  <Skeleton className="mb-2 h-5 w-4/5" />
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
              ))}
            </div>
          </div>

          {/* Recent Milestones - Empty State */}
          <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5" />
              <Skeleton className="h-6 w-40" />
            </h2>
            <div className="flex items-center justify-center py-8">
              <Skeleton className="h-5 w-32" />
            </div>
          </div>
        </div>

        {/* Two Column Layout - Pull Requests and Releases */}
        <div className="grid-cols-2 gap-4 lg:grid">
          {/* Recent Pull Requests */}
          <div className="mb-8 min-h-[600px] rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5" />
              <Skeleton className="h-6 w-48" />
            </h2>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={`pr-${i}`}
                  className="mb-4 rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900"
                >
                  <Skeleton className="mb-2 h-5 w-3/4" />
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
              ))}
            </div>
          </div>

          {/* Recent Releases */}
          <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
              <Skeleton className="h-5 w-5" />
              <Skeleton className="h-6 w-36" />
            </h2>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={`release-${i}`}
                  className="rounded-lg border-1 border-gray-200 bg-white p-4 shadow-xs dark:border-gray-700 dark:bg-gray-900"
                >
                  <Skeleton className="mb-2 h-5 w-2/3" />
                  <div className="mt-2 flex flex-wrap items-center text-sm">
                    <div className="mr-4 flex items-center">
                      <Skeleton className="mr-2 h-4 w-4" />
                      <Skeleton className="h-4 w-20" />
                    </div>
                    <div className="flex items-center">
                      <Skeleton className="mr-2 h-4 w-4" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Repositories Section */}
        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 flex flex-row items-center gap-2 text-2xl font-semibold">
            <Skeleton className="h-5 w-5" />
            <Skeleton className="h-6 w-32" />
          </h2>
          <div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={`repo-${i}`}
                  className="flex h-46 w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
                >
                  <Skeleton className="h-5 w-3/4" />
                  <div className="flex flex-col gap-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-4 w-4" />
                      <Skeleton className="h-4 w-10" />
                      <Skeleton className="h-4 w-10" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-4 w-4" />
                      <Skeleton className="h-4 w-10" />
                      <Skeleton className="h-4 w-12" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-4 w-4" />
                      <Skeleton className="h-4 w-16" />
                      <Skeleton className="h-4 w-20" />
                    </div>
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-4 w-4" />
                      <Skeleton className="h-4 w-10" />
                      <Skeleton className="h-4 w-10" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 flex justify-center">
              <Skeleton className="h-10 w-24 rounded-md" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MemberDetailsPageSkeleton
