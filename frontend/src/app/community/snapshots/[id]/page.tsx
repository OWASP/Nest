'use client'
import { useQuery } from '@apollo/client/react'
import { useRouter, useParams } from 'next/navigation'
import React, { useEffect } from 'react'
import { FaCalendar, FaRightToBracket } from 'react-icons/fa6'
import { handleAppError, ErrorDisplay } from 'app/global-error'
import { GetSnapshotDetailsDocument } from 'types/__generated__/snapshotQueries.generated'
import type { Chapter } from 'types/chapter'
import type { Project } from 'types/project'
import { level } from 'utils/data'
import { formatDate } from 'utils/dateFormatter'
import { getFilteredIcons, handleSocialUrls } from 'utils/utility'
import Card from 'components/Card'
import ChapterMapWrapper from 'components/ChapterMapWrapper'
import LoadingSpinner from 'components/LoadingSpinner'
import Release from 'components/Release'

const SnapshotDetailsPage: React.FC = () => {
  const { id: snapshotKey } = useParams<{ id: string }>()
  const router = useRouter()

  const {
    data,
    error: graphQLRequestError,
    loading: isLoading,
  } = useQuery(GetSnapshotDetailsDocument, {
    variables: { key: snapshotKey },
  })

  const snapshot = data?.snapshot

  useEffect(() => {
    if (graphQLRequestError) {
      handleAppError(graphQLRequestError)
    }
  }, [graphQLRequestError, snapshotKey])

  const renderProjectCard = (project: Project) => {
    const params: string[] = ['forksCount', 'starsCount', 'contributorsCount']
    const filteredIcons = getFilteredIcons(project, params)

    const handleButtonClick = () => {
      router.push(`/projects/${project.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FaRightToBracket className="h-4 w-4" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
        cardKey={project.key}
        icons={filteredIcons}
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
      icon: <FaRightToBracket className="h-4 w-4" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        button={submitButton}
        cardKey={chapter.key}
        icons={filteredIcons}
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

  if (graphQLRequestError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error loading snapshot"
        message="An error occurred while loading the snapshot data"
      />
    )
  }

  if (!data || !snapshot) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="Snapshot not found"
        message="Sorry, the snapshot you're looking for doesn't exist"
      />
    )
  }

  return (
    <div className="mx-auto min-h-screen max-w-6xl p-4">
      <div className="mt-8 mb-8 rounded-lg border-1 border-gray-200 bg-white p-6 shadow-xs dark:border-gray-700 dark:bg-gray-800">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="mb-2 text-3xl font-bold text-gray-700 dark:text-gray-200">
              {snapshot.title}
            </h1>
            <div className="flex flex-wrap items-center gap-2 text-gray-800 dark:text-gray-300">
              <div className="flex items-center">
                <FaCalendar className="mr-1 h-4 w-4" />
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
              showLocationSharing={true}
              style={{ height: '400px', width: '100%', zIndex: '0' }}
            />
          </div>
          <div className="flex flex-col gap-6">
            {snapshot.newChapters
              .filter((chapter) => chapter.isActive)
              .map((chapter) => (
                <React.Fragment key={chapter.key}>{renderChapterCard(chapter)}</React.Fragment>
              ))}
          </div>
        </div>
      )}

      {snapshot.newProjects && snapshot.newProjects.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 text-2xl font-semibold text-gray-700 dark:text-gray-200">
            New Projects
          </h2>
          <div className="flex flex-col gap-6">
            {snapshot.newProjects
              .filter((project) => project.isActive)
              .map((project) => (
                <React.Fragment key={project.key}>{renderProjectCard(project)}</React.Fragment>
              ))}
          </div>
        </div>
      )}

      {snapshot.newReleases && snapshot.newReleases.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-4 text-2xl font-semibold text-gray-700 dark:text-gray-200">
            New Releases
          </h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {snapshot.newReleases.map((release, index) => {
              return (
                <Release
                  key={release.id || `${release.tagName}-${release.repositoryName}-${index}`}
                  release={release}
                  showAvatar={true}
                  index={index}
                />
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default SnapshotDetailsPage
