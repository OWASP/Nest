import { useQuery } from '@apollo/client'
import {
  faCodeFork,
  faStar,
  faUsers,
  faBook,
  faCode,
  faFileCode,
  faCalendar,
  faTag,
  faChevronDown,
  faChevronUp,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { GET_PROJECT_BY_KEY } from 'api/queries/projectQueries'
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import LoadingSpinner from 'components/LoadingSpinner'

export const formatDate = (input: number | string) => {
  const date =
    typeof input === 'number'
      ? new Date(input * 1000) // Unix timestamp in seconds
      : new Date(input) // ISO date string

  if (isNaN(date.getTime())) {
    throw new Error('Invalid date')
  }

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [project, setProject] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showAllContributors, setShowAllContributors] = useState(false)
  const [showAllLanguages, setShowAllLanguages] = useState(false)
  const [showAllTopics, setShowAllTopics] = useState(false)
  const [recentReleases, setRecentReleases] = useState([])
  const [recentIssues, setRecentIssues] = useState([])

  const { data, loading } = useQuery(GET_PROJECT_BY_KEY, {
    variables: { key: 'www-project-' + projectKey },
    skip: !projectKey,
  })

  useEffect(() => {
    const fetchProjectData = async () => {
      setIsLoading(true)
      const { hits } = await fetchAlgoliaData('projects', projectKey, 1, projectKey)
      if (hits && hits.length > 0) {
        setProject(hits[0])
      }
      setIsLoading(false)
    }

    fetchProjectData()
  }, [projectKey])

  useEffect(() => {
    if (data) {
      setRecentReleases(data?.project?.recentReleases)
      setRecentIssues(data?.project?.recentIssues)
    }
  }, [data])

  const navigate = useNavigate()

  if (isLoading || loading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!project)
    return (
      <ErrorDisplay
        statusCode={404}
        title="Project not found"
        message="Sorry, the project you're looking for doesn't exist"
      />
    )

  const toggleContributors = () => setShowAllContributors(!showAllContributors)
  const toggleLanguages = () => setShowAllLanguages(!showAllLanguages)
  const toggleTopics = () => setShowAllTopics(!showAllTopics)

  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">{project.name}</h1>
        <p className="mb-6 text-xl">{project.description}</p>
        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">Summary</h2>
          <p>{project.summary}</p>
        </div>
        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800 md:col-span-2">
            <h2 className="mb-4 text-2xl font-semibold">Project Details</h2>
            <p>
              <strong>Type:</strong> {project.type[0].toUpperCase() + project.type.slice(1)}
            </p>
            <p>
              <strong>Level:</strong> {project.level[0].toUpperCase() + project.level.slice(1)}
            </p>
            <p>
              <strong>Organization:</strong> {project.organizations}
            </p>
            <div>
              <p>
                <strong>Project Leaders:</strong> {project.leaders.join(', ')}
              </p>
            </div>
            <p>
              <strong>Last Updated:</strong> {formatDate(project.updated_at)}
            </p>
            <p>
              <strong>URL:</strong>{' '}
              <a href={project.url} className="hover:underline dark:text-sky-600">
                {project.url}
              </a>
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">Statistics</h2>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faUsers} className="mr-2" />{' '}
              <span>{project.contributors_count} Contributors</span>
            </div>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faCodeFork} className="mr-2" />{' '}
              <span>{project.forks_count} Forks</span>
            </div>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faStar} className="mr-2" />{' '}
              <span>{project.stars_count} Stars</span>
            </div>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faBook} className="mr-2" />{' '}
              <span>{project.issues_count} Issues</span>
            </div>
            <div className="flex items-center">
              <FontAwesomeIcon icon={faCode} className="mr-2" />{' '}
              <span>{project.repositories_count} Repositories</span>
            </div>
          </div>
        </div>
        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">Languages</h2>
            <div className="flex flex-wrap gap-2">
              {(showAllLanguages ? project.languages : project.languages.slice(0, 10)).map(
                (lang, index) => (
                  <span
                    key={index}
                    className="rounded-lg border border-gray-400 px-2 py-1 text-sm dark:border-gray-300"
                  >
                    {lang}
                  </span>
                )
              )}
            </div>
            {project.languages.length > 10 && (
              <button
                onClick={toggleLanguages}
                className="mt-4 flex items-center text-[#1d7bd7] hover:underline dark:text-sky-600"
              >
                {showAllLanguages ? (
                  <>
                    Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
                  </>
                ) : (
                  <>
                    Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
                  </>
                )}
              </button>
            )}
          </div>

          <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">Topics</h2>
            <div className="flex flex-wrap gap-2">
              {(showAllTopics ? project.topics : project.topics.slice(0, 10)).map(
                (topic, index) => (
                  <span
                    key={index}
                    className="rounded-lg border border-gray-400 px-2 py-1 text-sm dark:border-gray-300"
                  >
                    {topic}
                  </span>
                )
              )}
            </div>
            {project.topics.length > 10 && (
              <button
                onClick={toggleTopics}
                className="mt-4 flex items-center text-[#1d7bd7] hover:underline dark:text-sky-600"
              >
                {showAllTopics ? (
                  <>
                    Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
                  </>
                ) : (
                  <>
                    Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">Top Contributors</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
            {(showAllContributors
              ? project.top_contributors
              : project.top_contributors.slice(0, 6)
            ).map((contributor, index) => (
              <div
                key={index}
                className="flex cursor-pointer items-center"
                onClick={() => {
                  navigate(`/community/users/${contributor.login}`)
                }}
              >
                <img
                  src={contributor.avatar_url}
                  alt={contributor.name || contributor.login}
                  className="mr-3 h-10 w-10 rounded-full"
                />
                <div>
                  <p className="font-semibold">{contributor.name || contributor.login}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {contributor.contributions_count} contributions
                  </p>
                </div>
              </div>
            ))}
          </div>
          {project.top_contributors.length > 5 && (
            <button
              onClick={toggleContributors}
              className="mt-4 flex items-center text-[#1d7bd7] hover:underline dark:text-sky-600"
            >
              {showAllContributors ? (
                <>
                  Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
                </>
              ) : (
                <>
                  Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
                </>
              )}
            </button>
          )}
        </div>

        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">Recent Issues</h2>
          {recentIssues && recentIssues.length > 0 ? (
            <div className="h-64 overflow-y-auto pr-2">
              {recentIssues.map((issue, index) => (
                <div key={index} className="mb-4 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <h3 className="font-semibold">{issue.title}</h3>
                  <div className="mt-2 flex items-center">
                    <img
                      src={issue?.author?.avatarUrl}
                      alt={issue?.author?.name}
                      className="mr-2 h-6 w-6 rounded-full"
                    />
                    <span className="text-sm">{issue?.author?.name}</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(issue.createdAt)}</span>
                    <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
                    <span>{issue.commentsCount} comments</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No recent issues.</p>
          )}
        </div>

        <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">Recent Releases</h2>
          {recentReleases && recentReleases.length > 0 ? (
            <div className="h-64 overflow-y-auto pr-2">
              {recentReleases.map((release, index) => (
                <div key={index} className="mb-4 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <h3 className="font-semibold">{release.name}</h3>
                  <div className="mt-2 flex items-center">
                    <img
                      src={release?.author?.avatarUrl}
                      alt={release?.author?.name}
                      className="mr-2 h-6 w-6 rounded-full"
                    />
                    <span className="text-sm">{release?.author?.name}</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(release.publishedAt)}</span>
                    <FontAwesomeIcon icon={faTag} className="ml-4 mr-2 h-4 w-4" />
                    <span>{release.tagName}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No recent releases.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProjectDetailsPage
