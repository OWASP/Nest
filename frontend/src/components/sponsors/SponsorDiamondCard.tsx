import Image from 'next/image'
import Link from 'next/link'
import type { SponsorData } from 'types/sponsor'

const DIAMOND_MOTTO_FALLBACK = 'Security for everyone, built in the open.'

interface SponsorDiamondCardProps {
  sponsor: SponsorData
}

/**
 * Featured credit row — Blender-style hero tile for the top tier.
 */
export default function SponsorDiamondCard({ sponsor }: SponsorDiamondCardProps) {
  const mottoAside = sponsor.motto?.trim() || DIAMOND_MOTTO_FALLBACK

  const logoInner = sponsor.imageUrl ? (
    <Image
      src={sponsor.imageUrl}
      alt=""
      width={220}
      height={110}
      className="max-h-24 max-w-full object-contain opacity-[0.95] transition group-hover:opacity-100 sm:max-h-28"
    />
  ) : (
    <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Logo</span>
  )

  return (
    <Link
      href={sponsor.url}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`${sponsor.name} (opens in new tab)`}
      className="group block overflow-hidden rounded-lg border border-gray-200 bg-gray-200 outline-none transition-all duration-300 hover:border-black hover:bg-blue-100 focus-visible:ring-2 focus-visible:ring-gray-900/25 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:hover:border-white dark:hover:bg-gray-600 dark:focus-visible:ring-gray-300/35 dark:focus-visible:ring-offset-[#212529]"
    >
      <div className="flex flex-col gap-6 p-8 sm:flex-row sm:items-center sm:gap-10 sm:p-10 md:gap-12">
        <div className="flex min-h-[7.5rem] flex-1 items-center justify-center sm:min-h-[8.5rem] sm:max-w-xs sm:flex-none md:max-w-sm">
          {logoInner}
        </div>
        <div className="min-w-0 flex-1 text-center sm:text-left">
          <h3 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white md:text-3xl">
            {sponsor.name}
          </h3>
          <p className="mt-4 text-sm font-medium text-gray-800 md:text-base dark:text-gray-200">
            &ldquo;{mottoAside}&rdquo;
          </p>
        </div>
      </div>
    </Link>
  )
}
