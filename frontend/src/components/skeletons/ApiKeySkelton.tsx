export function ApiKeysSkeleton() {
  const totalRows = 3

  return (
    <div className="flex min-h-[80vh] flex-col items-center p-8">
      <div className="w-full max-w-4xl">
        {/* Header skeleton */}
        <div className="mb-8">
          <div className="animate-pulse mb-2 h-10 w-80 rounded bg-gray-200 dark:bg-gray-700"></div>
          <div className="animate-pulse h-4 w-96 rounded bg-gray-200 dark:bg-gray-700"></div>
        </div>

        {/* Info box skeleton */}
        <div className="mb-6 rounded-lg border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-start gap-3">
            <div className="animate-pulse mt-0.5 h-5 w-5 rounded bg-gray-200 dark:bg-gray-700"></div>
            <div className="flex-1">
              <div className="animate-pulse mb-2 h-5 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="animate-pulse mb-1 h-4 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="animate-pulse h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
            </div>
          </div>
        </div>

        {/* API Keys section skeleton */}
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="mb-4 flex items-center gap-3">
            <div className="animate-pulse h-5 w-5 rounded bg-gray-200 dark:bg-gray-700"></div>
            <div className="animate-pulse h-6 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
          </div>

          <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center">
              <div className="animate-pulse mr-2 h-4 w-4 rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="animate-pulse h-4 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
            </div>
            <div className="animate-pulse h-10 w-48 rounded bg-gray-200 dark:bg-gray-700"></div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
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
                  <tr key={i} className="border-b border-gray-200 dark:border-gray-700">
                    <td className="py-3">
                      <div className="animate-pulse h-4 w-24 rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="animate-pulse h-4 w-16 rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="animate-pulse h-4 w-20 rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="animate-pulse h-4 w-16 rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3">
                      <div className="animate-pulse h-6 w-16 rounded-full bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                    <td className="py-3 text-right">
                      <div className="animate-pulse h-8 w-8 rounded bg-gray-200 dark:bg-gray-700"></div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* API Usage section skeleton */}
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="animate-pulse mb-4 h-6 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
          <div className="space-y-4">
            <div className="animate-pulse h-4 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
            <div className="animate-pulse h-16 w-full rounded bg-gray-100 dark:bg-gray-800"></div>
            <div className="rounded-md border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800">
              <div className="animate-pulse mb-2 h-4 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
              <div className="animate-pulse h-4 w-3/4 rounded bg-gray-200 dark:bg-gray-700"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
