'use client'
import { useQuery } from '@apollo/client/react'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { FaBuilding, FaHandHoldingHeart } from 'react-icons/fa'
import { FaArrowUpRightFromSquare } from 'react-icons/fa6'
import { GetSponsorsDataDocument } from 'types/__generated__/sponsorQueries.generated'
import SecondaryCard from 'components/SecondaryCard'

type Sponsor = {
  id: string
  name: string
  url: string
  description: string
  imageUrl: string
}

const SponsorLogo = ({ sponsor }: { sponsor: Sponsor }) => {
  if (sponsor.imageUrl) {
    return (
      <div className="relative h-full w-full">
        <Image
          src={sponsor.imageUrl}
          alt={`${sponsor.name} logo`}
          className="h-full w-full object-contain"
          width={168}
          height={72}
        />
      </div>
    )
  }

  return (
    <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white text-gray-400 dark:border-gray-600 dark:bg-gray-900/40 dark:text-gray-500">
      <FaBuilding className="h-5 w-5" aria-hidden="true" />
    </div>
  )
}

const SponsorEntryCard = ({ sponsor }: { sponsor: Sponsor }) => (
  <div className="flex h-auto w-full max-w-[300px] flex-col rounded-2xl border border-gray-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:border-gray-700 dark:bg-gray-900/40">
    <div className="flex flex-col gap-4">
      <div className="flex h-[120px] items-center justify-center overflow-hidden rounded-xl bg-white p-4 ring-1 ring-gray-100 dark:bg-white dark:ring-white/10">
        <SponsorLogo sponsor={sponsor} />
      </div>
      <div className="text-center text-xl font-medium text-gray-900 dark:text-white">
        {sponsor.name}
      </div>
    </div>
    {sponsor.url && (
      <Link
        href={sponsor.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-2 inline-flex items-center gap-2 self-center text-sm font-semibold text-blue-600 transition-colors hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
      >
        Visit website
        <FaArrowUpRightFromSquare className="h-3.5 w-3.5" aria-hidden="true" />
      </Link>
    )}
  </div>
)

export default function SponsorsPage() {
  const router = useRouter()

  const { data: sponsorsData, loading, error } = useQuery(GetSponsorsDataDocument)

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <span className="text-gray-500">Loading sponsors...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <span className="text-red-500">Failed to load sponsors. Please try again later.</span>
      </div>
    )
  }

  return (
    <div className="min-h-screen w-full px-8 py-10 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <SecondaryCard
        icon={FaHandHoldingHeart}
        title="Become a Sponsor"
        className="rounded-[1.75rem] bg-gray-100 p-8 dark:bg-gray-800"
      >
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none dark:focus:ring-offset-gray-800"
            onClick={() => router.push('/sponsors/apply')}
          >
            Apply here for Sponsorship
          </button>
        </div>
      </SecondaryCard>

      {sponsorsData?.activeSponsors && sponsorsData?.activeSponsors.length > 0 ? (
        <div className="grid grid-cols-1 justify-items-center gap-6 sm:grid-cols-2 xl:grid-cols-4">
          {sponsorsData.activeSponsors.map((sponsor: Sponsor) => (
            <SponsorEntryCard key={sponsor.id} sponsor={sponsor} />
          ))}
        </div>
      ) : (
        <p className="text-center text-lg font-medium">No Sponsors Found</p>
      )}
    </div>
  )
}
