import { useQuery } from '@apollo/client'
import { IconProp } from '@fortawesome/fontawesome-svg-core'
import {
  faBook,
  faCalendar,
  faCode,
  faFileCode,
  faMapMarkerAlt,
  faTag,
  faUsers,
  faUser,
  faFolder,
  faTriangleExclamation,
  faCodePullRequest,
  faNewspaper,
  faGlobe,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { GET_MAIN_PAGE_DATA } from 'api/queries/homeQueries'
import { useEffect, useState } from 'react'
import { AlgoliaResponseType } from 'types/algolia'
import { ChapterTypeAlgolia } from 'types/chapter'
import { EventType } from 'types/event'
import { MainPageData } from 'types/home'
import { capitalize } from 'utils/capitalize'
import { formatDate, formatDateRange } from 'utils/dateFormatter'
import AnimatedCounter from 'components/AnimatedCounter'
import ChapterMap from 'components/ChapterMap'
import ItemCardList from 'components/ItemCardList'
import LeadersList from 'components/LeadersList'
import LoadingSpinner from 'components/LoadingSpinner'
import MovingLogos from 'components/LogoCarousel'
import Modal from 'components/Modal'
import MultiSearchBar from 'components/MultiSearch'
import SecondaryCard from 'components/SecondaryCard'
import TopContributors from 'components/TopContributors'
import { TruncatedText } from 'components/TruncatedText'
import { toaster } from 'components/ui/toaster'

export default function Home() {
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [data, setData] = useState<MainPageData>(null)
  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_MAIN_PAGE_DATA, {
    variables: { distinct: true },
  })

  const [geoLocData, setGeoLocData] = useState<ChapterTypeAlgolia[]>([])
  const [modalOpenIndex, setModalOpenIndex] = useState<number | null>(null)

  useEffect(() => {
    if (graphQLData) {
      setData(graphQLData)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toaster.create({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        type: 'error',
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
      const data: AlgoliaResponseType<ChapterTypeAlgolia> = await fetchAlgoliaData(
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

  const getProjectIcon = (projectType: string) => {
    switch (projectType.toLowerCase()) {
      case 'code':
        return faCode
      case 'documentation':
        return faBook
      case 'other':
        return faFileCode
      case 'tool':
        return faTag
      default:
        return faFileCode
    }
  }

  const counterData = [
    {
      label: 'Active Projects',
      value: data.statsOverview.activeProjectsStats.toString().concat('+'),
    },
    {
      label: 'Contributors',
      value: data.statsOverview.contributorsStats.toString().concat('+'),
    },
    {
      label: 'Local Chapters',
      value: data.statsOverview.activeChaptersStats.toString().concat('+'),
    },
    {
      label: 'Countries',
      value: data.statsOverview.countriesStats.toString().concat('+'),
    },
  ]

  return (
    <div className="mt-16 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <div className="pt-5 text-center sm:mb-20">
          <div className="flex flex-col items-center py-10">
            <h1 className="text-3xl font-medium tracking-tighter sm:text-5xl md:text-6xl">
              Welcome to OWASP Nest
            </h1>
            <p className="max-w-[700px] pt-6 text-muted-foreground md:text-xl">
              Your gateway to OWASP. Discover, engage, and help shape the future!
            </p>
          </div>
          <div className="mx-auto mb-8 flex max-w-2xl justify-center">
            <MultiSearchBar
              eventData={data.upcomingEvents}
              isLoaded={true}
              placeholder="Search the OWASP community"
              indexes={['chapters', 'projects', 'users']}
            />
          </div>
        </div>
        <SecondaryCard icon={faCalendar} title="Upcoming Events" className="overflow-hidden">
          <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {data.upcomingEvents.map((event: EventType, index: number) => (
              <div key={`card-${event.name}`} className="overflow-hidden">
                <div className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <button
                    className="mb-2 w-full text-left text-lg font-semibold text-blue-400 hover:underline"
                    onClick={() => setModalOpenIndex(index)}
                  >
                    <TruncatedText text={event.name} />
                  </button>
                  <div className="flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
                    <div className="mr-2 flex items-center">
                      <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                      <span>{formatDateRange(event.startDate, event.endDate)}</span>
                    </div>
                    {event.suggestedLocation && (
                      <div className="flex items-center">
                        <FontAwesomeIcon icon={faMapMarkerAlt} className="mr-1 h-4 w-4" />
                        <span>{event.suggestedLocation}</span>
                      </div>
                    )}
                  </div>
                </div>
                <Modal
                  key={`modal-${event.name}`}
                  isOpen={modalOpenIndex === index}
                  onClose={() => setModalOpenIndex(null)}
                  title={event.name}
                  summary={event.summary}
                  button={{ label: 'View Event', url: event.url }}
                  description="The event summary has been generated by AI"
                ></Modal>
              </div>
            ))}
          </div>
        </SecondaryCard>
        <div className="grid gap-4 md:grid-cols-2">
          <SecondaryCard icon={faMapMarkerAlt} title="New Chapters" className="overflow-hidden">
            <div className="space-y-4">
              {data.recentChapters.map((chapter) => (
                <div key={chapter.key} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <h3 className="mb-2 text-lg font-semibold">
                    <a href={`/chapters/${chapter.key}`} className="text-blue-400 hover:underline">
                      <TruncatedText text={chapter.name} />
                    </a>
                  </h3>
                  <div className="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
                    <div className="mr-4 flex items-center">
                      <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                      <span>{formatDate(chapter.createdAt)}</span>
                    </div>
                    <div className="mr-4 flex flex-1 items-center overflow-hidden">
                      <FontAwesomeIcon icon={faMapMarkerAlt} className="mr-2 h-4 w-4" />
                      <TruncatedText text={chapter.suggestedLocation} />
                    </div>
                  </div>

                  {chapter.leaders.length > 0 && (
                    <div className="mr-4 mt-1 flex items-center gap-x-2 text-sm text-gray-600 dark:text-gray-400">
                      {' '}
                      <FontAwesomeIcon icon={faUsers} className="h-4 w-4" />
                      <LeadersList leaders={String(chapter.leaders)} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </SecondaryCard>
          <SecondaryCard icon={faFolder} title="New Projects" className="overflow-hidden">
            <div className="space-y-4">
              {data.recentProjects.map((project) => (
                <div key={project.key} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <a href={`/projects/${project.key}`} className="text-blue-400 hover:underline">
                    <h3 className="mb-2 truncate text-wrap text-lg font-semibold md:text-nowrap">
                      <TruncatedText text={project.name} />
                    </h3>
                  </a>
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <div className="mr-4 flex items-center">
                      <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                      <span>{formatDate(project.createdAt)}</span>
                    </div>
                    <div className="mr-4 flex items-center">
                      <FontAwesomeIcon
                        icon={getProjectIcon(project.type) as IconProp}
                        className="mr-2 h-4 w-4"
                      />
                      <span>{capitalize(project.type)}</span>
                    </div>
                  </div>

                  {project.leaders.length > 0 && (
                    <div className="mr-4 mt-1 flex items-center gap-x-2 text-sm text-gray-600 dark:text-gray-400">
                      <FontAwesomeIcon icon={faUsers} className="h-4 w-4" />
                      <LeadersList leaders={String(project.leaders)} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </SecondaryCard>
        </div>
        <div className="mb-20">
          <h2 className="mb-4 text-2xl font-semibold">
            <FontAwesomeIcon icon={faGlobe} className="mr-2 h-5 w-5" />
            Chapters Worldwide
          </h2>
          <ChapterMap
            geoLocData={geoLocData}
            showLocal={false}
            style={{
              height: '400px',
              width: '100%',
              zIndex: '0',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
          />
        </div>
        <TopContributors
          icon={faUsers}
          contributors={data.topContributors}
          type="company"
          maxInitialDisplay={9}
        />
        <div className="grid-cols-2 gap-4 lg:grid">
          <ItemCardList
            title="Recent Issues"
            data={data.recentIssues}
            icon={faTriangleExclamation}
            renderDetails={(item) => (
              <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
                <div className="mr-4 flex items-center">
                  <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                  <span>{formatDate(item.createdAt)}</span>
                </div>
                {item?.commentsCount ? (
                  <div className="flex items-center">
                    <FontAwesomeIcon icon={faFileCode} className="mr-2 h-4 w-4" />
                    <span>{item.commentsCount} comments</span>
                  </div>
                ) : null}
              </div>
            )}
          />
          <ItemCardList
            title="Recent Pull Requests"
            data={data.recentPullRequests}
            icon={faCodePullRequest}
            renderDetails={(item) => (
              <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
                <div className="mr-4 flex items-center">
                  <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                  <span>{formatDate(item.createdAt)}</span>
                </div>

                {item?.author.name || item?.author.login ? (
                  <div className="flex items-center">
                    <FontAwesomeIcon icon={faUser} className="mr-2 h-4 w-4" />
                    <span>{item.author.name || item.author.login}</span>
                  </div>
                ) : null}
              </div>
            )}
          />
        </div>
        <SecondaryCard icon={faTag} title="Recent Releases" className="overflow-hidden">
          {data.recentReleases && data.recentReleases.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
              {data.recentReleases.map((item, index) => (
                <div
                  key={index}
                  className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
                >
                  <div className="flex w-full flex-col justify-between">
                    <div className="flex w-full items-center">
                      <a
                        className="flex-shrink-0 text-blue-400 hover:underline"
                        href={`/community/users/${item?.author?.login}`}
                      >
                        <img
                          src={item?.author?.avatarUrl}
                          alt={item?.author?.name}
                          className="mr-2 h-6 w-6 rounded-full"
                        />
                      </a>

                      <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                        <a
                          className="text-blue-400 hover:underline"
                          href={item?.url}
                          target="_blank"
                        >
                          {item.name}
                        </a>
                      </h3>
                    </div>
                    <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
                      <div className="mr-4 flex items-center">
                        <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                        <span>{formatDate(item.publishedAt)}</span>
                      </div>
                      <div className="flex items-center">
                        <FontAwesomeIcon icon={faTag} className="mr-2 h-4 w-4" />
                        <span>{item.tagName}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No recent releases.</p>
          )}
        </SecondaryCard>
        <SecondaryCard icon={faNewspaper} title="News & Opinions" className="overflow-hidden">
          <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
            {data.recentPosts.map((post) => (
              <div
                key={post.title}
                className="overflow-hidden rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
              >
                <h3 className="mb-1 text-lg font-semibold">
                  <a
                    href={post.url}
                    className="text-blue-400 hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <TruncatedText text={post.title} />
                  </a>
                </h3>
                <div className="mt-2 flex flex-col flex-wrap items-start text-sm text-gray-600 dark:text-gray-400 md:flex-row">
                  <div className="mr-4 flex items-center">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(post.publishedAt)}</span>
                  </div>
                  <div className="flex items-center">
                    <FontAwesomeIcon icon={faUser} className="mr-2 h-4 w-4" />
                    <span>{post.authorName}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SecondaryCard>
        <div className="grid gap-6 md:grid-cols-4">
          {counterData.map((stat, index) => (
            <SecondaryCard key={index} className="text-center">
              <div className="mb-2 text-3xl font-bold text-blue-400">
                <AnimatedCounter end={parseInt(stat.value)} duration={2} />+
              </div>
              <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
            </SecondaryCard>
          ))}
        </div>

        <div className="mb-20 mt-8">
          <SecondaryCard className="text-center">
            <h3 className="mb-4 text-2xl font-semibold">Ready to Make a Difference?</h3>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
              Join OWASP and be part of the global cybersecurity community.
            </p>
            <a
              href="https://owasp.glueup.com/organization/6727/memberships/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block rounded bg-blue-500 px-6 py-3 font-bold text-white hover:bg-blue-600"
            >
              Join OWASP
            </a>
          </SecondaryCard>
          <SecondaryCard>
            <MovingLogos sponsors={data.sponsors} />
          </SecondaryCard>
        </div>
      </div>
    </div>
  )
}
