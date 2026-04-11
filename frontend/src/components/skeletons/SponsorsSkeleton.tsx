import { Skeleton } from '@heroui/skeleton'

const SponsorsSkeleton = () => {
  return (
    <div className="min-h-screen w-full flex-1 px-8 pt-0 pb-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 pt-4 text-center">
          <Skeleton className="mx-auto mb-4 h-4 w-40" />
          <Skeleton className="mx-auto mb-4 h-12 w-full max-w-xl md:h-16" />
          <Skeleton className="mx-auto mb-2 h-5 w-full max-w-xl" />
          <Skeleton className="mx-auto mb-6 h-5 w-full max-w-md" />
          <div className="flex flex-wrap justify-center gap-4">
            <Skeleton className="h-11 w-44 rounded-full" />
            <Skeleton className="h-11 w-36 rounded-full" />
          </div>
        </div>

        <hr className="mb-6 border-gray-200 dark:border-gray-700" />
        {[1, 2].map((tierIdx) => (
          <div key={`tier-skeleton-${tierIdx}`} className="mb-10 md:mb-12">
            <div className="mb-6 border-b border-gray-200 pb-4 dark:border-gray-700">
              <Skeleton className="mb-2 h-3 w-20" />
              <Skeleton className="h-7 w-48" />
            </div>
            <div
              className={`grid gap-4 sm:gap-5 ${tierIdx === 1 ? 'sm:grid-cols-2' : 'sm:grid-cols-2 md:grid-cols-3'}`}
            >
              {Array.from({ length: tierIdx === 1 ? 2 : 3 }).map((_, i) => (
                <div
                  key={`card-skeleton-${tierIdx}-${i}`}
                  className="flex flex-col items-center rounded-lg bg-gray-200 px-4 py-7 dark:bg-gray-700"
                >
                  <Skeleton className="mb-4 h-16 w-28 rounded-lg sm:h-20 sm:w-32 dark:bg-gray-600" />
                  <Skeleton className="h-4 w-3/4" />
                  {tierIdx === 1 && (
                    <>
                      <Skeleton className="mt-2 h-3 w-full max-w-[14rem]" />
                      <Skeleton className="mt-1 h-3 w-5/6 max-w-[12rem]" />
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="mt-16 md:mt-20">
          <Skeleton className="mx-auto mb-10 h-8 w-full max-w-lg md:h-9" />
          <div className="grid gap-6 md:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div
                key={`showcase-${i}`}
                className="rounded-2xl bg-gray-50 p-6 sm:p-7 dark:bg-gray-800"
              >
                <Skeleton className="mb-5 h-9 w-full rounded-lg dark:bg-gray-600" />
                <Skeleton className="mb-3 h-6 w-5/6" />
                <Skeleton className="mb-2 h-4 w-full" />
                <Skeleton className="mb-1 h-4 w-full" />
                <Skeleton className="mt-5 h-4 w-32" />
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 rounded-lg bg-gray-100 p-8 shadow-md sm:p-10 md:mt-20 dark:bg-gray-800">
          <div className="grid gap-8 md:grid-cols-2 md:gap-12">
            <div>
              <Skeleton className="mb-2 h-6 w-48" />
              <Skeleton className="mb-4 h-4 w-full max-w-sm" />
              <Skeleton className="h-10 w-40 rounded-full" />
            </div>
            <div>
              <Skeleton className="mb-2 h-6 w-44" />
              <Skeleton className="mb-4 h-4 w-full max-w-sm" />
              <Skeleton className="h-10 w-36 rounded-full" />
            </div>
          </div>
        </div>

        <div className="mx-auto mt-16 max-w-2xl md:mt-24">
          <Skeleton className="mx-auto mb-10 h-8 w-64 md:h-9" />
          {[1, 2, 3].map((i) => (
            <div key={`faq-${i}`} className="border-b border-gray-200 py-4 dark:border-gray-700">
              <Skeleton className="h-5 w-full max-w-md" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SponsorsSkeleton
