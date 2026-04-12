'use client'

import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import Image from 'next/image'
import Link from 'next/link'
import { useEffect } from 'react'
import { FaGem, FaHandHoldingHeart } from 'react-icons/fa'
import { FaArrowUpRightFromSquare } from 'react-icons/fa6'
import { GetSponsorsDataDocument } from 'types/__generated__/sponsorQueries.generated'
import type { Sponsor } from 'types/home'
import AnchorTitle from 'components/AnchorTitle'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'

const TIER_ORDER = ['Diamond', 'Platinum', 'Gold', 'Silver', 'Supporter']

const TIER_STYLES: Record<string, { gradient: string; border: string; badge: string }> = {
  diamond: {
    gradient: 'from-cyan-50 to-blue-50 dark:from-cyan-900/20 dark:to-blue-900/20',
    border: 'border-cyan-300 dark:border-cyan-600',
    badge: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300',
  },
  platinum: {
    gradient: 'from-slate-50 to-gray-100 dark:from-slate-800/40 dark:to-gray-800/40',
    border: 'border-slate-300 dark:border-slate-500',
    badge: 'bg-slate-100 text-slate-700 dark:bg-slate-800/60 dark:text-slate-300',
  },
  gold: {
    gradient: 'from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20',
    border: 'border-amber-300 dark:border-amber-600',
    badge: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
  },
  silver: {
    gradient: 'from-gray-50 to-slate-50 dark:from-gray-800/30 dark:to-slate-800/30',
    border: 'border-gray-300 dark:border-gray-600',
    badge: 'bg-gray-100 text-gray-700 dark:bg-gray-700/60 dark:text-gray-300',
  },
  supporter: {
    gradient: 'from-emerald-50 to-green-50 dark:from-emerald-900/20 dark:to-green-900/20',
    border: 'border-emerald-300 dark:border-emerald-600',
    badge: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  },
}

const SponsorTierCard = ({ sponsor }: { sponsor: Sponsor }) => {
  const style = TIER_STYLES[sponsor.sponsorType.toLowerCase()] || TIER_STYLES.supporter

  return (
    <div
      className={`group relative overflow-hidden rounded-xl border bg-gradient-to-br p-5 transition-all duration-300 hover:shadow-lg ${style.gradient} ${style.border}`}
    >
      <div className="flex items-start gap-4">
        <div className="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-white p-2 shadow-sm">
          {sponsor.imageUrl ? (
            <Image
              alt={`${sponsor.name} logo`}
              className="h-full w-full object-contain"
              height={56}
              src={sponsor.imageUrl}
              width={56}
            />
          ) : (
            <FaGem className="h-8 w-8 text-gray-300" />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            <h3 className="truncate text-lg font-semibold text-gray-800 dark:text-gray-100">
              {sponsor.name}
            </h3>
            <span
              className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${style.badge}`}
            >
              {sponsor.sponsorType}
            </span>
          </div>
          {sponsor.description && (
            <p className="mb-1 line-clamp-2 text-sm text-gray-600 dark:text-gray-400">
              {sponsor.description}
            </p>
          )}
          {sponsor.url && (
            <Link
              href={sponsor.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-blue-500 transition-colors hover:text-blue-600 hover:underline"
            >
              Visit website
              <FaArrowUpRightFromSquare className="h-3 w-3" />
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}

export default function SponsorsPage() {
  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetSponsorsDataDocument)

  useEffect(() => {
    if (graphQLRequestError) {
      addToast({
        description: 'Unable to load sponsors data.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
    }
  }, [graphQLRequestError])

  if (isLoading) {
    return <LoadingSpinner />
  }

  const sponsors = graphQLData?.sponsors ?? []

  const groupedSponsors = TIER_ORDER.reduce<Record<string, Sponsor[]>>((acc, tier) => {
    const tierSponsors = sponsors.filter((s) => s.sponsorType === tier)
    if (tierSponsors.length > 0) {
      acc[tier] = tierSponsors
    }
    return acc
  }, {})

  const otherSponsors = sponsors.filter(
    (s) => !TIER_ORDER.includes(s.sponsorType) && s.sponsorType !== 'Not a Sponsor'
  )
  if (otherSponsors.length > 0) {
    groupedSponsors['Other'] = otherSponsors
  }

  return (
    <div className="mt-16 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-800 dark:text-gray-100">
            Our Sponsors
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-500 dark:text-gray-400">
            These organizations generously support OWASP Nest, helping us build a stronger and more
            secure open-source community.
          </p>
        </div>

        {Object.keys(groupedSponsors).length === 0 ? (
          <SecondaryCard className="text-center">
            <div className="py-12">
              <FaGem className="mx-auto mb-4 h-12 w-12 text-gray-300 dark:text-gray-600" />
              <h3 className="mb-2 text-xl font-semibold text-gray-700 dark:text-gray-300">
                No Sponsors Yet
              </h3>
              <p className="mb-6 text-gray-500 dark:text-gray-400">
                Be the first to support the OWASP Nest project!
              </p>
              <Link
                href="/sponsors/apply"
                className="inline-block rounded-lg bg-blue-500 px-8 py-3 font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-600 hover:shadow-lg"
              >
                Become a Sponsor
              </Link>
            </div>
          </SecondaryCard>
        ) : (
          <>
            {Object.entries(groupedSponsors).map(([tier, tierSponsors]) => (
              <SecondaryCard
                key={tier}
                icon={FaGem}
                title={
                  <div className="flex items-center gap-2">
                    <AnchorTitle title={`${tier} Sponsors`} />
                    <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-sm font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                      {tierSponsors.length}
                    </span>
                  </div>
                }
              >
                <div
                  className={`grid gap-4 ${
                    tier === 'Diamond' || tier === 'Platinum'
                      ? 'sm:grid-cols-1 md:grid-cols-2'
                      : 'sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
                  }`}
                >
                  {tierSponsors.map((sponsor) => (
                    <SponsorTierCard key={sponsor.id || sponsor.name} sponsor={sponsor} />
                  ))}
                </div>
              </SecondaryCard>
            ))}
          </>
        )}

        <SecondaryCard icon={FaHandHoldingHeart} title={<AnchorTitle title="Become a Sponsor" />}>
          <div className="text-center">
            <p className="mx-auto mb-6 max-w-2xl text-gray-600 dark:text-gray-400">
              Interested in supporting the OWASP Nest project? Your sponsorship helps us maintain
              and improve the platform for the global cybersecurity community.
            </p>
            <Link
              href="/sponsors/apply"
              className="mr-4 inline-block rounded-lg bg-blue-500 px-8 py-3 font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-600 hover:shadow-lg"
            >
              Apply to Sponsor
            </Link>
            <Link
              href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP+Nest"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block rounded-lg border border-blue-500 px-8 py-3 font-semibold text-blue-500 transition-all duration-200 hover:bg-blue-50 dark:hover:bg-blue-900/20"
            >
              Donate via OWASP
            </Link>
          </div>
        </SecondaryCard>
      </div>
    </div>
  )
}
