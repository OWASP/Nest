import { useQuery } from '@apollo/client'
import {
  faBook,
  faCalendar,
  faCode,
  faExclamationCircle,
  faFileCode,
  faGlobe,
  faMapMarkerAlt,
  faTag,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { GET_MAIN_PAGE_DATA } from 'api/queries/homeQueries'
import { toast } from 'hooks/useToast'
import { useEffect, useState } from 'react'
import { AlgoliaResponseType } from 'types/algolia'
import { ChapterTypeAlgolia } from 'types/chapter'
import { MainPageData } from 'types/home'
import { formatDate } from 'utils/dateFormatter'
import AnimatedCounter from 'components/AnimatedCounter'
import ChapterMap from 'components/ChapterMap'
import ItemCardList from 'components/ItemCardList'
import LoadingSpinner from 'components/LoadingSpinner'
import SearchComponent from 'components/Search'
import SecondaryCard from 'components/SecondaryCard'
import TopContributors from 'components/ToggleContributors'

export default function Home() {
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [data, setData] = useState<MainPageData>(null)
  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_MAIN_PAGE_DATA)
  const [geoLocData, setGeoLocData] = useState<ChapterTypeAlgolia[]>([])

  useEffect(() => {
    if (graphQLData) {
      setData(graphQLData)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      toast({
        description: 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        variant: 'destructive',
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
        filterKey: '',
        hitsPerPage: 25,
      }
      const data: AlgoliaResponseType<ChapterTypeAlgolia> = await fetchAlgoliaData(
        searchParams.indexName,
        searchParams.query,
        searchParams.currentPage,
        searchParams.filterKey,
        searchParams.hitsPerPage
      )
      setGeoLocData(data.hits)
    }
    fetchData()
  }, [])

  if (isLoading || !data || !geoLocData) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  const counterData = [
    {
      label: 'Active Projects',
      value: data.countsOverview.activeProjectsCount.toString().concat('+'),
    },
    {
      label: 'Contributors',
      value: data.countsOverview.contributorsCount.toString().concat('+'),
    },
    {
      label: 'Local Chapters',
      value: data.countsOverview.chaptersCount.toString().concat('+'),
    },
    {
      label: 'Countries',
      value: data.countsOverview.countriesCount.toString().concat('+'),
    },
  ]

  return (
    <div className="mx-auto min-h-screen max-w-6xl text-white">
      <div className="mb-20 pt-20 text-center">
        <div className="flex flex-col items-center py-10">
          <h1 className="text-3xl font-medium tracking-tighter sm:text-5xl md:text-6xl">
            Welcome to OWASP Community
          </h1>
          <p className="max-w-[700px] pt-6 text-muted-foreground md:text-xl">
            OWASP is a nonprofit organization that aims to improve software security through
            education, tools, and collaboration.
          </p>
        </div>
        <div className="mx-auto mb-8 flex max-w-2xl justify-center">
          <SearchComponent
            onSearch={() => {}}
            placeholder="Search for projects, chapters, and more..."
            indexName="projects"
            onReady={() => {}}
          />
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <SecondaryCard title="Recent Projects">
          <div className="space-y-4">
            {data.recentProjects.map((project) => (
              <div key={project.key} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                <h3 className="mb-2 text-lg font-semibold">
                  <a href={`/projects/${project.key}`} className="hover:underline">
                    {project.name}
                  </a>
                </h3>
                <div className="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-300">
                  <div className="mr-4 flex items-center">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(project.createdAt)}</span>
                  </div>
                  <div className="mr-4 flex items-center">
                    <FontAwesomeIcon
                      icon={project.type === 'DOCUMENTATION' ? faBook : faCode}
                      className="mr-2 h-4 w-4"
                    />
                    <span>{project.type}</span>
                  </div>
                  <div className="mr-4 flex items-center">
                    <FontAwesomeIcon icon={faExclamationCircle} className="mr-2 h-4 w-4" />
                    <span>{project.openIssuesCount} open issues</span>
                  </div>
                  <div className="flex items-center">
                    <FontAwesomeIcon icon={faCode} className="mr-2 h-4 w-4" />
                    <span>
                      {project.repositoriesCount}{' '}
                      {project.repositoriesCount === 1 ? 'repository' : 'repositories'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SecondaryCard>
        <SecondaryCard title="Recent Chapters">
          <div className="space-y-4">
            {data.recentChapters.map((chapter) => (
              <div key={chapter.key} className="rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                <h3 className="mb-2 text-lg font-semibold">
                  <a href={`/chapters/${chapter.key}`} className="hover:underline">
                    {chapter.name}
                  </a>
                </h3>
                <div className="flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-300">
                  <div className="mr-4 flex items-center">
                    <FontAwesomeIcon icon={faMapMarkerAlt} className="mr-2 h-4 w-4" />
                    <span>{chapter.suggestedLocation}</span>
                  </div>
                  <div className="mr-4 flex items-center">
                    <FontAwesomeIcon icon={faGlobe} className="mr-2 h-4 w-4" />
                    <span>{chapter.region}</span>
                  </div>
                  <div className="flex items-center">
                    <FontAwesomeIcon icon={faUsers} className="mr-2 h-4 w-4" />
                    <span>{chapter.topContributors.length} top contributors</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SecondaryCard>
      </div>
      <TopContributors contributors={data.topContributors} maxInitialDisplay={6} />
      <div className="mb-20">
        <h2 className="mb-6 text-3xl font-semibold">OWASP Chapters Worldwide</h2>
        <ChapterMap
          geoLocData={geoLocData}
          style={{ height: '400px', width: '100%', zIndex: '0' }}
        />
      </div>
      <>
        <ItemCardList
          title="Recent Issues"
          data={data.recentIssue}
          renderDetails={(item) => (
            <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
              <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
              <span>{formatDate(item.createdAt)}</span>
              <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
              <span>{item.commentsCount} comments</span>
            </div>
          )}
        />
        <ItemCardList
          title="Recent Releases"
          data={data.recentRelease}
          renderDetails={(item) => (
            <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
              <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
              <span>{formatDate(item.publishedAt)}</span>
              <FontAwesomeIcon icon={faTag} className="ml-4 mr-2 h-4 w-4" />
              <span>{item.tagName}</span>
            </div>
          )}
        />
      </>
      <div className="mb-20 grid gap-6 md:grid-cols-4">
        {counterData.map((stat, index) => (
          <SecondaryCard key={index} className="text-center">
            <div className="mb-2 text-3xl font-bold text-blue-400">
              <AnimatedCounter end={parseInt(stat.value)} duration={2} />+
            </div>
            <div className="text-gray-300">{stat.label}</div>
          </SecondaryCard>
        ))}
      </div>
    </div>
  )
}
