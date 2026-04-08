import Image from 'next/image'
import Link from 'next/link'
import type { SponsorData, SponsorTier } from 'types/sponsor'

import SponsorDiamondCard from 'components/sponsors/SponsorDiamondCard'

interface SponsorTierCardProps {
  sponsor: SponsorData
  size: 'lg' | 'md' | 'sm'
  tier: SponsorTier
}

const tileBase =
  'group flex flex-col items-center rounded-lg bg-gray-200 text-center outline-none transition-all duration-300 hover:bg-blue-100 focus-visible:ring-2 focus-visible:ring-gray-900/25 focus-visible:ring-offset-2 focus-visible:ring-offset-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus-visible:ring-gray-300/35 dark:focus-visible:ring-offset-[#212529]'

export default function SponsorTierCard({ sponsor, size, tier }: SponsorTierCardProps) {
  if (tier === 'Diamond') {
    return <SponsorDiamondCard sponsor={sponsor} />
  }

  const padding =
    size === 'lg' ? 'px-5 py-8 sm:py-10' : size === 'md' ? 'px-4 py-7 sm:py-8' : 'px-3 py-5 sm:py-6'

  const logoArea =
    size === 'lg'
      ? 'min-h-[5.75rem] sm:min-h-[6.75rem]'
      : size === 'md'
        ? 'min-h-[4.75rem] sm:min-h-[5.25rem]'
        : 'min-h-[3.75rem] sm:min-h-16'

  const nameClass =
    size === 'lg'
      ? 'text-base font-semibold sm:text-lg'
      : size === 'md'
        ? 'text-sm font-semibold sm:text-base'
        : 'text-xs font-semibold sm:text-sm'

  const imgW = size === 'lg' ? 200 : size === 'md' ? 160 : 120
  const imgH = size === 'lg' ? 80 : size === 'md' ? 64 : 48

  return (
    <Link
      href={sponsor.url}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`${sponsor.name} (opens in new tab)`}
      className={`${tileBase} ${padding}`}
    >
      <div className={`flex w-full max-w-[13rem] items-center justify-center sm:max-w-[15rem] ${logoArea}`}>
        {sponsor.imageUrl ? (
          <Image
            src={sponsor.imageUrl}
            alt=""
            width={imgW}
            height={imgH}
            className="max-h-full max-w-[92%] object-contain opacity-[0.92] transition group-hover:opacity-100"
          />
        ) : (
          <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Logo</span>
        )}
      </div>
      <p className={`mt-3 leading-snug text-gray-900 dark:text-gray-100 ${nameClass}`}>
        {sponsor.name}
      </p>
    </Link>
  )
}
