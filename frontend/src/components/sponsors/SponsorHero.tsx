import Link from 'next/link'
import { OWASP_NEST_DONATE_URL } from 'utils/constants'

export default function SponsorHero() {
  return (
    <header className="mb-8 pt-4 text-center">
      <p className="mb-4 text-xs font-medium tracking-[0.2em] text-gray-500 uppercase sm:text-sm dark:text-gray-400">
        Community Support
      </p>
      <h1 className="mb-4 text-4xl font-semibold tracking-tight text-gray-900 sm:text-5xl md:text-6xl dark:text-white">
        Organizations powering OWASP Nest
      </h1>
      <p className="mx-auto mb-2 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
        These organizations invest in open, secure software for everyone.
      </p>
      <p className="mx-auto mb-8 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
        Their support keeps OWASP Nest free, open source, and community-driven.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6">
        <Link
          href="/sponsors/apply"
          className="inline-flex items-center gap-2 rounded-full bg-gray-900 px-6 py-3 text-sm font-medium text-white transition-opacity hover:opacity-90 dark:bg-white dark:text-gray-900 sm:text-base"
        >
          Become a sponsor
          <span aria-hidden className="opacity-70">
            &rarr;
          </span>
        </Link>
        <a
          href={OWASP_NEST_DONATE_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-gray-600 underline decoration-gray-300 underline-offset-4 transition-colors hover:text-gray-900 dark:text-gray-400 dark:decoration-white/20 dark:hover:text-white sm:text-base"
        >
          One-time donation
        </a>
      </div>
    </header>
  )
}
