import { useQuery } from '@apollo/client'
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
import { GET_PROJECT_DATA } from 'api/queries/projectQueries'
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
  const [recentReleases, setRecentReleases] = useState([])
  const [recentIssues, setRecentIssues] = useState([])

  const { data, loading: isGraphQlDataLoading } = useQuery(GET_PROJECT_DATA, {
    variables: { key: 'www-project-' + projectKey },
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

  if (isLoading || isGraphQlDataLoading)
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

  return (
    <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 mt-4 text-4xl font-bold">{project.name}</h1>
        {!project.is_active && (
          <span className="ml-2 rounded bg-red-200 px-2 py-1 text-sm text-red-800">Inactive</span>
        )}
        <p className="mb-6 text-xl">{project.description}</p>
        <SecondaryCard title="Summary">
          <p>{project.summary}</p>
        </SecondaryCard>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <SecondaryCard title="Project Details" className="gap-2 md:col-span-2">
            <p className="pb-1" >
              <strong>Type:</strong> {project.type[0].toUpperCase() + project.type.slice(1)}
            </p>
            <p className="pb-1" >
              <strong>Level:</strong> {project.level[0].toUpperCase() + project.level.slice(1)}
            </p>
          
            <p className="pb-1" >
              <strong>Project Leaders:</strong> {project.leaders.join(', ')}
            </p>
            <p className="pb-1" >
              <strong>Last Updated:</strong> {formatDate(project.updated_at)}
            </p>
            <p className="pb-1" >
              <strong>URL:</strong>{' '}
              <a href={project.url} className="hover:underline dark:text-sky-600">
                {project.url}
              </a>
            </p>
          </SecondaryCard>
          <SecondaryCard title="Statistics">

            <InfoBlock className="pb-1"  icon={faUsers} value={`${project.contributors_count} Contributors`}/>
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
        </SecondaryCard>
        <SecondaryCard title="Recent Releases">
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
        </SecondaryCard>
      </div>
    </div>
  )
}

export default ProjectDetailsPage
