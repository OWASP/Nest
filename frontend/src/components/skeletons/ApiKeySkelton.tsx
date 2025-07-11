export default function ApiKeysSkeleton() {
  const totalRows = 3
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-gray-200 dark:border-gray-700">
            <th className="py-3 text-left font-semibold">Name</th>
            <th className="py-3 text-left font-semibold">Key Suffix</th>
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
  )
}
