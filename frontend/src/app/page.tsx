'use client'
import { useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import upperFirst from 'lodash/upperFirst'
import millify from 'millify'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import type { IconType } from 'react-icons'
import { FaCalendarAlt, FaMapMarkerAlt } from 'react-icons/fa'
import {
  FaBook,
  FaCalendar,
  FaCode,
  FaFileCode,
  FaFolder,
  FaGlobe,
  FaNewspaper,
  FaTag,
  FaUser,
} from 'react-icons/fa6'
import { HiUserGroup } from 'react-icons/hi'
import { IconWrapper } from 'wrappers/IconWrapper'
import { fetchAlgoliaData } from 'server/fetchAlgoliaData'
import { GetMainPageDataDocument } from 'types/__generated__/homeQueries.generated'
import type { AlgoliaResponse } from 'types/algolia'
import type { Chapter } from 'types/chapter'
import type { Event } from 'types/event'
import type { MainPageData } from 'types/home'

import { formatDate, formatDateRange } from 'utils/dateFormatter'
import AnchorTitle from 'components/AnchorTitle'
import CalendarButton from 'components/CalendarButton'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import LeadersList from 'components/LeadersList'
import LoadingSpinner from 'components/LoadingSpinner'
import MovingLogos from 'components/LogoCarousel'
import Milestones from 'components/Milestones'
import DialogComp from 'components/Modal'
import MultiSearchBar from 'components/MultiSearch'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import RecentReleases from 'components/RecentReleases'
import SecondaryCard from 'components/SecondaryCard'
import TopContributorsList from 'components/TopContributorsList'
import { TruncatedText } from 'components/TruncatedText'

export default function Home() {
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [data, setData] = useState<MainPageData>(null)
  const { data: graphQLData, error: graphQLRequestError } = useQuery(GetMainPageDataDocument, {
    variables: { distinct: true },
  })

  const [geoLocData, setGeoLocData] = useState<Chapter[]>([])
  const [modalOpenIndex, setModalOpenIndex] = useState<number | null>(null)

  useEffect(() => {
    if (graphQLData) {
      setData(graphQLData)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      addToast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError])

  useEffect(() => {
    const fetchData = async () => {
      const searchParams = {
        indexName: 'chapters',
        query: '',
        currentPage: 1,
        hitsPerPage: 1000,
      }
      const data: AlgoliaResponse<Chapter> = await fetchAlgoliaData(
        searchParams.indexName,
        searchParams.query,
        searchParams.currentPage,
        searchParams.hitsPerPage
      )
      setGeoLocData(data.hits)
    }
    fetchData()
  }, [])

  if (isLoading || !graphQLData || !geoLocData) {
    return <LoadingSpinner />
  }

  const getProjectIcon = (projectType: string): IconType => {
    switch (projectType.toLowerCase()) {
      case 'code':
        return FaCode
      case 'documentation':
        return FaBook
      case 'other':
        return FaFileCode
      case 'tool':
        return FaTag
      default:
        return FaFileCode
    }
  }

  const counterData = [
    {
      label: 'Active Projects',
      value: data.statsOverview.activeProjectsStats,
    },
    {
      label: 'Contributors',
      value: data.statsOverview.contributorsStats,
    },
    {
      label: 'Local Chapters',
      value: data.statsOverview.activeChaptersStats,
    },
    {
      label: 'Countries',
      value: data.statsOverview.countriesStats,
    },
    {
      label: 'Slack Community',
      value: data.statsOverview.slackWorkspaceStats,
    },
  ]

  return (
    <div className="mt-16 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="pt-5 text-center sm:mb-10">
          <div className="flex flex-col items-center py-10">
            <h1 className="text-3xl font-medium tracking-tighter sm:text-5xl md:text-6xl">
              Welcome to OWASP Nest
            </h1>
            <p className="text-muted-foreground max-w-[700px] pt-6 md:text-xl">
              Your gateway to OWASP. Discover, engage, and help shape the future!
            </p>
          </div>
          <div className="mx-auto mb-8 flex max-w-2xl justify-center">
            <MultiSearchBar
              eventData={data.upcomingEvents}
              isLoaded={true}
              placeholder="Search the OWASP community"
              indexes={['chapters', 'organizations', 'projects', 'users']}
            />
          </div>
        </div>
        <SecondaryCard
          icon={FaCalendarAlt}
          title={
            <div className="flex items-center gap-2">
              <AnchorTitle title="Upcoming Events" className="flex items-center leading-none" />
            </div>
          }
          className="overflow-hidden"
        >
          <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {data.upcomingEvents.map((event: Event, index: number) => (
              <div key={`card-${event.name}`} className="overflow-hidden">
                <div className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <button
                      className="min-w-0 flex-1 cursor-pointer text-left text-lg font-semibold text-blue-400 hover:underline"
                      type="button"
                      onClick={() => setModalOpenIndex(index)}
                    >
                      <TruncatedText text={event.name} />
                    </button>
                  </div>
                  <div className="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
                    <div className="mr-2 flex items-center">
                      <CalendarButton
                        className="text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                        event={{
                          title: event.name,
                          description: event.summary || '',
                          location: event.suggestedLocation || '',
                          startDate: event.startDate,
                          endDate: event.endDate,
                          url: event.url,
                        }}
                        iconClassName="h-4 w-4 mr-1"
                        label={formatDateRange(event.startDate, event.endDate)}
                        showLabel
                      />
                    </div>
                    {event.suggestedLocation && (
                      <div className="flex flex-1 items-center overflow-hidden">
                        <FaMapMarkerAlt className="mr-1 h-4 w-4" />
                        <TruncatedText text={event.suggestedLocation} />
                      </div>
                    )}
                  </div>
                </div>
                <DialogComp
                  key={`modal-${event.name}`}
                  isOpen={modalOpenIndex === index}
                  onClose={() => setModalOpenIndex(null)}
                  title={event.name}
                  summary={event.summary}
                  button={{ label: 'View Event', url: event.url }}
                  description="The event summary has been generated by AI"
                ></DialogComp>
              </div>
            ))}
          </div>
        </SecondaryCard>
        <div className="grid gap-4 md:grid-cols-2">
          <SecondaryCard
            icon={FaMapMarkerAlt}
            title={
              <div className="flex items-center gap-2">
                <AnchorTitle title="New Chapters" className="flex items-center leading-none" />
              </div>
            }
            className="overflow-hidden"
          >
            <div className="flex flex-col gap-4">
              {data.recentChapters?.map((chapter) => (
                <div key={chapter.key} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <h3 className="mb-2 text-lg font-semibold">
                    <Link
                      href={`/chapters/${chapter.key}`}
                      className="text-blue-400 hover:underline"
                    >
                      <TruncatedText text={chapter.name} />
                    </Link>
                  </h3>
                  <div className="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
                    <div className="mr-4 flex items-center">
                      <FaCalendar className="mr-2 h-4 w-4" />
                      <span>{formatDate(chapter.createdAt)}</span>
                    </div>
                    {chapter.suggestedLocation && (
                      <div className="flex flex-1 items-center overflow-hidden">
                        <FaMapMarkerAlt className="mr-2 h-4 w-4" />
                        <TruncatedText text={chapter.suggestedLocation} />
                      </div>
                    )}
                  </div>

                  {chapter.leaders.length > 0 && (
                    <div className="mt-1 flex items-center gap-x-2 text-sm text-gray-600 dark:text-gray-400">
                      {' '}
                      <HiUserGroup className="mr-2 h-4 w-4 shrink-0" />
                      <LeadersList leaders={String(chapter.leaders)} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </SecondaryCard>
          <SecondaryCard
            icon={FaFolder}
            title={
              <div className="flex items-center gap-2">
                <AnchorTitle title="New Projects" className="flex items-center leading-none" />
              </div>
            }
            className="overflow-hidden"
          >
            <div className="flex flex-col gap-4">
              {data.recentProjects?.map((project) => (
                <div key={project.key} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <Link href={`/projects/${project.key}`} className="text-blue-400 hover:underline">
                    <h3 className="mb-2 truncate text-lg font-semibold text-wrap md:text-nowrap">
                      <TruncatedText text={project.name} />
                    </h3>
                  </Link>
                  <div className="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
                    <div className="mr-4 flex items-center">
                      <FaCalendar className="mr-2 h-4 w-4" />
                      <span>{formatDate(project.createdAt)}</span>
                    </div>
                    <div className="mr-4 flex flex-1 items-center overflow-hidden">
                      <IconWrapper icon={getProjectIcon(project.type)} className="mr-2 h-4 w-4" />
                      <TruncatedText text={upperFirst(project.type)} />
                    </div>
                  </div>
                  {project.leaders.length > 0 && (
                    <div className="mt-1 flex items-center gap-x-2 text-sm text-gray-600 dark:text-gray-400">
                      <HiUserGroup className="h-4 w-4 shrink-0" />
                      <LeadersList leaders={String(project.leaders)} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </SecondaryCard>
        </div>
        <div className="mb-20">
          <div className="mb-4 flex items-center gap-2">
            <FaGlobe className="h-4 w-4" style={{ verticalAlign: 'middle' }} />
            <AnchorTitle title="Chapters Worldwide" className="flex items-center leading-none" />
          </div>
          <ChapterMapWrapper
            geoLocData={geoLocData}
            showLocal={false}
            showLocationSharing={true}
            style={{
              height: '400px',
              width: '100%',
              zIndex: '0',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
          />
        </div>
        <TopContributorsList
          contributors={data?.topContributors}
          icon={HiUserGroup}
          maxInitialDisplay={20}
        />
        <div className="grid-cols-2 gap-4 lg:grid">
          <RecentIssues data={data?.recentIssues} />
          <Milestones data={data?.recentMilestones} />
        </div>
        <div className="grid-cols-2 gap-4 lg:grid">
          <RecentPullRequests data={data?.recentPullRequests} />
          <RecentReleases data={data?.recentReleases} showSingleColumn={true} />
        </div>
        <SecondaryCard
          icon={FaNewspaper}
          title={
            <div className="flex items-center gap-2">
              <AnchorTitle title="News & Opinions" className="flex items-center leading-none" />
            </div>
          }
          className="overflow-hidden"
        >
          <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
            {data?.recentPosts.map((post) => (
              <div
                key={post.title}
                className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
              >
                <h3 className="mb-1 text-lg font-semibold">
                  <Link
                    href={post.url}
                    className="text-blue-400 hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <TruncatedText text={post.title} />
                  </Link>
                </h3>
                <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
                  <div className="mr-4 flex items-center">
                    <FaCalendar className="mr-2 h-4 w-4" />
                    <span>{formatDate(post.publishedAt)}</span>
                  </div>
                  <div className="flex flex-1 items-center overflow-hidden">
                    <FaUser className="mr-2 h-4 w-4" />
                    <LeadersList leaders={post.authorName} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SecondaryCard>
        <div className="grid gap-6 lg:grid-cols-5">
          {counterData.map((stat) => (
            <div key={stat.label}>
              <SecondaryCard className="text-center">
                <div className="mb-2 text-3xl font-bold text-blue-400">{millify(stat.value)}+</div>
                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
              </SecondaryCard>
            </div>
          ))}
        </div>

        <div className="mt-8 mb-20">
          <SecondaryCard className="text-center">
            <h3 className="mb-4 text-2xl font-semibold">Ready to Make a Difference?</h3>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Join OWASP and be part of the global cybersecurity community.
            </p>
            <Link
              href="https://owasp.glueup.com/organization/6727/memberships/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block rounded bg-blue-500 px-6 py-3 font-bold text-white hover:bg-blue-600"
            >
              Join OWASP
            </Link>
          </SecondaryCard>
          <SecondaryCard>
            <MovingLogos sponsors={data?.sponsors} />
          </SecondaryCard>
        </div>
      </div>
    </div>
  )
}
