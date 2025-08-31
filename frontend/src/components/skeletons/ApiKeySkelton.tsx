export function ApiKeysSkeleton() {
  const totalRows = 3

  return (
    <div className="flex min-h-[80vh] flex-col items-center p-8">
      <div className="w-full max-w-4xl">
        {/* Header skeleton */}
        <div className="mb-8">
          <div className="mb-2 h-10 w-80 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
          <div className="h-4 w-96 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
        </div>

        {/* Info box skeleton */}
        <div className="mb-6 rounded-lg border-1 border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 h-5 w-5 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
            <div className="flex-1">
              <div className="mb-2 h-5 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="mb-1 h-4 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="h-4 w-3/4 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
            </div>
          </div>
        </div>

        {/* API Keys section skeleton */}
        <div className="mb-6 rounded-lg border-1 border-gray-200 bg-white p-6 shadow-xs dark:border-gray-700 dark:bg-gray-800">
          <div className="mb-4 flex items-center gap-3">
            <div className="h-5 w-5 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
            <div className="h-6 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
          </div>

          <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center">
              <div className="mr-2 h-4 w-4 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="h-4 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
            </div>
            <div className="h-10 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b-1 border-b-gray-200 dark:border-b-gray-700">
                  <th className="py-3 text-left font-semibold">Name</th>
                  <th className="py-3 text-left font-semibold">Id</th>
                  <th className="py-3 text-left font-semibold">Created</th>
                  <th className="py-3 text-left font-semibold">Expires</th>
                  <th className="py-3 text-left font-semibold">Status</th>
                  <th className="py-3 text-right font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {[...Array(totalRows)].map((_, i) => (
                  <tr key={i} className="border-b-1 border-b-gray-200 dark:border-b-gray-700">
                    <td className="py-3">
                      <div className="h-4 w-24 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="h-4 w-16 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="h-4 w-20 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="h-4 w-16 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="h-6 w-16 animate-pulse rounded-full bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3 text-right">
                      <div className="h-8 w-8 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* API Usage section skeleton */}
        <div className="mb-6 rounded-lg border-1 border-gray-200 bg-white p-6 shadow-xs dark:border-gray-700 dark:bg-gray-800">
          <div className="mb-4 h-6 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
          <div className="flex flex-col gap-4">
            <div className="h-4 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
            <div className="h-16 w-full animate-pulse rounded bg-gray-100 dark:bg-gray-800"></div>
            <div className="rounded-md border-1 border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
              <div className="mb-2 h-4 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="h-4 w-3/4 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
