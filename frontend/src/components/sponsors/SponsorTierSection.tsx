'use client'

import { useState } from 'react'
import type { SponsorData, SponsorTier } from 'types/sponsor'
import { TIER_LABEL } from 'types/sponsor'

import SponsorTierCard from 'components/sponsors/SponsorTierCard'

interface SponsorTierSectionProps {
  tier: SponsorTier
  sponsors: SponsorData[]
}

const TIER_GRID: Record<SponsorTier, { cols: string; size: 'lg' | 'md' | 'sm' }> = {
  diamond: { cols: 'grid-cols-1', size: 'lg' },
  platinum: { cols: 'grid-cols-1 sm:grid-cols-2', size: 'lg' },
  gold: { cols: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3', size: 'md' },
  silver: { cols: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4', size: 'sm' },
  supporter: { cols: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4', size: 'sm' },
}

const tierHeadingId = (tier: SponsorTier) => `sponsors-tier-${tier}`

export default function SponsorTierSection({ tier, sponsors }: SponsorTierSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (sponsors.length === 0) return null

  const sortedSponsors = [...sponsors].sort((a, b) => a.name.localeCompare(b.name))
  const { cols, size } = TIER_GRID[tier]
  const label = TIER_LABEL[tier]

  const isSupporter = tier === 'supporter'
  const maxItems = 8
  const hasMore = isSupporter && sortedSponsors.length > maxItems
  const visibleSponsors =
    hasMore && !isExpanded ? sortedSponsors.slice(0, maxItems) : sortedSponsors

  return (
    <section className="mb-10 md:mb-12" aria-labelledby={tierHeadingId(tier)}>
      <div className="mb-6 border-b border-gray-200 pb-4 dark:border-gray-700">
        <p className="text-[11px] font-medium tracking-[0.16em] text-gray-500 uppercase dark:text-gray-500">
          {label}
        </p>
        <h2
          id={tierHeadingId(tier)}
          className="mt-1.5 text-xl font-semibold tracking-tight text-gray-900 md:text-2xl dark:text-white"
        >
          {label} sponsors
        </h2>
      </div>

      <div className={`grid gap-4 sm:gap-5 md:gap-6 ${cols}`}>
        {visibleSponsors.map((sponsor) => (
          <SponsorTierCard key={sponsor.id} sponsor={sponsor} size={size} tier={tier} />
        ))}
      </div>

      {hasMore && (
        <div className="mt-8 flex justify-center">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 rounded-full border border-gray-200 bg-white px-6 py-2.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 hover:text-gray-900 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none dark:border-gray-700 dark:bg-[#2A2E33] dark:text-gray-300 dark:hover:bg-[#32363C] dark:hover:text-white"
          >
            {isExpanded ? 'Show Less' : 'Show More'}
            <svg
              className={`h-4 w-4 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </div>
      )}
    </section>
  )
}
