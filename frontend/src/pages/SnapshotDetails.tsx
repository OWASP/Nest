import { useQuery } from '@apollo/client'
import { faCalendar } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { GET_SNAPSHOT_DETAILS } from 'api/queries/snapshotQueries'
import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ChapterTypeGraphQL } from 'types/chapter'
import { ProjectTypeGraphql } from 'types/project'
import { SnapshotDetailsProps } from 'types/snapshot'
import { level } from 'utils/data'
import { formatDate } from 'utils/dateFormatter'
import { getFilteredIconsGraphql, handleSocialUrls } from 'utils/utility'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import ChapterMap from 'components/ChapterMap'
import LoadingSpinner from 'components/LoadingSpinner'
import MetadataManager from 'components/MetadataManager'
import { toaster } from 'components/ui/toaster'

const SnapshotDetailsPage: React.FC = () => {
  const { id: snapshotKey } = useParams()
  const [snapshot, setSnapshot] = useState<SnapshotDetailsProps | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const navigate = useNavigate()

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_SNAPSHOT_DETAILS, {
    variables: { key: snapshotKey },
  })

  useEffect(() => {
    if (graphQLData) {
      setSnapshot(graphQLData.snapshot)
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
  }, [graphQLData, graphQLRequestError, snapshotKey])

  const renderProjectCard = (project: ProjectTypeGraphql) => {
    const params: string[] = ['forksCount', 'starsCount', 'contributorsCount']
    const filteredIcons = getFilteredIconsGraphql(project, params)

    const handleButtonClick = () => {
      navigate(`/projects/${project.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={SubmitButton}
        icons={filteredIcons}
        key={project.key}
        level={level[`${project.level.toLowerCase() as keyof typeof level}`]}
        summary={project.summary}
        title={project.name}
        topContributors={project.topContributors}
        url={`/projects/${project.key}`}
      />
    )
  }

  const renderChapterCard = (chapter: ChapterTypeGraphQL) => {
    const params: string[] = ['updatedAt']
    const filteredIcons = getFilteredIconsGraphql(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.relatedUrls)

    const handleButtonClick = () => {
      navigate(`/chapters/${chapter.key}`)
    }

    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={chapter.key}
        title={chapter.name}
        url={`/chapters/${chapter.key}`}
        summary={chapter.summary}
        icons={filteredIcons}
        topContributors={chapter.topContributors}
        button={SubmitButton}
        social={formattedUrls}
      />
    )
  }

  if (isLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!isLoading && snapshot == null) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Snapshot not found"
        message="Sorry, the snapshot you're looking for doesn't exist"
      />
    )
  }

  return (
    <MetadataManager pageTitle={snapshot.title} description={`OWASP Snapshot: ${snapshot.key}`}>
      <div className="mx-auto mt-24 min-h-screen max-w-6xl p-4">
        <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="mb-2 text-3xl font-bold text-gray-700 dark:text-gray-200">
                {snapshot.title}
              </h1>
              <div className="flex flex-wrap items-center gap-2 text-gray-600 dark:text-gray-300">
                <div className="flex items-center">
                  <FontAwesomeIcon icon={faCalendar} className="mr-1 h-4 w-4" />
                  <span>
                    {formatDate(snapshot.startAt)} - {formatDate(snapshot.endAt)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {snapshot.newChapters && snapshot.newChapters.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-6 text-2xl font-semibold text-gray-700 dark:text-gray-200">
              New Chapters
            </h2>
            <div className="mb-4">
              <ChapterMap
                geoLocData={snapshot.newChapters}
                showLocal={false}
                style={{ height: '400px', width: '100%', zIndex: '0' }}
              />
            </div>
            <div className="flex flex-col gap-6">
              {snapshot.newChapters.filter((chapter) => chapter.isActive).map(renderChapterCard)}
            </div>
          </div>
        )}

        {snapshot.newProjects && snapshot.newProjects.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold text-gray-700 dark:text-gray-200">
              New Projects
            </h2>
            <div className="flex flex-col gap-6">
              {snapshot.newProjects.filter((project) => project.isActive).map(renderProjectCard)}
            </div>
          </div>
        )}

        {snapshot.newReleases && snapshot.newReleases.length > 0 && (
          <div className="mb-8">
            <h2 className="mb-4 text-2xl font-semibold">New Releases</h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {snapshot.newReleases.map((release, index) => (
                <div
                  key={`${release.tagName}-${index}`}
                  className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
                >
                  <div className="p-4">
                    <div className="mb-3 flex items-center justify-between">
                      <div className="truncate text-lg font-medium text-gray-700 dark:text-gray-200">
                        {release.name}
                      </div>
                    </div>
                    <div className="mb-3 flex items-center gap-2">
                      <span className="truncate text-sm font-medium text-gray-700 dark:text-gray-300">
                        {release.projectName}
                      </span>
                      <span className="shrink-0 px-2.5 py-0.5 text-xs font-medium text-gray-500 dark:bg-transparent dark:text-blue-200">
                        {release.tagName}
                      </span>
                    </div>
                    <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                      <FontAwesomeIcon icon={faCalendar} className="mr-1.5 h-3 w-3" />
                      Released: {formatDate(release.publishedAt)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </MetadataManager>
  )
}

export default SnapshotDetailsPage
