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
      className="group block overflow-hidden rounded-2xl border border-gray-200/80 bg-gray-50/90 outline-none transition hover:border-amber-300/60 hover:bg-white focus-visible:ring-2 focus-visible:ring-amber-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-50 dark:border-gray-600/60 dark:bg-[#2b2e32] dark:hover:border-amber-500/40 dark:hover:bg-[#32363c] dark:focus-visible:ring-amber-400/60 dark:focus-visible:ring-offset-[#212529]"
    >
      <div className="flex flex-col gap-6 p-8 sm:flex-row sm:items-center sm:gap-10 sm:p-10 md:gap-12">
        <div className="flex min-h-[7.5rem] flex-1 items-center justify-center sm:min-h-[8.5rem] sm:max-w-xs sm:flex-none md:max-w-sm">
          {logoInner}
        </div>
        <div className="min-w-0 flex-1 text-center sm:text-left">
          <h3 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white md:text-3xl">
            {sponsor.name}
          </h3>
          {sponsor.description?.trim() && (
            <p className="mt-3 max-w-2xl text-base leading-relaxed text-gray-600 dark:text-gray-400 sm:line-clamp-5">
              {sponsor.description}
            </p>
          )}
          <p className="mt-4 text-sm font-medium text-amber-800 dark:text-amber-400 md:text-base">
            &ldquo;{mottoAside}&rdquo;
          </p>
        </div>
      </div>
    </Link>
  )
}
