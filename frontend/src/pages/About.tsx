import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useEffect, useState } from 'react'
import { ProjectTypeAlgolia } from 'types/project'
import { aboutText, leaders, roadmap } from 'utils/aboutData'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import AnimatedCounter from 'components/AnimatedCounter'
import LoadingSpinner from 'components/LoadingSpinner'
import Markdown from 'components/MarkdownWrapper'
import SecondaryCard from 'components/SecondaryCard'
import TopContributors from 'components/ToggleContributors'
import UserCard from 'components/UserCard'

const About = () => {
  const [projectNestData, setProjectNestData] = useState<ProjectTypeAlgolia | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const searchParams = {
          indexName: 'projects',
          query: '',
          currentPage: 1,
          hitsPerPage: 10,
          facetFilters: ['idx_key:nest'],
        }
        const data = await fetchAlgoliaData<ProjectTypeAlgolia>(
          searchParams.indexName,
          searchParams.query,
          searchParams.currentPage,
          searchParams.hitsPerPage,
          searchParams.facetFilters
        )

        if (data.hits.length > 0) {
          setProjectNestData(data.hits[0])
        }
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  if (!projectNestData) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-gray-500">
        No data available.
      </div>
    )
  }

  return (
    <div
      data-testid="about-page"
      className="mt-16 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300"
    >
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">About</h1>
        {aboutText && (
          <SecondaryCard title="Project history">
            <Markdown content={aboutText} />
          </SecondaryCard>
        )}

        <SecondaryCard title="Leaders">
          <div className="flex w-full flex-col items-center justify-around overflow-hidden md:flex-row">
            {leaders.map((leader) => (
              <UserCard
                key={leader.github_profile_url}
                avatar={leader.avatar_url}
                company={leader.company}
                name={leader.name}
                button={{
                  label: 'View GitHub profile',
                  icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
                  onclick: () =>
                    window.open(leader.github_profile_url, '_blank', 'noopener,noreferrer'),
                }}
                email=""
                location=""
                className="h-64 w-40 bg-inherit"
              />
            ))}
          </div>
        </SecondaryCard>

        {projectNestData.top_contributors && (
          <TopContributors
            contributors={projectNestData.top_contributors}
            maxInitialDisplay={6}
            type="contributor"
          />
        )}

        <SecondaryCard title="Roadmap">
          <ul>
            {roadmap.map((item) => (
              <li key={item} className="mb-4 flex flex-row items-center gap-2">
                <div className="h-2 w-2 flex-shrink-0 rounded-full bg-white"></div>
                {item}
              </li>
            ))}
          </ul>
        </SecondaryCard>

        <div className="grid gap-6 md:grid-cols-4">
          {[
            { label: 'Contributors', value: projectNestData.contributors_count },
            { label: 'Issues', value: projectNestData.issues_count },
            { label: 'Forks', value: projectNestData.forks_count },
            { label: 'Stars', value: projectNestData.stars_count },
          ].map((stat, index) => (
            <SecondaryCard key={index} className="text-center">
              <div className="mb-2 text-3xl font-bold text-blue-400">
                <AnimatedCounter end={Math.floor(stat.value / 10) * 10} duration={2} />+
              </div>
              <div className="text-gray-600 dark:text-gray-300">{stat.label}</div>
            </SecondaryCard>
          ))}
        </div>
      </div>
    </div>
  )
}

export default About
