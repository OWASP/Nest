'use client'

import { useQuery } from '@apollo/client/react'
import { useEffect, useMemo } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetSponsorsPageDataDocument } from 'types/__generated__/sponsorQueries.generated'
import type { SponsorData, SponsorTier } from 'types/sponsor'
import { TIER_ORDER } from 'types/sponsor'
import SponsorsSkeleton from 'components/skeletons/SponsorsSkeleton'
import BecomeSponsorCTA from 'components/sponsors/BecomeSponsorCTA'
import SponsorHero from 'components/sponsors/SponsorHero'
import SponsorsFaqSection from 'components/sponsors/SponsorsFaqSection'
import SponsorsOpenSourceShowcase from 'components/sponsors/SponsorsOpenSourceShowcase'
import SponsorTierSection from 'components/sponsors/SponsorTierSection'

const SponsorsPage = () => {
  const { data, loading, error } = useQuery(GetSponsorsPageDataDocument)

  useEffect(() => {
    if (error) {
      handleAppError(error)
    }
  }, [error])

  const sponsorsByTier = useMemo(() => {
    if (!data?.sponsors) {
      return [] as { tier: SponsorTier; sponsors: SponsorData[] }[]
    }

    const mapSponsor = (sponsor: (typeof data.sponsors)[number]): SponsorData => ({
      id: sponsor.id,
      imageUrl: sponsor.imageUrl,
      name: sponsor.name,
      sponsorType: sponsor.sponsorType,
      url: sponsor.url,
    })

    const grouped: Record<string, SponsorData[]> = {}
    for (const sponsor of data.sponsors) {
      const tier = sponsor.sponsorType || 'Supporter'
      if (!grouped[tier]) grouped[tier] = []
      grouped[tier].push(mapSponsor(sponsor))
    }

    return TIER_ORDER.filter((tier) => grouped[tier]?.length > 0).map((tier) => ({
      tier,
      sponsors: grouped[tier],
    }))
  }, [data])

  if (loading) return <SponsorsSkeleton />

  if (error) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Unable to load sponsors"
        message="Something went wrong while loading sponsor data."
      />
    )
  }

  return (
    <div className="min-h-screen w-full flex-1 px-8 pb-8 pt-0 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <SponsorHero />

        <hr className="mb-6 border-gray-200 dark:border-gray-700" />

        {sponsorsByTier.length > 0 ? (
          sponsorsByTier.map(({ tier, sponsors }) => (
            <SponsorTierSection key={tier} tier={tier as SponsorTier} sponsors={sponsors} />
          ))
        ) : (
          <div className="py-16 text-center">
            <p className="text-lg text-gray-500 dark:text-gray-400">
              No sponsors yet. Be the first to support OWASP Nest!
            </p>
          </div>
        )}

        <SponsorsOpenSourceShowcase />

        <BecomeSponsorCTA />

        <SponsorsFaqSection />
      </div>
    </div>
  )
}

export default SponsorsPage
