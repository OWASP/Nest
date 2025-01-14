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
  faUser,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import LoadingSpinner from 'components/LoadingSpinner'

export const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleDateString('en-US', {
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

  if (isLoading)
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
    <div className="mt-20 min-h-screen bg-white p-8 text-gray-900 dark:bg-[#212529] dark:text-white">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-4xl font-bold">{project.idx_name}</h1>
        <p className="mb-6 text-xl">{project.idx_description}</p>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">Project Details</h2>
            <p>
              <strong>Type:</strong> {project.idx_type}
            </p>
            <p>
              <strong>Level:</strong> {project.idx_level}
            </p>
            <p>
              <strong>Organization:</strong> {project.idx_organizations}
            </p>
            <div>
              <p>
                {' '}
                <strong>Project Leaders:</strong>
                <span className="ml-2 gap-2">
                  {project.idx_leaders.map((leader, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center rounded-full bg-blue-200 px-3 py-0.5 text-sm font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                    >
                      <FontAwesomeIcon icon={faUser} className="mr-1.5 h-3 w-3" />
                      {leader}
                    </span>
                  ))}
                </span>
              </p>
            </div>
            <p>
              <strong>Last Updated:</strong> {formatDate(project.idx_updated_at)}
            </p>
            <p>
              <strong>URL:</strong>{' '}
              <a
                href={project.idx_url}
                className="text-blue-600 hover:underline dark:text-blue-400"
              >
                {project.idx_url}
              </a>
            </p>
          </div>

          <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">Statistics</h2>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faUsers} className="mr-2" />{' '}
              <span>{project.idx_contributors_count} Contributors</span>
            </div>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faCodeFork} className="mr-2" />{' '}
              <span>{project.idx_forks_count} Forks</span>
            </div>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faStar} className="mr-2" />{' '}
              <span>{project.idx_stars_count} Stars</span>
            </div>
            <div className="mb-2 flex items-center">
              <FontAwesomeIcon icon={faBook} className="mr-2" />{' '}
              <span>{project.idx_issues_count} Issues</span>
            </div>
            <div className="flex items-center">
              <FontAwesomeIcon icon={faCode} className="mr-2" />{' '}
              <span>{project.idx_repositories_count} Repositories</span>
            </div>
          </div>
        </div>

        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">Summary</h2>
          <p>{project.idx_summary}</p>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          <div className="rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
            <h2 className="mb-4 text-2xl font-semibold">Languages</h2>
            <div className="flex flex-wrap gap-2">
              {(showAllLanguages ? project.idx_languages : project.idx_languages.slice(0, 10)).map(
                (lang, index) => (
                  <span
                    key={index}
                    className="rounded-full bg-blue-500 px-2 py-1 text-sm text-white"
                  >
                    {lang}
                  </span>
                )
              )}
            </div>
            {project.idx_languages.length > 10 && (
              <button
                onClick={toggleLanguages}
                className="mt-4 flex items-center text-blue-600 hover:underline dark:text-blue-400"
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
              {(showAllTopics ? project.idx_topics : project.idx_topics.slice(0, 10)).map(
                (topic, index) => (
                  <span
                    key={index}
                    className="rounded-full border border-gray-400 px-2 py-1 text-sm dark:border-gray-300"
                  >
                    {topic}
                  </span>
                )
              )}
            </div>
            {project.idx_topics.length > 10 && (
              <button
                onClick={toggleTopics}
                className="mt-4 flex items-center text-blue-600 hover:underline dark:text-blue-400"
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
              ? project.idx_top_contributors
              : project.idx_top_contributors.slice(0, 5)
            ).map((contributor, index) => (
              <div key={index} className="flex items-center">
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
          {project.idx_top_contributors.length > 5 && (
            <button
              onClick={toggleContributors}
              className="mt-4 flex items-center text-blue-600 hover:underline dark:text-blue-400"
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
          {project.idx_issues && project.idx_issues.length > 0 ? (
            <div className="h-64 overflow-y-auto pr-2">
              {project.idx_issues.map((issue, index) => (
                <div key={index} className="mb-4 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <h3 className="font-semibold">{issue.title}</h3>
                  <div className="mt-2 flex items-center">
                    <img
                      src={issue.author.avatar_url}
                      alt={issue.author.name}
                      className="mr-2 h-6 w-6 rounded-full"
                    />
                    <span className="text-sm">{issue.author.name}</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(issue.created_at)}</span>
                    <FontAwesomeIcon icon={faFileCode} className="ml-4 mr-2 h-4 w-4" />
                    <span>{issue.comments_count} comments</span>
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
          {project.idx_releases && project.idx_releases.length > 0 ? (
            <div className="h-64 overflow-y-auto pr-2">
              {project.idx_releases.map((release, index) => (
                <div key={index} className="mb-4 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <h3 className="font-semibold">{release.name}</h3>
                  <div className="mt-2 flex items-center">
                    <img
                      src={release.author.avatar_url}
                      alt={release.author.name}
                      className="mr-2 h-6 w-6 rounded-full"
                    />
                    <span className="text-sm">{release.author.name}</span>
                  </div>
                  <div className="mt-2 flex items-center text-sm text-gray-600 dark:text-gray-400">
                    <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
                    <span>{formatDate(release.published_at)}</span>
                    <FontAwesomeIcon icon={faTag} className="ml-4 mr-2 h-4 w-4" />
                    <span>{release.tag_name}</span>
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
