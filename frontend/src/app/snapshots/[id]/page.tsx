'use client'
import { useQuery } from '@apollo/client'
import { faCalendar } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter, useParams } from 'next/navigation'
import React, { useState, useEffect } from 'react'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GET_SNAPSHOT_DETAILS } from 'server/queries/snapshotQueries'
import type { Chapter } from 'types/chapter'
import type { Project } from 'types/project'
import type { SnapshotDetails } from 'types/snapshot'
import { level } from 'utils/data'
import { formatDate } from 'utils/dateFormatter'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import LoadingSpinner from 'components/LoadingSpinner'
import PageLayout from 'components/PageLayout'

const SnapshotDetailsPage: React.FC = () => {
  const { id: snapshotKey } = useParams()
  const [snapshot, setSnapshot] = useState<SnapshotDetails | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const router = useRouter()

  const { data: graphQLData, error: graphQLRequestError } = useQuery(GET_SNAPSHOT_DETAILS, {
    variables: { key: snapshotKey },
  })

  useEffect(() => {
    if (graphQLData) {
      setSnapshot(graphQLData.snapshot)
      setIsLoading(false)
    }
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
      setIsLoading(false)
    }
  }, [graphQLData, graphQLRequestError, snapshotKey])

  const renderProjectCard = (project: Project) => {
    const params: string[] = ['forksCount', 'starsCount', 'contributorsCount']
    const filteredIcons = getFilteredIcons(project, params)

    const handleButtonClick = () => {
      router.push(`/projects/${project.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
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

  const renderChapterCard = (chapter: Chapter) => {
    const params: string[] = ['updatedAt']
    const filteredIcons = getFilteredIcons(chapter, params)
    const formattedUrls = handleSocialUrls(chapter.relatedUrls)

    const handleButtonClick = () => {
      router.push(`/chapters/${chapter.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
        icons={filteredIcons}
        key={chapter.key}
        social={formattedUrls}
        summary={chapter.summary}
        title={chapter.name}
        url={`/chapters/${chapter.key}`}
      />
    )
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

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
    <PageLayout breadcrumbItems={{ title: snapshot?.title || 'Snapshot Details' }}>
      <div className="mx-auto min-h-screen max-w-6xl p-4">
        <div className="mb-8 mt-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
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
              <ChapterMapWrapper
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
    </PageLayout>
  )
}

export default SnapshotDetailsPage
