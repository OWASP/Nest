import {
  faBook,
  faCalendar,
  faCode,
  faCodeFork,
  faFileCode,
  faStar,
  faTag,
  faUsers,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { formatDate } from 'utils/dateFormatter'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import InfoBlock from 'components/InfoBlock'
import LoadingSpinner from 'components/LoadingSpinner'
import SecondaryCard from 'components/SecondaryCard'
import TopContributors from 'components/ToggleContributors'
import ToggleableList from 'components/ToogleList'

const ProjectDetailsPage = () => {
  const { projectKey } = useParams()
  const [project, setProject] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchProjectData = async () => {
      setIsLoading(true)
      try {
        const { hits } = await fetchAlgoliaData('projects', projectKey, 1, projectKey)
        if (hits && hits.length > 0) {
          setProject(hits[0])
        }
      } catch (error) {
        return error
      } finally {
        setIsLoading(false)
      }
    }

    fetchProjectData()
  }, [projectKey])

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )
  }

  if (!project) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Project not found"
        message="Sorry, the project you're looking for doesn't exist."
      />
    )
  }

  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">{project.name}</h1>
        {!project.is_active && (
          <span className="ml-2 rounded bg-red-200 px-2 py-1 text-sm text-red-800">Inactive</span>
        )}
        <p className="mb-6 text-xl">{project.description}</p>

        <div className="mb-8 rounded-lg bg-gray-100 p-6 shadow-md dark:bg-gray-800">
          <h2 className="mb-4 text-2xl font-semibold">Summary</h2>
          <p>{project.summary}</p>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
          <SecondaryCard title="Project Details" className="md:col-span-2">
            <p>
              <strong>Type:</strong> {project.type[0].toUpperCase() + project.type.slice(1)}
            </p>
            <p>
              <strong>Level:</strong> {project.level[0].toUpperCase() + project.level.slice(1)}
            </p>
            <p>
              <strong>Organization:</strong> {project.organizations}
            </p>
            <p>
              <strong>Project Leaders:</strong> {project.leaders.join(', ')}
            </p>
            <p>
              <strong>Last Updated:</strong> {formatDate(project.updated_at)}
            </p>
            <p>
              <strong>URL:</strong>{' '}
              <a href={project.url} className="hover:underline dark:text-sky-600">
                {project.url}
              </a>
            </p>
          </SecondaryCard>

          <SecondaryCard title="Statistics">
            <InfoBlock
              className="pb-1"
              icon={faUsers}
              value={`${project.contributors_count} Contributors`}
            />
            <InfoBlock className="pb-1" icon={faCodeFork} value={`${project.forks_count} Forks`} />
            <InfoBlock className="pb-1" icon={faStar} value={`${project.stars_count} Stars`} />
            <InfoBlock className="pb-1" icon={faBook} value={`${project.issues_count} Issues`} />
            <InfoBlock
              className="pb-1"
              icon={faCode}
              value={`${project.repositories_count} Repositories`}
            />
          </SecondaryCard>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          <ToggleableList items={project.languages} label="Languages" />
          <ToggleableList items={project.topics} label="Topics" />
        </div>

        <TopContributors contributors={project.top_contributors} maxInitialDisplay={6} />

        <SecondaryCard title="Recent Issues">
          {project.issues && project.issues.length > 0 ? (
            <div className="h-64 overflow-y-auto pr-2">
              {project.issues.map((issue, index) => (
                <div key={index} className="mb-4 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
                  <h3 className="font-semibold">
                    <a
                      href={
                        issue.repository &&
                        `https://github.com/OWASP/${issue.repository.key}/issues/${issue.number}`
                      }
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#1d7bd7] hover:underline dark:text-sky-600"
                    >
                      {issue.title}
                    </a>
                  </h3>
                  <div className="mt-2 flex items-center">
                    <a
                      href={`https://nest.owasp.dev/community/users/${issue.author.key}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center"
                    >
                      <img
                        src={issue.author.avatar_url}
                        alt={issue.author.name}
                        className="mr-2 h-6 w-6 rounded-full"
                      />
                      <span className="text-sm">{issue.author.name}</span>
                    </a>
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
        </SecondaryCard>

        <SecondaryCard title="Recent Releases">
          {project.releases && project.releases.length > 0 ? (
            <div className="h-64 overflow-y-auto pr-2">
              {project.releases.map((release, index) => (
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
        </SecondaryCard>
      </div>
    </div>
  )
}

export default ProjectDetailsPage
