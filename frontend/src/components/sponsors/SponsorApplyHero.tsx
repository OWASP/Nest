import Link from 'next/link'

export default function SponsorApplyHero() {
  return (
    <header className="mb-6 flex flex-col gap-4 border-b border-gray-200 pt-4 pb-6 sm:flex-row sm:items-start sm:justify-between dark:border-gray-700">
      <div className="min-w-0">
        <h1 className="text-2xl font-semibold tracking-tight text-gray-900 sm:text-3xl dark:text-white">
          Sponsor application
        </h1>
        <p className="mt-1 max-w-xl text-sm text-gray-600 dark:text-gray-400">
          Continue to a pre-filled GitHub issue draft — the Nest team tracks inquiries there.
        </p>
      </div>
      <Link
        href="/sponsors"
        className="shrink-0 text-sm font-medium text-blue-600 underline-offset-4 hover:underline dark:text-blue-400"
      >
        &larr; Back to sponsors
      </Link>
    </header>
  )
}
