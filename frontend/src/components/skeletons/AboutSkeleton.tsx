import { Skeleton } from '@heroui/skeleton'

const AboutSkeleton = () => {
  return (
    <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        {/* Title Skeleton */}
        <Skeleton className="mt-4 mb-6 h-10 w-32" />

        {/* Our Mission and Who It's For Grid */}
        <div className="grid gap-0 md:grid-cols-2 md:gap-6">
          <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
            <Skeleton className="mb-4 h-6 w-40" />
            <Skeleton className="mb-2 h-4 w-full" />
            <Skeleton className="mb-2 h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
          <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
            <Skeleton className="mb-4 h-6 w-40" />
            <Skeleton className="mb-2 h-4 w-full" />
            <Skeleton className="mb-2 h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>

        {/* Key Features Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-40" />
          <div className="grid gap-4 md:grid-cols-2">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                <Skeleton className="mb-2 h-5 w-3/4" />
                <Skeleton className="mb-2 h-4 w-full" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </div>

        {/* Leaders Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-32" />
          <div className="grid gap-4 md:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex flex-col items-center">
                <Skeleton className="mb-3 h-24 w-24 rounded-full" />
                <Skeleton className="mb-2 h-5 w-32" />
                <Skeleton className="h-4 w-24" />
              </div>
            ))}
          </div>
        </div>

        {/* Top Contributors Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-48" />
          <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((i) => (
              <div key={i} className="flex flex-col items-center">
                <Skeleton className="mb-2 h-16 w-16 rounded-full" />
                <Skeleton className="mb-1 h-4 w-24" />
                <Skeleton className="h-3 w-16" />
              </div>
            ))}
          </div>
        </div>

        {/* Technologies Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-52" />
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i}>
                <Skeleton className="mb-3 h-5 w-32" />
                <div className="flex flex-col gap-3">
                  {[1, 2, 3, 4].map((j) => (
                    <div key={j} className="flex items-center gap-2">
                      <Skeleton className="h-6 w-6 rounded" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Get Involved Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-40" />
          <Skeleton className="mb-2 h-4 w-full" />
          <div className="mb-6 space-y-2">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-4 w-full" />
            ))}
          </div>
          <Skeleton className="h-4 w-2/3" />
        </div>

        {/* Roadmap Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-32" />
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="rounded-lg bg-gray-200 p-6 dark:bg-gray-700">
                <Skeleton className="mb-2 h-6 w-2/3" />
                <Skeleton className="mb-2 h-4 w-full" />
                <Skeleton className="h-4 w-full" />
              </div>
            ))}
          </div>
        </div>

        {/* Our Story Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-32" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="mb-4">
              <Skeleton className="mb-2 h-4 w-full" />
              <Skeleton className="mb-2 h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ))}
        </div>

        {/* Project Timeline Section */}
        <div className="mb-6 rounded-lg bg-gray-100 p-6 dark:bg-gray-800">
          <Skeleton className="mb-4 h-6 w-48" />
          <div className="space-y-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="relative pl-10">
                <Skeleton className="absolute top-[10px] left-0 h-3 w-3 rounded-full" />
                <Skeleton className="mb-1 h-5 w-48" />
                <Skeleton className="mb-2 h-4 w-24" />
                <Skeleton className="mb-1 h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-0 md:grid-cols-4 md:gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="mb-6 rounded-lg bg-gray-100 p-6 text-center dark:bg-gray-800">
              <Skeleton className="mx-auto mb-2 h-8 w-20" />
              <Skeleton className="mx-auto h-4 w-24" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default AboutSkeleton
