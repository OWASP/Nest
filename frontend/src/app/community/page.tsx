'use client'
import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import millify from 'millify'
import Image from 'next/image'
import Link from 'next/link'
import React, { useEffect } from 'react'
import { FaMapMarkerAlt, FaUsers } from 'react-icons/fa'
import { FaBuilding, FaCamera, FaLocationDot, FaPeopleGroup } from 'react-icons/fa6'
import { ErrorDisplay } from 'app/global-error'
import { GetCommunityPageDataDocument } from 'types/__generated__/communityQueries.generated'
import { formatDate } from 'utils/dateFormatter'
import { getMemberUrl } from 'utils/urlFormatter'
import AnchorTitle from 'components/AnchorTitle'
import ChapterCard from 'components/ChapterCard'
import LoadingSpinner from 'components/LoadingSpinner'
import MultiSearchBar from 'components/MultiSearch'
import SecondaryCard from 'components/SecondaryCard'
import { TruncatedText } from 'components/TruncatedText'

interface NavCardProps {
  href: string
  icon: React.ReactNode
  title: string
  description: string
}

const NavCard = ({ href, icon, title, description }: NavCardProps) => (
  <Link
    href={href}
    className="flex flex-col items-center rounded-lg bg-gray-200 p-6 text-center transition-transform duration-300 hover:scale-105 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
  >
    <div className="mb-3 text-blue-400">{icon}</div>
    <h3 className="mb-1 font-semibold text-blue-400">{title}</h3>
    <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
  </Link>
)

export default function CommunityPage() {
  const {
    data: graphQLData,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetCommunityPageDataDocument)

  useEffect(() => {
    if (graphQLRequestError) {
      addToast({
        description: 'Unable to complete the requested operation.',
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

  if (graphQLRequestError || !graphQLData) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading community data"
        message="Unable to load community information. Please try again later."
      />
    )
  }

  const data = graphQLData

  const statsOverview = data.statsOverview
  const statsData = statsOverview
    ? [
        { label: 'Active Chapters', value: statsOverview.activeChaptersStats },
        { label: 'Active Projects', value: statsOverview.activeProjectsStats },
        { label: 'Contributors', value: statsOverview.contributorsStats },
        { label: 'Countries', value: statsOverview.countriesStats },
      ]
    : []

  return (
    <div className="mt-6 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="text-center sm:mb-10">
          <div className="flex flex-col items-center py-2">
            <h1 className="text-3xl font-medium tracking-tighter sm:text-5xl md:text-6xl">
              OWASP Community
            </h1>
            <p className="text-muted-foreground max-w-[700px] pt-6 md:text-xl">
              Connect, collaborate, and contribute to the world&apos;s largest application security
              community.
            </p>
          </div>
          <div className="mx-auto mt-8 mb-8 flex max-w-2xl justify-center">
            <MultiSearchBar
              isLoaded={true}
              placeholder="Search the OWASP community"
              indexes={['chapters', 'organizations', 'projects', 'users']}
            />
          </div>
        </div>

        <h2 className="sr-only">Explore Community</h2>
        <div className="mb-8 grid grid-cols-2 gap-4 md:grid-cols-4">
          <NavCard
            href="/chapters"
            icon={<FaLocationDot className="h-8 w-8" />}
            title="Chapters"
            description="Find local chapters near you"
          />
          <NavCard
            href="/members"
            icon={<FaPeopleGroup className="h-8 w-8" />}
            title="Members"
            description="Connect with community members"
          />
          <NavCard
            href="/organizations"
            icon={<FaBuilding className="h-8 w-8" />}
            title="Organizations"
            description="Explore supporting organizations"
          />
          <NavCard
            href="/community/snapshots"
            icon={<FaCamera className="h-8 w-8" />}
            title="Snapshots"
            description="View community snapshots"
          />
        </div>

        <SecondaryCard
          icon={FaMapMarkerAlt}
          title={
            <div className="flex items-center gap-2">
              <AnchorTitle title="New Chapters" />
            </div>
          }
          className="overflow-hidden"
        >
          <div className="grid gap-4 md:grid-cols-2">
            {data.recentChapters?.map((chapter) => (
              <ChapterCard
                key={chapter.key}
                chapterKey={chapter.key}
                name={chapter.name}
                createdAt={chapter.createdAt}
                suggestedLocation={chapter.suggestedLocation}
                leaders={chapter.leaders}
              />
            ))}
          </div>
        </SecondaryCard>

        <div className="mb-8 grid items-stretch gap-4 md:grid-cols-2">
          <SecondaryCard
            icon={FaBuilding}
            title={
              <div className="flex items-center gap-2">
                <AnchorTitle title="New Organizations" />
              </div>
            }
            className="!mb-0 flex h-full flex-col overflow-hidden"
          >
            <div className="flex flex-1 flex-col justify-between gap-4">
              {data.recentOrganizations?.map((org) => (
                <div
                  key={org.login}
                  className="flex flex-1 items-center rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
                >
                  <div className="flex items-center gap-3">
                    {org.avatarUrl && (
                      <Image
                        src={`${org.avatarUrl}${org.avatarUrl.includes('?') ? '&' : '?'}s=80`}
                        alt={org.name || org.login}
                        width={40}
                        height={40}
                        className="rounded"
                      />
                    )}
                    <Link
                      href={`/organizations/${org.login}`}
                      className="font-semibold text-blue-400 hover:underline"
                    >
                      <TruncatedText text={org.name || org.login} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </SecondaryCard>

          <SecondaryCard
            icon={FaCamera}
            title={
              <div className="flex items-center gap-2">
                <AnchorTitle title="Snapshots" />
              </div>
            }
            className="!mb-0 flex h-full flex-col overflow-hidden"
          >
            <div className="flex flex-1 flex-col justify-between gap-4">
              {data.snapshots?.map((snapshot) => (
                <div
                  key={snapshot.key}
                  className="flex flex-1 flex-col justify-center rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
                >
                  <Link
                    href={`/community/snapshots/${snapshot.key}`}
                    className="font-semibold text-blue-400 hover:underline"
                  >
                    <TruncatedText text={snapshot.title} />
                  </Link>
                  <div className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                    {formatDate(snapshot.startAt)} - {formatDate(snapshot.endAt)}
                  </div>
                </div>
              ))}
            </div>
          </SecondaryCard>
        </div>

        <SecondaryCard
          icon={FaUsers}
          title={
            <div className="flex items-center gap-2">
              <AnchorTitle title="Top Contributors" />
            </div>
          }
        >
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {data.topContributors?.map((contributor) => (
              <div
                key={contributor.login}
                className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
              >
                <div className="flex w-full items-center gap-2">
                  {contributor.avatarUrl && (
                    <Image
                      alt={contributor.name ? `${contributor.name}'s avatar` : 'Contributor avatar'}
                      className="rounded-full"
                      height={24}
                      src={`${contributor.avatarUrl}${contributor.avatarUrl.includes('?') ? '&' : '?'}s=60`}
                      title={contributor.name || contributor.login}
                      width={24}
                    />
                  )}
                  <Link
                    className="cursor-pointer overflow-hidden font-semibold text-ellipsis whitespace-nowrap text-blue-400 hover:underline"
                    href={getMemberUrl(contributor.login)}
                    title={contributor.name || contributor.login}
                  >
                    {contributor.name || contributor.login}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </SecondaryCard>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {statsData.map((stat) => (
            <div key={stat.label}>
              <SecondaryCard className="text-center">
                <div className="mb-2 text-3xl font-bold text-blue-400">{millify(stat.value)}+</div>
                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
              </SecondaryCard>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
