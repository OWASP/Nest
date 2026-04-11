import Link from 'next/link'
import { OWASP_NEST_DONATE_URL } from 'utils/constants'

export default function BecomeSponsorCTA() {
  return (
    <div className="mt-16 rounded-lg bg-gray-100 p-6 shadow-md sm:p-8 md:mt-20 dark:bg-gray-800">
      <div className="grid gap-8 md:grid-cols-2 md:gap-10 md:divide-x md:divide-gray-300 dark:md:divide-gray-600">
        <div className="text-center md:pr-8 md:text-left">
          <h3 className="text-lg font-semibold text-gray-900 md:text-xl dark:text-white">
            Corporate sponsorship
          </h3>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Your organization can appear here. Applications are reviewed by the OWASP Nest team.
          </p>
          <Link
            href="/sponsors/apply"
            className="mt-5 inline-flex items-center gap-2 rounded-full bg-gray-900 px-5 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90 dark:bg-white dark:text-gray-900"
          >
            Apply to sponsor
            <span aria-hidden className="opacity-70">
              &rarr;
            </span>
          </Link>
        </div>

        <div className="text-center md:pl-8 md:text-left">
          <h3 className="text-lg font-semibold text-gray-900 md:text-xl dark:text-white">
            One-time donation
          </h3>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Support Nest and OWASP with a single gift through the Foundation — no sponsorship
            application required.
          </p>
          <a
            href={OWASP_NEST_DONATE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-5 inline-flex items-center gap-2 rounded-full border border-gray-300 bg-gray-200 px-5 py-2.5 text-sm font-medium text-gray-900 transition-colors hover:bg-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
          >
            Donate once
            <span aria-hidden className="opacity-70">
              &rarr;
            </span>
          </a>
        </div>
      </div>
    </div>
  )
}
