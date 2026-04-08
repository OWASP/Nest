import type { SponsorData, SponsorTier } from 'types/sponsor'

import SponsorTierCard from 'components/sponsors/SponsorTierCard'

interface SponsorTierSectionProps {
  tier: SponsorTier
  sponsors: SponsorData[]
}

const TIER_GRID: Record<SponsorTier, { cols: string; size: 'lg' | 'md' | 'sm' }> = {
  Diamond: { cols: 'grid-cols-1', size: 'lg' },
  Platinum: { cols: 'grid-cols-1 sm:grid-cols-2', size: 'lg' },
  Gold: { cols: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3', size: 'md' },
  Silver: { cols: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4', size: 'sm' },
  Supporter: { cols: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4', size: 'sm' },
}

const tierHeadingId = (tier: SponsorTier) => `sponsors-tier-${tier.toLowerCase()}`

export default function SponsorTierSection({ tier, sponsors }: SponsorTierSectionProps) {
  if (sponsors.length === 0) return null

  const sortedSponsors = [...sponsors].sort((a, b) => a.name.localeCompare(b.name))
  const { cols, size } = TIER_GRID[tier]

  return (
    <section className="mb-10 md:mb-12" aria-labelledby={tierHeadingId(tier)}>
      <div className="mb-6 border-b border-gray-200 pb-4 dark:border-gray-700">
        <p className="text-[11px] font-medium tracking-[0.16em] text-gray-500 uppercase dark:text-gray-500">
          {tier}
        </p>
        <h2
          id={tierHeadingId(tier)}
          className="mt-1.5 text-xl font-semibold tracking-tight text-gray-900 md:text-2xl dark:text-white"
        >
          {tier} sponsors
        </h2>
      </div>

      <div className={`grid gap-4 sm:gap-5 md:gap-6 ${cols}`}>
        {sortedSponsors.map((sponsor) => (
          <SponsorTierCard key={sponsor.id} sponsor={sponsor} size={size} tier={tier} />
        ))}
      </div>
    </section>
  )
}
