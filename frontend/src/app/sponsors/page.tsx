'use client'

import { useQuery } from '@apollo/client/react'
import Image from 'next/image'
import Link from 'next/link'
import { useMemo } from 'react'
import { GetSponsorsDocument } from 'types/__generated__/sponsorQueries.generated'
import type { Sponsor } from 'types/home'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'

const SponsorsPage = () => {
  const { data, loading, error } = useQuery(GetSponsorsDocument)

  const groupedSponsors = useMemo(() => {
    const sponsors = data?.sponsors ?? []
    const groups: Record<string, Sponsor[]> = {
      diamond: [],
      platinum: [],
      gold: [],
      silver: [],
      supporter: [],
    }

    sponsors.forEach((sponsor: Sponsor) => {
      const sponsorTypeKey = sponsor.sponsorType.toLowerCase()
      if (sponsorTypeKey in groups) {
        groups[sponsorTypeKey].push(sponsor)
      }
    })

    return groups
  }, [data?.sponsors])

  if (loading) {
    return (
      <PageLayout title="Sponsors" path="/sponsors">
        <div className="flex min-h-screen items-center justify-center">
          <LoadingSpinner />
        </div>
      </PageLayout>
    )
  }

  if (error) {
    return (
      <PageLayout title="Sponsors" path="/sponsors">
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <h1 className="mb-4 text-2xl font-bold text-red-500">Error Loading Sponsors</h1>
            <p className="text-gray-600 dark:text-gray-400">Please try again later.</p>
          </div>
        </div>
      </PageLayout>
    )
  }

  const logoWrapperBase =
    'flex items-center justify-center rounded-lg px-3 py-2 border bg-white dark:bg-[#e8e8e8]/90 border-gray-200 dark:border-transparent'

  const renderDiamondCard = (sponsor: Sponsor) => {
    return (
      <Link
        key={sponsor.id}
        href={sponsor.url || '#'}
        target={sponsor.url ? '_blank' : undefined}
        rel={sponsor.url ? 'noopener noreferrer' : undefined}
        className="group relative mb-6 flex cursor-pointer flex-row items-center justify-start gap-8 rounded-lg bg-gradient-to-r from-white to-blue-50 p-7 transition-all duration-300 ease-in-out hover:scale-[1.01] hover:shadow-lg dark:from-[#2d3139] dark:to-[#3a4250] dark:hover:shadow-xl"
      >
        {sponsor.imageUrl && (
          <div className={`h-28 w-48 shrink-0 shadow-sm ${logoWrapperBase}`}>
            <Image
              src={sponsor.imageUrl}
              alt={sponsor.name}
              height={112}
              width={192}
              className="h-full w-full object-contain"
              unoptimized
            />
          </div>
        )}

        <div className="flex flex-col gap-3">
          <h3 className="text-xl leading-tight font-bold text-gray-900 dark:text-gray-100">
            {sponsor.name}
          </h3>
          {sponsor.description && (
            <p className="line-clamp-3 text-sm text-gray-700 dark:text-gray-200">
              {sponsor.description}
            </p>
          )}
        </div>
      </Link>
    )
  }

  const renderSponsorCard = (sponsor: Sponsor, size: 'large' | 'medium' | 'small') => {
    const cardClasses = {
      large: 'p-5 gap-4',
      medium: 'p-4 gap-3',
      small: 'p-3 gap-2',
    }

    const logoSizeClasses = {
      large: 'h-24 w-48',
      medium: 'h-20 w-40',
      small: 'h-14 w-32',
    }

    const logoDimensions = {
      large: { height: 96, width: 192 },
      medium: { height: 80, width: 160 },
      small: { height: 56, width: 128 },
    }

    return (
      <Link
        key={sponsor.id}
        href={sponsor.url || '#'}
        target={sponsor.url ? '_blank' : undefined}
        rel={sponsor.url ? 'noopener noreferrer' : undefined}
        className="group relative flex cursor-pointer flex-col items-center justify-center rounded-lg border border-gray-200 bg-white transition-all duration-300 ease-in-out hover:scale-[1.02] hover:shadow-lg dark:border-gray-700 dark:bg-[#2d3139] dark:hover:border-gray-500 dark:hover:shadow-xl"
      >
        <div
          className={`relative flex w-full flex-col items-center justify-center ${cardClasses[size]}`}
        >
          {sponsor.imageUrl && (
            <div className={`${logoSizeClasses[size]} shadow-sm ${logoWrapperBase}`}>
              <Image
                src={sponsor.imageUrl}
                alt={sponsor.name}
                height={logoDimensions[size].height}
                width={logoDimensions[size].width}
                className="h-full w-full object-contain"
                unoptimized
              />
            </div>
          )}
          <h3
            className={`line-clamp-2 text-center font-semibold text-gray-900 dark:text-gray-100 ${size === 'large' ? 'text-base' : size === 'medium' ? 'text-sm' : 'text-xs'}`}
          >
            {sponsor.name}
          </h3>
          {size === 'large' && sponsor.description && (
            <p className="line-clamp-2 text-center text-xs text-gray-600 dark:text-gray-300">
              {sponsor.description}
            </p>
          )}
        </div>
      </Link>
    )
  }

  const hasDiamond = groupedSponsors.diamond.length > 0
  const hasPlatinum = groupedSponsors.platinum.length > 0
  const hasGold = groupedSponsors.gold.length > 0
  const hasSilver = groupedSponsors.silver.length > 0
  const hasSupporter = groupedSponsors.supporter.length > 0
  const hasAnySponsor = hasDiamond || hasPlatinum || hasGold || hasSilver || hasSupporter

  return (
    <PageLayout title="Sponsors" path="/sponsors">
      <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
        <div className="mx-auto max-w-6xl">
          <div className="mb-20 text-center">
            <h1 className="mb-4 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl dark:text-white">
              Sponsors
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-gray-600 dark:text-gray-300">
              Supporting OWASP Nest and its global community of contributors.
            </p>
            <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center sm:gap-4">
              <Link
                href="/sponsors/apply"
                className="inline-block rounded-lg bg-blue-600 px-6 py-2 font-medium text-white transition-colors hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600"
              >
                Apply to Sponsor
              </Link>
              <Link
                href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP%20Nest"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block rounded-lg border-2 border-blue-600 px-6 py-2 font-medium text-blue-600 transition-colors hover:bg-blue-50 dark:border-blue-400 dark:text-blue-400 dark:hover:bg-blue-900/20"
              >
                Direct Donation
              </Link>
            </div>
          </div>

          {!hasAnySponsor ? (
            <div className="rounded-lg border border-gray-200 bg-white p-12 text-center dark:border-gray-700 dark:bg-[#212529]">
              <p className="text-gray-600 dark:text-gray-300">No active sponsors at this time.</p>
            </div>
          ) : (
            <>
              {hasDiamond && (
                <section className="mb-16">
                  <div className="mb-8 flex items-center gap-6">
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                    <h2 className="border-b-2 border-blue-600 pb-2 text-lg font-semibold tracking-widest text-gray-700 uppercase dark:text-gray-300">
                      Diamond Sponsors
                    </h2>
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                  </div>
                  <div className="space-y-6">
                    {groupedSponsors.diamond.map((sponsor) => renderDiamondCard(sponsor))}
                  </div>
                </section>
              )}

              {hasPlatinum && (
                <section className="mb-16">
                  <div className="mb-8 flex items-center gap-6">
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                    <h2 className="border-b-2 border-cyan-400 pb-2 text-lg font-semibold tracking-widest text-gray-700 uppercase dark:text-gray-300">
                      Platinum Sponsors
                    </h2>
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                  </div>
                  <div className="grid gap-5 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2">
                    {groupedSponsors.platinum.map((sponsor) => renderSponsorCard(sponsor, 'large'))}
                  </div>
                </section>
              )}

              {hasGold && (
                <section className="mb-16">
                  <div className="mb-8 flex items-center gap-6">
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                    <h2 className="border-b-2 border-yellow-500 pb-2 text-lg font-semibold tracking-widest text-gray-700 uppercase dark:text-gray-300">
                      Gold Sponsors
                    </h2>
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
                    {groupedSponsors.gold.map((sponsor) => renderSponsorCard(sponsor, 'medium'))}
                  </div>
                </section>
              )}

              {hasSilver && (
                <section className="mb-16">
                  <div className="mb-8 flex items-center gap-6">
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                    <h2 className="border-b-2 border-gray-400 pb-2 text-lg font-semibold tracking-widest text-gray-700 uppercase dark:text-gray-300">
                      Silver Sponsors
                    </h2>
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                  </div>
                  <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                    {groupedSponsors.silver.map((sponsor) => renderSponsorCard(sponsor, 'small'))}
                  </div>
                </section>
              )}

              {hasSupporter && (
                <section className="mb-16">
                  <div className="mb-8 flex items-center gap-6">
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                    <h2 className="border-b-2 border-green-500 pb-2 text-lg font-semibold tracking-widest text-gray-700 uppercase dark:text-gray-300">
                      Supporters
                    </h2>
                    <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
                  </div>
                  <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                    {groupedSponsors.supporter.map((sponsor) =>
                      renderSponsorCard(sponsor, 'small')
                    )}
                  </div>
                </section>
              )}
            </>
          )}

          <div className="mt-20 rounded-lg border border-gray-200 bg-white p-8 text-center dark:border-gray-700 dark:bg-[#2d3139]">
            <h3 className="mb-2 text-2xl font-bold text-gray-900 dark:text-white">
              Interested in Sponsoring OWASP Nest?
            </h3>
            <p className="mb-6 text-gray-600 dark:text-gray-300">
              Help us support the global cybersecurity community and expand open-source security
              initiatives.
            </p>
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-center sm:gap-3">
              <Link
                href="/sponsors/apply"
                className="inline-block rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600"
              >
                Apply to Sponsor
              </Link>
              <Link
                href="https://owasp.org/donate/?reponame=www-project-nest&title=OWASP%20Nest"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block rounded-lg border-2 border-blue-600 px-6 py-3 font-medium text-blue-600 transition-colors hover:bg-blue-50 dark:border-blue-400 dark:text-blue-400 dark:hover:bg-blue-900/20"
              >
                Donate Now
              </Link>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  )
}

export default SponsorsPage
